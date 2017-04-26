# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per http://bam.forumcommunity.net/
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# By MrTruth
# ------------------------------------------------------------

import re

from core import logger
from core import servertools
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "bleachanimemanga"
__category__ = "A"
__type__ = "generic"
__title__ = "BleachAnimeManga"
__language__ = "IT"

host = "http://bam.forumcommunity.net"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host]
]

def isGeneric():
    return True

# ----------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info("[BleachAnimeManga.py]==> mainlist")
    itemlist = [Item(channel=__channel__,
                     action="perlettere",
                     title=color("Lista Anime", "azure"),
                     url="%s/?f=8462733" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png")]

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def perlettere(item):
    logger.info("[BleachAnimeManga.py]==> perlettere")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)

    patron = r'<option value="(\d+)">-\s*&nbsp;(\.?[A-Z\-1-9]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedid, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_anime",
                 title=scrapedtitle,
                 url="%s/?f=%s&st=0" % (host, scrapedid),
                 folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def lista_anime(item):
    logger.info("[BleachAnimeManga.py]==> lista_anime")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)

    patron = '<a HREF="([^"]+)".*?>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.strip())
        if "Lista Episodi" in scrapedtitle:
            scrapedtitle = scrapedtitle.replace("Lista Episodi", "")
            lang = scrapertools.find_single_match(scrapedtitle, r'(?:SUB ITA|ITA)')
            scrapedtitle = scrapedtitle.replace(lang, "").strip()
            covertitle = re.sub(r'[^a-zA-Z0-9]+', '', scrapedtitle)
            thumbnail = "http://www.animeclick.it/images/serie/%s/%s-cover.jpg" % (covertitle, covertitle)
            itemlist.append(infoSod(
                Item(channel=__channel__,
                    action="episodi",
                    title="%s (%s)" % (scrapedtitle, color(lang, "red")),
                    fulltitle=scrapedtitle,
                    url=scrapedurl,
                    thumbnail=thumbnail,
                    show=scrapedtitle,
                    folder=True), tipo="tv"))

    # Gestione pagine ------------------------------------------------------------------------------
    patron = r'<a href="javascript:page_jump\(\'[^\']+\',(\d+),30\)" rel="nofollow">'
    pgNumbers = scrapertools.find_single_match(data, patron)
    if pgNumbers:
        pgNumbers = int(pgNumbers)
        lastPGNumber = 30*(pgNumbers-1)
        currentpagenumber = int(item.url.split('=')[-1])
        if pgNumbers > 0 and currentpagenumber < lastPGNumber:
            url = "%s&st=%s" % (item.url, currentpagenumber+30)
            itemlist.append(
                Item(channel=__channel__,
                    action="HomePage",
                    title=color("Torna Home", "yellow"),
                    folder=True))
            itemlist.append(
                Item(channel=__channel__,
                    action="lista_anime",
                    title=color("Successivo >>", "orange"),
                    url=url,
                    thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                    folder=True))
    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def episodi(item):
    logger.info("[BleachAnimeManga.py]==> episodi")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)

    blocco = scrapertools.find_single_match(data, r'</div>\s*<td class="right Item" width="\d+%">(.*?)</table>')

    patron = r'(<a href="[^"]+" target="_blank">)((?:Episodio|Streaming)\s*[0-9\.]+).*?</a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    index = 0
    for scrapedhtml, scrapedtitle in matches:
        if ("Special" in scrapedtitle) or ("OAV" in scrapedtitle): continue # Salto gli OAV e i movies
        if len(itemlist) > 0:
            if "Streaming" in scrapedtitle: # Se c'è un link alternativo dello stesso episodio unisco la sua parte HTML con quella dell'item precedente e continuo senza aggiungere l'item
                itemlist[index-1].url = itemlist[index-1].url + scrapedhtml
                continue
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 contentType="episode",
                 url=scrapedhtml,
                 thumbnail=item.thumbnail,
                 folder=True))
        index += 1
    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def findvideos(item):
    logger.info("[BleachAnimeManga.py]==> findvideos")

    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, color(videoitem.title, "orange")])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = videoitem.thumbnail
        videoitem.channel = __channel__
    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def color(text, color):
    return "[COLOR "+color+"]"+text+"[/COLOR]"

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

# ================================================================================================================
