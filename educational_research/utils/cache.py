"""Polite cached HTTP. Offline mode never opens a socket."""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import httpx
from ..config import today


class FetchError(RuntimeError):
    pass


class Client:
    def __init__(self, cache_dir, offline=False, transport=None, sleep=time.sleep, ttl=86400):
        self.cache = Path(cache_dir)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.offline, self.sleep, self.ttl = offline, sleep, ttl
        contact = os.getenv("RESEARCH_CONTACT", "")
        self.http = httpx.Client(
            timeout=25,
            follow_redirects=True,
            transport=transport,
            headers={"User-Agent": f"EducationalResearchSkill/0.1 ({contact or 'research-tool'})"},
        )
        self.log = []

    def get(self, url, params=None, headers=None):
        if self.offline:
            raise FetchError("OFFLINE: network disabled, including cached provider search claims")
        safe_params = {k: v for k, v in (params or {}).items() if k not in {"api_key", "key"}}
        key = hashlib.sha256(json.dumps([url, safe_params], sort_keys=True).encode()).hexdigest()
        path = self.cache / (key + ".json")
        entry = {"url": url, "params": safe_params, "checked_at": today(), "cache": False}
        if path.exists() and time.time() - path.stat().st_mtime < self.ttl:
            cached = json.loads(path.read_text())
            self.log.append(
                {**entry, "cache": True, "observed_at": cached["observed_at"], "status": 200}
            )
            return cached["data"]
        for attempt in range(3):
            try:
                response = self.http.get(url, params=params, headers=headers)
                if response.status_code == 429 or response.status_code >= 500:
                    if attempt < 2:
                        retry = response.headers.get("Retry-After", str(2**attempt))
                        try:
                            delay = float(retry)
                        except ValueError:
                            try:
                                delay = (
                                    parsedate_to_datetime(retry) - datetime.now(timezone.utc)
                                ).total_seconds()
                            except (ValueError, TypeError):
                                delay = 2**attempt
                        if delay > 60:
                            raise FetchError("Provider requested a long Retry-After; resume later")
                        self.sleep(max(0, delay))
                        continue
                response.raise_for_status()
                data = response.json()
                path.write_text(json.dumps({"observed_at": today(), "data": data}), encoding="utf-8")
                self.log.append({**entry, "status": response.status_code})
                return data
            except (httpx.HTTPError, ValueError) as exc:
                if attempt == 2 or isinstance(exc, httpx.HTTPStatusError):
                    self.log.append({**entry, "status": "FAILED", "error_type": type(exc).__name__})
                    # Do not expose authenticated URL parameters or response bodies.
                    raise FetchError(f"{url}: {type(exc).__name__}") from None
                self.sleep(2**attempt)
        raise FetchError("Provider exhausted retries")

    def close(self):
        self.http.close()
