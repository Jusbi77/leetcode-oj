"""从本地 Edge 浏览器读取并解密 leetcode.cn 的登录 cookie;.env 兜底。

仅在抓取(fetch)时使用,依赖 pycryptodome。做题/判题不 import 本模块。
"""
import os
import sqlite3
import shutil
import subprocess
import tempfile
from pathlib import Path

EDGE_COOKIES = Path.home() / "Library/Application Support/Microsoft Edge/Default/Cookies"
KEYCHAIN_SERVICE = "Microsoft Edge Safe Storage"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def from_env():
    """从 .env 文件或环境变量读取手填的 cookie;缺任一则返回 None。"""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    sess = env.get("LEETCODE_SESSION") or os.environ.get("LEETCODE_SESSION")
    csrf = env.get("LEETCODE_CSRFTOKEN") or os.environ.get("LEETCODE_CSRFTOKEN")
    if sess and csrf:
        return {"LEETCODE_SESSION": sess, "csrftoken": csrf}
    return None


def _keychain_password():
    """从 macOS 钥匙串取 Edge 的 Safe Storage 密码(会触发一次授权弹窗)。"""
    out = subprocess.check_output(
        ["security", "find-generic-password", "-wa", KEYCHAIN_SERVICE],
        stderr=subprocess.DEVNULL)
    return out.strip()


def decrypt_chromium_value(encrypted: bytes, key: bytes) -> str:
    """解密单个 Chromium/Edge cookie 值(macOS:AES-128-CBC,v10/v11 前缀)。"""
    from Crypto.Cipher import AES
    if encrypted[:3] in (b"v10", b"v11"):
        encrypted = encrypted[3:]
    iv = b" " * 16
    cipher = AES.new(key, AES.MODE_CBC, iv)
    dec = cipher.decrypt(encrypted)
    pad = dec[-1]
    if 0 < pad <= 16:
        dec = dec[:-pad]
    try:
        return dec.decode("utf-8")
    except UnicodeDecodeError:
        # 新版 Chromium 明文前有 32 字节域哈希前缀
        return dec[32:].decode("utf-8", errors="replace")


def _from_edge():
    """从 Edge cookie 库读取并解密 leetcode.cn 的两个关键 cookie。"""
    if not EDGE_COOKIES.exists():
        return None
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Hash import SHA1
    passwd = _keychain_password()
    key = PBKDF2(passwd, b"saltysalt", 16, count=1003, hmac_hash_module=SHA1)
    tmp = Path(tempfile.gettempdir()) / "oj_edge_cookies_copy.sqlite"
    shutil.copy2(EDGE_COOKIES, tmp)  # 复制一份,避免 Edge 占用数据库锁
    try:
        con = sqlite3.connect(str(tmp))
        rows = con.execute(
            "SELECT name, encrypted_value FROM cookies WHERE host_key LIKE '%leetcode.cn%'"
        ).fetchall()
        con.close()
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass
    out = {}
    for name, enc in rows:
        if name in ("LEETCODE_SESSION", "csrftoken"):
            try:
                out[name] = decrypt_chromium_value(enc, key)
            except Exception:
                pass
    if out.get("LEETCODE_SESSION") and out.get("csrftoken"):
        return out
    return None


def get_leetcode_cookies() -> dict:
    """优先从 Edge 自动读取,失败回退 .env;都没有则抛 RuntimeError 带指引。"""
    try:
        c = _from_edge()
    except Exception:
        c = None
    if c:
        return c
    c = from_env()
    if c:
        return c
    raise RuntimeError(
        "无法获取 leetcode.cn 登录 cookie。\n"
        "请确认已在 Edge 登录 leetcode.cn 会员账号;\n"
        "或手动复制 LEETCODE_SESSION 和 LEETCODE_CSRFTOKEN 到 .env\n"
        "(浏览器开发者工具 → Application → Cookies → https://leetcode.cn)。")
