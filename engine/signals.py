import math
import pandas as pd

def _num(value):
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def build_option_metrics(payload):
    data = payload.get("data", payload)
    oc = data.get("oc", {}) if isinstance(data, dict) else {}
    rows = []
    if not isinstance(oc, dict):
        return pd.DataFrame()
    for strike_key, sides in oc.items():
        try:
            strike = float(strike_key)
        except (TypeError, ValueError):
            continue
        ce = sides.get("ce", {}) if isinstance(sides, dict) else {}
        pe = sides.get("pe", {}) if isinstance(sides, dict) else {}
        rows.append({
            "strike": strike,
            "ce_ltp": _num(ce.get("last_price")),
            "ce_oi": _num(ce.get("oi")),
            "ce_oi_change": _num(ce.get("oi") ) - _num(ce.get("previous_oi")),
            "ce_volume": _num(ce.get("volume")),
            "pe_ltp": _num(pe.get("last_price")),
            "pe_oi": _num(pe.get("oi")),
            "pe_oi_change": _num(pe.get("oi")) - _num(pe.get("previous_oi")),
            "pe_volume": _num(pe.get("volume")),
        })
    return pd.DataFrame(rows).sort_values("strike") if rows else pd.DataFrame()

def score_market(df, spot=None):
    if df.empty:
        return {"pcr": None, "call_oi": 0, "put_oi": 0, "atm": None, "bias": "NO DATA", "bias_note": "No chain", "score": 0}
    call_oi = float(df.ce_oi.sum())
    put_oi = float(df.pe_oi.sum())
    pcr = put_oi / call_oi if call_oi else None
    call_add = float(df.ce_oi_change.sum())
    put_add = float(df.pe_oi_change.sum())
    atm = float(df.iloc[(df["strike"] - (spot or df["strike"].median())).abs().argsort()[:1]]["strike"].iloc[0])
    score = 50
    if pcr is not None:
        score += 15 if pcr > 1.15 else (-15 if pcr < 0.85 else 0)
    if put_add > call_add:
        score += 15
    elif call_add > put_add:
        score -= 15
    score = max(0, min(100, score))
    if score >= 65:
        bias, note = "BULLISH", "Put-side support / OI strength"
    elif score <= 35:
        bias, note = "BEARISH", "Call-side pressure / OI strength"
    else:
        bias, note = "NEUTRAL", "Mixed or inconclusive positioning"
    return {"pcr": pcr, "call_oi": call_oi, "put_oi": put_oi, "atm": atm, "bias": bias, "bias_note": note, "score": score}
