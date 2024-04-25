import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied

import time
import os
import threading
import json

with open('config.json', 'r') as f: DATA = json.load(f)
def getenv(var): return os.environ.get(var) or DATA.get(var, None)

bot_token = getenv("TOKEN")
api_hash = getenv("HASH")
api_id = getenv("ID")
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

ss = getenv("STRING")
if ss is not None:
  acc = Client("myacc" ,api_id=api_id, api_hash=api_hash, session_string=ss)
  acc.start()
else: acc = None

# download status
def downstatus(statusfile,message):
  while True:
    if os.path.exists(statusfile):
      break

  time.sleep(3)
  while os.path.exists(statusfile):
    with open(statusfile,"r") as downread:
      txt = downread.read()
    try:
      bot.edit_message_text(message.chat.id, message.id, f"__Downloaded__ : **{txt}**")
      time.sleep(10)
    except:
      time.sleep(5)


# upload status
def upstatus(statusfile,message):
  while True:
    if os.path.exists(statusfile):
      break

  time.sleep(3)
  while os.path.exists(statusfile):
    with open(statusfile,"r") as upread:
      txt = upread.read()
    try:
      bot.edit_message_text(message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
      time.sleep(10)
    except:
      time.sleep(5)


# progress writter
def progress(current, total, message, type):
  with open(f'{message.id}{type}status.txt',"w") as fileup:
    fileup.write(f"{current * 100 / total:.1f}%")


# start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
  bot.send_message(message.chat.id, f"__ Hi **{message.from_user.mention}**, I am Save Restricted Bot, I can send you restricted content by it's post link__\n\n{USAGE}",
  reply_markup=InlineKeyboardMarkup([[ InlineKeyboardButton(" Source Code", url="https://github.com/bipinkrish/Save-Restricted-Bot")]]), reply_to_message_id=message.id)


# message processing (with channel forwarding)
@bot.on_message(filters.channel & filters.chat(getenv("SOURCE_CHANNEL_ID")))  # Listen to source channel only
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
  print(message.text)

  # joining chats
  if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:

    if acc is None:
      bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
      return

    try:
      try: acc.join_chat(message.text)
      except Exception as e: 
        bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)
        return
      bot.send_message(message.chat.id,"**Chat Joined**", reply_to_message_id=message.id)
    except UserAlreadyParticipant:
      bot.send_message(message.chat.id,"**Chat alredy Joined**", reply_to_message_id=message.id)
    
  except InviteHashExpired:
      bot.send_message(message.chat.id,"**Invalid Link**", reply_to_message_id=message.id)

  # getting message
  elif "https://t.me/" in message.text:

    datas = message.text.split("/")
    temp = datas[-1].replace("?single","").split("-")
    fromID = int(temp[0].strip())
    try: toID = int(temp[1].strip())
    except: toID = fromID

    for msgid in range(fromID, toID+1):

      # private
      if "https://t.me/c/" in message.text:
        chatid = int("-100" + datas[4])

        if acc is None:
          bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
          return

        handle_private(message,chatid,msgid)
        # try: handle_private(message,chatid,msgid)
        # except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)

      # bot
      elif "https://t.me/b/" in message.text:
        username = datas[4]

        if acc is None:
          bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
          return
        try: handle_private(message,username,msgid)
        except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)

      # public
      else:
        username = datas[3]

        try: msg = bot.get_messages(username,msgid)
        except UsernameNotOccupied: 
          bot.send_message(message.chat.id,f"**The username is not occupied by anyone**", reply_to_message_id=message.id)
          return

        try: 
          # Forward the message to the target channel
          bot.copy_message(
              getenv("TARGET_CHANNEL_ID"),  # Replace with your target channel ID
              message.chat.id,
              msgid,
              reply_to_message_id=message.id
          )
          bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        except:
          if acc is None:
            bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
            return
          try: handle_private(message,username,msgid)
          except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)

      # wait time
      time.sleep(3)


# handle private
def handle_private(message: pyrogram.types.messages_and_media.message.Message, chatid: int, msgid: int):
  msg: pyrogram.types.messages_and_media.message.Message = acc.get_messages(chatid,msgid)
  msg_type = get_message_type(msg)

  if "Text" == msg_type:
    bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
    return

  smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.id)
  dosta = threading.Thread(target=lambda:downstatus(f'{message.id}downstatus.txt',smsg),daemon=True)
  dosta.start()
  file = acc.download_media(msg, progress=progress, progress_args=[message,"down"])
  os.remove(f'{message.id}downstatus.txt')

  upmsg = bot.send_message(message.chat.id, '__Uploading__', reply_to_message_id=message.id)
    upsta = threading.Thread(target=lambda: upstatus(f'{message.id}upstatus.txt',upmsg), daemon=True)
  upsta.start()
  bot.send_document(message.chat.id, file, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
  os.remove(f'{message.id}upstatus.txt')
  os.remove(file)


# get message type
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
  if msg.text:
    return "Text"
  elif msg.document:
    return "Document"
  elif msg.photo:
    return "Photo"
  elif msg.video:
    return "Video"
  elif msg.audio:
    return "Audio"
  else:
    return "Unsupported"


bot.run()
