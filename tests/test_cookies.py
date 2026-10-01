from oj import cookies


def test_from_env(monkeypatch, tmp_path):
    # 避免读到仓库里真实 .env;指向一个不存在的 env 文件
    monkeypatch.setattr(cookies, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setenv("LEETCODE_SESSION", "sess123")
    monkeypatch.setenv("LEETCODE_CSRFTOKEN", "csrf456")
    c = cookies.from_env()
    assert c == {"LEETCODE_SESSION": "sess123", "csrftoken": "csrf456"}


def test_from_env_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(cookies, "ENV_FILE", tmp_path / ".env")
    monkeypatch.delenv("LEETCODE_SESSION", raising=False)
    monkeypatch.delenv("LEETCODE_CSRFTOKEN", raising=False)
    assert cookies.from_env() is None


def test_decrypt_roundtrip():
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Hash import SHA1
    key = PBKDF2(b"peanuts", b"saltysalt", 16, count=1003, hmac_hash_module=SHA1)
    iv = b" " * 16
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain = b"hello-session-value"
    pad = 16 - len(plain) % 16
    enc = b"v10" + cipher.encrypt(plain + bytes([pad]) * pad)
    assert cookies.decrypt_chromium_value(enc, key) == "hello-session-value"
