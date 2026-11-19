# BANK NIFTY Smart Money PRO — DhanHQ

यह शुरुआती PRO dashboard DhanHQ से BANK NIFTY option-chain और index snapshot पढ़ता है। यह **read-only** है; कोई order place नहीं करता।

## इसमें क्या है
- BANK NIFTY option-chain expiry list और live chain
- PCR (OI), Call/Put OI, strike-wise OI chart
- संभावित Call resistance और Put support zones
- Rule-based bullish / bearish / neutral bias score
- Streamlit dashboard, Railway deployment-ready

## Android से शुरू करने के चरण
1. ZIP को extract करें।
2. GitHub में नया repository बनाएं, जैसे `banknifty-smart-money-pro`।
3. Extract की हुई सभी files GitHub repository में upload करें।
4. Railway में **New Project → Deploy from GitHub Repo** चुनकर repository connect करें।
5. Railway → Variables में ये दो variables जोड़ें:
   - `DHAN_CLIENT_ID`
   - `DHAN_ACCESS_TOKEN`
6. Deploy करें। Railway public domain generate करे तो उसे खोलें।
7. Dashboard sidebar में credentials भरकर भी चला सकते हैं; बेहतर है Railway Variables का उपयोग करें।

## Local run (PC)
```bash
pip install -r requirements.txt
cp .env.example .env
# .env में अपने credentials भरें
streamlit run app.py
```

## सुरक्षा
- Access Token कभी GitHub पर upload न करें।
- `.env` file commit न करें।
- Token expire हो तो Dhan से नया token बनाकर Railway Variables update करें।
- यह software automatic trading नहीं करता।

## महत्वपूर्ण सीमाएँ
- Dhan option-chain endpoint की rate limit का सम्मान करें; लगातार 3 सेकंड से कम अंतर पर request न करें।
- Option-chain snapshots में `previous_oi` उपलब्ध न होने पर OI-change शून्य दिख सकता है। वास्तविक OI delta के लिए हमें समय के साथ snapshots store करके तुलना करनी होगी।
- यह version option-chain based analysis है। Tick-by-tick futures/options WebSocket collector, cumulative delta, 20-level depth, persistent database, alerts और historical backtest अगले development चरण हैं।
- OI concentration support/resistance की गारंटी नहीं है; expiry, volume, price action और risk management के साथ पुष्टि करें।

## तकनीकी संदर्भ
DhanHQ API: https://dhanhq.co/docs/v2/
Live feed: https://dhanhq.co/docs/v2/live-market-feed/
Option chain: https://dhanhq.co/docs/v2/option-chain/
