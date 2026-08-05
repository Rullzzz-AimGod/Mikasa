#!/data/data/com.termux/files/usr/bin/bash

R='\033[1;31m'
G='\033[1;32m'
Y='\033[1;33m'
P='\033[1;35m'
C='\033[1;36m'
W='\033[1;37m'
N='\033[0m'

stop_animasi=0

detect_home() {
    if [ -n "$ZSH_VERSION" ]; then
        echo "$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        echo "$HOME/.bashrc"
    else
        echo "$HOME/.bashrc"
    fi
}

konfigurasi=$(detect_home)

is_termux_arm64() {
    if [[ "$(uname -o)" == "Android" ]]; then
        arch=$(uname -m)
        if [[ "$arch" == "aarch64" ]] || [[ "$arch" == "arm64" ]] || [[ "$arch" == "armv8l" ]]; then
            return 0
        fi
    fi
    return 1
}

loading_bar_warna() {
    local text="$1"
    local length=10
    local color_index=0
    local colors=('\x1b[1;91m' '\x1b[1;93m' '\x1b[1;92m' '\x1b[1;94m')
    local reset='\x1b[0m'
    
    while [ $stop_animasi -eq 0 ]; do
        for ((i=0; i<=length; i++)); do
            if [ $stop_animasi -eq 1 ]; then
                break
            fi
            local filled=""
            local empty=""
            for ((j=0; j<i; j++)); do
                filled="${filled}■"
            done
            for ((j=i; j<length; j++)); do
                empty="${empty}□"
            done
            local color=${colors[$((color_index % ${#colors[@]}))]}
            printf "\r ${G}# ${W}${text} [[${color}${filled}${reset}${empty}${W}]]"
            color_index=$((color_index + 1))
            sleep 0.05
        done
    done
    printf "\r%120s\r" ""
}

kill_lock_process() {
    for cmd in apt dpkg; do
        pgrep "$cmd" | while read pid; do
            kill -9 "$pid" 2>/dev/null
        done
    done
    return 0
}

clear_lock_files() {
    local lock_files=(
        "/data/data/com.termux/files/usr/var/lib/dpkg/lock-frontend"
        "/data/data/com.termux/files/usr/var/lib/dpkg/lock"
        "/data/data/com.termux/cache/apt/archives/lock"
    )
    for lock in "${lock_files[@]}"; do
        [ -f "$lock" ] && rm -f "$lock"
    done
    return 0
}

check_termux_pkg() {
    pkg list-installed 2>/dev/null | grep -q "$1"
    return $?
}

install_termux_pkg() {
    kill_lock_process
    clear_lock_files
    sleep 0.5
    if pkg install "$1" -y >/dev/null 2>&1; then
        return 0
    else
        apt install "$1" -y >/dev/null 2>&1
        return $?
    fi
}

get_python_executable() {
    if [ -f "$HOME/.pyenv/versions/3.13.5/bin/python3" ]; then
        echo "$HOME/.pyenv/versions/3.13.5/bin/python3"
    else
        command -v python3
    fi
}

install_python_pkg() {
    local python_exe=$(get_python_executable)
    if "$python_exe" -m pip install "$1" --break-system-packages >/dev/null 2>&1; then
        return 0
    else
        "$python_exe" -m pip install "$1" >/dev/null 2>&1
        return $?
    fi
}

check_python_pkg() {
    local python_exe=$(get_python_executable)
    local import_name="$1"
    case "$1" in
        "fake-useragent") import_name="fake_useragent" ;;
        "beautifulsoup4") import_name="bs4" ;;
        "yt-dlp") import_name="yt_dlp" ;;
        "phonenumbers") import_name="phonenumbers" ;;
        "tgcrypto") import_name="tgcrypto" ;;
        "pyrogram") import_name="pyrogram" ;;
        "pycryptodome") import_name="pycryptodome" ;;
        "pydub") import_name="pydub" ;;
        "lolcat") import_name="lolcat" ;;
    esac
    
    if "$python_exe" -c "import $import_name" >/dev/null 2>&1; then
        return 0
    fi
    
    if "$python_exe" -m pip show "$1" >/dev/null 2>&1; then
        return 0
    fi
    
    return 1
}

