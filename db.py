"""
db.py — IBM Cloudant persistence layer for QA Management System.

Uses the Cloudant HTTP REST API directly via `requests` — no IBM SDK required.

Environment variables required:
  CLOUDANT_URL      — https://<instance>.cloudantnosqldb.appdomain.cloud
  CLOUDANT_APIKEY   — IAM API key  (preferred)
  -- OR --
  CLOUDANT_USERNAME — legacy credentials username
  CLOUDANT_PASSWORD — legacy credentials password
"""

import json
import os
import re
import uuid
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

BASE_DIR = Path(__file__).parent

# ── Database names ────────────────────────────────────────────────────────────
DB_USERS = "qa_users"
ALL_DBS  = [DB_USERS]

# ── Session singleton ─────────────────────────────────────────────────────────

_session  = None
_base_url = ""


def _get_iam_token(api_key: str) -> str:
    resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key.strip()},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _make_session():
    url = os.environ.get("CLOUDANT_URL", "").strip().rstrip("/")
    if not url:
        raise RuntimeError("CLOUDANT_URL environment variable is not set.")

    s = requests.Session()
    s.headers.update({"Content-Type": "application/json", "Accept": "application/json"})

    username = os.environ.get("CLOUDANT_USERNAME", "").strip()
    password = os.environ.get("CLOUDANT_PASSWORD", "").strip()
    if username and password:
        s.auth = HTTPBasicAuth(username, password)
    else:
        apikey = os.environ.get("CLOUDANT_APIKEY", "").strip()
        if not apikey:
            raise RuntimeError(
                "Set CLOUDANT_APIKEY or both CLOUDANT_USERNAME and CLOUDANT_PASSWORD."
            )
        token = _get_iam_token(apikey)
        s.headers["Authorization"] = f"Bearer {token}"

    return s, url


def _refresh_token():
    global _session
    apikey = os.environ.get("CLOUDANT_APIKEY", "").strip()
    if not apikey:
        return
    token = _get_iam_token(apikey)
    if _session is not None:
        _session.headers["Authorization"] = f"Bearer {token}"


def _s():
    global _session, _base_url
    if _session is None:
        _session, _base_url = _make_session()
    return _session, _base_url


# ── Generic helpers ───────────────────────────────────────────────────────────

def _request(method: str, url: str, **kwargs):
    session, _ = _s()
    r = getattr(session, method)(url, **kwargs)
    if r.status_code == 401:
        _refresh_token()
        session, _ = _s()
        r = getattr(session, method)(url, **kwargs)
    return r


def _all_docs(db_name: str) -> list:
    _, base = _s()
    r = _request("get", f"{base}/{db_name}/_all_docs", params={"include_docs": "true"}, timeout=30)
    r.raise_for_status()
    docs = []
    for row in r.json().get("rows", []):
        doc = row.get("doc", {})
        clean = {k: v for k, v in doc.items() if not k.startswith("_")}
        docs.append(clean)
    return docs


def _get_doc_with_rev(db_name: str, doc_id: str):
    _, base = _s()
    r = _request("get", f"{base}/{db_name}/{requests.utils.quote(doc_id, safe='')}", timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def _upsert(db_name: str, doc_id: str, data: dict) -> dict:
    _, base = _s()
    existing = _get_doc_with_rev(db_name, doc_id)
    payload  = {"_id": doc_id, **{k: v for k, v in data.items() if k not in ("_id", "_rev")}}
    if existing:
        payload["_rev"] = existing["_rev"]
    url = f"{base}/{db_name}/{requests.utils.quote(doc_id, safe='')}"
    r = _request("put", url, json=payload, timeout=30)
    r.raise_for_status()
    return {k: v for k, v in payload.items() if not k.startswith("_")}


def _delete_doc(db_name: str, doc_id: str) -> bool:
    existing = _get_doc_with_rev(db_name, doc_id)
    if not existing:
        return False
    _, base = _s()
    r = _request(
        "delete",
        f"{base}/{db_name}/{requests.utils.quote(doc_id, safe='')}",
        params={"rev": existing["_rev"]},
        timeout=30,
    )
    return r.status_code in (200, 202)


# ── Bootstrap ─────────────────────────────────────────────────────────────────

def _db_exists(name: str) -> bool:
    _, base = _s()
    r = _request("get", f"{base}/{name}", timeout=30)
    return r.status_code == 200


def _seed_db(db_name: str, json_file: str, key: str, id_field: str) -> None:
    _, base = _s()
    r = _request("get", f"{base}/{db_name}", timeout=30)
    r.raise_for_status()
    if r.json().get("doc_count", 0) > 0:
        return  # already seeded

    path = BASE_DIR / json_file
    if not path.exists():
        return

    records = json.loads(path.read_text(encoding="utf-8")).get(key, [])
    docs = [{"_id": rec.get(id_field, str(uuid.uuid4())), **rec} for rec in records]

    if docs:
        r = _request("post", f"{base}/{db_name}/_bulk_docs", json={"docs": docs}, timeout=60)
        r.raise_for_status()
        print(f"  Seeded {len(docs)} records into '{db_name}'")


def bootstrap() -> None:
    _, base = _s()
    print("Cloudant bootstrap starting...")
    for name in ALL_DBS:
        if not _db_exists(name):
            r = _request("put", f"{base}/{name}", timeout=30)
            if r.status_code not in (201, 202, 412):
                r.raise_for_status()
            print(f"  Created database '{name}'")

    _seed_db(DB_USERS, "users.json", "users", "userId")
    print("Cloudant bootstrap complete.")


# ── Users ─────────────────────────────────────────────────────────────────────

def get_users(dept: str = "", status: str = "") -> list:
    users = _all_docs(DB_USERS)
    if dept:
        users = [u for u in users if u.get("dept") == dept]
    if status:
        users = [u for u in users if u.get("status") == status]
    return sorted(users, key=lambda u: u.get("name", ""))


def get_user(user_id: str):
    doc = _get_doc_with_rev(DB_USERS, user_id)
    if not doc:
        return None
    return {k: v for k, v in doc.items() if not k.startswith("_")}


def add_user(data: dict) -> dict:
    user_id = data.get("userId") or str(uuid.uuid4())
    data["userId"] = user_id
    return _upsert(DB_USERS, user_id, data)


def update_user(user_id: str, fields: dict) -> dict | None:
    doc = _get_doc_with_rev(DB_USERS, user_id)
    if not doc:
        return None
    doc.update({k: v for k, v in fields.items() if not k.startswith("_")})
    return _upsert(DB_USERS, user_id, {k: v for k, v in doc.items() if not k.startswith("_")})


def delete_user(user_id: str) -> bool:
    return _delete_doc(DB_USERS, user_id)
