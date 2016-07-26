# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import Queue
import glob
import os
import re
import time
from threading import Thread

from core import channeltools
from core import config
from core import logger
from core.item import Item
from lib.fuzzywuzzy import fuzz
from platformcode import platformtools

logger.info("streamondemand.channels.buscador init")

DEBUG = config.get_setting("debug")

TIMEOUT_TOTAL = 90


def mainlist(item, preferred_thumbnail="squares"):
    logger.info("streamondemand.channels.buscador mainlist")

    itemlist = list()
    itemlist.append(Item(channel=item.channel, action="search", title="Ricerca generica..."))

    itemlist.append(Item(channel=item.channel, action="search", title="Ricerca per categoria...", extra="categorias"))
    # itemlist.append(Item(channel=item.channel, action="opciones", title="Opciones"))

    saved_searches_list = get_saved_searches()

    for saved_search_text in saved_searches_list:
        itemlist.append(Item(channel=item.channel, action="do_search", title=' "' + saved_search_text + '"',
                             extra=saved_search_text))

    return itemlist


def opciones(item):
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="settingCanal", title="Scegli canali inclusi nella ricerca"))
    itemlist.append(Item(channel=item.channel, action="clear_saved_searches", title="Cancella ricerche salvate"))
    itemlist.append(Item(channel=item.channel, action="settings", title="Altre impostazioni"))
    return itemlist


def settings(item):
    return platformtools.show_channel_settings()


def settingCanal(item):
    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    channel_language = config.get_setting("channel_language")

    if channel_language == "":
        channel_language = "all"

    list_controls = []
    for infile in sorted(glob.glob(channels_path)):
        channel_name = os.path.basename(infile)[:-4]
        channel_parameters = channeltools.get_channel_parameters(channel_name)

        # No incluir si es un canal inactivo
        if channel_parameters["active"] != "true":
            continue

        # No incluir si es un canal para adultos, y el modo adulto está desactivado
        if channel_parameters["adult"] == "true" and config.get_setting("adult_mode") == "false":
            continue

        # No incluir si el canal es en un idioma filtrado
        if channel_language != "all" and channel_parameters["language"] != channel_language:
            continue

        # No incluir si en la configuracion del canal no existe "include_in_global_search"
        include_in_global_search = config.get_setting("include_in_global_search", channel_name)
        if include_in_global_search == "":
            continue

        control = {'id': channel_name,
                   'type': "bool",
                   'label': channel_parameters["title"],
                   'default': include_in_global_search,
                   'enabled': True,
                   'visible': True}

        list_controls.append(control)

    return platformtools.show_channel_settings(list_controls=list_controls,
                                               caption="Canales incluidos en la búsqueda global",
                                               callback="save_settings", item=item)


def save_settings(item, dict_values):
    for v in dict_values:
        config.set_setting("include_in_global_search", dict_values[v], v)


def searchbycat(item):
    # Only in xbmc/kodi
    # Abre un cuadro de dialogo con las categorías en las que hacer la búsqueda
    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    channel_language = config.get_setting("channel_language")
    if channel_language == "":
        channel_language = "all"

    categories = ["Películas", "Series", "Anime", "Documentales", "VOS", "Latino"]
    categories_id = ["movie", "serie", "anime", "documentary", "vos", "latino"]
    list_controls = []
    for i, category in enumerate(categories):
        control = {'id': categories_id[i],
                   'type': "bool",
                   'label': category,
                   'default': False,
                   'enabled': True,
                   'visible': True}

        list_controls.append(control)
    control = {'id': "separador",
               'type': "label",
               'label': '',
               'default': "",
               'enabled': True,
               'visible': True}
    list_controls.append(control)
    control = {'id': "torrent",
               'type': "bool",
               'label': 'Incluir en la búsqueda canales Torrent',
               'default': True,
               'enabled': True,
               'visible': True}
    list_controls.append(control)

    return platformtools.show_channel_settings(list_controls=list_controls, caption="Scegliere le categorie",
                                               callback="search_cb", item=item)