get_python_version_str() {
    python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null
}

find_existing_python313() {
    local candidates=(
        "$(command -v python3.13 2>/dev/null)"
        "$HOME/.pyenv/versions/3.13.5/bin/python3"
        "/data/data/com.termux/files/usr/bin/python3.13"
    )
    for c in "${candidates[@]}"; do
        if [ -n "$c" ] && [ -f "$c" ]; then
            echo "$c"
            return 0
        fi
    done
    return 1
}

install_pyenv() {
    local pyenv_root="$HOME/.pyenv"
    [ -d "$pyenv_root" ] && rm -rf "$pyenv_root"
    
    curl -s https://pyenv.run | bash >/dev/null 2>&1
    
    if [ ! -d "$pyenv_root" ]; then
        return 1
    fi
    
    local cfg_lines=(
        'export PYENV_ROOT="$HOME/.pyenv"'
        '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"'
        'eval "$(pyenv init -)"'
    )
    
    for line in "${cfg_lines[@]}"; do
        if ! grep -q "$line" "$konfigurasi" 2>/dev/null; then
            echo "$line" >> "$konfigurasi"
        fi
    done
    
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    
    return 0
}

is_pyenv_working() {
    [ -f "$HOME/.pyenv/bin/pyenv" ] || return 1
    "$HOME/.pyenv/bin/pyenv" --version >/dev/null 2>&1
    return $?
}

build_python313_via_pyenv() {
    local pyenv_root="$HOME/.pyenv"
    local pyenv_bin="$pyenv_root/bin/pyenv"
    
    export PYENV_ROOT="$pyenv_root"
    export PATH="$pyenv_root/bin:$PATH"
    eval "$(pyenv init -)"
    
    export CPPFLAGS="-Wno-error=implicit-function-declaration -Wno-implicit-function-declaration -Wno-error=int-conversion -Wno-int-conversion"
    export LDFLAGS="-latomic"
    export ac_cv_func_getpwent="no"
    export ac_cv_func_copy_file_range="no"
    export ac_cv_func_sendfile="no"
    export ac_cv_func_posix_spawn="no"
    export ac_cv_func_posix_spawnp="no"
    export PYTHON_CONFIGURE_OPTS="--disable-shared"
    
    if is_termux_arm64; then
        export CFLAGS="-O2 -march=armv8-a+crc -mtune=cortex-a53"
        export MAKEFLAGS="-j2"
    fi
    
    echo -e "  ${Y}[!]${W} Build Python 3.13.5 bisa memakan waktu 10-30 menit, mohon tunggu...${N}"
    
    if $pyenv_bin install 3.13.5 >/dev/null 2>&1; then
        local target="$pyenv_root/versions/3.13.5/bin/python3"
        if [ -f "$target" ]; then
            echo "$target"
            return 0
        fi
    fi
    return 1
}

ensure_python313() {
    echo -e "  [ ${G}>${W} ] Cek Python... \c"
    
    local pyversion=$(python3 --version 2>&1)
    
    if echo "$pyversion" | grep -q "3.13"; then
        echo -e "${G}✓ OK (versi 3.13)${N}"
        return 0
    fi
    
    local current_ver=$(get_python_version_str)
    echo -e "${Y}✗ DETECTED $current_ver, downgrade ke 3.13.5${N}"
    
    local target=$(find_existing_python313)
    if [ -n "$target" ]; then
        echo -e "  ${G}[✓]${W} Python 3.13 ditemukan di $target${N}"
        return 0
    fi
    
    echo -e "  [ ${G}>${W} ] Cek pyenv... \c"
    if is_pyenv_working; then
        echo -e "${G}✓ OK${N}"
    else
        echo -e "${R}✗ MISSING${N}"
        stop_animasi=0
        loading_bar_warna "Menginstall pyenv" &
        local pid=$!
        install_pyenv
        stop_animasi=1
        wait $pid 2>/dev/null
        if is_pyenv_working; then
            echo -e "\r  ${G}[✓]${W} pyenv berhasil diinstall${N}"
        else
            echo -e "\r  ${R}[✗]${W} pyenv gagal diinstall (coba manual: curl -s https://pyenv.run | bash)${N}"
            return 1
        fi
    fi
    
    local target=$(build_python313_via_pyenv)
    
    if [ -n "$target" ]; then
        echo -e "  ${G}[✓]${W} Python 3.13.5 berhasil diinstall${N}"
        return 0
    else
        echo -e "  ${R}[✗]${W} Python 3.13.5 gagal diinstall (coba manual: pyenv install 3.13.5)${N}"
        return 1
    fi
}

