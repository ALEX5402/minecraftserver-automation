import json
import os
import re
import pexpect
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

ADMIN_FILE = 'admins.json'
admins = []
MONITOR_CHAT_ID = -1002420089111
bot_token = "bot_token"
server_session = None
server_stopped_manually = False
server_start_time = None  # Track when the server was started
serverdelay = 30
serveris_on = True
screen_session = None
backup_in_progress = False
backupseasson =  False


def load_or_create_admins(file_path=ADMIN_FILE):
    global admins
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            json.dump({"admins": []}, file, indent=4)
        send_telegram_notification(f"Created {file_path} with an empty list of admins.")
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            admins.extend(data.get("admins", []))
    except Exception as e:
         send_telegram_notification(f"Error loading admin file: {e}")

async def start(update: Update, context):
    await update.message.reply_text('Hi! Send ".hi" to get a greeting. created by @alex5402 to manage his minecraft server')

async def start_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global server_session , server_start_time
    if update.effective_user.id not in admins:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    if server_session is not None:
        await update.message.reply_text("The server is already running.")
        return
    try:
        server_session = pexpect.spawn(
            "bash server.sh", 
            encoding="utf-8", 
            timeout=None
        )
        server_start_time = datetime.now()
        asyncio.create_task(checkserver())
        await update.message.reply_text("Minecraft server started successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error starting server: {e}")

def clean_output(output):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', output)


async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global server_session
    if update.effective_user.id not in admins:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    if server_session is None:
        await update.message.reply_text("The server is not running. Use /startserver to start it.")
        return
    if not context.args:
        await update.message.reply_text("Please provide a command to send.")
        return
    command = " ".join(context.args)
    try:
        while True:
            try:
                _ = server_session.read_nonblocking(size=1024, timeout=0.1)
            except pexpect.TIMEOUT:
                break
            except pexpect.EOF:
                break
        server_session.sendline(command)
        await asyncio.sleep(0.5)
        new_output = []
        while True:
            try:
                chunk = server_session.read_nonblocking(size=1024, timeout=0.1)
                if chunk:
                    new_output.append(chunk)
            except pexpect.TIMEOUT:
                break
            except pexpect.EOF:
                break
        new_output_text = clean_output("".join(new_output).strip())
        if new_output_text:
            await update.message.reply_text(f"Command executed: {command}\nNew Output:\n{new_output_text}")
        else:
            await update.message.reply_text(f"Command executed: {command}\nNo new output detected.")
    except Exception as e:
        await update.message.reply_text(f"Error executing command: {e}")

async def stop_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global server_session, server_stopped_manually,serveris_on , server_start_time
    if update.effective_user.id not in admins:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    if server_session is None:
        await update.message.reply_text("The server is not running. Use /startserver to start it first.")
        return
    
    if server_start_time and datetime.now() - server_start_time < timedelta(seconds=serverdelay):
        await update.message.reply_text("You need to wait 30 seconds after starting the server before stopping it.")
        return

    try:
        server_stopped_manually = True
        serveris_on = False
        await asyncio.sleep(2)
        server_session.sendline("stop")
        await update.message.reply_text("Minecraft server stopped successfully!")
        server_session = None
        server_stopped_manually = False
    except Exception as e:
        await update.message.reply_text(f"Error stopping server: {e}")


async def send_telegram_notification(message: str):
    application = Application.builder().token(bot_token).build()
    await application.bot.send_message(chat_id=MONITOR_CHAT_ID, text=message)

async def handle_message(update: Update, context):
    global admins
    if update.message.chat.id == MONITOR_CHAT_ID or update.message.chat.type == "private":
        user_id = update.message.from_user.id
        if user_id in admins:
            if update.message.text == ".hi":
                await update.message.reply_text("Hello")
        else:
            await update.message.reply_text("You don't have access to use me.")


async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global server_session

    if update.effective_user.id not in admins:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    if server_session is True:
        await send_telegram_notification("Server is still running. Use /stop to stop it.")
        return

    if server_session is None:
        try:
            pexpect.spawn("bash clean.sh", 
                              encoding="utf-8", 
                              timeout=None)
                                 
            await send_telegram_notification(f"all Lock Files are removed.")
        except Exception as e:
            await send_telegram_notification(f"Error deleting files: {e}")
        await asyncio.sleep(5) 


async def checkserver():
    global serveris_on, screen_session, server_session
    while serveris_on:
        try:
            if server_session is None:
                await asyncio.sleep(5)
                continue
            
            # Check if the screen session exists
            screen_session = pexpect.spawn("screen -list", encoding="utf-8", timeout=None)
            screen_session.expect(pexpect.EOF)
            output = screen_session.before
            
            if "minectaftserver" in output:
                serveris_on = True
            else:
                # Restart the server
                server_session = None
                server_session = pexpect.spawn("bash server.sh", encoding="utf-8", timeout=None)
                await send_telegram_notification("Server crashed and is being restarted.")
            
            # Add a delay between checks
            await asyncio.sleep(5)
        except Exception as e:
            await send_telegram_notification(f"Error in server check: {e}")
            await asyncio.sleep(5)

async def execute_backup_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global backup_in_progress ,  backupseasson

    if update.effective_user.id not in admins:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if backup_in_progress:
        await send_telegram_notification("Backup is already in progress.")
        return

    try:
        # Run the backup script
        backup_in_progress = True
        await send_telegram_notification(f"Backup started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        backupseasson = pexpect.spawn(
            "bash backup.sh",
            encoding="utf-8",
            timeout=None
        )
        if backupseasson == None:
            backup_in_progress = False

    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"Error executing backup script: {e}")
        await send_telegram_notification(f"Error executing backup script: {e}")



def main() -> None:
    global admins
    load_or_create_admins()
    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("startserver", start_server))
    application.add_handler(CommandHandler("sendcommand", send_command))
    application.add_handler(CommandHandler("stop", stop_server))
    application.add_handler(CommandHandler("clean", clean))
    application.add_handler(CommandHandler("backup", execute_backup_script))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()
    logging.basicConfig(level=logging.INFO)
    logging.info("Message or event details")

if __name__ == '__main__':
    main()
