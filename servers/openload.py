# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for openload.co
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import re

from core import config
from core import logger
from core import scrapertools

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}


def test_video_exists(page_url):
    logger.info("streamondemand.servers.openload test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.downloadpageWithoutCookies(page_url)

    if 'We are sorry!' in data:
        return False, "[Openload] Il file non esiste o è stato rimosso"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.openload url=" + page_url)
    video_urls = []

    data = scrapertools.downloadpageWithoutCookies(page_url)
    subtitle = scrapertools.find_single_match(data, '<track kind="captions" src="([^"]+)" srclang="it"')
    # Header para la descarga
    header_down = "|User-Agent=" + headers['User-Agent']

    from lib.aadecode import decode as aadecode
    text_encode = scrapertools.find_multiple_matches(data, '(ﾟωﾟ.*?\(\'\_\'\));')
    text_decode = ""
    for t in text_encode:
        text_decode += aadecode(t)

    varfnc = scrapertools.find_single_match(text_decode, 'charCodeAt\(0\)\s*\+\s*(\w+)\(\)')
    number = scrapertools.find_single_match(text_decode, 'function\s*' + varfnc + '\(\)\s*{\s*return\s*([^;]+);\s*}')
    number = eval(number)
    varj = scrapertools.find_single_match(text_decode, 'var magic\s*=\s*(\w+)\.slice')
    varhidden = scrapertools.find_single_match(text_decode, 'var\s*' + varj + '\s*=\s*\$\("[#]*([^"]+)"\).text')
    valuehidden = scrapertools.find_single_match(data, 'id="' + varhidden + '">(.*?)<')
    magic = ord(valuehidden[-1])
    valuehidden = valuehidden.split(chr(magic - 1))
    valuehidden = "\t".join(valuehidden)
    valuehidden = valuehidden.split(valuehidden[-1])
    valuehidden = chr(magic - 1).join(valuehidden)
    valuehidden = valuehidden.split("\t")
    valuehidden = chr(magic).join(valuehidden)

    videourl = decode_hidden(valuehidden, number)

    extension = scrapertools.find_single_match(data, '<meta name="description" content="([^"]+)"')
    extension = "." + extension.rsplit(".", 1)[1]
    if config.get_platform() != "plex":
        video_urls.append([extension + " [Openload] ", videourl + header_down, 0, subtitle])
    else:
        video_urls.append([extension + " [Openload] ", videourl, 0, subtitle])

    for video_url in video_urls:
        logger.info("streamondemand.servers.openload %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = '(?:openload|oload).../(?:embed|f)/([0-9a-zA-Z-_]+)'
    logger.info("streamondemand.servers.openload find_videos #" + patronvideos + "#")

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


def decode_hidden(text, number):
    text = text.replace("&gt9", ">").replace("&quot9", '"').replace("&lt9", '<') \
        .replace("&amp9", '&').replace("&gt;", ">").replace("&lt;", "<")
    text = scrapertools.decodeHtmlentities(text)
    s = []
    for char in text:
        j = ord(char)
        s.append(chr(33 + ((j + 14) % 94)))

    temp = "".join(s)
    text_decode = temp[0:-1] + chr(ord(temp[-1]) + number)
    videourl = "https://openload.co/stream/{0}?mime=true".format(text_decode)

    return videourl