install_ffmpeg() {
    echo -e "  [ ${G}>${W} ] Cek ffmpeg... \c"
    if command -v ffmpeg >/dev/null 2>&1; then
        echo -e "${G}✓ OK${N}"
        return 0
    fi
    
    echo -e "${R}✗ MISSING${N}"
    echo -e "  [ ${G}>${W} ] Menginstall ffmpeg...${N}"
    
    stop_animasi=0
    loading_bar_warna "ffmpeg" &
    local pid=$!
    
    kill_lock_process
    clear_lock_files
    sleep 0.5
    
    if pkg install ffmpeg -y >/dev/null 2>&1; then
        stop_animasi=1
        wait $pid 2>/dev/null
        echo -e "\r  ${G}[✓]${W} ffmpeg berhasil diinstall${N}"
        return 0
    elif apt install ffmpeg -y >/dev/null 2>&1; then
        stop_animasi=1
        wait $pid 2>/dev/null
        echo -e "\r  ${G}[✓]${W} ffmpeg berhasil diinstall${N}"
        return 0
    else
        stop_animasi=1
        wait $pid 2>/dev/null
        echo -e "\r  ${R}[✗]${W} ffmpeg gagal diinstall (coba manual: pkg install ffmpeg)${N}"
        return 1
    fi
}

install_nmap() {
    echo -e "  [ ${G}>${W} ] Cek nmap... \c"
    if command -v nmap >/dev/null 2>&1; then
        echo -e "${G}✓ OK${N}"
        return 0
    fi
    
    echo -e "${R}✗ MISSING${N}"
    echo -e "  [ ${G}>${W} ] Menginstall nmap...${N}"
    
    stop_animasi=0
    loading_bar_warna "nmap" &
    local pid=$!
    
    kill_lock_process
    clear_lock_files
    sleep 0.5
    
    if pkg install nmap -y >/dev/null 2>&1; then
        stop_animasi=1
        wait $pid 2>/dev/null
        echo -e "\r  ${G}[✓]${W} nmap berhasil diinstall${N}"
        return 0
    elif apt install nmap -y >/dev/null 2>&1; then
        stop_animasi=1
        wait $pid 2>/dev/null
        echo -e "\r  ${G}[✓]${W} nmap berhasil diinstall${N}"
        return 0
    else
        stop_animasi=1
        wait $pid 2>/dev/null
        echo -e "\r  ${R}[✗]${W} nmap gagal diinstall (coba manual: pkg install nmap)${N}"
        return 1
    fi
}

install_mpv() {
    echo -e "  [ ${G}>${W} ] Cek mpv... \c"
    if command -v mpv >/dev/null 2>&1; then
        echo -e "${G}✓ OK${N}"
        return 0
    fi
    
    echo -e "${R}✗ MISSING${N}"
    echo -e "  [ ${G}>${W} ] Menginstall mpv...${N}"
    
    stop_animasi=0
    loading_bar_warna "mpv" &
    local pid=$!
    
    kill_lock_process
    clear_lock_files
    sleep 0.5
    
    if pkg install mpv -y >/dev/null 2>&1; then
        stop_animasi=1
        wait $pid 2>/dev/null
        echo -e "\r  ${G}[✓]${W} mpv berhasil diinstall${N}"
        return 0
    elif apt install mpv -y >/dev/null 2>&1; then
        stop_animasi=1
        wait $pid 2>/dev/null
        echo -e "\r  ${G}[✓]${W} mpv berhasil diinstall${N}"
        return 0
    else
        stop_animasi=1
        wait $pid 2>/dev/null
        echo -e "\r  ${R}[✗]${W} mpv gagal diinstall (coba manual: pkg install mpv)${N}"
        return 1
    fi
}

