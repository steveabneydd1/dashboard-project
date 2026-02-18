---
name: vapi-caller
description: Make phone calls using Vapi. Use when the user asks to call someone, make a phone call, dial a number, or reach out to someone by phone.
---

# Vapi Phone Calling

This skill enables OpenClaw to make phone calls using the Vapi API.

## Usage

When the user requests a phone call, use the `make_call.py` script:
```bash
python ~/.openclaw/workspace/vapi-caller/scripts/make_call.py --phone "+1234567890" --task "Remind them about the meeting tomorrow at 2pm"
```

## Configuration

The script requires two environment variables:
- `VAPI_API_KEY`: Your Vapi private API key
- `VAPI_ASSISTANT_ID`: Your Vapi assistant ID

Set these before using the skill.
