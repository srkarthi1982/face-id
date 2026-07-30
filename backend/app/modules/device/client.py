import json
import logging

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10.0
DEFAULT_API_PASSWORD = "admin123"


class DeviceHttpClient:
    """HTTP client for the face device LAN API (V5.1.14, port 8090).

    Device endpoints accept application/x-www-form-urlencoded bodies and
    return JSON: {"code": "LAN_SUS-0", "data": ..., "msg": ..., "result": 1, "success": true}
    """

    def __init__(
        self,
        ip_address: str,
        port: int = 8090,
        api_password: str = "",
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.base_url = f"http://{ip_address}:{port}"
        self.api_password = api_password or DEFAULT_API_PASSWORD
        self.timeout = timeout

    def create_person(self, person: dict, faces: list[dict] | None = None) -> dict:
        """POST /person/create — register a person (optionally with up to 3 photos)."""
        data = {
            "pass": self.api_password,
            "person": json.dumps(person, ensure_ascii=False),
        }
        for index, face in enumerate((faces or [])[:3], start=1):
            data[f"face{index}"] = json.dumps(face, ensure_ascii=False)
        return self._post("/person/create", data)

    def _post(self, path: str, data: dict) -> dict:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, data=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.warning(f"Device {url} returned HTTP {e.response.status_code}")
            return {
                "success": False,
                "code": "HTTP_ERROR",
                "msg": f"Device returned HTTP {e.response.status_code}",
                "result": 0,
            }
        except httpx.HTTPError as e:
            logger.warning(f"Device {url} unreachable: {e}")
            return {
                "success": False,
                "code": "CONNECTION_ERROR",
                "msg": f"Device unreachable: {e}",
                "result": 0,
            }
        except ValueError:
            logger.warning(f"Device {url} returned non-JSON response")
            return {
                "success": False,
                "code": "INVALID_RESPONSE",
                "msg": "Device returned a non-JSON response",
                "result": 0,
            }