def search_cb(item, values=""):
    cat = []
    for c in values:
        if values[c]:
            cat.append(c)

    if not len(cat):
        return None
    else:
        logger.info(item.tostring())
        logger.info(str(cat))
        return do_search(item, cat)


# Al llamar a esta función, el sistema pedirá primero el texto a buscar
# y lo pasará en el parámetro "tecleado"
def search(item, tecleado):
    logger.info("streamondemand.channels.buscador search")

    if tecleado != "":
        save_search(tecleado)

    if item.extra == "categorias":
        item.extra = tecleado
        return searchbycat(item)

    item.extra = tecleado
    return do_search(item, [])


def channel_result(item):
    extra = item.extra.split("{}")[0]
    channel = item.extra.split("{}")[1]
    tecleado = item.extra.split("{}")[2]
    if '###' in tecleado:
        tecleado, title_year = tecleado.split('###')
        title_year = int(title_year)
    else:
        title_year = 0
    exec "from channels import " + channel + " as module"
    item.channel = channel
    item.extra = extra
    itemlist = []
    for item in module.search(item, tecleado):
        title = item.fulltitle

        # If the release year is known, check if it matches the year found in the title
        if title_year > 0:
            year_match = re.search('\(.*(\d{4}).*\)', title)
            if year_match and abs(int(year_match.group(1)) - title_year) > 1:
                continue

        # Clean up a bit the returned title to improve the fuzzy matching
        title = re.sub(r'\(.*\)', '', title)  # Anything within ()
        title = re.sub(r'\[.*\]', '', title)  # Anything within []

        # Check if the found title fuzzy matches the searched one
        if fuzz.token_sort_ratio(tecleado, title) > 85: itemlist.append(item)
    return itemlist


def channel_search(queue, channel_parameters, categories, tecleado):
    try:
        search_results = {}

        exec "from channels import " + channel_parameters["channel"] + " as module"
        mainlist = module.mainlist(Item(channel=channel_parameters["channel"]))
        search_items = [item for item in mainlist if item.action == "search" and (len(categories) == 0 or item.extra in categories)]

        if '###' in tecleado:
            tecleado, title_year = tecleado.split('###')
            title_year = int(title_year)
        else:
            title_year = 0

        for item in search_items:
            result = []
            for res_item in module.search(item.clone(), tecleado):
                title = res_item.fulltitle

                # If the release year is known, check if it matches the year found in the title
                if title_year > 0:
                    year_match = re.search('\(.*(\d{4}).*\)', title)
                    if year_match and abs(int(year_match.group(1)) - title_year) > 1:
                        continue

                # Clean up a bit the returned title to improve the fuzzy matching
                title = re.sub(r'\(.*\)', '', title)  # Anything within ()
                title = re.sub(r'\[.*\]', '', title)  # Anything within []

                # Check if the found title fuzzy matches the searched one
                if fuzz.token_sort_ratio(tecleado, title) > 85: result.append(res_item)

            if len(result):
                if not channel_parameters["title"] in search_results:
                    search_results[channel_parameters["title"]] = []
                search_results[channel_parameters["title"]].append({"item": item, "itemlist": result})

        queue.put(search_results)

    except:
        logger.error("No se puede buscar en: " + channel_parameters["title"])
        import traceback
        logger.error(traceback.format_exc())


