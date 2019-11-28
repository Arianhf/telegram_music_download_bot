#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
from uuid import uuid4
from lastfm_handler import get_tags

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import (
    Updater,
    InlineQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
)
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ForceReply,
    MessageEntity,
    ChatAction,
)
from telegram.utils.helpers import escape_markdown
from telegram.ext.filters import Filters

from deezer_handler import DeezerHandler
from db_handler import (
    create_track_record,
    update_track_record,
    retreive_track_record,
    create_music_table,
    alter_music_table_add_music_info,
    create_download_table,
    create_download_record,
    retreive_download_history
)
from datetime import datetime
from utils import timezone_time

create_music_table()
alter_music_table_add_music_info()
create_download_table()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


from functools import wraps


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action
            )
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


send_typing_action = send_action(ChatAction.TYPING)
send_upload_video_action = send_action(ChatAction.UPLOAD_VIDEO)
send_upload_photo_action = send_action(ChatAction.UPLOAD_PHOTO)
send_upload_audio_action = send_action(ChatAction.UPLOAD_AUDIO)
send_upload_file_action = send_action(ChatAction.UPLOAD_DOCUMENT)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")

def get_download_history(update, context):
    chat_id = update.message.chat_id
    with open("download_history.txt","w") as f:
        f.write(str(retreive_download_history()))
    update.message.reply_text("downloading!")
    context.bot.send_document(document=open('download_history.txt', 'rb'), chat_id=chat_id)
#    update.message.reply_text(retreive_download_history())

def get_message(update, context):
    keyboard = [
        #[
         #   InlineKeyboardButton(
          #      "Search by artist",
           #     switch_inline_query_current_chat=f"Artist:{update.message.text}",
          #  ),
           # InlineKeyboardButton(
            #    "Search by album",
             #   switch_inline_query_current_chat=f"Album:{update.message.text}",
         #   ),
       # ],
        [
            InlineKeyboardButton(
                "Global search",
                switch_inline_query_current_chat=f"{update.message.text}",
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Please choose:", reply_markup=reply_markup)


# create a func that downloads music for single file
# use it in a for to get albums.
@send_upload_file_action
def get_link(update, context):
    deezer = DeezerHandler()
    chat_id = update.message.chat_id

    update.message.reply_text("Downloading...")
    track_retreive = {
        "deezer_link": update.message.text,
    }
    audio_in_db = retreive_track_record(track_retreive)
    
    if audio_in_db is None:
        items = deezer.download_url(update.message.text)
    else:
        update.message.reply_text("Download done, Uploading...")
        file = context.bot.send_audio(chat_id=chat_id, audio=audio_in_db[1])
        
        track_update = {
            "last_downloaded": timezone_time(datetime.now()),
            "deezer_link": update.message.text,
            "performer": file.audio.performer,
            "title":file.audio.title
        }
        update_track_record(track_update)
        download_record = {
            "telegram_full_name":update.message.from_user.full_name,
            "telegram_id":update.message.from_user.id,
            "telegram_link":update.message.from_user.link,
            "telegram_name":update.message.from_user.name,
            "telegram_username":update.message.from_user.username,
            "music_id":audio_in_db[0]
        }
        create_download_record(download_record)
        
        return
    update.message.reply_text("Download done, Uploading...")

    # fix this! items is not a list of songs
    # add if update.message has album in it!
    if isinstance(items, list):
        for item in items:
            context.bot.send_audio(chat_id=chat_id, audio=open(item, "rb"))
    else:
        try:
            song = context.user_data["data_dict"][update.message.text]
        except:
            context.user_data["data_dict"] = {}
            song = deezer.get_full_track(update.message.text.split("/")[-1])

        authors = []
        for author in song.contributors:
            authors.append(author["name"])
        author_names = ", ".join(authors)
        tags = get_tags(song.artist.name, song.title)
        if tags is not None:
            text = ""
            for i, tag in enumerate(tags):
                if i == len(tags) - 1:
                    text += f"#{tag}"
                else:
                    text += f"#{tag}, "
            try:
                context.bot.send_message(chat_id=chat_id, text=text)
            except:
                pass
        file = context.bot.send_audio(
            chat_id=chat_id,
            audio=open(items, "rb"),
            title=song.title,
            performer=author_names,
            thumb=song.album.cover_medium,
        )

        track = {
            "telegram_file_id": file.audio.file_id,
            "deezer_link": update.message.text,
            "download_count": 1,
            "last_downloaded": timezone_time(datetime.now()),
            "performer": file.audio.performer,
            "title": file.audio.title,
        }
        track_id = create_track_record(track)
        
        download_record = {
            "telegram_full_name":update.message.from_user.full_name,
            "telegram_id":update.message.from_user.id,
            "telegram_link":update.message.from_user.link,
            "telegram_name":update.message.from_user.name,
            "telegram_username":update.message.from_user.username,
            "music_id":track_id
        }
        create_download_record(download_record)
        context.user_data["data_dict"] = {}


def inlinequery(update, context):
    """Handle the inline query."""
    deezer = DeezerHandler()
    query = update.inline_query.query
    data_dict = {}
    if query.startswith("Artist:"):
        artist_name = query[7:]

        results = []
        item = None
        for item in deezer.get_artist(artist_name)[:15]:
            data_dict[item.link] = item
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=item.name,
                    thumb_url=item.picture_medium,
                    input_message_content=InputTextMessageContent(item.link),
                    description=item.artist.name,
                )
            )
    elif query.startswith("Album:"):
        album_name = query[6:]

        results = []
        item = None
        for item in deezer.get_album(album_name)[:5]:
            data_dict[item.link] = item
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=item.title,
                    thumb_url=item.cover_medium,
                    input_message_content=InputTextMessageContent(item.link),
                    description=item.artist.name,
                )
            )
    else:
        song = query

        results = []
        item = None
        for item in deezer.get_song(song)[:15]:
            data_dict[item.link] = deezer.get_full_track(item.id)
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=item.title,
                    thumb_url=item.get_album().cover_medium,
                    input_message_content=InputTextMessageContent(item.link),
                    description=item.artist.name,
                )
            )
    context.user_data["data_dict"] = data_dict
    update.inline_query.answer(results)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(
        'Update "%s" with context data  "%s" caused error "%s"',
        update,
        context.user_data,
        context.error,
    )


def button(update, context):
    query = update.callback_query
    # query.edit_message_text(text="Selected option: {}".format(query.data))


def main():
    import json

    with open('config.json') as json_config_file:
        json_config = json.load(json_config_file)
    TELEGRAM_TOKEN = json_config['TELEGRAM_TOKEN'] 
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        TELEGRAM_TOKEN, use_context=True
    )

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("get_download_history", get_download_history))
    dp.add_handler(
        MessageHandler(
            Filters.text
            & (
                Filters.entity(MessageEntity.URL)
                | Filters.entity(MessageEntity.TEXT_LINK)
            ),
            get_link,
        )
    )
    dp.add_handler(MessageHandler(Filters.text, get_message))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
