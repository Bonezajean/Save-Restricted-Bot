import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied

import time
import os
import threading
import json

# Load configuration from config.json
with open('config.json', 'r') as f:
    DATA = json.load(f)

def getenv(var):
    return os.environ.get(var) or DATA.get(var, None)

# Initialize bot with configuration
bot_token = getenv("TOKEN") 
api_hash = getenv("HASH") 
api_id = getenv("ID")
bot = pyrogram.Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define the source and destination channels (change these to your channel IDs)
source_channel = "-1002029423962"
destination_channel = "-1002107541705"

# Function to forward messages
def forward_message(client, message):
    # Forward the message from source channel to destination channel
    client.forward_messages(destination_channel, source_channel, [message.message_id])

# Message handler for messages in the source channel
@bot.on_message(pyrogram.filters.chat(source_channel))
def handle_message(client, message):
    # Forward the message to the destination channel
    forward_message(client, message)
    
USAGE = """**FOR PUBLIC CHATS**

__just send post/s link__

**FOR PRIVATE CHATS**

__first send invite link of the chat (unnecessary if the account of string session already member of the chat)
then send post/s link__

**FOR BOT CHATS**

__send link with '/b/', bot's username and message id, you might want to install some unofficial client to get the id like below__

https://t.me/b/botusername/4321

**MULTI POSTS**

__send public/private posts link as explained above with formate "from - to" to send multiple messages like below__

https://t.me/xxxx/1001-1010

https://t.me/c/xxxx/101 - 120

__note that space in between doesn't matter__
"""

@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bot.send_message(message.chat.id, f"__👋 Hi **{message.from_user.mention}**, I am Save Restricted Bot, I can send you restricted content by it's post link__\n\n{USAGE}",
                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Source Code", url="https://github.com/bipinkrish/Save-Restricted-Bot")]]),
                     reply_to_message_id=message.id)


bot.run()
