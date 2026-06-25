#!/usr/bin/env python3
# MIKASA - RUNNER (Auto Install Package)

import os
import sys
import subprocess
import time
import threading

# ===================== WARNA =====================
R = '\033[1;31m'
G = '\033[1;32m'
Y = '\033[1;33m'
P = '\033[1;35m'
C = '\033[1;36m'
W = '\033[1;37m'
N = '\033[0m'

# ===================== ANIMASI =====================
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

def animasi_putar(text="Menginstall", durasi=2):
    chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
    i = 0
    start = time.time()
    while not stop_animasi and (time.time() - start) < durasi:
        sys.stdout.write(f"\r{R}  {Y}{text}{W} {R}{{ {Y}{chars[i % len(chars)]}{R} }}{N}")
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 50 + "\r")

# ===================== CEK PKG TERMUX =====================
def check_termux_pkg(pkg):
    try:
        result = subprocess.check_output(["pkg", "list-installed"], text=True)
        return pkg in result
    except:
        return False

def install_termux_pkg(pkg):
    try:
        subprocess.check_call(["pkg", "install", pkg, "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

# ===================== CEK PKG PYTHON =====================
def check_python_pkg(pkg):
    try:
        __import__(pkg)
        return True
    except ImportError:
        return False

def install_python_pkg(pkg):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

# ===================== MAIN =====================
def auto_install():
    global stop_animasi
    
    os.system('clear')
    
    print(f"""
{R}╔═╗╔═╦══╦╗╔═╦═══╦═══╦═══╗
{R}║║╚╝║╠╣╠╣║║╔╣╔═╗║╔═╗║╔═╗║
{R}║╔╗╔╗║║║║╚╝╝║║─║║╚══╣║─║║
{R}║║║║║║║║║╔╗║║╚═╝╠══╗║╚═╝║
{R}║║║║║╠╣╠╣║║╚╣╔═╗║╚═╝║╔═╗║
{R}╚╝╚╝╚╩══╩╝╚═╩╝─╚╩═══╩╝─╚╝{N}

{R}─────────────────────────────────────────────────────────────{N}
{R}       {W}MIKASA {N}v1.0.0{N}
{R}       {W}Sedang mengecek dependencies...{N}
{R}─────────────────────────────────────────────────────────────{N}
    """)
    
    time.sleep(1)
    
    # ===== CEK & INSTALL PKG TERMUX =====
    termux_pkgs = ["python", "python-pip", "git", "wget", "curl", "nano"]
    
    print(f"{Y}[•] Mengecek package Termux...{N}")
    time.sleep(0.5)
    
    missing_termux = []
    for pkg in termux_pkgs:
        print(f"  {Y}[*]{W} Cek {pkg}... ", end="")
        try:
            result = subprocess.check_output(["pkg", "list-installed"], text=True)
            if pkg in result:
                print(f"{G}✓ OK{N}")
            else:
                print(f"{R}✗ MISSING{N}")
                missing_termux.append(pkg)
        except:
            print(f"{R}✗ ERROR{N}")
            missing_termux.append(pkg)
        time.sleep(0.2)
    
    if missing_termux:
        print(f"\n{Y}[•] Menginstall package Termux yang hilang...{N}")
        for pkg in missing_termux:
            stop_animasi = False
            t = threading.Thread(target=animasi_putar, args=(f"Menginstall {pkg}", 2))
            t.daemon = True
            t.start()
            
            try:
                subprocess.check_call(["pkg", "install", pkg, "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"\r  {G}[✓]{W} {pkg} berhasil diinstall{N}")
            except:
                print(f"\r  {R}[✗]{W} {pkg} gagal diinstall (coba manual){N}")
            
            stop_animasi = True
            t.join(timeout=0.5)
            time.sleep(0.5)
    
    # ===== CEK & INSTALL PKG PYTHON =====
    python_pkgs = ["requests", "flask", "beautifulsoup4", "cryptography", "colorama", "phonenumbers", "fake-useragent"]
    
    print(f"\n{Y}[•] Mengecek package Python...{N}")
    time.sleep(0.5)
    
    missing_python = []
    for pkg in python_pkgs:
        print(f"  {Y}[*]{W} Cek {pkg}... ", end="")
        try:
            __import__(pkg)
            print(f"{G}✓ OK{N}")
        except ImportError:
            print(f"{R}✗ MISSING{N}")
            missing_python.append(pkg)
        time.sleep(0.2)
    
    if missing_python:
        print(f"\n{Y}[•] Menginstall package Python yang hilang...{N}")
        for pkg in missing_python:
            stop_animasi = False
            t = threading.Thread(target=animasi_putar, args=(f"Menginstall {pkg}", 2))
            t.daemon = True
            t.start()
            
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"\r  {G}[✓]{W} {pkg} berhasil diinstall{N}")
            except:
                print(f"\r  {R}[✗]{W} {pkg} gagal diinstall (coba manual){N}")
            
            stop_animasi = True
            t.join(timeout=0.5)
            time.sleep(0.5)
    
    # ===== SELESAI =====
    print(f"""
{G}─────────────────────────────────────────────────────────────{N}
{G}  [✓] Semua dependencies berhasil diinstall!{N}
{G}  [•] Melanjutkan ke MIKASA...{N}
{G}─────────────────────────────────────────────────────────────{N}
    """)
    
    time.sleep(2)
    
    try:
        os.execv(sys.executable, [sys.executable, "Mikasa.py"])
    except FileNotFoundError:
        print(f"{R}[!] File Mikasa.py tidak ditemukan!{N}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        auto_install()
    except KeyboardInterrupt:
        print(f"\n\n{R}[!] Keluar...{N}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{R}[!] Error: {e}{N}")
        time.sleep(2)
        sys.exit(1)
