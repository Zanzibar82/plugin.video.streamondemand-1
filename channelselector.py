# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand 5
# Copyright 2015 tvalacarta@gmail.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of streamondemand 5.
#
# streamondemand 5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# streamondemand 5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with streamondemand 5.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------

import glob
import os
import traceback
import urlparse

from core import channeltools
from core import config
from core import logger
from core.item import Item

DEBUG = config.get_setting("debug")


def getmainlist(preferred_thumb=""):
    logger.info("channelselector.getmainlist")
    itemlist = list()

    # Añade los canales que forman el menú principal
    itemlist.append(Item(title=config.get_localized_string(30130), channel="novedades", action="mainlist",
                         thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb), "thumb_novedades.png"),
                         viewmode="movie"))
    itemlist.append(Item(title=config.get_localized_string(30118), channel="channelselector", action="channeltypes",
                         thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb), "thumb_canales.png"),
                         viewmode="movie"))
    itemlist.append(Item(title=config.get_localized_string(30103), channel="buscador", action="mainlist",
                         thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb), "thumb_buscar.png"),
                         viewmode="list"))
    itemlist.append(Item(title=config.get_localized_string(30102), channel="favoritos", action="mainlist",
                         thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb), "thumb_favoritos.png"),
                         viewmode="movie"))
    if config.get_library_support():
        itemlist.append(Item(title=config.get_localized_string(30131), channel="biblioteca", action="mainlist",
                             thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb), "thumb_biblioteca.png"),
                             viewmode="movie"))
    itemlist.append(Item(title=config.get_localized_string(30101), channel="descargas", action="mainlist",
                         thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb), "thumb_descargas.png"),
                         viewmode="movie"))

    if "xbmceden" in config.get_platform():
        itemlist.append(Item(title=config.get_localized_string(30100), channel="configuracion", action="mainlist",
                             thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb), "thumb_configuracion.png"),
                             folder=False, viewmode="list"))
    else:
        itemlist.append(Item(title=config.get_localized_string(30100), channel="configuracion", action="mainlist",
                             thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb), "thumb_configuracion.png"),
                             viewmode="list"))

    itemlist.append(Item(title=config.get_localized_string(30104), channel="ayuda", action="mainlist",
                         thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb), "thumb_ayuda.png"),
                         viewmode="list"))
    return itemlist


def getchanneltypes(preferred_thumb=""):
    logger.info("channelselector getchanneltypes")

    # Lista de categorias
    valid_types = ["movie", "serie", "anime", "documentary", "vos", "torrent", "latino", "adult"]
    dict_cat_lang = {'movie': config.get_localized_string(30122), 'serie': config.get_localized_string(30123),
                     'anime': config.get_localized_string(30124), 'documentary': config.get_localized_string(30125),
                     'vos': config.get_localized_string(30136), 'adult': config.get_localized_string(30126),
                     'latino': config.get_localized_string(30127)}

    # Lee la lista de canales
    channel_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    logger.info("channelselector.getchanneltypes channel_path="+channel_path)

    channel_files = glob.glob(channel_path)

    channel_language = config.get_setting("channel_language")
    logger.info("channelselector.getchanneltypes channel_language="+channel_language)

    # Construye la lista de tipos
    channel_types = []

    for index, channel in enumerate(channel_files):
        logger.info("channelselector.getchanneltypes channel="+channel)
        if channel.endswith(".xml"):
            try:
                channel_parameters = channeltools.get_channel_parameters(channel[:-4])
                logger.info("channelselector.filterchannels channel_parameters="+repr(channel_parameters))

                # Si es un canal para adultos y el modo adulto está desactivado, se lo salta
                if channel_parameters["adult"] == "true" and config.get_setting("adult_mode") == "false":
                    continue

                # Si el canal está en un idioma filtrado
                if channel_language != "all" and channel_parameters["language"] != channel_language:
                    continue

                categories = channel_parameters["categories"]
                for category in categories:
                    logger.info("channelselector.filterchannels category="+category)
                    if category not in channel_types and category in valid_types:
                        channel_types.append(category)

            except:
                logger.info("Se ha producido un error al leer los datos del canal " + channel + traceback.format_exc())

    logger.info("channelselector.getchanneltypes Encontrados:")
    for channel_type in channel_types:
        logger.info("channelselector.getchanneltypes channel_type="+channel_type)

    # Ahora construye el itemlist ordenadamente
    itemlist = list()

    itemlist.append(Item(title=config.get_localized_string(30121), channel="channelselector", action="listchannels",
                         category="all", thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),
                                                                    "thumb_canales_todos.png"), viewmode="movie"))
    logger.info("channelselector.getchanneltypes Ordenados:")
    for channel_type in valid_types:
        logger.info("channelselector.getchanneltypes channel_type="+channel_type)
        if channel_type in channel_types:
            title = dict_cat_lang.get(channel_type, channel_type)
            itemlist.append(Item(title=title, channel="channelselector", action="listchannels", category=channel_type,
                                 thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),
                                                            "thumb_canales_"+channel_type+".png"), viewmode="movie"))

    return itemlist


