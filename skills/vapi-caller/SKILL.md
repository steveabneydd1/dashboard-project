---
name: vapi-caller
description: Make outbound phone calls using the Vapi AI voice API. Use when the user wants to initiate an automated phone call, have an AI assistant call someone, or check on a previous call's status/transcript.
---

# Vapi Caller

Make outbound AI phone calls via the Vapi API.

## Prerequisites

Environment variables must be set:
- `VAPI_API_KEY` - Your Vapi private API key
- `VAPI_ASSISTANT_ID` - Your Vapi assistant ID
- `VAPI_PHONE_NUMBER_ID` - Phone number ID for outbound caller ID (required)

See `references/credentials.md` for Steve's configured values.

## Making a Call

Use `scripts/make_call.py` to initiate an outbound call:

```bash
python scripts/make_call.py --phone "+15551234567" --task "Schedule a dental appointment for next Tuesday"
```

**Parameters:**
- `--phone` (required): E.164 format phone number (e.g., +15551234567)
- `--task` (required): What the assistant should accomplish
- `--assistant-id`: Override the default assistant
- `--phone-number-id`: Specify caller ID phone number

**Response:** Returns call ID and status. Save the call ID to check results later.

## Checking Call Status

Use `scripts/get_call.py` to retrieve call details:

```bash
python scripts/get_call.py --call-id "abc123-def456"
```

**Returns:** Status, transcript, recording URL, duration, cost breakdown.

## Call Statuses

- `queued` - Call is queued
- `ringing` - Phone is ringing
- `in-progress` - Call is active
- `forwarding` - Being transferred
- `ended` - Call completed

## Task Variable

The `--task` parameter is passed to the assistant as a variable. Configure your Vapi assistant to use `{{task}}` in its system prompt to receive dynamic instructions per call.

Example assistant prompt:
```
You are a helpful assistant. Your task for this call: {{task}}
```

## Error Handling

Common errors:
- **401**: Invalid API key
- **400**: Invalid phone number format (must be E.164)
- **402**: Insufficient credits
- **404**: Assistant or phone number ID not found
