# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para streaminto
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("[streamcloud.py] test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(url=page_url)
    if "File was deleted" in data:
        return False, "El archivo no existe<br/>en streaminto o ha sido borrado."
    elif "Video is processing now" in data:
        return False, "El archivo está siendo procesado<br/>Prueba dentro de un rato."
    else:
        return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.streaminto url=" + page_url)

    data = re.sub(r'\n|\t|\s+', '', scrapertools.cache_page(page_url))

    video_urls = []
    # {type:"html5",config:{file:'http://95.211.191.133:8777/3ki7frw76xuzcg3h5f6cbf7a34mbb2zr44g7sdojszegjqx5tdsaxgwr42vq/v.flv','provider':'http'}
    media_url = scrapertools.get_match(data, """{type:"html5",config:{file:'([^']+)','provider':'http'}""")
    video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [streaminto]", media_url])

    # streamer:"rtmp://95.211.191.133:1935/vod?h=3ki7frw76xuzcg3h5f6cbf7a34mbb2zr44g7sdojszegjqx5tdsaxgwr42vq"
    rtmp_url = scrapertools.get_match(data, 'streamer:"([^"]+)"')
    # ({file:"53/7269023927_n.flv?h=3ki7frw76xuzcg3h5f6cbf7a34mbb2zr44g7sdojszegjqx5tdsaxgwr42vq",
    playpath = scrapertools.get_match(data, '\({file:"([^"]+)",')
    swfUrl = "http://streamin.to/player/player.swf"
    media_url = rtmp_url + " playpath=" + playpath + " swfUrl=" + swfUrl
    video_urls.append(["RTMP [streaminto]", media_url])

    for video_url in video_urls:
        logger.info("streamondemand.servers.streaminto %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    encontrados.add("http://streamin.to/embed-theme.html")
    encontrados.add("http://streamin.to/embed-jquery.html")
    encontrados.add("http://streamin.to/embed-s.html")
    encontrados.add("http://streamin.to/embed-images.html")
    encontrados.add("http://streamin.to/embed-faq.html")
    encontrados.add("http://streamin.to/embed-embed.html")
    encontrados.add("http://streamin.to/embed-ri.html")
    encontrados.add("http://streamin.to/embed-d.html")
    encontrados.add("http://streamin.to/embed-css.html")
    encontrados.add("http://streamin.to/embed-js.html")
    encontrados.add("http://streamin.to/embed-player.html")
    encontrados.add("http://streamin.to/embed-cgi.html")
    devuelve = []

    # http://streamin.to/z3nnqbspjyne
    patronvideos = 'streamin.to/([a-z0-9A-Z]+)'
    logger.info("streamondemand.servers.streaminto find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[streaminto]"
        url = "http://streamin.to/embed-" + match + ".html"
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'streaminto'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    # http://streamin.to/embed-z3nnqbspjyne.html
    patronvideos = 'streamin.to/embed-([a-z0-9A-Z]+)'
    logger.info("streamondemand.servers.streaminto find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[streaminto]"
        url = "http://streamin.to/embed-" + match + ".html"
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'streaminto'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
