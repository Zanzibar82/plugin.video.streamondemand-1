# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# streamondemand - XBMC Plugin
# ayuda - Videos de ayuda y tutoriales para streamondemand
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# contribuci?n de jurrabi
# ----------------------------------------------------------------------
from channels import youtube_channel
from core import config
from core import logger
from core.item import Item


def mainlist(item):
    logger.info("streamondemand.channels.ayuda mainlist")
    itemlist = []

    cuantos = 0
    if config.is_xbmc():
        itemlist.append(Item(channel=item.channel, action="force_creation_advancedsettings",
                             title="Crea advancedsettings.xml ottimizzato"))
        cuantos += cuantos
        
    if config.is_xbmc():
        itemlist.append(Item(channel=item.channel, action="updatebiblio",
                             title="Cerca nuovi episodi e aggiorna la biblioteca"))
        cuantos += cuantos

    if cuantos > 0:
        itemlist.append(Item(channel=item.channel, action="tutoriales", title="Consulta i video tutorial"))
    else:
        itemlist.extend(tutoriales(item))

    return itemlist


def tutoriales(item):
    playlists = youtube_channel.playlists(item,"tvalacarta")

    itemlist = []

    for playlist in playlists:
        if playlist.title == "Tutorial di streamondemand":
            itemlist = youtube_channel.videos(playlist)

    return itemlist


def force_creation_advancedsettings(item):

    # Ruta del advancedsettings
    import xbmc,os
    from platformcode import platformtools
    advancedsettings = xbmc.translatePath("special://userdata/advancedsettings.xml")

    # Copia el advancedsettings.xml desde el directorio resources al userdata
    fichero = open(os.path.join(config.get_runtime_path(), "resources", "advancedsettings.xml"))
    texto = fichero.read()
    fichero.close()
    
    fichero = open(advancedsettings, "w")
    fichero.write(texto)
    fichero.close()
                
    platformtools.dialog_ok("plugin", "Si è creato advancedsettings.xml","con le impostazioni ottimizzate per lo streaming")

    return []


def updatebiblio(item):
    logger.info("streamondemand.channels.ayuda updatebiblio")
    import library_service
    library_service.main()

    return []
