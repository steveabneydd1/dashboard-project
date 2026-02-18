# Microsoft Graph API Setup Request

**Requested by:** Steve Abney  
**Date:** February 5, 2026  
**Purpose:** Enable automated email sending from Steve's Walker Ranch Holdings mailbox

---

## Summary

Steve needs to send business emails (with attachments) from his Walker Ranch Holdings email address using an automated assistant. This requires setting up an Azure AD application with Microsoft Graph API permissions.

**What this enables:**
- Send emails as Steve's Walker Ranch email address
- Attach PDF documents to outgoing emails
- Emails appear in Steve's Sent folder (full audit trail)
- Read Steve's calendar and create/modify appointments

**What this does NOT do:**
- No access to other users' mailboxes or calendars
- No changes to existing email settings
- No access to files, Teams, or other M365 services (unless requested later)

---

## Setup Steps

### Step 1: Register an Application in Azure AD

1. Go to **Azure Portal** → [portal.azure.com](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **+ New registration**
4. Configure:
   - **Name:** `Walker Ranch Email Assistant` (or similar)
   - **Supported account types:** "Accounts in this organizational directory only"
   - **Redirect URI:** Leave blank (not needed for this flow)
5. Click **Register**

### Step 2: Note the Application IDs

After registration, you'll see an overview page. **Record these values:**

| Field | Where to Find |
|-------|---------------|
| **Application (client) ID** | Overview page, top section |
| **Directory (tenant) ID** | Overview page, top section |

### Step 3: Create a Client Secret

1. In the app registration, go to **Certificates & secrets**
2. Click **+ New client secret**
3. Add a description: `Email assistant secret`
4. Choose expiration: **24 months** (recommended)
5. Click **Add**
6. **Immediately copy the secret Value** (it won't be shown again)

| Field | Value |
|-------|-------|
| **Client Secret** | (copy the Value, not the Secret ID) |

### Step 4: Add API Permissions

1. In the app registration, go to **API permissions**
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Select **Application permissions** (not Delegated)
5. Search and add these permissions:

| Permission | Purpose |
|------------|---------|
| `Mail.Send` | Send emails as any user (will be scoped to Steve only via policy) |
| `Calendars.ReadWrite` | Read and create/modify calendar events |

**Optional — add if Steve wants additional access later:**

| Permission | Purpose |
|------------|---------|
| `Mail.ReadWrite` | Read and manage emails |
| `Mail.Read` | Read emails (read-only) |
| `Calendars.Read` | Read calendar (read-only, if ReadWrite is too broad) |

6. Click **Add permissions**
7. Click **Grant admin consent for [Organization]** (requires admin)
8. Confirm all permissions show green checkmarks

### Step 5: (Recommended) Scope to Steve's Mailbox Only

To restrict this app to ONLY Steve's mailbox (security best practice):

1. Go to **Exchange Admin Center** → [admin.exchange.microsoft.com](https://admin.exchange.microsoft.com)
2. Navigate to **Roles** → **Admin roles**
3. Create an **Application Access Policy** using PowerShell:

```powershell
# Connect to Exchange Online
Connect-ExchangeOnline

# Create a mail-enabled security group with just Steve
New-DistributionGroup -Name "Walker Ranch Email Assistant Users" -Type Security -Members steve@walkerranchholdings.com

# Restrict the app to only this group
New-ApplicationAccessPolicy -AppId <APPLICATION_CLIENT_ID> -PolicyScopeGroupId "Walker Ranch Email Assistant Users" -AccessRight RestrictAccess -Description "Limit email assistant to Steve only"

# Test the policy
Test-ApplicationAccessPolicy -Identity steve@walkerranchholdings.com -AppId <APPLICATION_CLIENT_ID>
```

*(Replace `steve@walkerranchholdings.com` with Steve's actual email address and `<APPLICATION_CLIENT_ID>` with the Application ID from Step 2)*

---

## Information to Return to Steve

Please provide Steve with the following (via secure channel):

```
Tenant ID: ____________________________________
Client ID: ____________________________________
Client Secret: ________________________________
Steve's Email Address: ________________________
```

---

## Security Notes

- The client secret should be treated like a password
- The app can only send email (no read access unless Mail.Read is added)
- With the Application Access Policy, the app cannot access any mailbox except Steve's
- Consider setting a calendar reminder to rotate the client secret before expiration

---

## Questions?

Contact Steve Abney for clarification on requirements.
