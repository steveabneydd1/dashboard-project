# CME API Setup Instructions

Your CME credentials are set up securely—they stay in your terminal, never in the chat.

## Step 1: Run the Setup Script

From the `mineral-eval` directory, run:

```bash
python3 setup_cme.py
```

This will prompt you interactively for:
1. **CME Username** (type it normally)
2. **CME Password** (hidden input, won't display as you type)
3. **CME WebSocket Endpoint URL** (press Enter if you're not sure—defaults to `wss://api.cmegroup.com/ws`)

## Step 2: What Gets Saved

The script creates a file called `.env` with your credentials:
- **Location:** `/Users/steveabney/.openclaw/workspace/projects/mineral-eval/.env`
- **Permissions:** 600 (only you can read/write)
- **Git:** Automatically ignored (never committed to version control)

## Step 3: Test Your Setup

Once saved, verify the credentials load:

```bash
python3 cme_config.py
```

You should see:
```
✅ Credentials loaded successfully
   Username: <your_username>
   Endpoint: <your_endpoint>
```

## Step 4: Dashboard Integration

Once complete, the dashboard will automatically load your credentials when you run:

```bash
python3 -m streamlit run dashboard.py
```

---

## If You Need to Update Credentials

Just run `python3 setup_cme.py` again—it will overwrite the `.env` file.

## Troubleshooting

**"Command not found: python3"**
- Use `python` instead: `python setup_cme.py`

**".env file not found"**
- Make sure you ran `setup_cme.py` first

**"Missing credentials in .env"**
- Run `setup_cme.py` again and fill in all prompts

---

**Questions?** Check the CME DataMine documentation or contact CME support at cmedatasales@cmegroup.com
