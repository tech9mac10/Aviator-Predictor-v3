from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
import json
import logging
from typing import Dict, Any

# --- Configuration ---
WEBHOOK_SECRET = "mzQamGwdnaVu_22c7PtgZaPCHqREfjdCFTFFWWDN4Hs"  # ← MUST match the secret in your Bank API's webhooks table
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
TELEGRAM_CHAT_ID_MAP = {}  # In production: load from DB (user_id → chat_id)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bank Webhook Receiver", description="Receives real-time events from the Bank API")

@app.post("/webhooks/bank")
async def handle_bank_webhook(request: Request):
    """
    Receive and process webhook events from the Bank API.
    """
    # 1. Read raw body (needed for signature verification)
    body = await request.body()
    sig_header = request.headers.get("x-bank-signature")

    if not sig_header:
        logger.warning("Missing X-Bank-Signature header")
        raise HTTPException(status_code=401, detail="Missing signature")

    # 2. Verify signature
    expected_sig = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(f"sha256={expected_sig}", sig_header):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 3. Parse payload
    try:
        payload: Dict[str, Any] = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook body")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = payload.get("event")
    data = payload.get("data", {})

    logger.info(f"Received event: {event_type}")

    # 4. Handle events
    if event_type == "transaction.completed":
        print(payload)
        # await handle_transaction_completed(data)
    else:
        logger.info(f"Unhandled event type: {event_type}")
        # Still return 200 to avoid retries for unknown events
        return {"status": "ignored"}

    return {"status": "ok", "payload": payload}


# --- Event Handlers ---
async def handle_transaction_completed(data: Dict[str, Any]):
    """Handle a completed transaction."""
    try:
        amount = data["amount"]
        currency = data["currency"]
        to_user_id = data["to_user_id"]
        from_user_id = data["from_user_id"]

        # Example 1: Send Telegram notification
        chat_id = TELEGRAM_CHAT_ID_MAP.get(to_user_id)
        if chat_id:
            message = f"✅ You received {amount} {currency}!"
            await send_telegram_message(chat_id, message)

        # Example 2: Send mobile push (pseudo-code)
        # device_token = get_device_token(to_user_id)
        # if device_token:
        #     send_push_notification(device_token, "Payment Received", message)

        # Example 3: Send email (pseudo-code)
        # user_email = get_user_email(to_user_id)
        # if user_email:
        #     send_email(user_email, "You received money!", message)

        logger.info(f"Notification sent for transaction to user {to_user_id}")

    except Exception as e:
        logger.error(f"Error handling transaction.completed: {e}")
        # Do NOT re-raise — webhook should return 200 even if notification fails
        # (so Bank API doesn't retry indefinitely)


# --- Health Check (for monitoring) ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}
