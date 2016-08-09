# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector for openload.co
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import base64
import math
import re

from core import logger
from core import scrapertools
from lib import png

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
    # If you want to use the code for openload please at least put the info from were you take it:
    # for example: "Code take from plugin IPTVPlayer: "https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/"
    # It will be very nice if you send also email to me samsamsam@o2.pl and inform were this code will be used

    image_data = scrapertools.find_single_match(data, '''<img[^>]*?id="linkimg"[^>]*?src="([^"]+?)"''')
    image_data = base64.b64decode(image_data.split('base64,')[-1])
    _, _, pixel, _ = png.Reader(bytes=image_data).read()

    image_str = ''
    try:
        for item in pixel:
            for p in item:
                image_str += chr(p)
    except:
        pass

    image_tabs = []
    i = -1
    for idx in range(len(image_str)):
        if image_str[idx] == '\0':
            break
        if 0 == (idx % (12 * 20)):
            image_tabs.append([])
            i += 1
            j = -1
        if 0 == (idx % 20):
            image_tabs[i].append([])
            j += 1
        image_tabs[i][j].append(image_str[idx])

    data = scrapertools.downloadpageWithoutCookies('https://openload.co/assets/js/obfuscator/n.js')
    sign_str = scrapertools.find_single_match(data, '''['"]([^"^']+?)['"]''')

    # split signature data
    sign_tabs = []
    i = -1
    for idx in range(len(sign_str)):
        if sign_str[idx] == '\0':
            break
        if 0 == (idx % (11 * 26)):
            sign_tabs.append([])
            i += 1
            j = -1
        if 0 == (idx % 26):
            sign_tabs[i].append([])
            j += 1
        sign_tabs[i][j].append(sign_str[idx])

    # get link data
    link_data = {}
    for i in [2, 3, 5, 7]:
        link_data[i] = []
        tmp = ord('c')
        for j in range(len(sign_tabs[i])):
            for k in range(len(sign_tabs[i][j])):
                if tmp > 122:
                    tmp = ord('b')
                if sign_tabs[i][j][k] == chr(int(math.floor(tmp))):
                    if len(link_data[i]) > j:
                        continue
                    tmp += 2.5
                    if k < len(image_tabs[i][j]):
                        link_data[i].append(image_tabs[i][j][k])
    res = []
    for idx in link_data:
        res.append(''.join(link_data[idx]).replace(',', ''))

    res = res[3] + '~' + res[1] + '~' + res[2] + '~' + res[0]
    videourl = 'https://openload.co/stream/{0}?mime=true'.format(res)
    return videourl
