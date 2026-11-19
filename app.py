import os, time
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
from dhan_client import DhanClient
from engine.signals import build_option_metrics, score_market

load_dotenv()
IST = ZoneInfo("Asia/Kolkata")

st.set_page_config(page_title="BANK NIFTY Smart Money PRO", page_icon="📊", layout="wide")
st.title("📊 BANK NIFTY · SMART MONEY PRO")
st.caption("DhanHQ data | Intraday analytics | Signals are probabilistic, not institutional order identification")

with st.sidebar:
    st.header("Connection")
    client_id = st.text_input("Dhan Client ID", value=os.getenv("DHAN_CLIENT_ID", ""), type="password")
    token = st.text_input("Dhan Access Token", value=os.getenv("DHAN_ACCESS_TOKEN", ""), type="password")
    st.caption("Credentials stay in this session. Never share your token or commit it to GitHub.")
    refresh = st.selectbox("Refresh interval", [5, 10, 15, 30], index=1)
    st.caption("BANK NIFTY underlying: security ID 25 · segment IDX_I")

if not client_id or not token:
    st.info("पहले Dhan Client ID और Access Token sidebar में डालें। फिर Connect & Load दबाएँ।")
    st.stop()

@st.cache_resource
def make_client(cid, tok):
    return DhanClient(cid, tok)

try:
    api = make_client(client_id, token)
    expiries = api.expiry_list()
    if not expiries:
        st.error("Dhan से expiry list नहीं मिली। Token, Data API subscription और market access जाँचें।")
        st.stop()
    expiry = st.selectbox("Expiry", expiries, index=0)
    if st.button("Connect & Load BANK NIFTY", type="primary"):
        st.session_state["load"] = True
    if not st.session_state.get("load", True):
        st.stop()

    with st.spinner("Dhan से live option-chain और index snapshot लिया जा रहा है..."):
        spot = api.spot_ltp()
        chain_payload = api.option_chain(expiry)
        df = build_option_metrics(chain_payload)
    if df.empty:
        st.warning("Option-chain response मिला, लेकिन strikes parse नहीं हो पाए। Dhan response format जाँचें।")
        st.stop()

    metrics = score_market(df, spot)
    a,b,c,d = st.columns(4)
    a.metric("BANK NIFTY Spot", f"{spot:,.2f}" if spot else "N/A")
    b.metric("PCR (OI)", f"{metrics['pcr']:.2f}" if metrics["pcr"] is not None else "N/A")
    c.metric("Call OI", f"{metrics['call_oi']:,.0f}")
    d.metric("Put OI", f"{metrics['put_oi']:,.0f}")

    st.subheader("Smart Money Signal Board")
    x,y,z = st.columns(3)
    x.metric("Bias", metrics["bias"], metrics["bias_note"])
    y.metric("Signal Score", f"{metrics['score']}/100", "Rule-based confidence score")
    z.metric("ATM Strike", f"{metrics['atm']:,.0f}" if metrics["atm"] else "N/A")
    st.info("यह score OI, PCR और option volume के observable संकेतों का मिश्रण है। यह FII/बैंक की वास्तविक पहचान या निश्चित BUY/SELL call नहीं है।")

    st.subheader("Option Chain · near ATM")
    view = df.copy()
    if metrics["atm"] is not None:
        view["distance"] = (view["strike"] - metrics["atm"]).abs()
        view = view.sort_values("distance").head(15).sort_values("strike")
    show_cols = [c for c in ["strike","ce_ltp","ce_oi","ce_oi_change","ce_volume","pe_ltp","pe_oi","pe_oi_change","pe_volume"] if c in view.columns]
    st.dataframe(view[show_cols].round(2), use_container_width=True, hide_index=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["strike"], y=df["ce_oi"], name="Call OI"))
    fig.add_trace(go.Bar(x=df["strike"], y=df["pe_oi"], name="Put OI"))
    fig.update_layout(barmode="group", height=380, title="Strike-wise Open Interest", xaxis_title="Strike", yaxis_title="Open Interest")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Detected zones")
    l,r = st.columns(2)
    with l:
        st.write("**Call-side OI concentration (possible resistance)**")
        st.dataframe(df.nlargest(5, "ce_oi")[["strike","ce_oi","ce_oi_change"]], use_container_width=True, hide_index=True)
    with r:
        st.write("**Put-side OI concentration (possible support)**")
        st.dataframe(df.nlargest(5, "pe_oi")[["strike","pe_oi","pe_oi_change"]], use_container_width=True, hide_index=True)

    st.caption(f"Last update: {datetime.now(IST).strftime('%d-%m-%Y %H:%M:%S')} IST · Dhan option-chain rate limit: avoid polling more often than every 3 seconds.")
    if st.button("Refresh data"):
        st.rerun()
except Exception as e:
    st.error(f"Data connection error: {e}")
    st.write("जाँचें: Client ID, token validity, active Data API plan, internet और Dhan API status.")
