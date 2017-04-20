# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Script per la ricerca di un canale in base al testo inserito
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# by MrTruth
#------------------------------------------------------------

import os, glob
from core import channeltools
from core import config
from core import logger
from core.item import Item

DEBUG = config.get_setting("debug")

def search(item, texto):
    logger.info("[searchchannel.py] search texto="+texto)
    itemlist = []
    
    directory = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    files = glob.glob(directory)
    for file in files:
        file = file.replace(".xml", "")
        channel_parameters = channeltools.get_channel_parameters(file)
        if channel_parameters['active'] == "true":
            file = os.path.basename(file)
            if DEBUG: logger.info("File .xml trovato: " + file)
            texto = texto.lower().replace("+", "")
            name = channel_parameters['title'].lower().replace(" ", "")
            if texto in name:
                itemlist.append(Item(title=channel_parameters['title'], action="mainlist", channel=file, thumbnail=channel_parameters["thumbnail"], type="generic", viewmode="movie"))

    return itemlist
