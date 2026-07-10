#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import threading
import shutil
import warnings

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

def kill_lock_process():
    try:
        for cmd in ["apt", "dpkg"]:
            result = subprocess.run(["pgrep", cmd], capture_output=True, text=True)
            if result.stdout:
                for pid in result.stdout.strip().split():
                    try:
                        subprocess.run(["kill", "-9", pid], capture_output=True)
                    except:
                        pass
        return True
    except:
        return False

def clear_lock_files():
    try:
        lock_files = [
            "/data/data/com.termux/files/usr/var/lib/dpkg/lock-frontend",
            "/data/data/com.termux/files/usr/var/lib/dpkg/lock",
            "/data/data/com.termux/cache/apt/archives/lock"
        ]
        for lock in lock_files:
            if os.path.exists(lock):
                try:
                    os.remove(lock)
                except:
                    pass
        return True
    except:
        return False

def check_termux_pkg(pkg):
    try:
        result = subprocess.check_output(["pkg", "list-installed"], text=True, stderr=subprocess.DEVNULL)
        return pkg in result
    except:
        return False

def install_termux_pkg(pkg):
    try:
        kill_lock_process()
        clear_lock_files()
        time.sleep(0.5)
        subprocess.check_call(["pkg", "install", pkg, "-y"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        try:
            subprocess.check_call(["apt", "install", pkg, "-y"], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            return False

def check_python_pkg(pkg):
    try:
        import_name = pkg
        if pkg == "fake-useragent":
            import_name = "fake_useragent"
        elif pkg == "beautifulsoup4":
            import_name = "bs4"
        elif pkg == "yt-dlp":
            import_name = "yt_dlp"
        elif pkg == "cryptography":
            import_name = "cryptography"
        elif pkg == "phonenumbers":
            import_name = "phonenumbers"
        elif pkg == "tgcrypto":
            import_name = "tgcrypto"
        elif pkg == "pyrogram":
            import_name = "pyrogram"
        __import__(import_name)
        return True
    except ImportError:
        return False

def install_python_pkg(pkg):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--break-system-packages"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            return False

def install_nmap():
    print(f"  {Y}[*]{W} Cek nmap... ", end="")
    try:
        subprocess.run(['nmap', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{G}✓ OK{N}")
        return True
    except:
        print(f"{R}✗ MISSING{N}")
        print(f"  {Y}[*]{W} Menginstall nmap...{N}")
        try:
            kill_lock_process()
            clear_lock_files()
            time.sleep(0.5)
            subprocess.check_call(["pkg", "install", "nmap", "-y"], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  {G}[✓]{W} nmap berhasil diinstall{N}")
            return True
        except:
            try:
                subprocess.check_call(["apt", "install", "nmap", "-y"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"  {G}[✓]{W} nmap berhasil diinstall{N}")
                return True
            except:
                print(f"  {R}[✗]{W} nmap gagal diinstall (coba manual: pkg install nmap){N}")
                return False

def install_ffmpeg():
    print(f"  {Y}[*]{W} Cek ffmpeg... ", end="")
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{G}✓ OK{N}")
        return True
    except:
        print(f"{R}✗ MISSING{N}")
        print(f"  {Y}[*]{W} Menginstall ffmpeg...{N}")
        try:
            kill_lock_process()
            clear_lock_files()
            time.sleep(0.5)
            subprocess.check_call(["pkg", "install", "ffmpeg", "-y"], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  {G}[✓]{W} ffmpeg berhasil diinstall{N}")
            return True
        except:
            try:
                subprocess.check_call(["apt", "install", "ffmpeg", "-y"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"  {G}[✓]{W} ffmpeg berhasil diinstall{N}")
                return True
            except:
                print(f"  {R}[✗]{W} ffmpeg gagal diinstall (coba manual: pkg install ffmpeg){N}")
                return False

def install_termux_media():
    print(f"  {Y}[*]{W} Cek termux-media-player... ", end="")
    try:
        subprocess.run(['termux-media-player', '--help'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{G}✓ OK{N}")
        return True
    except:
        print(f"{R}✗ MISSING{N}")
        print(f"  {Y}[*]{W} Menginstall termux-media-player...{N}")
        try:
            kill_lock_process()
            clear_lock_files()
            time.sleep(0.5)
            subprocess.check_call(["pkg", "install", "termux-media-player", "-y"], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  {G}[✓]{W} termux-media-player berhasil diinstall{N}")
            return True
        except:
            print(f"  {R}[✗]{W} termux-media-player gagal diinstall (coba manual){N}")
            return False

def install_mpv():
    print(f"  {Y}[*]{W} Cek mpv... ", end="")
    try:
        subprocess.run(['mpv', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{G}✓ OK{N}")
        return True
    except:
        print(f"{R}✗ MISSING{N}")
        print(f"  {Y}[*]{W} Menginstall mpv...{N}")
        try:
            kill_lock_process()
            clear_lock_files()
            time.sleep(0.5)
            subprocess.check_call(["pkg", "install", "mpv", "-y"], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  {G}[✓]{W} mpv berhasil diinstall{N}")
            return True
        except:
            try:
                subprocess.check_call(["apt", "install", "mpv", "-y"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"  {G}[✓]{W} mpv berhasil diinstall{N}")
                return True
            except:
                print(f"  {R}[✗]{W} mpv gagal diinstall (coba manual: pkg install mpv){N}")
                return False

def create_music_folder():
    music_dirs = [
        os.path.join(os.path.expanduser("~"), "Music"),
        "/sdcard/Music",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
    ]
    for dir_path in music_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            if os.path.exists(dir_path):
                return True
        except:
            pass
    return False

def check_tgcrypto():
    try:
        import tgcrypto
        return True
    except ImportError:
        return False

def auto_install():
    global stop_animasi
    
    os.system('clear')
    
    print(f"""
{C}┌─────────────────────────────────────────────────────────────┐{N}
{C}│{W}  Sedang Mengecek & Mendownload Dependencies...          {C}│{N}
{C}│{W}  Ini sedang mengecek dependencies, tunggu aja           {C}│{N}
{C}│{W}  ga usah nanya-nanya admin                             {C}│{N}
{C}│{W}  Sampai pengecekan & mendownload selesai               {C}│{N}
{C}└─────────────────────────────────────────────────────────────┘{N}
""")
    
    time.sleep(1)
    
    if sys.version_info.major == 3 and sys.version_info.minor >= 14:
        print(f"{Y}[•] Mengecek versi Python...{N}")
        check_python_version()
    
    termux_pkgs = ["python", "python-pip", "git", "wget", "curl", "nano"]
    
    print(f"\n{Y}[•] Mengecek package Termux...{N}")
    time.sleep(0.5)
    
    missing_termux = []
    for pkg in termux_pkgs:
        print(f"  {Y}[*]{W} Cek {pkg}... ", end="")
        try:
            result = subprocess.check_output(["pkg", "list-installed"], text=True, stderr=subprocess.DEVNULL)
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
                kill_lock_process()
                clear_lock_files()
                time.sleep(0.5)
                subprocess.check_call(["pkg", "install", pkg, "-y"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"\r  {G}[✓]{W} {pkg} berhasil diinstall{N}")
            except:
                try:
                    subprocess.check_call(["apt", "install", pkg, "-y"], 
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"\r  {G}[✓]{W} {pkg} berhasil diinstall{N}")
                except:
                    print(f"\r  {R}[✗]{W} {pkg} gagal diinstall (coba manual){N}")
            
            stop_animasi = True
            t.join(timeout=0.5)
            time.sleep(0.5)
    
    python_pkgs = [
        "requests", "flask", "beautifulsoup4", "cryptography", 
        "colorama", "phonenumbers", "fake-useragent", "yt-dlp",
        "pydub", "pyrogram", "rich", "pystyle", "tgcrypto"
    ]
    
    print(f"\n{Y}[•] Mengecek package Python...{N}")
    time.sleep(0.5)
    
    missing_python = []
    for pkg in python_pkgs:
        print(f"  {Y}[*]{W} Cek {pkg}... ", end="")
        try:
            import_name = pkg
            if pkg == "fake-useragent":
                import_name = "fake_useragent"
            elif pkg == "beautifulsoup4":
                import_name = "bs4"
            elif pkg == "yt-dlp":
                import_name = "yt_dlp"
            elif pkg == "phonenumbers":
                import_name = "phonenumbers"
            elif pkg == "cryptography":
                import_name = "cryptography"
            elif pkg == "tgcrypto":
                import_name = "tgcrypto"
            elif pkg == "pyrogram":
                import_name = "pyrogram"
            __import__(import_name)
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
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--break-system-packages"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"\r  {G}[✓]{W} {pkg} berhasil diinstall{N}")
            except:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg], 
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"\r  {G}[✓]{W} {pkg} berhasil diinstall{N}")
                except:
                    print(f"\r  {R}[✗]{W} {pkg} gagal diinstall (coba manual){N}")
            
            stop_animasi = True
            t.join(timeout=0.5)
            time.sleep(0.5)
    
    print(f"\n{Y}[•] Mengecek ffmpeg...{N}")
    install_ffmpeg()
    
    print(f"\n{Y}[•] Mengecek nmap...{N}")
    install_nmap()
    
    print(f"\n{Y}[•] Mengecek mpv...{N}")
    install_mpv()
    
    print(f"\n{Y}[•] Mengecek termux-media-player...{N}")
    install_termux_media()
    
    print(f"\n{Y}[•] Membuat folder Musik...{N}")
    if create_music_folder():
        print(f"  {G}[✓]{W} Folder Musik berhasil dibuat{N}")
    else:
        print(f"  {Y}[!]{W} Folder Musik gagal dibuat, coba manual{N}")
    
    item_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "item")
    try:
        os.makedirs(item_folder, exist_ok=True)
        print(f"  {G}[✓]{W} Folder 'item' berhasil dibuat{N}")
    except:
        print(f"  {Y}[!]{W} Gagal membuat folder 'item'{N}")
    
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
        print(f"{Y}[*] Pastikan file Mikasa.py ada di folder ini{N}")
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
