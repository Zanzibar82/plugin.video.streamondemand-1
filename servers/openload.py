# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector for openload.co
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'}


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    header = {}
    if "|" in page_url:
        page_url, referer = page_url.split("|", 1)
        header = {'Referer': referer}
    data = httptools.downloadpage(page_url, headers=header, cookies=False).data
    if 'We’re Sorry!' in data:
        data = httptools.downloadpage(page_url.replace("/embed/", "/f/"), headers=header, cookies=False).data
        if 'We’re Sorry!' in data:
            return False, "[Openload] Il file non esiste o è stato cancellato"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []

    header = {}
    if "|" in page_url:
        page_url, referer = page_url.split("|", 1)
        header = {'Referer': referer}
    data = httptools.downloadpage(page_url, headers=header, cookies=False).data
    subtitle = scrapertools.find_single_match(data, '<track kind="captions" src="([^"]+)" srclang="es"')
    # Header para la descarga
    header_down = "|User-Agent=" + headers['User-Agent']

    try:
        from lib.aadecode import decode as aadecode
        if "videocontainer" not in data:
            url = page_url.replace("/embed/", "/f/")
            data = httptools.downloadpage(url, cookies=False).data

        text_encode = scrapertools.find_multiple_matches(data, '(ﾟωﾟ.*?\(\'\_\'\));')
        text_decode = ""
        for t in text_encode:
            text_decode += aadecode(t)

        var_r = scrapertools.find_single_match(text_decode, "window.r\s*=\s*['\"]([^'\"]+)['\"]")
        var_encodes = scrapertools.find_multiple_matches(data, 'id="%s[^"]*">([^<]+)<' % var_r)

        videourl = ""
        for encode in var_encodes:
            text_decode = []
            try:
                idx1 = max(2, ord(encode[0]) - 55)
                idx2 = min(idx1, len(encode) - 38)
                idx3 = encode[idx2:idx2 + 36]
                decode1 = []
                for i in range(0, len(idx3), 3):
                    decode1.append(int(idx3[i:i + 3], 8))
                v = encode[0:idx2] + encode[idx2 + 36:]
                i = 0
                h = 0
                while h < len(v):
                    B = v[h:h + 2]
                    C = v[h:h + 3]
                    f = int(B, 16)
                    h += 2

                    if (i % 3) == 0:
                        f = int(C, 8)
                        h += 1
                    elif i % 2 == 0 and i != 0 and ord(v[i - 1]) < 60:
                        f = int(C, 10)
                        h += 1

                    A = decode1[i % 7]
                    f = f ^ 213;
                    f = f ^ A;
                    text_decode.append(chr(f))
                    i += 1

                text_decode = "".join(text_decode)
            except:
                continue

            videourl = "https://openload.co/stream/%s?mime=true" % text_decode
            logger.info("Video URL: " + videourl)
            resp_headers = httptools.downloadpage(videourl, follow_redirects=False, only_headers=True)
            videourl = resp_headers.headers["location"].replace("https", "http").replace("?mime=true", "")
            extension = resp_headers.headers["content-type"]
            break

        # Falla el método, se utiliza la api aunque en horas punta no funciona
        if not videourl:
            videourl, extension = get_link_api(page_url)
    except:
        import traceback
        logger.info(traceback.format_exc())
        # Falla el método, se utiliza la api aunque en horas punta no funciona
        videourl, extension = get_link_api(page_url)

    extension = extension.replace("video/", ".").replace("application/x-", ".")
    if not extension:
        try:
            extension = scrapertools.find_single_match(data, '<meta name="description" content="([^"]+)"')
            extension = "." + extension.rsplit(".", 1)[1]
        except:
            pass

    if config.get_platform() != "plex":
        video_urls.append([extension + " [Openload] ", videourl + header_down, 0, subtitle])
    else:
        video_urls.append([extension + " [Openload] ", videourl, 0, subtitle])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    referer = ""
    if "|Referer=" in text:
        referer = "|" + text.split("|Referer=", 1)[1]
    patronvideos = '(?:openload|oload).../(?:embed|f)/([0-9a-zA-Z-_]+)'
    logger.info("#" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(text)
    for media_id in matches:
        titulo = "[Openload]"
        url = 'https://openload.co/embed/%s/%s' % (media_id, referer)
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'openload'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve


def get_link_api(page_url):
    from core import jsontools
    file_id = scrapertools.find_single_match(page_url, '(?:embed|f)/([0-9a-zA-Z-_]+)')
    login = "97b2326d7db81f0f"
    key = "AQFO3QJQ"
    data = httptools.downloadpage(
        "https://api.openload.co/1/file/dlticket?file=%s&login=%s&key=%s" % (file_id, login, key)).data
    data = jsontools.load_json(data)

    if data["status"] == 200:
        ticket = data["result"]["ticket"]
        data = httptools.downloadpage("https://api.openload.co/1/file/dl?file=%s&ticket=%s" % (file_id, ticket)).data
        data = jsontools.load_json(data)
        extension = data["result"]["content_type"]
        videourl = data['result']['url']
        videourl = videourl.replace("https", "http")
        return videourl, extension

    return "", ""
