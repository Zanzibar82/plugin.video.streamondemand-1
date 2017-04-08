# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para thevideo.me
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------

import re
import urllib

from core import logger
from core import scrapertools

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0'],
           ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'],
           ['Accept-Language', 'en-US,en;q=0.5'],
           ['Accept-Encoding', 'gzip, deflate'],
           ['Cache-Control', 'max-age=0']]


def test_video_exists(page_url):
    logger.info("streamondemand.servers.thevideome test_video_exists(page_url='%s')" % page_url)
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.thevideome url=" + page_url)

    if "embed" not in page_url:
        page_url = page_url.replace("http://thevideo.me/", "http://thevideo.me/embed-") + ".html"

    headers.append(['Referer', page_url])

    data = scrapertools.cache_page(page_url, headers=headers)

    mpri_Key = scrapertools.find_single_match(data, "var better_luck_next_time='([^']+)'")

    data_vt = scrapertools.downloadpage("https://thevideo.me/vsign/player/%s" % mpri_Key, headers=headers)

    vt = max(scrapertools.find_single_match(data_vt, ",'([^']+?)'\.split\('\|'\),").split('|'), key=len)

    media_urls = scrapertools.find_multiple_matches(data, '\{"file"\s*\:\s*"([^"]+)"\s*,\s*"label"\s*\:\s*"([^"]+)"')

    video_urls = []
    _headers = urllib.urlencode(dict(headers))

    for media_url, label in media_urls:
        video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " (" + label + ") [thevideo.me]", media_url + "?direct=false&ua=1&vt=%s" % vt + '|' + _headers])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    patronvideos = '(?://|\.)thevideo\.me/(?:embed-|download/)?([0-9a-zA-Z]+)'
    logger.info("streamondemand.servers.thevideome find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[thevideo.me]"
        url = "http://thevideo.me/embed-%s.html" % match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'thevideome'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)
    return devuelve
