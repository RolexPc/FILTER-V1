# Kanged From @TroJanZheX
# REDIRECT added https://github.com/Joelkb
import asyncio
import re
import ast
import math
import random
lock = asyncio.Lock()
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, FILE_CHANNEL, NO_RESULTS_MSG, AUTH_USERS, CUSTOM_FILE_CAPTION, NOR_IMG, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, SPELL_IMG, MSG_ALRT, FILE_FORWARD, MAIN_CHANNEL, LOG_CHANNEL, PICS, SUPPORT_CHAT_ID, REQ_CHANNEL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import (
    find_gfilter,
    get_gfilters,
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}
FILTER_MODE = {}

NON_IMG = """<b>‼️ FILE NOT FOUND ? ‼️

1️⃣ സിനിമയുടെ സ്പെല്ലിങ്ങ് ഗൂഗിളിൽ ഉള്ളത് പോലെ ആണോ നിങ്ങൾ അടിച്ചത് എന്ന് ഉറപ്പ് വരുത്തുക..!!

2️⃣ നിങ്ങൾ ചോദിച്ച സിനിമ OTT റിലീസ് ആയതാണോ എന്ന് @OTT_ARAKAL_THERAVAD_MOVIESS യിൽ ചെക്ക് ചെയ്യുക..!!

3️⃣ മൂവിക്ക് വേണ്ടി മെസ്സേജ് അയക്കുമ്പോൾ മൂവിയുടെ പേര് ഇറങ്ങിയ വർഷം മാത്രം അയക്കുക..!!

4⃣<i>‼ 𝖱𝖾𝗉𝗈𝗋𝗍 𝗍𝗈 𝖺𝖽𝗆𝗂𝗇 ▶ @ARAKAL_THERAVAD_MOVIES_02_bot</b>"""

@Client.on_message(filters.command('autofilter') & filters.user(ADMINS))
async def fil_mod(client, message): 
      mode_on = ["yes", "on", "true"]
      mode_of = ["no", "off", "false"]

      try: 
         args = message.text.split(None, 1)[1].lower() 
      except: 
         return await message.reply("**𝙸𝙽𝙲𝙾𝙼𝙿𝙴𝚃𝙴𝙽𝚃 𝙲𝙾𝙼𝙼𝙰𝙳...**")
      
      m = await message.reply("**𝚂𝙴𝚃𝚃𝙸𝙽𝙶.../**")

      if args in mode_on:
          FILTER_MODE[str(message.chat.id)] = "True" 
          await m.edit("**𝙰𝚄𝚃𝙾𝙵𝙸𝙻𝚃𝙴𝚁 𝙴𝙽𝙰𝙱𝙻𝙴𝙳**")
      
      elif args in mode_of:
          FILTER_MODE[str(message.chat.id)] = "False"
          await m.edit("**𝙰𝚄𝚃𝙾𝙵𝙸𝙻𝚃𝙴𝚁 𝙳𝙸𝚂𝙰𝙱𝙻𝙴𝙳**")
      else:
          await m.edit("𝚄𝚂𝙴 :- /autofilter on 𝙾𝚁 /autofilter off")

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    await auto_filter(bot, message)
            
