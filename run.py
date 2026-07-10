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

def loading_bar_warna(stop_event, text="Menginstall"):
    COLORS = ['\x1b[1;91m', '\x1b[1;93m', '\x1b[1;92m', '\x1b[1;94m']
    RESET = '\x1b[0m'
    length = 10
    color_index = 0

    while not stop_event.is_set():
        for i in range(length + 1):
            if stop_event.is_set():
                break
            filled_color = COLORS[color_index % len(COLORS)] + '■' * i + RESET
            empty = '□' * (length - i)
            sys.stdout.write(f'\r {G}# {W}{text} [[{filled_color}{empty}{W}]]')
            sys.stdout.flush()
            time.sleep(0.05)
            color_index += 1

    sys.stdout.write('\r' + ' ' * 120 + '\r')
    sys.stdout.flush()

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

def pkg_update_upgrade():
    print(f"\n{G}[>]{W} Menjalankan pkg update && pkg upgrade{N}")
    time.sleep(0.5)
    try:
        kill_lock_process()
        clear_lock_files()
        time.sleep(0.5)
        
        stop_event = threading.Event()
        t = threading.Thread(target=loading_bar_warna, args=(stop_event, "pkg update"))
        t.daemon = True
        t.start()
        
        subprocess.check_call(["pkg", "update", "-y"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        stop_event.set()
        t.join(timeout=0.5)
        print(f"\r  {G}[✓]{W} pkg update selesai{N}")
        
        stop_event = threading.Event()
        t = threading.Thread(target=loading_bar_warna, args=(stop_event, "pkg upgrade"))
        t.daemon = True
        t.start()
        
        subprocess.check_call(["pkg", "upgrade", "-y"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        stop_event.set()
        t.join(timeout=0.5)
        print(f"\r  {G}[✓]{W} pkg upgrade selesai{N}")
        return True
    except:
        print(f"  {R}[✗]{W} pkg update/upgrade gagal, lanjut install...{N}")
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

def get_python_version_str():
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def find_existing_python313():
    candidates = [
        shutil.which("python3.13"),
        os.path.expanduser("~/.pyenv/versions/3.13.5/bin/python3"),
        "/data/data/com.termux/files/usr/bin/python3.13",
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None

def install_python313_via_pyenv():
    pyenv_root = os.path.expanduser("~/.pyenv")

    try:
        if not os.path.isdir(pyenv_root):
            print(f"  {Y}[*]{W} Menginstall pyenv...{N}")
            subprocess.check_call(
                ["git", "clone", "https://github.com/pyenv/pyenv.git", pyenv_root],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        pyenv_bin = os.path.join(pyenv_root, "bin", "pyenv")
        env = os.environ.copy()
        env["PYENV_ROOT"] = pyenv_root
        env["PATH"] = f"{pyenv_root}/bin:{env.get('PATH', '')}"

        installed = subprocess.run([pyenv_bin, "versions"], capture_output=True, text=True, env=env)
        if "3.13.5" not in installed.stdout:
            print(f"  {Y}[*]{W} Menyiapkan dependency build...{N}")
            build_deps = ["build-essential", "openssl", "libffi", "zlib", "readline", "sqlite", "bzip2", "ncurses"]
            for dep in build_deps:
                if not check_termux_pkg(dep):
                    install_termux_pkg(dep)

            print(f"  {Y}[*]{W} Build Python 3.13.5 dari source (bisa makan waktu 10-20 menit, jangan ditutup)...{N}")
            stop_event = threading.Event()
            t = threading.Thread(target=loading_bar_warna, args=(stop_event, "Build Python 3.13.5"))
            t.daemon = True
            t.start()

            result = subprocess.run(
                [pyenv_bin, "install", "3.13.5"],
                env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            stop_event.set()
            t.join(timeout=0.5)

            if result.returncode != 0:
                print(f"\r  {R}[✗]{W} Build Python 3.13.5 gagal (cek manual: pyenv install 3.13.5){N}")
                return None

            print(f"\r  {G}[✓]{W} Python 3.13.5 berhasil dibuild{N}")

        target = os.path.join(pyenv_root, "versions", "3.13.5", "bin", "python3")
        return target if os.path.isfile(target) else None
    except Exception as e:
        print(f"  {R}[✗]{W} Gagal setup pyenv: {e}{N}")
        return None

def ensure_python313():
    if sys.version_info[:2] < (3, 14):
        return

    print(f"\n{Y}[•] Python {get_python_version_str()} terdeteksi tidak kompatibel dengan pyrogram dkk (butuh <3.14){N}")

    target = find_existing_python313()
    if not target:
        target = install_python313_via_pyenv()

    if target:
        print(f"  {G}[✓]{W} Beralih otomatis ke {target}{N}")
        time.sleep(1)
        os.execv(target, [target] + sys.argv)
    else:
        print(f"  {R}[✗]{W} Gagal menyiapkan Python 3.13.5, lanjut pakai Python {get_python_version_str()}{N}")
        print(f"  {Y}[!]{W} Beberapa package (pyrogram) mungkin masih error{N}")
        time.sleep(2)

def install_ffmpeg():
    print(f"  {Y}[*]{W} Cek ffmpeg... ", end="")
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{G}✓ OK{N}")
        return True
    except:
        print(f"{R}✗ MISSING{N}")
        print(f"  {Y}[*]{W} Menginstall ffmpeg...{N}")
        
        stop_event = threading.Event()
        t = threading.Thread(target=loading_bar_warna, args=(stop_event, "ffmpeg"))
        t.daemon = True
        t.start()
        
        try:
            kill_lock_process()
            clear_lock_files()
            time.sleep(0.5)
            subprocess.check_call(["pkg", "install", "ffmpeg", "-y"], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            stop_event.set()
            t.join(timeout=0.5)
            print(f"\r  {G}[✓]{W} ffmpeg berhasil diinstall{N}")
            return True
        except:
            try:
                subprocess.check_call(["apt", "install", "ffmpeg", "-y"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                stop_event.set()
                t.join(timeout=0.5)
                print(f"\r  {G}[✓]{W} ffmpeg berhasil diinstall{N}")
                return True
            except:
                stop_event.set()
                t.join(timeout=0.5)
                print(f"\r  {R}[✗]{W} ffmpeg gagal diinstall (coba manual: pkg install ffmpeg){N}")
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
        
        stop_event = threading.Event()
        t = threading.Thread(target=loading_bar_warna, args=(stop_event, "nmap"))
        t.daemon = True
        t.start()
        
        try:
            kill_lock_process()
            clear_lock_files()
            time.sleep(0.5)
            subprocess.check_call(["pkg", "install", "nmap", "-y"], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            stop_event.set()
            t.join(timeout=0.5)
            print(f"\r  {G}[✓]{W} nmap berhasil diinstall{N}")
            return True
        except:
            try:
                subprocess.check_call(["apt", "install", "nmap", "-y"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                stop_event.set()
                t.join(timeout=0.5)
                print(f"\r  {G}[✓]{W} nmap berhasil diinstall{N}")
                return True
            except:
                stop_event.set()
                t.join(timeout=0.5)
                print(f"\r  {R}[✗]{W} nmap gagal diinstall (coba manual: pkg install nmap){N}")
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
        
        stop_event = threading.Event()
        t = threading.Thread(target=loading_bar_warna, args=(stop_event, "mpv"))
        t.daemon = True
        t.start()
        
        try:
            kill_lock_process()
            clear_lock_files()
            time.sleep(0.5)
            subprocess.check_call(["pkg", "install", "mpv", "-y"], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            stop_event.set()
            t.join(timeout=0.5)
            print(f"\r  {G}[✓]{W} mpv berhasil diinstall{N}")
            return True
        except:
            try:
                subprocess.check_call(["apt", "install", "mpv", "-y"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                stop_event.set()
                t.join(timeout=0.5)
                print(f"\r  {G}[✓]{W} mpv berhasil diinstall{N}")
                return True
            except:
                stop_event.set()
                t.join(timeout=0.5)
                print(f"\r  {R}[✗]{W} mpv gagal diinstall (coba manual: pkg install mpv){N}")
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
        
        stop_event = threading.Event()
        t = threading.Thread(target=loading_bar_warna, args=(stop_event, "termux-media-player"))
        t.daemon = True
        t.start()
        
        try:
            kill_lock_process()
            clear_lock_files()
            time.sleep(0.5)
            subprocess.check_call(["pkg", "install", "termux-media-player", "-y"], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            stop_event.set()
            t.join(timeout=0.5)
            print(f"\r  {G}[✓]{W} termux-media-player berhasil diinstall{N}")
            return True
        except:
            stop_event.set()
            t.join(timeout=0.5)
            print(f"\r  {R}[✗]{W} termux-media-player gagal diinstall (coba manual){N}")
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

def auto_install():
    global stop_animasi

    ensure_python313()

    os.system('clear')
    
    print(f"""
{W}╭───────────────────────────────────────────────────────────╮{N}
{W}│ Pilih Opsi menu untuk memulai {G}Penginstalan{W}Package{N}
{W}│ Pada Access {R}Tools{W} Dimulai {R}|{W} Ketik {G}mulai{N}
{W}│ Untuk Memulai {G}Penginstalan{W} Atau Ketik {R}exit{N}
{W}│ Untuk Membatalkan Atau keluar dari penginstalan{N}
{W}╰───────────────────────────────────────────────────────────╯{N}
""")
    
    while True:
        print(f"\n{W}╭─────────────────────────────────────────────────────────────╮{N}")
        print(f"{W}│  [{G}✦{W}] mulai{N}")
        print(f"{W}│  [{G}✦{W}] exit{N}")
        print(f"{W}╰[ {G}O P S I{W} ]─────────────────────────────────────────────────╯{N}")
        pilihan = input(f"{W}╰─{R}❯{N} ").strip()
        
        if pilihan == "exit":
            print(f"\n{R}[!] Keluar...{N}")
            sys.exit(0)
        elif pilihan == "mulai":
            break
        else:
            print(f"\n{R}[!] Pilihan tidak valid!{N}")
            time.sleep(1)
            os.system('clear')
            print(f"""
{W}╭───────────────────────────────────────────────────────────╮{N}
{W}│ Pilih Opsi menu untuk memulai {G}Penginstalan{W}Package{N}
{W}│ Pada Access {R}Tools{W} Dimulai {R}|{W} Ketik {G}mulai{N}
{W}│ Untuk Memulai {G}Penginstalan{W} Atau Ketik {R}exit{N}
{W}│ Untuk Membatalkan Atau keluar dari penginstalan{N}
{W}╰───────────────────────────────────────────────────────────╯{N}
""")
    
    pkg_update_upgrade()
    
    termux_pkgs = [
        "python", "python-pip", "git", "wget", "curl", 
        "nano", "openssl", "ffmpeg", "nmap", "mpv",
        "termux-media-player"
    ]
    
    print(f"\n{G}[•]{W} Mengecek package Termux...{N}")
    time.sleep(0.5)
    
    missing_termux = []
    for pkg in termux_pkgs:
        print(f"  {Y}[*]{W} Cek {pkg}... ", end="")
        if check_termux_pkg(pkg):
            print(f"{G}✓ OK{N}")
        else:
            print(f"{R}✗ MISSING{N}")
            missing_termux.append(pkg)
        time.sleep(0.2)
    
    if missing_termux:
        print(f"\n{G}[•]{W} Menginstall package Termux yang hilang...{N}")
        for pkg in missing_termux:
            stop_event = threading.Event()
            t = threading.Thread(target=loading_bar_warna, args=(stop_event, f"Menginstall {pkg}"))
            t.daemon = True
            t.start()
            
            if install_termux_pkg(pkg):
                stop_event.set()
                t.join(timeout=0.5)
                print(f"\r  {G}[✓]{W} {pkg} berhasil diinstall{N}")
            else:
                stop_event.set()
                t.join(timeout=0.5)
                print(f"\r  {R}[✗]{W} {pkg} gagal diinstall (coba manual){N}")
            
            time.sleep(0.5)
    
    python_pkgs = [
        "requests", "flask", "beautifulsoup4", "cryptography", 
        "colorama", "phonenumbers", "fake-useragent", "yt-dlp",
        "pydub", "pyrogram", "rich", "pystyle", "tgcrypto",
        "pyfiglet", "lolcat"
    ]
    
    print(f"\n{Y}[•] Mengecek package Python...{N}")
    time.sleep(0.5)
    
    missing_python = []
    for pkg in python_pkgs:
        print(f"  {Y}[*]{W} Cek {pkg}... ", end="")
        if check_python_pkg(pkg):
            print(f"{G}✓ OK{N}")
        else:
            print(f"{R}✗ MISSING{N}")
            missing_python.append(pkg)
        time.sleep(0.2)
    
    if missing_python:
        print(f"\n{Y}[•] Menginstall package Python yang hilang...{N}")
        for pkg in missing_python:
            stop_event = threading.Event()
            t = threading.Thread(target=loading_bar_warna, args=(stop_event, f"Menginstall {pkg}"))
            t.daemon = True
            t.start()
            
            if install_python_pkg(pkg):
                stop_event.set()
                t.join(timeout=0.5)
                print(f"\r  {G}[✓]{W} {pkg} berhasil diinstall{N}")
            else:
                stop_event.set()
                t.join(timeout=0.5)
                print(f"\r  {R}[✗]{W} {pkg} gagal diinstall (coba manual){N}")
            
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
    
    print(f"{W}╭────────────────────────────────────────────────────────────────╮{N}")
    print(f"{W}│ Berhasil Melakukan {G}Penginstalan!{N}│")
    print(f"{W}│ Melanjutkan Proses Running {G}Tools{N}│")
    print(f"{W}╰────────────────────────────────────────────────────────────────╯{N}")
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
