import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# FRXM SETTINGS
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

REFERRAL_LINK = "https://www.xmglobal.com/referral?token=ClDr1GUguQcx731_PPRanA"
REFERRAL_CODE = "RAFWNYS93"

ADMIN_USERNAME = "Shubham22121"

# This will be detected automatically when the admin starts the bot.
ADMIN_CHAT_ID = None

# =========================
# LOGGING
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global ADMIN_CHAT_ID

    user = update.effective_user
    chat_id = update.effective_chat.id

    # Automatically recognize admin
    if user.username and user.username.lower() == ADMIN_USERNAME.lower():
        ADMIN_CHAT_ID = chat_id

        await update.message.reply_text(
            "🔐 Admin mode activated.\n\n"
            f"Your Telegram Chat ID is:\n`{chat_id}`\n\n"
            "FRXM bot is ready.",
            parse_mode="Markdown",
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "🔗 Create Account",
                url=REFERRAL_LINK
            )
        ],
        [
            InlineKeyboardButton(
                "✅ Account Created",
                callback_data="account_yes"
            ),
            InlineKeyboardButton(
                "❌ Not Yet",
                callback_data="account_no"
            )
        ]
    ]

    message = (
        "👋 *Welcome to FRXM!*\n\n"
        
        "📊 Before continuing, please create your account "
        "using our referral link below.\n\n"

        f"🔗 *Referral Link:*\n{REFERRAL_LINK}\n\n"

        f"🎟️ *Referral Code:*\n`{REFERRAL_CODE}`\n\n"

        "Please make sure you use the referral code while "
        "creating your account.\n\n"

        "👇 Have you created your account?"
    )

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True,
    )


# =========================
# BUTTON HANDLER
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    if query.data == "account_no":

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔗 Create Account",
                    url=REFERRAL_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Account Created",
                    callback_data="account_yes"
                )
            ]
        ]

        await query.edit_message_text(
            "👍 No problem!\n\n"
            "Please create your account using the referral "
            "link below and make sure you use the referral code:\n\n"
            f"🎟️ Referral Code: `{REFERRAL_CODE}`\n\n"
            "Once your account is created, click "
            "the button below.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True,
        )

    elif query.data == "account_yes":

        context.user_data["waiting_for_user_id"] = True

        await query.edit_message_text(
            "✅ Great!\n\n"
            "Please send your *User ID* here so we can "
            "review your profile.\n\n"
            "🔢 Example:\n"
            "`12345678`",
            parse_mode="Markdown",
        )


# =========================
# USER ID HANDLER
# =========================

async def receive_user_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    global ADMIN_CHAT_ID

    user = update.effective_user

    # Ignore messages that aren't part of verification
    if not context.user_data.get("waiting_for_user_id"):
        await update.message.reply_text(
            "Please use /start to begin the FRXM verification process."
        )
        return

    submitted_id = update.message.text.strip()

    # Save submitted ID for this conversation
    context.user_data["submitted_user_id"] = submitted_id
    context.user_data["waiting_for_user_id"] = False

    # Customer confirmation
    await update.message.reply_text(
        "✅ *Thank you!*\n\n"
        f"Your User ID `{submitted_id}` has been received.\n\n"
        "🔎 *Thanks, we are currently reviewing your profile.*\n\n"
        "You will receive a confirmation once your account "
        "has been successfully verified.\n\n"
        "Please wait for further updates. 🙏\n\n"
        "— *FRXM Team*",
        parse_mode="Markdown",
    )

    # Notify admin if admin has started the bot
    if ADMIN_CHAT_ID:

        username = (
            f"@{user.username}"
            if user.username
            else "No username"
        )

        admin_message = (
            "🚨 *NEW FRXM VERIFICATION*\n\n"
            f"👤 Name: {user.full_name}\n"
            f"📱 Username: {username}\n"
            f"🆔 Telegram ID: `{user.id}`\n\n"
            f"🔢 Submitted User ID:\n`{submitted_id}`\n\n"
            "Please review this account."
        )

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            parse_mode="Markdown",
        )


# =========================
# MAIN
# =========================

def main():

    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN environment variable is missing."
        )

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CallbackQueryHandler(button_handler)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_user_id
        )
    )

    print("🚀 FRXM Bot is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
