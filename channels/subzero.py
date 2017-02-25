# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per http://www.subzero.it
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# By MrTruth
# ------------------------------------------------------------

import re

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "subzero"
__category__ = "A, T"
__type__ = "generic"
__title__ = "SubZero"
__language__ = "IT"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:51.0) Gecko/20100101 Firefox/51.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', "http://www.subzero.it"]
]

def isGeneric():
    return True

# ----------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info("[SubZero.py]==> mainlist")
    itemlist = [Item(channel=__channel__,
                     action="ultimitorrent",
                     title=color("Ultimi torrent", "orange"),
                     url="https://www.nyaa.se/?page=separate&user=97824",
                     thumbnail="https://raw.githubusercontent.com/MrTruth0/imgs/master/SOD/Channels/SubZero.png",),
                Item(channel=__channel__,
                     action="listacompleta",
                     title=color("Lista completa", "azure"),
                     url="https://www.nyaa.se/?page=separate&user=97824",
                     thumbnail="https://raw.githubusercontent.com/MrTruth0/imgs/master/SOD/Channels/SubZero.png")
                ]

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def ultimitorrent(item):
    logger.info("[SubZero.py]==> ultimitorrent")
    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)
    blocco = scrapertools.get_match(data, '<table class="titleTable"><tr class="titleDivider">(.*?)</table>')
    patron = \
        '<tr class="[titleOdd|titleEven]+"><td class="name">\[.*?\](.*?)</td>[^>]+>[^>]+>([\-?\d]+).*?<[^>]+>[^>]+><td class="center">.*?(\d+p).*?</td>[^>]+>[^>]+>[^>]+><a href="(.*?)"'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedtitle, scrapedinfo1, scrapedinfo2, scrapedurl in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 server="torrent",
                 title=color((color(".torrent ", "darkkhaki") + color(encode(scrapedinfo1), "gold") + " | " + color(scrapedtitle, "deepskyblue") + "(" + color(scrapedinfo2, "orange") + ")"), "azure"),
                 url="https:" + scrapedurl.replace("#38;", ""),
                 thumbnail=item.thumbnail,
                 folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def listacompleta (item):
    logger.info("[SubZero.py]==> listacompleta")
    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)
    blocco = scrapertools.get_match(data, '<table class="titleTable"><tbody>(.*?)</table>')
    patron = '<tr class="titleColumn"><td class=".*?" colspan=".*?">.*?<.*?;">\[.*?\](.*?)</span></td>(.*?<a href="(.*?)">([\w|\-?\d]+).*?</a></td>.*?)</tbody>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    for scrapedtitle, scrapeddata, scrapedurl, scrapedinfo in matches:
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="content",
                 title=color(".torrent ", "darkkhaki") + color(encode(scrapedtitle.strip()), "deepskyblue"),
                 fulltitle=scrapedtitle,
                 url="https:" + scrapedurl.replace("#38;", ""),
                 extra=scrapeddata,
                 thumbnail=item.thumbnail,
                 folder=True), tipo="movie" if ("Movie" or "Special" or "Teaser") in scrapedinfo else "tv"))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def content(item):
    logger.info("[SubZero.py]==> episodi")
    itemlist = []

    data = item.extra
    patron = '<tr class="[titleOdd|titleEven]+">.*?>([\-?\d|\w]+).*?</a>.*?"center">.*?([\-\.a-zA-Z0-9\s]+)</td>.*?<a href="(.*?)".*?<td class="number">(.*?)</td>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapednumber, scrapedinfo, scrapedurl, scrapedsize in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 server="torrent",
                 title=color((item.title.replace(".torrent", color(".torrent ", "darkkhaki") + color(scrapednumber, "gold") + color(" | ", "azure")) + " (Play)"), "azure"),
                 plot="Peso: " + scrapedsize + "\n" + scrapedinfo,
                 url="https:" + scrapedurl.replace("#38;", ""),
                 thumbnail=item.thumbnail,
                 folder=False))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def encode(text):
    return text.decode("latin1").encode("utf8")

def color(text, color):
    return "[COLOR "+color+"]"+text+"[/COLOR]"
# ================================================================================================================