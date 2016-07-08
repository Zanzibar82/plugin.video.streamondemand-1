# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para corsaronero
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
#------------------------------------------------------------
import re
import urllib
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "corsaronero"
__category__ = "F"
__type__ = "generic"
__title__ = "Corsaro Nero (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://torcache.net/torrent/"
site = "http://ilcorsaronero.info"

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.corsaronero mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Novità-Film .torrent stream[/COLOR]", action="peliculas", url="http://ilcorsaronero.info/cat/1", thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"))
    
    return itemlist

def search(item,texto):
    logger.info("[corsaronero.py] "+item.url+" search "+texto)
    item.url = "http://ilcorsaronero.info/argh.php?search="+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("streamondemand.corsaronero peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, timeout=10)

    # Extrae las entradas (carpetas)
    patron = '<A class="tab" HREF="(.*?)"[^>]+>(.*?)</A>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.replace("."," "))
        proctitle1 = scrapertools.decodeHtmlentities(scrapedtitle.replace("19","("))
        proctitle = scrapertools.decodeHtmlentities(proctitle1.replace("20","("))
        title = proctitle.split("(")[0]
        url = site + scrapedurl
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append(infoSod(Item(channel=__channel__,
                                action="findvideos",
                                title="[COLOR darkkhaki].torrent [/COLOR][COLOR azure]" + title + "[/COLOR]",
                                fulltitle=title,
                                url=url,
                                thumbnail=scrapedthumbnail),
                                tipo="movie"))
    # Extrae el paginador
    patronvideos  = '<a href="([^>"]+)">pagine successive'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Successivo>>[/COLOR]" , url=scrapedurl , thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", folder=True) )

    return itemlist

def play(item):
    logger.info("[corsaronero.py] play")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron = '<a class="forbtn magnet" target="_blank" href="(magnet[^"]+)" title="Magnet" ></a>'
    patron = urllib.unquote(patron).decode('utf8')
    link = scrapertools.find_single_match(data, patron)
    link = urlparse.urljoin(item.url,link)

    itemlist.append( Item(channel=__channel__, action=play, server="torrent", title=item.title , url=link , thumbnail=item.thumbnail , plot=item.plot , folder=False) )

    return itemlist

