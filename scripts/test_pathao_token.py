import os
import sys
from pathlib import Path
import requests
from django.conf import settings

def require(value, name):
    if not value:
        raise RuntimeError(f"Missing credential: {name}. Check your .env and settings.PATHAO.")
    return value

def get_pathao_token():
    cfg = settings.PATHAO
    base = require(cfg.get("BASE_URL"), "BASE_URL").rstrip("/")
    client_id = require(cfg.get("CLIENT_ID"), "CLIENT_ID")
    client_secret = require(cfg.get("CLIENT_SECRET"), "CLIENT_SECRET")
    username = require(cfg.get("USERNAME"), "USERNAME")
    password = require(cfg.get("PASSWORD"), "PASSWORD")
    issue_path = cfg.get("ISSUE_TOKEN_PATH") or "/aladdin/api/v1/issue-token"

    url = f"{base}{issue_path}"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    resp = requests.post(url, data=data, headers=headers,
                         timeout=(cfg.get("CONNECT_TIMEOUT", 5), cfg.get("READ_TIMEOUT", 20)))
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"Pathao token request failed ({resp.status_code}): {resp.text}") from e

    payload = resp.json()
    token = payload.get("access_token") or payload.get("token")
    if not token:
        raise RuntimeError(f"Token missing in response: {payload}")
    return token, payload

if __name__ == "__main__":
    # Ensure Django is set up
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopaway.settings")
    import django
    try:
        django.setup()
    except Exception as e:
        print("Failed to setup Django. Ensure project root is on sys.path and DJANGO_SETTINGS_MODULE is correct.")
        raise

    try:
        tok, raw = get_pathao_token()
        print("Token:", tok)
        print("Raw:", raw)
    except Exception as e:
        # Print PATHAO config to help diagnose missing env
        print("PATHAO config:", settings.PATHAO)
        raise
