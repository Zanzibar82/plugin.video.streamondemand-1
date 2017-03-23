# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Connettore per https://vidlox.tv/
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# By MrTruth
# ------------------------------------------------------------

import re
import urllib

from core import logger
from core import scrapertools

# Prendo l'url del video dal sito
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[vidloxtv.py] url=" + page_url)
    video_urls = []

    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0' }

    html = scrapertools.cache_page(page_url, headers=headers)
    match = re.search('sources:\s*\[([^]]+)\]', html, re.DOTALL)
    if match:
        match = re.search('"(https://.*?[^"])"', match.group(1))
        if match:
            video_urls.append(["su vidlox.tv", match.group(1) + "|" + urllib.urlencode(dict(headers))])

    return video_urls


# Encuentra vídeos de este servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    # https://vidlox.tv/wfs2alc5tvhq
    patronvideos = r'(?://|\.)vidlox\.tv/(?:embed-|)([0-9A-Za-z]+)'
    logger.info("[vidloxtv.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for match in matches:
        titulo = "[vidloxtv]"
        url = "https://vidlox.tv/embed-%s" % match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'vidlox'])

            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
