# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import logging
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from database.ia_filterdb import get_search_results
from utils import is_subscribed, get_size, temp
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from database.connections_mdb import active_connection

logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME


async def inline_users(query: InlineQuery):
    if AUTH_USERS:
        if query.from_user and query.from_user.id in AUTH_USERS:
            return True
        else:
            return False
    if query.from_user and query.from_user.id not in temp.BANNED_USERS:
        return True
    return False


@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for given inline query"""
    chat_id = await active_connection(str(query.from_user.id))

    if not await inline_users(query):
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text='okDa',
            switch_pm_parameter="hehe",
        )
        return

    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text='You have to subscribe my channel to use the bot',
            switch_pm_parameter="subscribe",
        )
        return

    results = []
    if '|' in query.query:
        string, file_type = query.query.split('|', maxsplit=1)
        string = string.strip()
        file_type = file_type.strip().lower()
    else:
        string = query.query.strip()
        file_type = None

    offset = int(query.offset or 0)
    reply_markup = get_reply_markup(query=string)
    files, next_offset, total = await get_search_results(
        chat_id, string, file_type=file_type, max_results=10, offset=offset
    )

    for file in files:
        title = file['file_name']
        size = get_size(file['file_size'])
        f_caption = file.get('caption') or file['file_name']
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name='' if title is None else title,
                    file_size='' if size is None else size,
                    file_caption='' if f_caption is None else f_caption,
                )
            except Exception:
                pass

        user_id = query.from_user.id if query.from_user else 0

        # FIX: query.chat_type returns a ChatType enum object. Extracting .value prevents the AttributeError.
        chat_type = (query.chat_type.value if query.chat_type else '').lower()
        is_private_inline = chat_type in ('private', 'sender')
        
        # FIX: Added the missing if condition and fixed the indentation
        if is_private_inline:
            input_content = InputTextMessageContent(f"{title}\n\nSize: {size}")
            btn = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Open PM", url=f"https://t.me/{temp.U_NAME}")]]
            )
            results.append(
                InlineQueryResultArticle(
                    id=f"fallback-{file['file_id']}",
                    title=f_caption,
                    input_message_content=input_content,
                    description=f"Size: {size}",
                    reply_markup=btn,
                )
            )
        else:
            # Group/supergroup inline: always provide a message (article) that posts in group with a Get File button
            pm_link = f"https://t.me/{temp.U_NAME}?start=inline_{file['file_id']}"
            input_content = InputTextMessageContent(
                f"{f_caption}\n\n Click below to receive this file in PM.\n#INLINE_RESULT"
            )
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("Get File", url=pm_link)]])
            results.append(
                InlineQueryResultArticle(
                    id=f"pm-{file['file_id']}",
                    title=f"{f_caption} Get in PM",
                    input_message_content=input_content,
                    description=f"Size: {size}",
                    reply_markup=btn,
                )
            )

    try:
        if results:
            switch_pm_text = f"{emoji.FILE_FOLDER} Results - {total}"
            if string:
                switch_pm_text += f" for {string}"
            await query.answer(
                results=results,
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="start",
                next_offset=str(next_offset),
            )
        else:
            switch_pm_text = f"{emoji.CROSS_MARK} No results"
            if string:
                switch_pm_text += f' for "{string}"'
            await query.answer(
                results=[],
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="okay",
            )
    except QueryIdInvalid:
        pass
    except Exception as e:
        logging.exception(str(e))


def get_reply_markup(query):
    buttons = [[InlineKeyboardButton('Search again', switch_inline_query_current_chat=query)]]
    return InlineKeyboardMarkup(buttons)
