# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para lumfile
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import logger


def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[lumfile.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []
    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://lumfile.com/cwdddpi2d/aaa.html
    patronvideos  = '(lumfile.com/[a-z0-9]+/.*?\.html)'
    logger.info("[lumfile.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[lumfile]"
        url = "http://"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'lumfile' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
