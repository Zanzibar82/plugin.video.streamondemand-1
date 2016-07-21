# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para vureel
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------
# TODO: Este no tiene captcha, podría funcionar en free

import re

from core import logger
from core import scrapertools


def test_video_exists( page_url ):
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[vureel.py] get_video_url(page_url='%s')" % page_url)
    
    data = scrapertools.cache_page(page_url)
    location = scrapertools.get_match(data,'file\: "([^"]+)"')
    
    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(location)[-4:] + " [vureel]",location ] )

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    #hhttp://www.vureel.com/video/49204
    patronvideos  = '(vureel.com/video/\d+)'
    logger.info("[vureel.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[vureel]"
        url = "http://www."+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vureel' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
