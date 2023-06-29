# coding:utf-8
"""Some function to generate code."""
import random
import base64
import time
import string
import struct
import hmac
import hashlib
from uuid import UUID
from config import CFG as cfg

pool = string.ascii_letters + string.digits


def custom_round(n, d=8, arrow='bottom'):
    orgin_num = round(n, d + 2)
    n = round(n, d)
    if arrow == 'top' and n < orgin_num:
        n += 1 / (10**d)
    elif arrow == 'bottom' and n > orgin_num:
        n -= 1 / (10**d)

    return round(n, d)


def rand6():
    return ''.join(random.choice(pool) for _ in range(6))


def rand12():
    rand = ''.join(random.choice(pool) for _ in range(8))
    stamp = hex(int(time.time()))[-4:]
    return rand + stamp


_last_timestamp = None


def create_id(node=0):
    """Create a uuid."""

    nanoseconds = int(time.time() * 1e9)
    # 0x01b21dd213814000 is the number of 100-ns intervals between the
    # UUID epoch 1582-10-15 00:00:00 and the Unix epoch 1970-01-01 00:00:00.
    timestamp = int(nanoseconds / 100) + 0x01b21dd213814000

    global _last_timestamp
    if _last_timestamp is not None and timestamp <= _last_timestamp:
        timestamp = _last_timestamp + 1
    _last_timestamp = timestamp

    clock_seq = random.getrandbits(48)  # instead of stable storage
    time_low = timestamp & 0xffffffff
    time_mid = (timestamp >> 32) & 0xffff
    time_hi_version = (timestamp >> 48) & 0x0fff
    node_low = node & 0xff
    node_hi_variant = (node >> 8) & 0x3f

    return UUID(
        fields=(time_low, time_mid, time_hi_version, node_hi_variant, node_low,
                clock_seq),
        version=1)


def create_code():
    return ''.join(random.choices('0123456789', k=6))


def create_token():
    return ''.join(random.choices(pool, k=16)) + hex(int(
        time.time() * 1000))[2:]


def encode_passwd(passwd):
    return hmac.new(cfg.server.pass_mixin.encode('utf-8'),
                    passwd.encode()).hexdigest()


def encode_msg(code, timestamp, user_id):
    return hmac.new(code.encode(),
                    (str(timestamp) + str(user_id)).encode()).hexdigest()


def generate_cookie_secret():
    return base64.b64encode(
        bytes([random.choice(range(256)) for _ in range(32)]))


def get_hotp_token(secret, intervals_no):
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 15
    h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
    return h


def get_totp_token(secret):
    seed = int(time.time()) // 30
    result = list()
    for i in range(2):
        token = get_hotp_token(secret, intervals_no=seed - i)
        result.append(f'{token:06d}')
    return result


def get_totp_secret():
    byte_key = random.getrandbits(80).to_bytes(10, 'big')
    return base64.b32encode(byte_key).decode()


def get_appkey(user_id):
    head = hex(user_id)[2:]
    tail = ''.join(random.choices(pool, k=12 - len(head)))
    return (head + tail).lower()


def get_appsecret():
    return hashlib.md5(str(time.time()).encode()).hexdigest()
