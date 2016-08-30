# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector for openload.co
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re

from core import logger
from core import scrapertools
from lib import aadecode

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0'}


def test_video_exists(page_url):
    logger.info("stramondemand.servers.openload test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.downloadpageWithoutCookies(page_url)

    if 'We are sorry!' in data:
        return False, "[Openload] La risorsa non esiste o è stata eliminata"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.openload url=" + page_url)
    video_urls = []

    data = scrapertools.downloadpageWithoutCookies(page_url)

    subtitle = scrapertools.find_single_match(data, '<track kind="captions" src="([^"]+)" srclang="it"')
    # Header para la descarga
    header_down = "|User-Agent=" + headers['User-Agent'] + "|"

    extension = scrapertools.find_single_match(data, '<meta name="description" content="([^"]+)"')
    extension = "." + extension.rsplit(".", 1)[1]

    videourl = decode_openload(data)

    video_urls.append([extension + " [Openload] ", videourl + header_down + extension, 0, subtitle])

    for video_url in video_urls:
        logger.info("streamondemand.servers.openload %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = '//(?:www.)?openload.../(?:embed|f)/([0-9a-zA-Z-_]+)'
    logger.info("stramondemand.servers.openload find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for media_id in matches:
        titulo = "[Openload]"
        url = 'https://openload.co/embed/%s/' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'openload'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve


def decode_openload(data):
    hiddenurl = scrapertools.unescape(re.search('hiddenurl">(.+?)</span>', data, re.IGNORECASE).group(1))

    aastring = re.compile("<script[^>]+>(ﾟωﾟﾉ[^\n]+)\n", re.DOTALL | re.IGNORECASE).findall(data)[0]
    aastring = aadecode.decode(aastring)
    magicnumber = re.compile(r"charCodeAt\(\d+?\)\s*?\+\s*?(\d+?)\)", re.DOTALL | re.IGNORECASE).findall(aastring)[0]

    s = []
    for idx, i in enumerate(hiddenurl):
        j = ord(i)
        if 33 <= j <= 126:
            j = 33 + ((j + 14) % 94)
        if idx == len(hiddenurl) - 1:
            j += int(magicnumber)
        s.append(chr(j))
    res = ''.join(s)

    videourl = 'https://openload.co/stream/{0}?mime=true'.format(res)
    return videourl
