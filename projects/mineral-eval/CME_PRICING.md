# CME Pricing Integration

The dashboard now integrates real-time NYMEX forward curves from CME Group.

## Features

### 1. Live CME Price Fetch
- Connect to CME WebSocket API to stream WTI (CL) and Henry Hub (NG) forward curves
- One-click fetch in the "Commodity Prices & Differentials" section
- Requires CME API credentials (configured in `.env`)

### 2. Cap & Floor Controls
**Gas (Henry Hub / $/MMBtu)**
- Set minimum (floor) and maximum (cap) prices
- All months automatically clamped to the specified range
- Example: Floor $2.00, Cap $6.00 prevents extreme volatility assumptions

**Oil (WTI / $/Bbl)**
- Same cap/floor logic as gas
- Example: Floor $40, Cap $90

### 3. Year 4 Flat-to-Perpetuity
*Feature in progress*

When enabled:
- Dashboard calculates the average gas and oil prices for months 37-48 (Year 4)
- Holds that average price flat from month 49 onward (Year 5-50)
- Useful for conservative long-term assumptions when forward curves become sparse

## Setup

### Step 1: Configure CME Credentials
```bash
cd /Users/steveabney/.openclaw/workspace/projects/mineral-eval
python3 setup_cme.py
```

You'll be prompted for:
- CME Username
- CME Password (hidden input)
- CME WebSocket Endpoint URL (press Enter for default)

Credentials are stored securely in `.env` (not committed to git).

### Step 2: Start Dashboard
```bash
python3 -m streamlit run dashboard.py
```

## Usage

### Fetch Live Prices
1. Navigate to the **Economics** tab
2. Check **"Fetch live CME prices"** (under "📊 CME Market Prices")
3. Dashboard fetches WTI and NG strips from NYMEX
4. Use the fetched prices or adjust manually

### Apply Caps & Floors
1. In the **"⛓️ Price Caps & Floors"** section:
   - Set gas cap and floor ($/MMBtu)
   - Set oil cap and floor ($/Bbl)
2. Check **"Apply caps & floors"**
3. When you click "Calculate IRR & NPV", prices are automatically clamped

### Example: Conservative Case
- Gas: $2.50-$5.50/MMBtu (tight range, less volatility)
- Oil: $50-$75/Bbl
- Year 4 flat: Checked (stabilizes long-term assumptions)
- Result: More predictable returns, less exposed to price shocks

## Files

- **`cme_client.py`** — CME WebSocket client, price fetching, cap/floor logic
- **`cme_config.py`** — Load credentials from `.env`
- **`setup_cme.py`** — Interactive credential setup
- **`.env`** — Your CME credentials (created by `setup_cme.py`, not in git)
- **`dashboard.py`** — Updated Streamlit UI with price controls

## Troubleshooting

**"CME connection failed"**
- Check that your credentials in `.env` are correct
- Verify your CME account has WebSocket API access
- Check your network connection

**"Module not found: websocket"**
```bash
python3 -m pip install websocket-client
```

**"No module named cme_config"**
- Make sure you're running from the `mineral-eval` directory
- Run: `python3 setup_cme.py` first

## Next Steps

- **Year 4 flat logic** — Full implementation with multi-month averages
- **Scenario comparison** — Side-by-side analysis (strip A vs. strip B)
- **Export with prices** — Include applied cap/floor in CSV export
- **Price history** — Track strip curves over time

---

For CME API documentation: https://www.cmegroup.com/tools-information/datamine/