install_termux_media() {
    echo -e "  [ ${G}>${W} ] Cek termux-media-player... \c"
    if command -v termux-media-player >/dev/null 2>&1; then
        echo -e "${G}✓ OK${N}"
        return 0
    fi
    
    echo -e "${R}✗ MISSING${N}"
    echo -e "  [ ${G}>${W} ] Menginstall termux-media-player...${N}"
    
    stop_animasi=0
    loading_bar_warna "termux-media-player" &
    local pid=$!
    
    kill_lock_process
    clear_lock_files
    sleep 0.5
    
    if pkg install termux-media-player -y >/dev/null 2>&1; then
        stop_animasi=1
        wait $pid 2>/dev/null
        echo -e "\r  ${G}[✓]${W} termux-media-player berhasil diinstall${N}"
        return 0
    else
        stop_animasi=1
        wait $pid 2>/dev/null
        echo -e "\r  ${R}[✗]${W} termux-media-player gagal diinstall (coba manual)${N}"
        return 1
    fi
}

create_music_folder() {
    local music_dirs=(
        "$HOME/Music"
        "/sdcard/Music"
        "$(dirname "$(realpath "$0")")/music"
    )
    
    for dir in "${music_dirs[@]}"; do
        mkdir -p "$dir" 2>/dev/null
        if [ -d "$dir" ]; then
            return 0
        fi
    done
    return 1
}

