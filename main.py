from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from nudenet import NudeClassifier
import os

TOKEN = 8225295579:AAFOp87sXr6-GINjPFsgukwPjhZDtdbmTHU

classifier = NudeClassifier()

async def ban_user(update, context):
    await context.bot.ban_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

async def check_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"{photo.file_id}.jpg"
    await file.download_to_drive(path)

    result = classifier.classify(path)
    score = list(result.values())[0]["unsafe"]

    os.remove(path)

    if score > 0.7:
        await update.message.delete()
        await ban_user(update, context)

async def check_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.video:
        return

    video = update.message.video
    file = await video.get_file()
    path = f"{video.file_id}.mp4"
    await file.download_to_drive(path)

    result = classifier.classify(path)
    score = list(result.values())[0]["unsafe"]

    os.remove(path)

    if score > 0.7:
        await update.message.delete()
        await ban_user(update, context)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, check_photo))
app.add_handler(MessageHandler(filters.VIDEO, check_video))
app.run_polling()
