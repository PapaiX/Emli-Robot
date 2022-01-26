import re

import rapidjson as json
from bs4 import BeautifulSoup
from Emli import pbot

from hurry.filesize import size as sizee
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Update
from requests import get
from yaml import Loader, load


# Important credits:
# * The ofox command was originally developed by MrYacha.
# * The /twrp, /specs, /whatis, /variants, /samcheck and /samget
# commands were originally developed by KassemSYR.
#
# This module was inspired by Android Helper Bot by Vachounet.
# None of the code is taken from the bot itself, to avoid confusion.
# Please don't remove these comment, show respect to module contributors.


REALME_FIRM = "https://raw.githubusercontent.com/RealmeUpdater/realme-updates-tracker/master/data/latest.yml"


@pbot.on_message(filters.command("realmeui"))
async def realmeui(c: Client, update: Update):
    if len(update.command) != 2:
        message = "Please write a codename, example: `/realmeui RMX2061`"
        await update.reply_text(message)
        return

    codename = update.command[1]

    yaml_data = load(get(REALME_FIRM).content, Loader=Loader)
    data = [i for i in yaml_data if codename in i['codename']]

    if len(data) < 1:
        await update.reply_text("Provide a valid codename!")
        return

    for fw in data:
        reg = fw['region']
        link = fw['download']
        device = fw['device']
        version = fw['version']
        cdn = fw['codename']
        sys = fw['system']
        size = fw['size']
        date = fw['date']
        md5 = fw['md5']

        btn = reg + ' | ' + version

        keyboard = [[InlineKeyboardButton(text=btn, url=link)]]

    text = f"**RealmeUI - Last build for {codename}:**"
    text += f"\n\n**Device:** `{device}`"
    text += f"\n**System:** `{sys}`"
    text += f"\n**Size:** `{size}`"
    text += f"\n**Date:** `{date}`"
    text += f"\n**MD5:** `{md5}`"

    await update.reply_text(text,
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            parse_mode="markdown")


@pbot.on_message(filters.command("samspec"))
async def samspecs(c: Client, update: Update):
    if len(update.command) != 2:
        message = (
            "Please write your codename or model into it,\ni.e <code>/specs herolte</code> or <code>/specs sm-g610f</code>")
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
        return
    device = update.command[1]
    data = GetDevice(device).get()
    if data:
        name = data['name']
        model = data['model']
        device = name.lower().replace(' ', '-')
    else:
        message = "coudn't find your device, chack device & try!"
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
        return
    sfw = get(f'https://sfirmware.com/samsung-{model.lower()}/')
    if sfw.status_code == 200:
        page = BeautifulSoup(sfw.content, 'lxml')
        message = '<b>Device:</b> Samsung {}\n'.format(name)
        res = page.find_all('tr', {'class': 'mdata-group-val'})
        res = res[2:]
        for info in res:
            title = re.findall(r'<td>.*?</td>', str(info)
                               )[0].strip().replace('td', 'b')
            data = re.findall(r'<td>.*?</td>', str(info)
                              )[-1].strip().replace('td', 'code')
            message += "• {}: <code>{}</code>\n".format(title, data)

    else:
        message = "Device specs not found in bot database, make sure this is a Samsung device!"
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
        return

    await c.send_message(
        chat_id=update.chat.id,
        text=message)