def filterchannels(category,preferred_thumb=""):
    logger.info("channelselector.filterchannels")

    channelslist =[]

    # Lee la lista de canales
    channel_path = os.path.join( config.get_runtime_path() , "channels" , '*.xml' )
    logger.info("channelselector.filterchannels channel_path="+channel_path)

    channel_files = glob.glob(channel_path)
    logger.info("channelselector.filterchannels channel_files encontrados "+str(len(channel_files)))

    channel_language = config.get_setting("channel_language")
    logger.info("channelselector.filterchannels channel_language="+channel_language)
    if channel_language=="":
        channel_language = "all"
        logger.info("channelselector.filterchannels channel_language="+channel_language)

    for index, channel in enumerate(channel_files):
        logger.info("channelselector.filterchannels channel="+channel)
        if channel.endswith(".xml"):

            try:
                channel_parameters = channeltools.get_channel_parameters(channel[:-4])
                logger.info("channelselector.filterchannels channel_parameters="+repr(channel_parameters))

                # Si prefiere el bannermenu y el canal lo tiene, cambia ahora de idea
                if preferred_thumb=="bannermenu" and "bannermenu" in channel_parameters:
                    channel_parameters["thumbnail"] = channel_parameters["bannermenu"]

                # Se salta el canal si no está activo
                if not channel_parameters["active"] == "true":
                    continue

                # Se salta el canal para adultos si el modo adultos está desactivado
                if channel_parameters["adult"] == "true" and config.get_setting("adult_mode") != "true": 
                    continue

                # Se salta el canal si está en un idioma filtrado
                if channel_language!="all" and channel_parameters["language"]!=config.get_setting("channel_language"):
                    continue

                # Se salta el canal si está en una categoria filtrado
                if category!="all" and category not in channel_parameters["categories"]:
                    continue

                # Si ha llegado hasta aquí, lo añade
                channelslist.append(Item(title=channel_parameters["title"], channel=channel_parameters["channel"], action="mainlist", thumbnail=channel_parameters["thumbnail"] , fanart=channel_parameters["fanart"], category=", ".join(channel_parameters["categories"])[:-2], language=channel_parameters["language"], viewmode="list" ))
            
            except:
                logger.info("Se ha producido un error al leer los datos del canal " + channel)
                import traceback
                logger.info(traceback.format_exc())
           
    channelslist.sort(key=lambda item: item.title.lower().strip())

    if category=="all":
        if config.get_setting("personalchannel5")=="true":
            channelslist.insert( 0 , Item( title=config.get_setting("personalchannelname5") ,action="mainlist", channel="personal5" ,thumbnail=config.get_setting("personalchannellogo5") , type="generic" ,viewmode="list" ))
        if config.get_setting("personalchannel4")=="true":
            channelslist.insert( 0 , Item( title=config.get_setting("personalchannelname4") ,action="mainlist", channel="personal4" ,thumbnail=config.get_setting("personalchannellogo4") , type="generic" ,viewmode="list" ))
        if config.get_setting("personalchannel3")=="true":
            channelslist.insert( 0 , Item( title=config.get_setting("personalchannelname3") ,action="mainlist", channel="personal3" ,thumbnail=config.get_setting("personalchannellogo3") , type="generic" ,viewmode="list" ))
        if config.get_setting("personalchannel2")=="true":
            channelslist.insert( 0 , Item( title=config.get_setting("personalchannelname2") ,action="mainlist", channel="personal2" ,thumbnail=config.get_setting("personalchannellogo2") , type="generic" ,viewmode="list" ))
        if config.get_setting("personalchannel")=="true":
            channelslist.insert( 0 , Item( title=config.get_setting("personalchannelname")  ,action="mainlist", channel="personal"  ,thumbnail=config.get_setting("personalchannellogo") , type="generic" ,viewmode="list" ))

        channel_parameters = channeltools.get_channel_parameters("tengourl")
        # Si prefiere el bannermenu y el canal lo tiene, cambia ahora de idea
        if preferred_thumb=="bannermenu" and "bannermenu" in channel_parameters:
            channel_parameters["thumbnail"] = channel_parameters["bannermenu"]

        channelslist.insert( 0 , Item( title="[COLOR gray]Inserisci un URL[/COLOR]"  ,action="mainlist", channel="tengourl" , thumbnail=channel_parameters["thumbnail"], type="generic" ,viewmode="movie" ))

    return channelslist

def get_thumbnail_path(preferred_thumb=""):

    WEB_PATH = ""
    
    if preferred_thumb=="":
        thumbnail_type = config.get_setting("thumbnail_type")
        if thumbnail_type=="":
            thumbnail_type="2"

        if thumbnail_type=="0":
            WEB_PATH = "https://raw.githubusercontent.com/Zanzibar82/images/master/posters/"
        elif thumbnail_type=="1":
            WEB_PATH = "https://raw.githubusercontent.com/Zanzibar82/images/master/banners/"
        elif thumbnail_type=="2":
            WEB_PATH = "https://raw.githubusercontent.com/Zanzibar82/images/master/squares/"
    else:
        WEB_PATH = "https://raw.githubusercontent.com/Zanzibar82/images/master/" + preferred_thumb + "/"

    return WEB_PATH
