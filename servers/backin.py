# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para backin.net
# by DrZ3r0
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------

import re
import urllib

import xbmc

from core import logger
from core import scrapertools


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[backin.py] url=" + page_url)

    video_urls = []

    headers = [["User-Agent", "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0"],
               ["Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"],
               ["Accept-Language", "en-US,en;q=0.5"],
               ["Accept-Encoding", "gzip, deflate"]]

    # First access
    scrapertools.cache_page("http://backin.net/s/%s" % page_url, headers=headers)

    xbmc.sleep(10000)
    headers.append(["Referer", "http://backin.net/s/%s" % page_url])

    data = scrapertools.cache_page("http://backin.net/stream-%s-500x400.html" % page_url, headers=headers)

    data_pack = scrapertools.find_single_match(data, "(eval.function.p,a,c,k,e,.*?)\s*</script>")
    if data_pack:
        from lib import jsunpack
        data = jsunpack.unpack(data_pack)

    # URL
    url = scrapertools.find_single_match(data, 'file\s*:\s*"([^"]+)",')

    # URL del vídeo
    video_urls.append([".mp4" + " [backin]", url + '|' + urllib.urlencode(dict(headers))])

    for video_url in video_urls:
        logger.info("[backin.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos de este servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    # http://backin.net/iwbe6genso37
    patronvideos = '(?:backin).net/([A-Z0-9a-z]+)'
    logger.info("[backin.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for match in matches:
        titulo = "[backin]"
        if match not in encontrados:
            logger.info("  url=" + match)
            devuelve.append([titulo, match, 'backin'])
            encontrados.add(match)
        else:
            logger.info("  url duplicada=" + match)

    return devuelve