auto_install() {
    clear
    
    echo -e "
${W}╭───────────────────────────────────────────────────────────╮${N}
${W}│ Pilih Opsi menu untuk memulai ${G}Penginstalan${W}Package${N}
${W}│ Pada Access ${R}Tools${W} Dimulai ${R}|${W} Ketik ${G}mulai${N}
${W}│ Untuk Memulai ${G}Penginstalan${W} Atau Ketik ${R}exit${N}
${W}│ Untuk Membatalkan Atau keluar dari penginstalan${N}
${W}╰───────────────────────────────────────────────────────────╯${N}
"
    
    while true; do
        echo -e "\n${W}╭─────────────────────────────────────────────────────────────╮${N}"
        echo -e "${W}│  [${G}✦${W}] mulai${N}"
        echo -e "${W}│  [${G}✦${W}] exit${N}"
        echo -e "${W}╰[ ${G}O P S I${W} ]─────────────────────────────────────────────────╯${N}"
        echo -e "${W}╰─${R}❯${N} \c"
        read pilihan
        
        if [[ "$pilihan" == "exit" ]]; then
            echo -e "\n${R}[!] Keluar...${N}"
            exit 0
        elif [[ "$pilihan" == "mulai" ]]; then
            break
        else
            echo -e "\n${R}[!] Pilihan tidak valid!${N}"
            sleep 1
            clear
            echo -e "
${W}╭───────────────────────────────────────────────────────────╮${N}
${W}│ Pilih Opsi menu untuk memulai ${G}Penginstalan${W}Package${N}
${W}│ Pada Access ${R}Tools${W} Dimulai ${R}|${W} Ketik ${G}mulai${N}
${W}│ Untuk Memulai ${G}Penginstalan${W} Atau Ketik ${R}exit${N}
${W}│ Untuk Membatalkan Atau keluar dari penginstalan${N}
${W}╰───────────────────────────────────────────────────────────╯${N}
"
        fi
    done
    
    local termux_pkgs=(
        "python" "python-pip" "git" "wget" "curl"
        "nano" "openssl" "ffmpeg" "mpv"
    )
    
    echo -e "\n${G}[•]${W} Mengecek package Termux...${N}"
    sleep 0.5
    
    local missing_termux=()
    for pkg in "${termux_pkgs[@]}"; do
        echo -e "  [ ${G}>${W} ] Cek $pkg... \c"
        if check_termux_pkg "$pkg"; then
            echo -e "${G}✓ OK${N}"
        else
            echo -e "${R}✗ MISSING${N}"
            missing_termux+=("$pkg")
        fi
        sleep 0.2
    done
    
    if [ ${#missing_termux[@]} -gt 0 ]; then
        echo -e "\n${G}[•]${W} Menginstall package Termux yang hilang...${N}"
        for pkg in "${missing_termux[@]}"; do
            stop_animasi=0
            loading_bar_warna "Menginstall $pkg" &
            local pid=$!
            
            if install_termux_pkg "$pkg"; then
                stop_animasi=1
                wait $pid 2>/dev/null
                echo -e "\r  ${G}[✓]${W} $pkg berhasil diinstall${N}"
            else
                stop_animasi=1
                wait $pid 2>/dev/null
                echo -e "\r  ${R}[✗]${W} $pkg gagal diinstall (coba manual)${N}"
            fi
            sleep 0.5
        done
    fi
    
    echo -e "\n${G}[•]${W} Mengecek & Install Python 3.13.5...${N}"
    if ! ensure_python313; then
        echo -e "  ${R}[✗]${W} Gagal menginstall Python 3.13.5, lanjut dengan versi saat ini${N}"
    fi
    
    local python_pkgs=(
        "requests" "flask" "beautifulsoup4"
        "colorama" "phonenumbers" "fake-useragent" "yt-dlp"
        "pydub" "rich" "pystyle"
        "pyfiglet" "lolcat" "pycryptodome"
    )
    
    echo -e "\n${G}[•]${W} Mengecek package Python...${N}"
    sleep 0.5
    
    local missing_python=()
    for pkg in "${python_pkgs[@]}"; do
        echo -e "  [ ${G}>${W} ] Cek $pkg... \c"
        if check_python_pkg "$pkg"; then
            echo -e "${G}✓ OK${N}"
        else
            echo -e "${R}✗ MISSING${N}"
            missing_python+=("$pkg")
        fi
        sleep 0.2
    done
    
    if [ ${#missing_python[@]} -gt 0 ]; then
        echo -e "\n${R}[•]${W} Menginstall package Python yang hilang...${N}"
        for pkg in "${missing_python[@]}"; do
            stop_animasi=0
            loading_bar_warna "Menginstall $pkg" &
            local pid=$!
            
            if install_python_pkg "$pkg"; then
                stop_animasi=1
                wait $pid 2>/dev/null
                echo -e "\r  ${G}[✓]${W} $pkg berhasil diinstall${N}"
            else
                stop_animasi=1
                wait $pid 2>/dev/null
                echo -e "\r  ${R}[✗]${W} $pkg gagal diinstall (coba manual)${N}"
            fi
            sleep 0.5
        done
    fi
    
    echo -e "\n${G}[•]${W} Mengecek ffmpeg...${N}"
    sleep 2
    install_ffmpeg
    
    echo -e "\n${G}[•]${W} Mengecek nmap...${N}"
    sleep 2
    install_nmap
    
    echo -e "\n${G}[•]${W} Mengecek mpv...${N}"
    sleep 2
    install_mpv
    
    echo -e "\n${G}[•]${W} Mengecek termux-media-player...${N}"
    sleep 2
    install_termux_media
    
    echo -e "\n${G}[•]${W} Membuat folder Musik...${N}"
    sleep 3
    if create_music_folder; then
        echo -e "  ${G}[✓]${W} Folder Musik berhasil dibuat${N}"
    else
        echo -e "  ${R}[!]${W} Folder Musik gagal dibuat, coba manual${N}"
    fi
    
    echo -e "${W}╭────────────────────────────────────────────────────────────────╮${N}"
    echo -e "${W}│ Berhasil Melakukan ${G}Penginstalan!${N}│"
    echo -e "${W}│ Melanjutkan Proses Running ${G}Tools${N}│"
    echo -e "${W}╰────────────────────────────────────────────────────────────────╯${N}"
    sleep 2

    if [ -f "Mikasa.sh" ]; then
        sleep 1
        chmod +x Mikasa.sh
        ./Mikasa.sh
    else
        echo -e "${R}[!]${W} File Mikasa.sh tidak ditemukan!${N}"
        echo -e "  ${R}[!]${W} Pastikan file Mikasa.sh ada di folder ini${N}"
        exit 1
    fi
}

trap 'echo -e "\n\n${W}[ {G}!{W} ] Keluar...${N}"; exit 0' INT

auto_install
