# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per http://www.guardaserie.online/
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# By MrTruth
# ------------------------------------------------------------

import re

from core import logger
from core import config
from core import servertools
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "guardaserieonline"
__category__ = "S, A"
__type__ = "generic"
__title__ = "GuardaSerie.online"
__language__ = "IT"

host = "http://www.guardaserie.online"

DEBUG = config.get_setting("debug")

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host]
]

def isGeneric():
    return True

# ----------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info("[GuardaSerieOnline.py]==> mainlist")
    itemlist = [Item(channel=__channel__,
                     action="nuoveserie",
                     title=color("Nuove serie TV Aggiunte", "orange"),
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="serietvaggiornate",
                     title=color("Serie TV Aggiornate", "azure"),
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="lista_serie",
                     title=color("Anime", "azure"),
                     url="%s/category/animazione/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="categorie",
                     title=color("Categorie", "azure"),
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="search",
                     title=color("Cerca ...", "yellow"),
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def search(item, texto):
    logger.info("[GuardaSerieOnline.py]==> search")
    item.url = host + "/?s=" + texto
    try:
        return lista_serie(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def nuoveserie(item):
    logger.info("[GuardaSerieOnline.py]==> nuoveserie")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)
    blocco = scrapertools.get_match(data, '<div\s*class="container container-title-serie-new container-scheda" meta-slug="new">(.*?)</div></div><div')

    patron = '<a\s*href="([^"]+)".*?>\s*<img\s*.*?src="([^"]+)" />[^>]+>[^>]+>[^>]+>[^>]+>'
    patron += '[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>([^<]+)</p>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodi",
                 contentType="tv",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 extra="tv",
                 show=scrapedtitle,
                 thumbnail=scrapedthumbnail,
                 folder=True), tipo="tv"))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def serietvaggiornate(item):
    logger.info("[GuardaSerieOnline.py]==> serietvaggiornate")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)
    blocco = scrapertools.get_match(data, '<div\s*class="container container-title-serie-lastep  container-scheda" meta-slug="lastep">(.*?)</div></div><div')
    patron = '<a\s*.*?href="([^"]+)".*?> <img\s*.*?src="([^"]+)"[^>]+>[^>]+>[^>]+>[^>]+>'
    patron += '[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>([^<]+)</p>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if DEBUG: logger.info("Scrapedurl: " + scrapedurl + " | ScrapedThumbnail: " + scrapedthumbnail + " | ScrapedTitle: " + scrapedtitle)
        if "toroadvertisingmedia" in scrapedurl:
            scrapedurl = host + "/" + scrapedtitle.replace(" ", "-")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodi",
                 contentType="tv",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 extra="tv",
                 show=scrapedtitle,
                 thumbnail=scrapedthumbnail,
                 folder=True), tipo="tv"))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def categorie(item):
    logger.info("[GuardaSerieOnline.py]==> categorie")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)
    blocco = scrapertools.get_match(data, '<div\s*class="bottom-header-category hidden-xs"><div\s*class="row">(.*?)</div></div></div><div')
    patron = '<div\s*class="col-sm-3">\s+<a\s*href="([^"]+)".*?>([^<]+)</a></div>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_serie",
                 title=scrapedtitle,
                 contentType="tv",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 extra="tv",
                 folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def lista_serie(item):
    logger.info("[GuardaSerieOnline.py]==> lista_serie")
    itemlist = []
    
    data = scrapertools.anti_cloudflare(item.url, headers=headers)

    patron = '<a\s*href="([^"]+)".*?>\s*<img\s*.*?src="([^"]+)" />[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>([^<]+)</p></div>'
    blocco = scrapertools.get_match(data, '<div\s*class="col-xs-\d+ col-sm-\d+-\d+">(.*?)<div\s*class="container-fluid whitebg" style="">')
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    
    for scrapedurl, scrapedimg, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodi",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedimg,
                 extra=item.extra,
                 show=scrapedtitle,
                 folder=True), tipo="tv"))
    
    patron = '<a\s*class="nextpostslink" rel="next" href="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title=color("Torna Home", "yellow"),
                 folder=True))
        itemlist.append(
            Item(channel=__channel__,
                action="lista_serie",
                title=color("Successivo >>", "orange"),
                url=scrapedurl,
                thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                folder=True))
    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def episodi(item):
    logger.info("[GuardaSerieOnline.py]==> episodi")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)

    patron = '<img\s*.*?[meta-src|data-original]*="([^"]+)"\s*/>[^>]+>([^<]+)<[^>]+>[^>]+>[^>]+>'
    patron += '[^>]+>[^>]+>([^<]+)*<[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>'
    patron += '[^>]+>[^>]+>[^>]+>\s*<span\s*.*?(meta-embed="[^"]+">)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedthumbnail, scrapedep, scrapedeptitle, scrapedextra in matches:
        scrapedeptitle = scrapertools.decodeHtmlentities(scrapedeptitle).strip()
        scrapedep = scrapertools.decodeHtmlentities(scrapedep).strip()
        scrapedtitle = "%s - %s" % (scrapedep, scrapedeptitle) if scrapedeptitle != "" else scrapedep
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 contentType="episode",
                 extra=scrapedextra,
                 thumbnail=scrapedthumbnail,
                 folder=True))
    
    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodi",
                 show=item.show))
        itemlist.append(
            Item(channel=__channel__,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodi",
                 show=item.show))
    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def findvideos(item):
    logger.info("[GuardaSerieOnline.py]==> findvideos")
    itemlist = servertools.find_video_items(data=item.extra)

    # Non sono riuscito a trovare un modo migliore di questo, se qualcuno ha un metodo migliore di questo
    # per estrarre il video lo sistemi per favore.
    if len(itemlist) > 1:
        itemlist.remove(itemlist[1])
    itemlist[0].title = "".join([item.title, color(itemlist[0].title, "orange")])
    itemlist[0].fulltitle = item.fulltitle
    itemlist[0].show = item.show
    itemlist[0].thumbnail = item.thumbnail
    itemlist[0].channel = __channel__
    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def color(text, color):
    return "[COLOR "+color+"]"+text+"[/COLOR]"

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

# ================================================================================================================
