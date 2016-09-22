# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector for openload.co
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re
import urllib

from core import config
from core import logger
from core import scrapertools
from lib.jjdecode import JJDecoder

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}


def test_video_exists(page_url):
    logger.info("streamondemand.servers.openload test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.downloadpageWithoutCookies(page_url)

    if 'We are sorry!' in data:
        return False, "[Openload] File cancellato o inesistente"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.openload url=" + page_url)
    video_urls = []

    data = scrapertools.downloadpageWithoutCookies(page_url)
    subtitle = scrapertools.find_single_match(data, '<track kind="captions" src="([^"]+)" srclang="it"')
    # Header para la descarga
    header_down = "|User-Agent=" + headers['User-Agent'] + "|"

    videourl = decode_openLoad(data)

    extension = scrapertools.find_single_match(data, '<meta name="description" content="([^"]+)"')
    extension = "." + extension.rsplit(".", 1)[1]

    if config.get_platform() != "plex":
        video_urls.append([extension + " [Openload] ", videourl + header_down + extension, 0, subtitle])
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


def decode_openLoad(html):
    # fixed by the openload guy ;)  based on work by pitoosie

    jjstring = re.compile('a="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(html)[1]
    shiftint = re.compile(r";\}\((\d+)\)", re.DOTALL | re.IGNORECASE).findall(html)[1]

    def shiftChar(a):
        a = a.group()
        if a <= "Z":
            b = 90
        else:
            b = 122
        c = ord(a) + int(shiftint)
        if b >= c:
            a = c
        else:
            a = c - 26
        return chr(a)

    jjstring = re.sub(r'[a-zA-Z]', shiftChar, jjstring)
    jjstring = urllib.unquote_plus(jjstring)
    jjstring = jjstring.replace('0', 'j')
    jjstring = jjstring.replace('1', '_')
    jjstring = jjstring.replace('2', '__')
    jjstring = jjstring.replace('3', '___')
    jjstring = JJDecoder(jjstring).decode()

    magicnumber = re.compile(r"charCodeAt\(\d+?\)\s*?\+\s*?(\d+?)\)", re.DOTALL | re.IGNORECASE).findall(jjstring)[0]
    hiddenid = re.compile(r'=\s*?\$\("#([^"]+)"', re.DOTALL | re.IGNORECASE).findall(jjstring)[0]

    hiddenurl = scrapertools.unescape(
        re.compile(r'<span id="' + hiddenid + '">([^<]+)</span', re.DOTALL | re.IGNORECASE).findall(html)[0])

    s = []
    for idx, i in enumerate(hiddenurl):
        j = ord(i)
        if 33 <= j <= 126:
            j = 33 + ((j + 14) % 94)
        if idx == len(hiddenurl) - 1:
            j += int(magicnumber)
        s.append(chr(j))
    res = ''.join(s)

    return 'https://openload.co/stream/{0}?mime=true'.format(res)