@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client,message):
    group_id = message.chat.id
    name = message.text
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)
            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")
            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await message.reply_text(reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await message.reply_text(
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button)
                            )
                    elif btn == "[]":
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or ""
                        )
                    else:
                        button = eval(btn) 
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button)
                        )
                except Exception as e:
                    logger.exception(e)
                break 
    else:
        await auto_filter(client, message)
        return await asyncio.sleep(10)
                                                             


    
    
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name),show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(query.message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    if ENABLE_SHORTLINK == True:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"《{get_size(file.file_size)}》 {file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f'files_#{file.file_id}',
                    ),
                ]
                for file in files
        ]
    

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ 𝑷𝒓𝒆𝒗𝒊𝒐𝒖𝒔", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📖 𝑷𝒂𝒈𝒆𝒔 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
        btn.append(
                    [InlineKeyboardButton(text="🎬 𝑹𝑬𝑸𝑼𝑬𝑺𝑻 𝑮𝑹𝑶𝑼𝑷 🎬", url=f"https://t.me/+lHi0hcen1vJjNTll")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("𝑵𝒆𝒙𝒕 ⏩", callback_data=f"next_{req}_{key}_{n_offset}")])
        btn.append(
                    [InlineKeyboardButton(text="🎬 𝑹𝑬𝑸𝑼𝑬𝑺𝑻 𝑮𝑹𝑶𝑼𝑷 🎬", url=f"https://t.me/+lHi0hcen1vJjNTll")]
        )
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ 𝑷𝒓𝒆𝒗𝒊𝒐𝒖𝒔", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"📖 𝑷𝒂𝒈𝒆𝒔 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("𝑵𝒆𝒙𝒕 ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
        btn.append(
                    [InlineKeyboardButton(text="🎬 𝑹𝑬𝑸𝑼𝑬𝑺𝑻 𝑮𝑹𝑶𝑼𝑷 🎬", url=f"https://t.me/+lHi0hcen1vJjNTll")]
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT, show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT, show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer(script.TOP_ALRT_MSG)
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit(script.MVE_NT_FND)

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer(MSG_ALRT)
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer(MSG_ALRT)

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(MSG_ALRT)

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer(script.ALRT_TXT.format(query.from_user.first_name),show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(MSG_ALRT)
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(MSG_ALRT)
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer(MSG_ALRT)
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        clicked = query.from_user.id #fetching the ID of the user who clicked the button
        try:
            typed = query.message.reply_to_message.from_user.id #fetching user ID of the user who sent the movie request
        except:
            typed = clicked #if failed, uses the clicked user's ID as requested user ID
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        if query.message.chat.type == enums.ChatType.PRIVATE:
            await query.answer()
            await client.send_cached_media(
       
        chat_id=query.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True if 
        ident == "filep" else False,
            )
            return
            
        try:
            if REQ_CHANNEL and not await is_subscribed(client, query):
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
            elif settings['botpm']:
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
            else:
                if clicked == typed:
                    await client.send_cached_media(
                        chat_id=query.from_user.id,
                        file_id=file_id,
                        caption=f_caption,
                        protect_content=True if ident == "filep" else False,
                        )
   
                    await query.answer('Cʜᴇᴄᴋ PM, I ʜᴀᴠᴇ sᴇɴᴛ ғɪʟᴇs ɪɴ PM', show_alert=True)
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
        except UserIsBlocked:
            await query.answer('𝐔𝐧𝐛𝐥𝐨𝐜𝐤 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐦𝐚𝐡𝐧 !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if REQ_CHANNEL and not await is_subscribed(client, query):
            await query.answer("𝑰 𝑳𝒊𝒌𝒆 𝒀𝒐𝒖𝒓 𝑺𝒎𝒂𝒓𝒕𝒏𝒆𝒔𝒔, 𝑩𝒖𝒕 𝑫𝒐𝒏'𝒕 𝑩𝒆 𝑶𝒗𝒆𝒓𝒔𝒎𝒂𝒓𝒕 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    
    
    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        await query.message.edit_text(f"<b>Fᴇᴛᴄʜɪɴɢ Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} ᴏɴ DB... Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        files, total = await get_bad_files(keyword)
        await query.message.edit_text(f"<b>Fᴏᴜɴᴅ {total} Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nFɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ ᴘʀᴏᴄᴇss ᴡɪʟʟ sᴛᴀʀᴛ ɪɴ 5 sᴇᴄᴏɴᴅs!</b>")
        await asyncio.sleep(5)
        deleted = 0
        async with lock:
            try:
                for file in files:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                    deleted += 1
                    if deleted % 20 == 0:
                        await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
            except Exception as e:
                logger.exception(e)
                await query.message.edit_text(f'Eʀʀᴏʀ: {e}')
            else:
                await query.message.edit_text(f"<b>Pʀᴏᴄᴇss Cᴏᴍᴘʟᴇᴛᴇᴅ ғᴏʀ ғɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ !\n\nSᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}.</b>")

    elif query.data == "pages":
        await query.answer()

    elif query.data == "mfna":
        await query.answer("𝑴𝒂𝒏𝒖𝒂𝒍 𝑭𝒊𝒍𝒕𝒆𝒓 𝒊𝒔 𝑪𝒖𝒓𝒓𝒆𝒏𝒕𝒍𝒚 𝑫𝒊𝒔𝒂𝒃𝒍𝒆𝒅..!!", show_alert=True)

    elif query.data == "winfo":
        await query.answer("𝑪𝑶𝑶𝑴𝑰𝑵𝑮 𝑺𝑶𝑶𝑶𝑶𝑶𝑶𝑶𝑶𝑵...!!", show_alert=True)

    elif query.data == "qinfo":
        await query.answer("𝑮𝒍𝒐𝒃𝒂𝒍 𝑭𝒊𝒍𝒕𝒆𝒓𝒔 𝒊𝒔 𝑪𝒖𝒓𝒓𝒆𝒏𝒕𝒍𝒚 𝑫𝒊𝒔𝒂𝒃𝒍𝒆𝒅..!!", show_alert=True)

    elif query.data == "sped":
        await query.answer("𝟏𝟖𝟎 𝑴𝑩𝒔", show_alert=True)

    elif query.data == "ctex":
        await query.answer("© 𝑨𝑹𝑨𝑲𝑨𝑳 𝑻𝑯𝑬𝑹𝑨𝑽𝑨𝑫 𝑴𝑶𝑽𝑰𝑬𝑺 𝑶𝑵𝑳𝒀...", show_alert=True)
        
    elif query.data == "surprise":
        btn = [[
            InlineKeyboardButton('sᴜʀᴘʀɪsᴇ', callback_data='start')
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SUR_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton("👥 𝗚𝗥𝗢𝗨𝗣 - 𝟭", url=f"https://t.me/+hB6czljfX_diZjNl"),
            InlineKeyboardButton("👥 𝗚𝗥𝗢𝗨𝗣 - 𝟮", url=f"https://t.me/+un_DT-l-Td5iODc1")
            ],[
            InlineKeyboardButton("👥 𝗚𝗥𝗢𝗨𝗣 - 𝟯", url=f"https://t.me/ARAKAL_THERAVAD_GROUP_03"),
            InlineKeyboardButton("👥 𝗚𝗥𝗢𝗨𝗣 - 𝟰", url=f"https://t.me/ARAKAL_THERAVAD_GROUP_04")
            ],[
            InlineKeyboardButton("🖥 𝗡𝗘𝗪 𝗢𝗧𝗧 𝗨𝗣𝗗𝗔𝗧𝗘𝗦 🖥", url="https://t.me/OTT_ARAKAL_THERAVAD_MOVIESS")
            ],[
            InlineKeyboardButton("⭕️ 𝗚𝗘𝗧 𝗢𝗨𝗥 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗟𝗜𝗡𝗞𝗦 ⭕️", url="https://t.me/ARAKAL_THERAVAD_GROUP_LINKS")
            ],[
            InlineKeyboardButton('🎁 𝑺𝒑𝒆𝒄𝒊𝒂𝒍𝒊𝒕𝒚 🎁', callback_data='help'),
            InlineKeyboardButton('🛡 𝑬𝒙𝒕𝒓𝒂 🛡', callback_data='extra')
            ],[
            InlineKeyboardButton('🪬 𝑨𝒃𝒐𝒖𝒕 🪬', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )                      
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('🕹 𝑴𝒂𝒏𝒖𝒂𝒍 𝑭𝒊𝒍𝒕𝒆𝒓', 'mfna'),
            InlineKeyboardButton('🌏 𝑮𝒍𝒐𝒃𝒂𝒍 𝑭𝒊𝒍𝒕𝒆𝒓𝒔', 'qinfo'),
            InlineKeyboardButton('𝑨𝒖𝒕𝒐 𝒇𝒊𝒍𝒕𝒆𝒓 📥', callback_data='autofilter')
        ], [
            InlineKeyboardButton('📡 𝑪𝒐𝒏𝒏𝒆𝒄𝒕𝒊𝒐𝒏', 'ctex'),
            InlineKeyboardButton('📌 𝑷𝒊𝒏', 'winfo'),
            InlineKeyboardButton('𝑷𝒖𝒓𝒈𝒆 🗑️', 'winfo')
        ], [
            InlineKeyboardButton('🛜 𝑺𝒑𝒆𝒆𝒅', 'sped'),
            InlineKeyboardButton('🤐 𝑴𝒖𝒕𝒆', 'winfo'),
            InlineKeyboardButton('𝑲𝒊𝒄𝒌❌', 'winfo')
        ], [
            InlineKeyboardButton('⚒ 𝑹𝒆𝒑𝒐𝒓𝒕', 'winfo'),            
            InlineKeyboardButton('𝑬𝒙𝒕𝒓𝒂 📟', 'winfo')
        ], [            
            InlineKeyboardButton('📈 𝑺𝒕𝒂𝒕𝒖𝒔', callback_data='stats')
        ], [
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='start'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(                     
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[            
            InlineKeyboardButton('🪬 𝑯𝒐𝒎𝒆 🪬', callback_data='start')
        ], [
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='help'),
            InlineKeyboardButton('𝑪𝒍𝒐𝒔𝒆✖️', callback_data='close_data')            
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='help')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRA_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='help')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )           
    elif query.data == "stats":
        buttons = [[            
            InlineKeyboardButton('🪬 𝑯𝒐𝒎𝒆 🪬', callback_data='start'),
            InlineKeyboardButton('ʀᴇғʀᴇsʜ', callback_data='rfrsh')
        ], [
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='help'),
            InlineKeyboardButton('𝑪𝒍𝒐𝒔𝒆✖️', callback_data='close_data')            
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        if query.from_user.id in ADMINS:
            await query.message.edit_text(text=script.STATUS_TXT.format(total, users, chats, monsize, free), reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        else:
            await query.answer("⚠ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ⚠\n\nIᴛꜱ ᴏɴʟʏ ғᴏʀ ᴍʏ ADMINS\n\n©AC MOVIES", show_alert=True)
            await query.message.edit_text(text="നോക്കി നിന്നോ ഇപ്പോൾ കിട്ടും 😏", reply_markup=reply_markup)
    elif query.data == "rfrsh":
        await query.answer("𝙁𝙚𝙩𝙘𝙝𝙞𝙣𝙜 𝙈𝙤𝙣𝙜𝙤𝘿𝙗 𝘿𝙖𝙩𝙖𝘽𝙖𝙨𝙚")
        buttons = [[            
            InlineKeyboardButton('🪬 𝑯𝒐𝒎𝒆 🪬', callback_data='start'),
            InlineKeyboardButton('ʀᴇғʀᴇsʜ', callback_data='rfrsh')
        ], [
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='help'),
            InlineKeyboardButton('𝑪𝒍𝒐𝒔𝒆✖️', callback_data='close_data')            
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        if query.from_user.id in ADMINS:
            await query.message.edit_text(text=script.STATUS_TXT.format(total, users, chats, monsize, free), reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        else:
            await query.answer("⚠ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ⚠\n\nIᴛꜱ ᴏɴʟʏ ғᴏʀ ᴍʏ ADMINS\n\n©ᴍʟᴢ ʙᴏᴛᴢ", show_alert=True)
            await query.message.edit_text(text="umfi അല്ലെ 😂 എത്ര നോക്കി നിന്നാലും നിനക്ക് കാണാൻ പറ്റില്ല 😎", reply_markup=reply_markup)
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer(MSG_ALRT)

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)
        try:
            if settings['auto_delete']:
                settings = await get_settings(grp_id)
        except KeyError:
            await save_group_settings(grp_id, 'auto_delete', True)
            settings = await get_settings(grp_id)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Redirect To', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Bot PM' if settings["botpm"] else 'Auto Send',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Auto Delete',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 Mins' if settings["auto_delete"] else 'OFF',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ShortLink',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ ON' if settings["is_shortlink"] else '❌ OFF',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
                
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)


async def auto_filter(client, msg, spoll=False):
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    message = msg
    key = f"{message.id}"
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:                
                if settings["spell_check"]:
                    return await advantage_spell_chok(msg)
                else:
                    # if NO_RESULTS_MSG:
                    #     await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, search)))
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
        settings = await get_settings(message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    pre = 'filep' if settings['file_secure'] else 'file'
    if ENABLE_SHORTLINK == True:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"《{get_size(file.file_size)}》 {file.file_name}", url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"《{get_size(file.file_size)}》 {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                ]
                for file in files
            ]
    
    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"📖 𝑷𝒂𝒈𝒆𝒔 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="𝑵𝒆𝒙𝒕 ⏩", callback_data=f"next_{req}_{key}_{offset}")]
        ) 
        btn.append(
                    [InlineKeyboardButton(text="🎬 𝑹𝑬𝑸𝑼𝑬𝑺𝑻 𝑮𝑹𝑶𝑼𝑷 🎬", url=f"https://t.me/+lHi0hcen1vJjNTll")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🎬 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐆𝐑𝐎𝐔𝐏 🎬", url=f"https://t.me/+SAkK3icaGIJhMmY9")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b>📁 Here is What I Found In My Database For Your Query : {search}👇🏻</b>"
    if imdb and imdb.get('poster'):
        try:
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...</b>")
            else:
                hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hehe.delete()
                        await message.delete()
                        fcu = await message.reply(f"<b>👋 ഹൈയ് {message.from_user.mention} 😍\n\nനിങ്ങളുടെ അഭ്യർത്ഥന ഇല്ലാതാക്കി 🗑️\n(പകർപ്പവകാശ പ്രശ്നം ഒഴിവാക്കുന്നതിനാൽ 😌)\n\nആ ഫയലുകൾക്കായി വീണ്ടും അഭ്യർത്ഥിക്കുക ❤️\n\n𝐻𝑒𝑙𝑙𝑜 👋 {message.from_user.mention}😍\n\n𝐘𝐨𝐮𝐫 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 🗑️\n(𝑫𝒖𝒆 𝑻𝒐 𝑨𝒗𝒐𝒊𝒅 𝑪𝒐𝒑𝒚𝒓𝒊𝒈𝒉𝒕𝒔 𝑰𝒔𝒔𝒖𝒆😌)\n\n𝐈𝐅 𝐘𝐎𝐔 𝐖𝐀𝐍𝐓 𝐓𝐇𝐀𝐓 𝐅𝐈𝐋𝐄, 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐀𝐆𝐀𝐈𝐍 ❤️</b>")
                        await asyncio.sleep(100)
                        await fcu.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hehe.delete()
                        await message.delete()
                        fcu = await message.reply(f"<b>👋 ഹൈയ് {message.from_user.mention} 😍\n\nനിങ്ങളുടെ അഭ്യർത്ഥന ഇല്ലാതാക്കി 🗑️\n(പകർപ്പവകാശ പ്രശ്നം ഒഴിവാക്കുന്നതിനാൽ 😌)\n\nആ ഫയലുകൾക്കായി വീണ്ടും അഭ്യർത്ഥിക്കുക ❤️\n\n𝐻𝑒𝑙𝑙𝑜 👋 {message.from_user.mention}😍\n\n𝐘𝐨𝐮𝐫 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 🗑️\n(𝑫𝒖𝒆 𝑻𝒐 𝑨𝒗𝒐𝒊𝒅 𝑪𝒐𝒑𝒚𝒓𝒊𝒈𝒉𝒕𝒔 𝑰𝒔𝒔𝒖𝒆😌)\n\n𝐈𝐅 𝐘𝐎𝐔 𝐖𝐀𝐍𝐓 𝐓𝐇𝐀𝐓 𝐅𝐈𝐋𝐄, 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐀𝐆𝐀𝐈𝐍 ❤️</b>")
                        await asyncio.sleep(100)
                        await fcu.delete()
                        await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...</b>")
            else:
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                hmm = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hmm.delete()
                        await message.delete()
                        fcu = await message.reply(f"<b>👋 ഹൈയ് {message.from_user.mention} 😍\n\nനിങ്ങളുടെ അഭ്യർത്ഥന ഇല്ലാതാക്കി 🗑️\n(പകർപ്പവകാശ പ്രശ്നം ഒഴിവാക്കുന്നതിനാൽ 😌)\n\nആ ഫയലുകൾക്കായി വീണ്ടും അഭ്യർത്ഥിക്കുക ❤️\n\n𝐻𝑒𝑙𝑙𝑜 👋 {message.from_user.mention}😍\n\n𝐘𝐨𝐮𝐫 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 🗑️\n(𝑫𝒖𝒆 𝑻𝒐 𝑨𝒗𝒐𝒊𝒅 𝑪𝒐𝒑𝒚𝒓𝒊𝒈𝒉𝒕𝒔 𝑰𝒔𝒔𝒖𝒆😌)\n\n𝐈𝐅 𝐘𝐎𝐔 𝐖𝐀𝐍𝐓 𝐓𝐇𝐀𝐓 𝐅𝐈𝐋𝐄, 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐀𝐆𝐀𝐈𝐍 ❤️</b>")
                        await asyncio.sleep(100)
                        await fcu.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hmm.delete()
                        await message.delete()
                        fcu = await message.reply(f"<b>👋 ഹൈയ് {message.from_user.mention} 😍\n\nനിങ്ങളുടെ അഭ്യർത്ഥന ഇല്ലാതാക്കി 🗑️\n(പകർപ്പവകാശ പ്രശ്നം ഒഴിവാക്കുന്നതിനാൽ 😌)\n\nആ ഫയലുകൾക്കായി വീണ്ടും അഭ്യർത്ഥിക്കുക ❤️\n\n𝐻𝑒𝑙𝑙𝑜 👋 {message.from_user.mention}😍\n\n𝐘𝐨𝐮𝐫 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 🗑️\n(𝑫𝒖𝒆 𝑻𝒐 𝑨𝒗𝒐𝒊𝒅 𝑪𝒐𝒑𝒚𝒓𝒊𝒈𝒉𝒕𝒔 𝑰𝒔𝒔𝒖𝒆😌)\n\n𝐈𝐅 𝐘𝐎𝐔 𝐖𝐀𝐍𝐓 𝐓𝐇𝐀𝐓 𝐅𝐈𝐋𝐄, 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐀𝐆𝐀𝐈𝐍 ❤️</b>")
                        await asyncio.sleep(100)
                        await fcu.delete()
                        await message.delete()
        except Exception as e:
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...</b>")
            else:
                logger.exception(e)
                fuk = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await fek.delete()
                        fcu = await message.reply(f"<b>👋 ഹൈയ് {message.from_user.mention} 😍\n\nനിങ്ങളുടെ അഭ്യർത്ഥന ഇല്ലാതാക്കി 🗑️\n(പകർപ്പവകാശ പ്രശ്നം ഒഴിവാക്കുന്നതിനാൽ 😌)\n\nആ ഫയലുകൾക്കായി വീണ്ടും അഭ്യർത്ഥിക്കുക ❤️\n\n𝐻𝑒𝑙𝑙𝑜 👋 {message.from_user.mention}😍\n\n𝐘𝐨𝐮𝐫 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 🗑️\n(𝑫𝒖𝒆 𝑻𝒐 𝑨𝒗𝒐𝒊𝒅 𝑪𝒐𝒑𝒚𝒓𝒊𝒈𝒉𝒕𝒔 𝑰𝒔𝒔𝒖𝒆😌)\n\n𝐈𝐅 𝐘𝐎𝐔 𝐖𝐀𝐍𝐓 𝐓𝐇𝐀𝐓 𝐅𝐈𝐋𝐄, 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐀𝐆𝐀𝐈𝐍 ❤️</b>")
                        await asyncio.sleep(100)
                        await fcu.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await fek.delete()
                        fcu = await message.reply(f"<b>👋 ഹൈയ് {message.from_user.mention} 😍\n\nനിങ്ങളുടെ അഭ്യർത്ഥന ഇല്ലാതാക്കി 🗑️\n(പകർപ്പവകാശ പ്രശ്നം ഒഴിവാക്കുന്നതിനാൽ 😌)\n\nആ ഫയലുകൾക്കായി വീണ്ടും അഭ്യർത്ഥിക്കുക ❤️\n\n𝐻𝑒𝑙𝑙𝑜 👋 {message.from_user.mention}😍\n\n𝐘𝐨𝐮𝐫 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 🗑️\n(𝑫𝒖𝒆 𝑻𝒐 𝑨𝒗𝒐𝒊𝒅 𝑪𝒐𝒑𝒚𝒓𝒊𝒈𝒉𝒕𝒔 𝑰𝒔𝒔𝒖𝒆😌)\n\n𝐈𝐅 𝐘𝐎𝐔 𝐖𝐀𝐍𝐓 𝐓𝐇𝐀𝐓 𝐅𝐈𝐋𝐄, 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐀𝐆𝐀𝐈𝐍 ❤️</b>")
                        await asyncio.sleep(100)
                        await fcu.delete()
                        await message.delete()
    else:
        if message.chat.id == SUPPORT_CHAT_ID:
            await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...</b>",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ​ ", url=f"https://t.me/BugFilmsRequests")]]))
        else:
            fuk = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await fuk.delete()
                    fcu = await message.reply(f"<b>👋 ഹൈയ് {message.from_user.mention} 😍\n\nനിങ്ങളുടെ അഭ്യർത്ഥന ഇല്ലാതാക്കി 🗑️\n(പകർപ്പവകാശ പ്രശ്നം ഒഴിവാക്കുന്നതിനാൽ 😌)\n\nആ ഫയലുകൾക്കായി വീണ്ടും അഭ്യർത്ഥിക്കുക ❤️\n\n𝐻𝑒𝑙𝑙𝑜 👋 {message.from_user.mention}😍\n\n𝐘𝐨𝐮𝐫 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 🗑️\n(𝑫𝒖𝒆 𝑻𝒐 𝑨𝒗𝒐𝒊𝒅 𝑪𝒐𝒑𝒚𝒓𝒊𝒈𝒉𝒕𝒔 𝑰𝒔𝒔𝒖𝒆😌)\n\n𝐈𝐅 𝐘𝐎𝐔 𝐖𝐀𝐍𝐓 𝐓𝐇𝐀𝐓 𝐅𝐈𝐋𝐄, 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐀𝐆𝐀𝐈𝐍 ❤️</b>")
                    await asyncio.sleep(100)
                    await fcu.delete()
                    await message.delete()
            except KeyError:
                grpid = await active_connection(str(message.from_user.id))
                await save_group_settings(grpid, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await fuk.delete()
                    fcu = await message.reply(f"<b>👋 ഹൈയ് {message.from_user.mention} 😍\n\nനിങ്ങളുടെ അഭ്യർത്ഥന ഇല്ലാതാക്കി 🗑️\n(പകർപ്പവകാശ പ്രശ്നം ഒഴിവാക്കുന്നതിനാൽ 😌)\n\nആ ഫയലുകൾക്കായി വീണ്ടും അഭ്യർത്ഥിക്കുക ❤️\n\n𝐻𝑒𝑙𝑙𝑜 👋 {message.from_user.mention}😍\n\n𝐘𝐨𝐮𝐫 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 🗑️\n(𝑫𝒖𝒆 𝑻𝒐 𝑨𝒗𝒐𝒊𝒅 𝑪𝒐𝒑𝒚𝒓𝒊𝒈𝒉𝒕𝒔 𝑰𝒔𝒔𝒖𝒆😌)\n\n𝐈𝐅 𝐘𝐎𝐔 𝐖𝐀𝐍𝐓 𝐓𝐇𝐀𝐓 𝐅𝐈𝐋𝐄, 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐀𝐆𝐀𝐈𝐍 ❤️</b>")
                    await asyncio.sleep(100)
                    await fcu.delete()
                    await message.delete()
     
    if spoll:
        await msg.message.delete()

async def advantage_spell_chok(msg):
    mv_rqst = msg.text
    search = msg.text.replace(" ", "+")
    btn = [[
        InlineKeyboardButton(
            text="📢 Search in Google 📢",
            url=f"https://google.com/search?q={search}"
        )
            
    ]]
    spl = await msg.reply_photo(
            photo="https://telegra.ph/file/79bd06157a47319dbae24.jpg", 
            caption=NON_IMG.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(btn)
    )
    await asyncio.sleep()
    await spl.delete()
    await msg.delete()
    return


async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            elsa = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            try:
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await elsa.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await elsa.delete()

                        else:
                            button = eval(btn)
                            hmm = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            try:
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await hmm.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await hmm.delete()

                    elif btn == "[]":
                        oto = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        try:
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await oto.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_delete', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await oto.delete()

                    else:
                        button = eval(btn)
                        dlt = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        try:
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await dlt.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_delete', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await dlt.delete()

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            
                        else:
                            button = eval(btn)
                            hmm = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )

                    elif btn == "[]":
                        oto = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )

                    else:
                        button = eval(btn)
                        dlt = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )                       

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
