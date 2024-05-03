import os
import logging
import zipfile
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(" هذا البوت مخصص الاداء انشاء حسابات سافيوم وهوه يساعدك على وضع التوكن والايدي في المكان المناسب ويرسل لك الملف مع المتطلبات الازمه المطور موهان: @XX44G\n\n")

def receive_file(update: Update, context: CallbackContext) -> None:
    file = context.bot.get_file(update.message.document.file_id)
    file_name = update.message.document.file_name
    file.download(file_name)
    context.user_data["file_name"] = file_name
    update.message.reply_text("يرجى إرسال التوكن الآن 🔃")
    # Set state to switch_to_zeros
    context.user_data["state"] = "switch_to_zeros"

def receive_text(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    state = context.user_data.get("state")
    
    if state == "switch_to_zeros":
        context.user_data["zeros_text"] = text
        update.message.reply_text("تم وضع التوكن بنجاح. يرجى إرسال الايدي الآن 🆔")
        # Set state to switch_to_ones
        context.user_data["state"] = "switch_to_ones"
    elif state == "switch_to_ones":
        context.user_data["ones_text"] = text
        file_name = context.user_data.get("file_name")
        zeros_text = context.user_data.get("zeros_text")
        ones_text = context.user_data.get("ones_text")
        
        # Modify the file content
        with open(file_name, 'r') as file:
            original_text = file.read()

        modified_text = original_text.replace("0000", zeros_text)
        modified_text = modified_text.replace("1111", ones_text)

        # Write the modified content to a new file
        new_file_name = f"{file_name}"
        with open(new_file_name, 'w') as file:
            file.write(modified_text)

        # Create a ZIP archive containing the modified file, requirements.txt, and Procfile
        with zipfile.ZipFile(f"{file_name}_modified.zip", "w") as zipf:
            zipf.write(new_file_name)
            zipf.writestr("requirements.txt", "websocket-client==1.2.1\nrequests==2.26.0\ntelebot==0.0.4")
            zipf.writestr("Procfile", "bot: python main.py")

        # Send the ZIP archive
        context.bot.send_document(update.effective_chat.id, document=open(f"{file_name}_modified.zip", 'rb'), filename=f"{file_name}_modified.zip")

        # Cleanup
        os.remove(file_name)
        os.remove(new_file_name)
        os.remove(f"{file_name}_modified.zip")

def main() -> None:
    TOKEN = "6765671070:AAF-gOtVDtWeKf2DjggQcb8L34OZbGDHAxc"
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, receive_file))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, receive_text))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
