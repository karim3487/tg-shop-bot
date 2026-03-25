"""
Telegram WebApp initData authentication for DRF.

Flow:
  1. Client sends `Authorization: TelegramInitData <raw_init_data_string>` header.
  2. We validate HMAC-SHA256 signature.
  3. On success, we find-or-create the Client record and attach it to request.user.
"""

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl, unquote

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api.exceptions import InvalidInitDataError, InitDataExpiredError

from clients.models import Client


def _verify_init_data(init_data: str, bot_token: str) -> dict:
    """Validate Telegram initData and return parsed user dict on success."""
    params = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = params.pop("hash", None)
    if not received_hash:
        raise InvalidInitDataError("Missing hash in initData")

    # Build check string: sorted key=value pairs joined by \n
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))

    # Secret key = HMAC-SHA256("WebAppData", bot_token)
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise InvalidInitDataError("Invalid initData signature")

    # Replay Attack Prevention: Validate auth_date (expiry threshold 24 hours)
    auth_date_raw = params.get("auth_date")
    if not auth_date_raw:
        raise InvalidInitDataError("Missing auth_date in initData")

    try:
        auth_date = int(auth_date_raw)
    except (ValueError, TypeError):
        raise InvalidInitDataError("Invalid auth_date format")

    if time.time() - auth_date > 86400:
        raise InitDataExpiredError("initData has expired (protection against replay attacks)")

    # Parse the user JSON field
    raw_user = params.get("user")
    if not raw_user:
        raise InvalidInitDataError("No user field in initData")

    return json.loads(unquote(raw_user))


class TelegramInitDataAuthentication(BaseAuthentication):
    """DRF authentication via Telegram WebApp initData."""

    keyword = "TelegramInitData"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith(self.keyword + " "):
            return None  # not our scheme — let other authenticators try

        raw_init_data = auth_header[len(self.keyword) + 1:]
        bot_token = getattr(settings, "BOT_TOKEN", "")
        if not bot_token:
            raise AuthenticationFailed("BOT_TOKEN not configured on server")

        user_data = _verify_init_data(raw_init_data, bot_token)

        telegram_id = user_data.get("id")
        if not telegram_id:
            raise InvalidInitDataError("No id in Telegram user data")

        client, _ = Client.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": user_data.get("username", ""),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "is_active": True,
            },
        )

        return (client, raw_init_data)

    def authenticate_header(self, request):
        return self.keyword
