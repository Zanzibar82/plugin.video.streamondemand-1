# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per http://www.occhiodelwrestling.netsons.org/
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# By MrTruth
# ------------------------------------------------------------

import re

from core import logger
from core import servertools
from core import scrapertools
from core.item import Item
from servers import adfly

__channel__ = "occhiodelwrestling"
__category__ = "F"
__type__ = "generic"
__title__ = "Occhio Del Wrestling"
__language__ = "IT"

host = "http://www.occhiodelwrestling.netsons.org"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host]
]

def isGeneric():
    return True

# ----------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info("[OcchioDelWrestling.py]==> mainlist")
    itemlist = [Item(channel=__channel__,
                     action="categorie",
                     title=color("Lista categorie", "azure"),
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png")
                ]

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def categorie(item):
    logger.info("[OcchioDelWrestling.py]==> categorie")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)

    blocco = scrapertools.get_match(data, '<div class="menu-main-container">(.*?)</div>')

    patron = r'<li.*?menu-item-\d+"><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="loaditems",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def loaditems(item):
    logger.info("[OcchioDelWrestling.py]==> loaditems")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)

    patron = r'<img.*?src="([^"]+)".*?/>\s*<a href="([^"]+)" title="([^"]+)".*?>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedimg, scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedimg,
                 folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def findvideos(item):
    logger.info("[OcchioDelWrestling.py]==> findvideos")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)
    patron = r'<a href="(http://adf.ly/[^"]+)"(?: target="_blank"|)>(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    index = 1
    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="Link %s: %s" % (index, scrapedtitle),
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=item.thumbnail))
        index += 1
    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def play(item):
    logger.info("[OcchioDelWrestling.py]==> play")
    data = adfly.get_long_url(item.url)
    
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__
    
    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def color(text, color):
    return "[COLOR "+color+"]"+text+"[/COLOR]"

# ================================================================================================================