# Esta es la función que realmente realiza la búsqueda
def do_search(item, categories=None):
    if categories is None:
        categories = []

    result_mode = config.get_setting("result_mode", "buscador")
    logger.info("streamondemand.channels.buscador do_search")

    tecleado = item.extra

    itemlist = []

    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    logger.info("streamondemand.channels.buscador channels_path=" + channels_path)

    channel_language = config.get_setting("channel_language")
    logger.info("streamondemand.channels.buscador channel_language=" + channel_language)
    if channel_language == "":
        channel_language = "all"
        logger.info("streamondemand.channels.buscador channel_language=" + channel_language)

    progreso = platformtools.dialog_progress_bg("Cercando " + tecleado, "")
    channel_files = glob.glob(channels_path)

    searches = []
    search_results = {}
    queue = Queue.Queue()

    for index, infile in enumerate(channel_files):

        basename = os.path.basename(infile)
        basename_without_extension = basename[:-4]

        channel_parameters = channeltools.get_channel_parameters(basename_without_extension)

        # No busca si es un canal inactivo
        if channel_parameters["active"] != "true":
            continue

        # En caso de busqueda por categorias
        if categories:
            if not any(cat in channel_parameters["categories"] for cat in categories):
                continue

        # No busca si es un canal para adultos, y el modo adulto está desactivado
        if channel_parameters["adult"] == "true" and config.get_setting("adult_mode") == "false":
            continue

        # No busca si el canal es en un idioma filtrado
        if channel_language != "all" and channel_parameters["language"] != channel_language:
            continue

        # No busca si es un canal excluido de la busqueda global
        include_in_global_search = channel_parameters["include_in_global_search"]
        if include_in_global_search == "":
            # Buscar en la configuracion del canal
            include_in_global_search = str(config.get_setting("include_in_global_search", basename_without_extension))
        if include_in_global_search.lower() != "true":
            continue

        t = Thread(target=channel_search, args=[queue, channel_parameters, categories, tecleado])
        t.setDaemon(True)
        t.start()
        searches.append(t)

    start_time = int(time.time())

    number_of_channels = len(searches)
    completed_channels = 0
    while completed_channels < number_of_channels:

        delta_time = int(time.time()) - start_time
        if len(search_results) <= 0:
            timeout = None  # No result so far,lets the thread to continue working until a result is returned
        elif delta_time >= TIMEOUT_TOTAL:
            break  # At least a result matching the searched title has been found, lets stop the search
        else:
            timeout = TIMEOUT_TOTAL - delta_time  # Still time to gather other results

        progreso.update(completed_channels * 100 / number_of_channels)

        try:
            search_results.update(queue.get(timeout=timeout))
            completed_channels += 1
        except:
            # Expired timeout raise an exception
            break

    total = 0

    for channel in sorted(search_results.keys()):
        for search in search_results[channel]:
            total += len(search["itemlist"])
            if result_mode == 0:
                title = channel
                if len(search_results[channel]) > 1:
                    title += " [" + search["item"].title.strip() + "]"
                title += " (" + str(len(search["itemlist"])) + ")"

                title = re.sub("\[COLOR [^\]]+\]", "", title)
                title = re.sub("\[/COLOR]", "", title)

                extra = search["item"].extra + "{}" + search["item"].channel + "{}" + tecleado
                itemlist.append(
                    Item(title=title, channel="buscador", action="channel_result", url=search["item"].url, extra=extra, folder=True))
            else:
                itemlist.extend(search["itemlist"])

    title = "Cercando: '%s' | Localizzato: %d vídeos | Tempo: %2.f secondi" % (tecleado, total, time.time() - start_time)
    itemlist.insert(0, Item(title=title, color='yellow'))

    progreso.close()

    return itemlist


def save_search(text):
    saved_searches_limit = int((10, 20, 30, 40,)[int(config.get_setting("saved_searches_limit", "buscador"))])

    saved_searches_list = list(config.get_setting("saved_searches_list", "buscador"))

    if text in saved_searches_list:
        saved_searches_list.remove(text)

    saved_searches_list.insert(0, text)

    config.set_setting("saved_searches_list", saved_searches_list[:saved_searches_limit], "buscador")


def clear_saved_searches(item):
    config.set_setting("saved_searches_list", list(), "buscador")
    platformtools.dialog_ok("Ricerca", "Ricerche cancellate correttamente")


def get_saved_searches():
    return list(config.get_setting("saved_searches_list", "buscador"))
