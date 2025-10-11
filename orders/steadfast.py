import logging
import time
from typing import Any, Dict, Optional
import random
import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SteadfastClient:
    """Minimal Steadfast API client with retries.

    Auth: Api-Key and Secret-Key headers.
    Docs: https://portal.steadfast.com.bd/api/v1
    """

    def __init__(self) -> None:
        s = getattr(settings, "STEADFAST", {}) or {}
        self.base_url: str = (s.get("BASE_URL", "").rstrip("/"))
        self.api_key: str = s.get("API_KEY", "")
        self.secret_key: str = s.get("SECRET_KEY", "")
        self.use_mock: bool = bool(s.get("USE_MOCK", False))
        # Endpoint paths (configurable)
        self.create_order_path: str = s.get("CREATE_ORDER_PATH", "/create_order")
        self.status_by_cid_path: str = s.get("STATUS_BY_CID_PATH", "/status_by_cid/{consignment_id}")
        # Networking
        self.connect_timeout: float = float(s.get("CONNECT_TIMEOUT", 5))
        self.read_timeout: float = float(s.get("READ_TIMEOUT", 20))
        self.retries: int = int(s.get("RETRIES", 2))

        if not all([self.base_url, self.api_key, self.secret_key]):
            logger.warning("STEADFAST credentials/base URL are not fully configured.")

    # ---- HTTP helpers with retry ----
    def _headers(self) -> Dict[str, str]:
        return {
            "Api-Key": self.api_key,
            "Secret-Key": self.secret_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        retry: Optional[int] = None,
    ) -> requests.Response:
        if retry is None:
            retry = self.retries
        last_exc: Optional[Exception] = None
        for attempt in range(retry + 1):
            try:
                resp = requests.request(
                    method,
                    url,
                    headers=self._headers(),
                    json=json,
                    timeout=(self.connect_timeout, self.read_timeout),
                )
                # Steadfast returns 200 on success; raise for others
                resp.raise_for_status()
                return resp
            except requests.RequestException as exc:
                last_exc = exc
                logger.exception("Steadfast request error on %s %s: %s", method, url, exc)
                if attempt < retry:
                    time.sleep(1.0)
                    continue
        assert last_exc is not None
        raise last_exc

    # ---- Public API ----
    def _mock_consignment_id(self) -> str:
        # Example: SFYYYYMMDD + 6 hex chars
        ts = datetime.datetime.now().strftime("%Y%m%d")
        suffix = ("%06x" % random.randrange(16**6)).upper()
        return f"SF{ts}{suffix}"

    def _mock_create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        cid = self._mock_consignment_id()
        return {
            "message": "Mock order created",
            "status": "in_review",
            "consignment_id": cid,
            "tracking_code": cid,
            "cod_amount": payload.get("cod_amount"),
            "invoice": payload.get("invoice"),
        }

    def create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{self.create_order_path}"
        try:
            resp = self._request_with_retry("POST", url, json=payload)
            # If server misbehaves with 5xx but requests didn't raise (unlikely), fallback
            if 500 <= resp.status_code < 600 and self.use_mock:
                logger.warning("Steadfast 5xx received; using mock create_order response")
                return self._mock_create_order(payload)
            return resp.json()
        except Exception as exc:
            if self.use_mock:
                logger.warning("Steadfast create_order failed (%s); using mock. Error: %s", url, exc)
                return self._mock_create_order(payload)
            raise

    def _mock_status(self, consignment_id: str) -> Dict[str, Any]:
        # Simple progression demo
        choices = ["in_review", "processing", "in_transit", "out_for_delivery", "delivered"]
        return {"status": random.choice(choices), "consignment_id": consignment_id}

    def get_order_status(self, consignment_id: str) -> Dict[str, Any]:
        path = self.status_by_cid_path.format(consignment_id=consignment_id)
        url = f"{self.base_url}{path}"
        try:
            resp = self._request_with_retry("GET", url)
            if 500 <= resp.status_code < 600 and self.use_mock:
                logger.warning("Steadfast 5xx received; using mock status response")
                return self._mock_status(consignment_id)
            return resp.json()
        except Exception as exc:
            if self.use_mock:
                logger.warning("Steadfast get_order_status failed (%s); using mock. Error: %s", url, exc)
                return self._mock_status(consignment_id)
            raise
