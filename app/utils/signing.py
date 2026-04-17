from __future__ import annotations

import hmac
import time
from hashlib import sha256


def now_epoch() -> int:
    return int(time.time())


def sign(*, secret: str, message: str) -> str:
    return hmac.new(secret.encode("utf-8"), message.encode("utf-8"), sha256).hexdigest()


def verify(*, secret: str, message: str, signature: str) -> bool:
    expected = sign(secret=secret, message=message)
    return hmac.compare_digest(expected, signature)

