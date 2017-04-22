# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para imovie
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "imovie"
__category__ = "F"
__type__ = "generic"
__title__ = "imovie (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://imovie.name"

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.imovie mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
                     action="peliculas",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Per Categoria[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Per Anno[/COLOR]",
                     action="anno",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Per Paese[/COLOR]",
                     action="paese",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist

def categorias(item):
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    bloque = scrapertools.get_match(data, '<p class="title">Genere</p>(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<li><a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl

        if DEBUG: logger.info("title=[" + scrapedtitle + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                 folder=True))

    return itemlist

def anno(item):
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    bloque = scrapertools.get_match(data, '<p class="title">Anno</p>(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<li><a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl

        if DEBUG: logger.info("title=[" + scrapedtitle + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                 folder=True))

    return itemlist

def paese(item):
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    bloque = scrapertools.get_match(data, '<p class="title">Paese</p>(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<li><a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl

        if DEBUG: logger.info("title=[" + scrapedtitle + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                 folder=True))

    return itemlist

def search(item, texto):
    logger.info("[imovie.py] " + item.url + " search " + texto)
    item.url = host + "/?do=search&subaction=search&story=" + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info("streamondemand.imovie peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<div class="inform">\s*<p class="name_film"><a href="([^"]+)">(.*?)</a></p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("<span>", "")
        scrapedtitle = scrapedtitle.replace("</span>", "")
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<span>[^<]+<\/span> <a href="(.*?)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")
