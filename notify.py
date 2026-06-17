#!/usr/bin/env python3
"""
notify.py — WQ Brain notification utility
==========================================
Sends notifications via LINE Messaging API + macOS system notification.

Setup:
  1. Go to https://developers.line.biz/ → create a Provider + Messaging API channel
  2. From the channel page, copy:
       - "Channel access token" (long token, click Issue if blank)
       - "Your user ID" (starts with U — this is who receives the messages)
  3. Add both to credentials.json:
       {
         "email": "...",
         "password": "...",
         "line_channel_token": "YOUR_CHANNEL_ACCESS_TOKEN",
         "line_user_id": "Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
       }
  4. In LINE app: add your bot as a friend (scan QR code on the channel page)

Usage (from other scripts):
  from notify import notify
  notify("Alpha passed! Check mLXLPa35", urgent=True)
"""

import json
import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
CREDS_FILE = BASE_DIR / 'credentials.json'


def _load_line_creds() -> tuple[str | None, str | None]:
    """Return (channel_token, user_id). Env vars take priority over credentials.json."""
    token = os.environ.get('LINE_CHANNEL_TOKEN')
    user_id = os.environ.get('LINE_USER_ID')
    if token and user_id:
        return token, user_id
    try:
        with open(CREDS_FILE) as f:
            creds = json.load(f)
        return creds.get('line_channel_token'), creds.get('line_user_id')
    except Exception:
        return None, None


def _send_line(message: str, channel_token: str, user_id: str) -> bool:
    """Push a text message to the user via LINE Messaging API."""
    try:
        import urllib.request
        payload = json.dumps({
            'to': user_id,
            'messages': [{'type': 'text', 'text': message}]
        }).encode()
        req = urllib.request.Request(
            'https://api.line.me/v2/bot/message/push',
            data=payload,
            headers={
                'Authorization': f'Bearer {channel_token}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f'[notify] LINE Messaging API failed: {e}')
        return False


def _send_macos(title: str, message: str, sound: str = 'Ping') -> bool:
    try:
        script = f'display notification {json.dumps(message)} with title {json.dumps(title)} sound name "{sound}"'
        subprocess.run(['osascript', '-e', script],
                      capture_output=True, timeout=5)
        return True
    except Exception:
        return False


def notify(message: str, title: str = 'WQ Brain', urgent: bool = False):
    """
    Send a notification via LINE Notify and macOS system notification.

    Args:
        message: The notification body text
        title:   Notification title (macOS only)
        urgent:  If True, uses louder sound and prepends 🚨 to LINE message
    """
    # Format LINE message
    line_prefix = '🚨 ' if urgent else '🔔 '
    line_msg = f'\n{line_prefix}{title}\n{message}'

    # ── macOS notification ─────────────────────────────────────────
    sound = 'Glass' if urgent else 'Ping'
    _send_macos(title, message, sound)

    # ── LINE Messaging API ─────────────────────────────────────────
    channel_token, user_id = _load_line_creds()
    if channel_token and user_id:
        _send_line(line_msg, channel_token, user_id)
    else:
        print('[notify] LINE not configured — add "line_channel_token" and "line_user_id" to credentials.json')


if __name__ == '__main__':
    # Quick test
    notify('Test notification from WQ Brain orchestrator', urgent=False)
    print('Notification sent. Check your LINE and macOS notification center.')
