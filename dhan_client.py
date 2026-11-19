import requests

BASE = "https://api.dhan.co/v2"

class DhanClient:
    def __init__(self, client_id, access_token):
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "access-token": access_token,
            "client-id": client_id,
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _post(self, path, payload):
        response = self.session.post(BASE + path, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "failure":
            raise RuntimeError(data.get("remarks") or data.get("data") or "Dhan API failure")
        return data

    def expiry_list(self):
        result = self._post("/optionchain/expirylist", {
            "UnderlyingScrip": 25,
            "UnderlyingSeg": "IDX_I",
        })
        return result.get("data") or []

    def option_chain(self, expiry):
        return self._post("/optionchain", {
            "UnderlyingScrip": 25,
            "UnderlyingSeg": "IDX_I",
            "Expiry": expiry,
        })

    def spot_ltp(self):
        # Dhan index instrument snapshot; if this endpoint/segment is unavailable,
        # spot is left blank while option-chain analytics continue.
        try:
            result = self._post("/marketfeed/ltp", {"IDX_I": [25]})
            data = result.get("data", {}).get("IDX_I", {})
            item = data.get("25", {})
            return float(item.get("last_price") or 0) or None
        except Exception:
            return None
