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


def test_cache_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setattr(cookies, "CACHE_FILE", tmp_path / ".cookies.json")
    assert cookies._read_cache() is None
    cookies._write_cache({"LEETCODE_SESSION": "s", "csrftoken": "t"})
    assert cookies._read_cache() == {"LEETCODE_SESSION": "s", "csrftoken": "t"}


def test_get_prefers_cache_over_edge(monkeypatch, tmp_path):
    # env 空、缓存命中时,不应触碰 Edge/钥匙串
    monkeypatch.setattr(cookies, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setattr(cookies, "CACHE_FILE", tmp_path / ".cookies.json")
    monkeypatch.delenv("LEETCODE_SESSION", raising=False)
    monkeypatch.delenv("LEETCODE_CSRFTOKEN", raising=False)
    cookies._write_cache({"LEETCODE_SESSION": "cached", "csrftoken": "ct"})

    def _boom():
        raise AssertionError("不应调用 Edge")

    monkeypatch.setattr(cookies, "_from_edge", _boom)
    assert cookies.get_leetcode_cookies()["LEETCODE_SESSION"] == "cached"


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
