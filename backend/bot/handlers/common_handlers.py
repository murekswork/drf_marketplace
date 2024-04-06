from decorators import exception_logging
from keyboards import CommonMarkups
from replies import Replies
from schemas.schemas import couriers
from telegram import Update
from telegram.ext import CallbackContext


@exception_logging
async def profile_handler(update: Update, context: CallbackContext):
    user = update.message.chat
    await update.message.reply_html(
        text=Replies.COURIER_PROFILE_INFO.format(**couriers.get(int(user.id)).__dict__)
    )


@exception_logging
async def start_bot(update: Update, context: CallbackContext):
    await update.message.reply_text(
        text="Welcome!", reply_markup=CommonMarkups.MAIN_MARKUP
    )
