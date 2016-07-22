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
# Library Tools
# ------------------------------------------------------------

import errno
import math
import os
import re
import string
import sys
import urllib
from socket import gaierror

import xbmc
from core import config
from core import jsontools
from core import logger
from core import scrapertools
from core.item import Item
from platformcode import platformtools

try:
    from sambatools import libsmb as samba
except ImportError:
    librerias = xbmc.translatePath(os.path.join(config.get_runtime_path(), 'lib'))
    sys.path.append(librerias)
    from lib.sambatools import libsmb as samba

import urllib2

modo_cliente = int(config.get_setting("library_mode"))
# Host name where XBMC is running, leave as localhost if on this PC
# Make sure "Allow control of XBMC via HTTP" is set to ON in Settings ->
# Services -> Webserver
xbmc_host = config.get_setting("xbmc_host")
# Configured in Settings -> Services -> Webserver -> Port
xbmc_port = int(config.get_setting("xbmc_port"))
# Base URL of the json RPC calls. For GET calls we append a "request" URI
# parameter. For POSTs, we add the payload as JSON the the HTTP request body
xbmc_json_rpc_url = "http://{host}:{port}/jsonrpc".format(host=xbmc_host, port=xbmc_port)

DEBUG = config.get_setting("debug")


def path_exists(path):
    """
    comprueba si la ruta existe, samba necesita la raíz para conectar y la carpeta
    @type path: str
    @param path: la ruta del fichero
    @rtype:   str
    @return:  devuelve si existe la ruta.
    """
    if not samba.usingsamba(path):
        return os.path.exists(path)
    else:
        try:
            path_samba, folder_samba = path.rsplit('/', 1)
            return samba.folder_exists(folder_samba, path_samba)
        except gaierror:
            logger.info("streamondemand.platformcode.library path_exists: No es posible conectar con la ruta")
            platformtools.dialog_notification("No es posible conectar con la ruta", path)
            return True


def make_dir(path):
    """
    crea un directorio, samba necesita la raíz para conectar y la carpeta
    @type path: str
    @param path: la ruta del fichero
    """
    logger.info("streamondemand.platformcode.library make_dir")
    if not samba.usingsamba(path):
        try:
            os.mkdir(path)
        except OSError:
            logger.info("streamondemand.platformcode.library make_dir: Error al crear la ruta")
            platformtools.dialog_notification("Error al crear la ruta", path)
    else:
        try:
            path_samba, folder_samba = path.rsplit('/', 1)
            samba.create_directory(folder_samba, path_samba)
        except gaierror:
            logger.info("streamondemand.platformcode.library make_dir: Error al crear la ruta")
            platformtools.dialog_notification("Error al crear la ruta", path)


def join_path(path, *name):
    """
    une la ruta, el name puede ser carpeta o archivo
    @type path: str
    @param path: la ruta del fichero
    @type name: str
    @param name: nombre del fichero
    @rtype:   str
    @return:  devuelve si existe la ruta.
    """
    if not samba.usingsamba(path):
        path = xbmc.translatePath(os.path.join(path, *name))
    else:
        path = path + "/" + name

    return path


LIBRARY_PATH = config.get_library_path()
if not samba.usingsamba(LIBRARY_PATH):
    if not path_exists(LIBRARY_PATH):
        logger.info("streamondemand.platformcode.library Library path doesn't exist:" + LIBRARY_PATH)
        config.verify_directories_created()

# TODO permitir cambiar las rutas y nombres en settings para 'cine' y 'series'
FOLDER_MOVIES = "CINE"  # config.get_localized_string(30072)
MOVIES_PATH = join_path(LIBRARY_PATH, FOLDER_MOVIES)
if not path_exists(MOVIES_PATH):
    logger.info("streamondemand.platformcode.library Movies path doesn't exist:" + MOVIES_PATH)
    make_dir(MOVIES_PATH)

FOLDER_TVSHOWS = "SERIES"  # config.get_localized_string(30073)
TVSHOWS_PATH = join_path(LIBRARY_PATH, FOLDER_TVSHOWS)
if not path_exists(TVSHOWS_PATH):
    logger.info("streamondemand.platformcode.library Tvshows path doesn't exist:" + TVSHOWS_PATH)
    make_dir(TVSHOWS_PATH)

TVSHOW_FILE = "series.json"
TVSHOW_FILE_OLD = "series.xml"

# Versions compatible with JSONRPC v6
LIST_PLATFORM_COMPATIBLE = ["xbmc-frodo", "xbmc-gotham", "kodi-helix", "kodi-isengard", "kodi-jarvis"]


def is_compatible():
    """
    comprueba si la plataforma es xbmc/Kodi, la version es compatible y si está configurada la libreria en Kodi.
    @rtype:   bool
    @return:  si es compatible.

    """
    logger.info("streamondemand.platformcode.library is_compatible")
    if config.get_platform() in LIST_PLATFORM_COMPATIBLE and library_in_kodi():
        return True
    else:
        return False


def library_in_kodi():
    """
    comprueba si la libreria de streamondemand está configurada en xbmc/Kodi
    @rtype:   bool
    @return:  si está configurada la libreria en xbmc/Kodi.
    """
    logger.info("streamondemand.platformcode.library library_in_kodi")
    # TODO arreglar
    return True

    path = xbmc.translatePath(os.path.join("special://profile/", "sources.xml"))
    data = read_file(path)

    if config.get_library_path() in data:
        return True
    else:
        return False

def elimina_tildes(s):
    """
    elimina las tildes de la cadena
    @type s: str
    @param s: cadena.
    @rtype:   str
    @return:  cadena sin tildes.
    """
    logger.info("streamondemand.platformcode.library elimina_tildes")
    # import unicodedata
    # if not isinstance(s, unicode):
    #     s = s.decode("UTF-8")
    # return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    s = s.replace("Á", "a")
    s = s.replace("É", "e")
    s = s.replace("Í", "i")
    s = s.replace("Ó", "o")
    s = s.replace("Ú", "u")
    s = s.replace("á", "a")
    s = s.replace("é", "e")
    s = s.replace("í", "i")
    s = s.replace("ó", "o")
    s = s.replace("ú", "u")
    s = s.replace("À", "a")
    s = s.replace("È", "e")
    s = s.replace("Ì", "i")
    s = s.replace("Ò", "o")
    s = s.replace("Ù", "u")
    s = s.replace("à", "a")
    s = s.replace("è", "e")
    s = s.replace("ì", "i")
    s = s.replace("ò", "o")
    s = s.replace("ù", "u")
    s = s.replace("ç", "c")
    s = s.replace("Ç", "C")
    s = s.replace("Ñ", "n")
    s = s.replace("ñ", "n")

    return s

def title_to_filename(title):
    """
    devuelve un titulo con caracteres válidos para crear un fichero
    @type title: str
    @param title: title.
    @rtype:   str
    @return:  cadena correcta sin tildes.
    """
    logger.info("streamondemand.platformcode.library title_to_filename")
    safechars = string.letters + string.digits + " -_.[]()"
    folder_name = filter(lambda c: c in safechars, elimina_tildes(title))
    return str(folder_name)


def save_library_movie(item):
    """
    guarda en la libreria de peliculas el elemento item, con los valores que contiene.
    @type item: item
    @param item: elemento que se va a guardar.
    @rtype insertados: int
    @return:  el número de elementos insertados
    @rtype sobreescritos: int
    @return:  el número de elementos sobreescritos
    @rtype fallidos: int
    @return:  el número de elementos fallidos o -1 si ha fallado todo
    """
    logger.info("streamondemand.platformcode.library savelibrary_movie")
    insertados = 0
    sobreescritos = 0
    fallidos = 0
    logger.debug(item.tostring('\n'))

    if not item.fulltitle or not item.channel:
        return 0, 0, -1  # Salimos sin guardar

    # progress dialog
    p_dialog = platformtools.dialog_progress('streamondemand', 'Añadiendo película...')
    filename = title_to_filename("{0} [{1}].strm".format(item.fulltitle.strip().lower(),
                                                         item.channel))
    logger.debug(filename)
    fullfilename = join_path(MOVIES_PATH, filename)
    addon_name = sys.argv[0].strip()
    if not addon_name:
        addon_name = "plugin://plugin.video.streamondemand/"

    if path_exists(fullfilename):
        logger.info("streamondemand.platformcode.library savelibrary el fichero existe. Se sobreescribe")
        sobreescritos += 1
    else:
        insertados += 1

    p_dialog.update(100, 'Añadiendo película...', item.fulltitle)
    p_dialog.close()

    if save_file('{addon}?{url}'.format(addon=addon_name, url=item.tourl()), fullfilename):
        item = get_video_id_from_scraper(item, config.get_setting("scrap_ask_name") == "true", "movie")
        if 'id_Tmdb' in item.infoLabels:
            create_nfo_file(item.infoLabels['id_Tmdb'], fullfilename[:-5], "cine")
        return insertados, sobreescritos, fallidos
    else:
        return 0, 0, 1


def save_library_tvshow(serie, episodelist):
    """
    guarda en la libreria de series la serie con todos los capitulos incluidos en la lista episodelist
    @type serie: item
    @param serie: item que representa la serie a guardar
    @type episodelist: list
    @param episodelist: listado de items que representan los episodios que se van a guardar.
    @rtype insertados: int
    @return:  el número de episodios insertados
    @rtype sobreescritos: int
    @return:  el número de episodios sobreescritos
    @rtype fallidos: int
    @return:  el número de episodios fallidos o -1 si ha fallado toda la serie
    """
    logger.info("streamondemand.platformcode.library savelibrary_tvshow")

    if serie.show == "":  # TODO ¿otras opciones?
        return 0, 0, -1  # Salimos sin guardar: La serie no tiene el titulo fijado

    path = join_path(TVSHOWS_PATH, "{0} [{1}]".format(title_to_filename(serie.show.strip().lower()),
                                                      serie.channel).lower())
    if not path_exists(path):
        logger.info("streamondemand.platformcode.library savelibrary Creando directorio serie:" + path)
        try:
            make_dir(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    # Guardar los episodios
    insertados, sobreescritos, fallidos = save_library_episodes(path, episodelist)

    return insertados, sobreescritos, fallidos


def get_dict_series():
    """
    devuelve un diccionario con las series obtenidas de 'series.json'
    @rtype dict_series: dict
    @return:  diccionario con las series.
    """
    logger.info("streamondemand.platformcode.library get_dict_series")
    fname = join_path(config.get_data_path(), TVSHOW_FILE)
    dict_series = jsontools.load_json(read_file(fname))

    if dict_series=="":
        dict_series = {}

    return dict_series


def get_video_id_from_scraper(serie, ask=False, video_type="tv"):
    """
    Hace una busqueda con el scraper seleccionado *tmdb por defecto* por el nombre (y año si esta presente) y presenta
    una 'ventana' para seleccionar uno.
    Retorna el item pasado como parametro con algunos infoLabels actualizados
    @type serie: item
    @param serie: video para obtener identificar
    @type ask: bool
    @param ask: muestra la ventana de información para seleccionar el titulo correcto de la serie/pelicula.
    @type video_type: str
    @param video_type: tipo de video para buscar, 'tv' o 'movie'
    @rtype serie: item
    @return:  devuelve el item 'serie' con la información seteada.
    """
    logger.info("streamondemand.platformcode.library get_video_id_from_scraper")
    from core import tmdb
    otmdb = tmdb.Tmdb(texto_buscado=serie.infoLabels['title'], tipo=video_type, year=serie.infoLabels.get('year', ''))
    if ask:
        select = platformtools.show_video_info(otmdb.get_list_resultados(),
                                               caption="[{0}]: Selecciona la serie correcta".
                                               format(serie.infoLabels['title']), callback='cb_select_from_tmdb')
        if select:
            serie.infoLabels.update(select)
            logger.debug(tmdb.infoLabels_tostring(serie))
    else:
        if len(otmdb.get_list_resultados()) == 0:
            return serie

        # Fijamos los infoLabels
        serie.infoLabels.update(otmdb.get_list_resultados()[0])
        serie.infoLabels['id_Tmdb'] = otmdb.get_list_resultados()[0]['id']
        serie.infoLabels['title'] = otmdb.get_list_resultados()[0]['name'].strip()  # Si fuesen movies seria title

    return serie


def cb_select_from_tmdb(dic):
    # print repr(dic)
    return dic


def save_library_episodes(path, episodelist):
    """
    guarda en la ruta indicada todos los capitulos incluidos en la lista episodelist
    @type path: str
    @param path: ruta donde guardar los episodios
    @type episodelist: list
    @param episodelist: listado de items que representan los episodios que se van a guardar.
    @rtype insertados: int
    @return:  el número de episodios insertados
    @rtype sobreescritos: int
    @return:  el número de episodios sobreescritos
    @rtype fallidos: int
    @return:  el número de episodios fallidos
    """
    logger.info("streamondemand.platformcode.library savelibrary_episodes")
    insertados = 0
    sobreescritos = 0
    fallidos = 0

    # progress dialog
    p_dialog = platformtools.dialog_progress('streamondemand', 'Añadiendo episodios...')
    p_dialog.update(0, 'Añadiendo episodio...')
    # fix float porque la division se hace mal en python 2.x
    t = float(100) / len(episodelist)

    addon_name = sys.argv[0].strip()
    if not addon_name:
        addon_name = "plugin://plugin.video.streamondemand/"

    for i, e in enumerate(episodelist):
        p_dialog.update(int(math.ceil(i * t)), 'Añadiendo episodio...', e.title)
        # Añade todos menos el que dice "Añadir esta serie..." o "Descargar esta serie..."
        if e.action == "add_serie_to_library" or e.action == "download_all_episodes":
            continue

        e.action = "play_from_library"
        e.category = "Series"

        nuevo = False
        filename = "{0}.strm".format(scrapertools.get_season_and_episode(e.title.lower()))
        fullfilename = join_path(path, filename)
        # logger.debug(fullfilename)

        if not path_exists(fullfilename):
            nuevo = True

        if save_file('{addon}?{url}'.format(addon=addon_name, url=e.tourl()), fullfilename):
            if nuevo:
                insertados += 1
            else:
                sobreescritos += 1
        else:
            fallidos += 1

        if p_dialog.iscanceled():
            break

    p_dialog.close()

    logger.debug("insertados= {0}, sobreescritos={1}, fallidos={2}".format(insertados, sobreescritos, fallidos))
    return insertados, sobreescritos, fallidos


def read_file(fname):
    """
    pythonic way to read from file

    @type  fname: str
    @param fname: filename.

    @rtype:   str
    @return:  data from filename.
    """
    logger.info("streamondemand.platformcode.library read_file")
    data = ""

    if not samba.usingsamba(fname):
        if os.path.isfile(fname):
            try:
                with open(fname, "r") as f:
                    for line in f:
                        data += line
            except EnvironmentError:
                logger.info("ERROR al leer el archivo: {0}".format(fname))
    else:
        path, filename = fname.rsplit('/', 1)
        if samba.file_exists(filename, path):
            try:
                from samba.smb.smb_structs import OperationFailure
                with samba.get_file_handle_for_reading(filename, path) as f:
                    for line in f:
                        data += line
            except OperationFailure:
                logger.info("ERROR al leer el archivo: {0}".format(filename))

    # logger.info("streamondemand.platformcode.library read_file-data {0}".format(data))
    return data


def save_file(data, fname):
    """
    pythonic way to write a file

    @type  fname: str
    @param fname: filename.
    @type  data: str
    @param data: data to save.

    @rtype:   bool
    @return:  result of saving.
    """
    logger.info("streamondemand.platformcode.library save_file")
    logger.info("default encoding: {0}".format(sys.getdefaultencoding()))
    if not samba.usingsamba(fname):
        try:
            with open(fname, "w") as f:
                try:
                    f.write(data)
                except UnicodeEncodeError:
                    logger.info("Error al realizar el encode, se usa uft8")
                    f.write(data.encode('utf-8'))
        except EnvironmentError:
            logger.info("streamondemand.platformcode.library save_file - Error al guardar el archivo: {0}".format(fname))
            return False
    else:
        try:
            from samba.smb.smb_structs import OperationFailure
            path, filename = fname.rsplit('/', 1)
            try:
                samba.store_file(filename, data, path)
            except UnicodeEncodeError:
                logger.info("Error al realizar el encode, se usa uft8")
                samba.store_file(filename, data.encode('utf-8'), path)
        except OperationFailure:
            logger.info("streamondemand.platformcode.library save_file - Error al guardar el archivo: {0}".format(fname))
            return False

    return True


def set_infoLabels_from_library(itemlist, tipo):
    """
    guarda los datos (thumbnail, fanart, plot, actores, etc) a mostrar de la library de Kodi.
    @type itemlist: list
    @param itemlist: item
    @type tipo: str
    @param tipo:
    @rtype:   infoLabels
    @return:  result of saving.
    """
    logger.info("streamondemand.platformcode.library set_infoLabels_from_library")
    payload = dict()
    result = list()

    if tipo == 'Movies':
        payload = {"jsonrpc": "2.0",
                   "method": "VideoLibrary.GetMovies",
                   "params": {"properties": ["title", "year", "rating", "trailer", "tagline", "plot", "plotoutline",
                                             "originaltitle", "lastplayed", "playcount", "writer", "mpaa", "cast",
                                             "imdbnumber", "runtime", "set", "top250", "votes", "fanart", "tag",
                                             "thumbnail", "file", "director", "country", "studio", "genre",
                                             "sorttitle", "setid", "dateadded"
                                             ]},
                   "id": "libMovies"}

    elif tipo == 'TVShows':
        payload = {"jsonrpc": "2.0",
                   "method": "VideoLibrary.GetTVShows",
                   "params": {"properties": ["title", "genre", "year", "rating", "plot", "studio", "mpaa", "cast",
                                             "playcount", "episode", "imdbnumber", "premiered", "votes", "lastplayed",
                                             "fanart", "thumbnail", "file", "originaltitle", "sorttitle",
                                             "episodeguide", "season", "watchedepisodes", "dateadded", "tag"
                                             ]},
                   "id": "libTvShows"}

    elif tipo == 'Episodes' and 'tvshowid' in itemlist[0].infoLabels and itemlist[0].infoLabels['tvshowid']:
        tvshowid = itemlist[0].infoLabels['tvshowid']
        payload = {"jsonrpc": "2.0",
                   "method": "VideoLibrary.GetEpisodes",
                   "params": {"tvshowid": tvshowid,
                              "properties": ["title", "plot", "votes", "rating", "writer", "firstaired", "playcount",
                                             "runtime", "director", "productioncode", "season", "episode",
                                             "originaltitle",
                                             "showtitle", "cast", "lastplayed", "fanart", "thumbnail",
                                             "file", "dateadded", "tvshowid"
                                             ]},
                   "id": 1}

    data = get_data(payload)
    logger.debug("JSON-RPC: {0}".format(data))

    if 'error' in data:
        logger.error("JSON-RPC: {0}".format(data))

    elif 'movies' in data['result']:
        result = data['result']['movies']

    elif 'tvshows' in data['result']:
        result = data['result']['tvshows']

    elif 'episodes' in data['result']:
        result = data['result']['episodes']

    if result:
        for i in itemlist:
            for r in result:
                r_filename_aux = r['file'][:-1] if r['file'].endswith(os.sep) or r['file'].endswith('/') else r['file']
                r_filename = os.path.basename(r_filename_aux)
                # logger.debug(os.path.basename(i.path) + '\n' + r_filename)
                i_filename = os.path.basename(i.path)
                if i_filename == r_filename:
                    infoLabels = r

                    # Obtener imagenes y asignarlas al item
                    if 'thumbnail' in infoLabels:
                        infoLabels['thumbnail'] = urllib.unquote_plus(infoLabels['thumbnail']).replace('image://', '')
                        i.thumbnail = infoLabels['thumbnail'][:-1] if infoLabels['thumbnail'].endswith('/') else \
                            infoLabels['thumbnail']
                    if 'fanart' in infoLabels:
                        infoLabels['fanart'] = urllib.unquote_plus(infoLabels['fanart']).replace('image://', '')
                        i.fanart = infoLabels['fanart'][:-1] if infoLabels['fanart'].endswith('/') else infoLabels[
                            'fanart']

                    # Adaptar algunos campos al formato infoLables
                    if 'cast' in infoLabels:
                        l_castandrole = list()
                        for c in sorted(infoLabels['cast'], key=lambda _c: _c["order"]):
                            l_castandrole.append((c['name'], c['role']))
                        infoLabels.pop('cast')
                        infoLabels['castandrole'] = l_castandrole
                    if 'genre' in infoLabels:
                        infoLabels['genre'] = ', '.join(infoLabels['genre'])
                    if 'writer' in infoLabels:
                        infoLabels['writer'] = ', '.join(infoLabels['writer'])
                    if 'director' in infoLabels:
                        infoLabels['director'] = ', '.join(infoLabels['director'])
                    if 'country' in infoLabels:
                        infoLabels['country'] = ', '.join(infoLabels['country'])
                    if 'studio' in infoLabels:
                        infoLabels['studio'] = ', '.join(infoLabels['studio'])
                    if 'runtime' in infoLabels:
                        infoLabels['duration'] = infoLabels.pop('runtime')

                    # Fijar el titulo si existe y añadir infoLabels al item
                    if 'label' in infoLabels:
                        i.title = infoLabels['label']
                    i.infoLabels = infoLabels
                    result.remove(r)
                    break


def clean_up_file(item):
    """
    borra los elementos del fichero "series" que no existen como carpetas en la libreria de "SERIES"
    @type item: item
    @param item: elemento
    @rtype:   list
    @return:  vacío para navegue.
    """
    logger.info("streamondemand.platformcode.library clean_up_file")

    path = TVSHOWS_PATH

    dict_data = item.dict_fichero
    
    # Obtenemos las carpetas de las series
    raiz, carpetas_series, files = os.walk(path).next()
    
    for tvshow_id in dict_data.keys():
        for channel in dict_data[tvshow_id]["channels"].keys():
            carpeta = "{0} [{1}]".format(title_to_filename(dict_data[tvshow_id]["channels"][channel]["tvshow"].lower()),
                                         channel)
            if carpeta not in carpetas_series:
                dict_data[tvshow_id]["channels"].pop(channel, None)
                if not dict_data[tvshow_id]["channels"]:
                    dict_data.pop(tvshow_id, None)
    
    json_data = jsontools.dump_json(dict_data)
    save_file(json_data, join_path(config.get_data_path(), TVSHOW_FILE))

    return []


def save_tvshow_in_file(serie):
    """
    Guarda los datos de la serie dentro del fichero 'series.json'
    @type serie: item
    @param serie: elemento
    """
    logger.info("streamondemand.platformcode.library save_tvshow_in_file")
    fname = join_path(config.get_data_path(), TVSHOW_FILE)
    # TODO soporte samba
    if not os.path.isfile(fname):
        convert_xml_to_json()

    if 'infoLabels' not in serie:
        serie.infoLabels = {}

    patron = "^(.+)[\s]\((\d{4})\)$"
    matches = re.compile(patron, re.DOTALL).findall(serie.show)

    if matches:
        serie.infoLabels['title'] = matches[0][0]
        serie.infoLabels['year'] = matches[0][1]

    if 'title' not in serie.infoLabels:
        serie.infoLabels['title'] = serie.show

    # Abrir ventana de seleccion de serie
    serie = get_video_id_from_scraper(serie, config.get_setting("scrap_ask_name") == "true")

    create_nfo = False
    if 'id_Tmdb' in serie.infoLabels:
        tvshow_id = serie.infoLabels['id_Tmdb']
        create_nfo = True
    else:
        tvshow_id = "t_{0}_[{1}]".format(serie.show.strip().replace(" ", "_"), serie.channel)

    # Cargar el registro series.json
    fname = join_path(config.get_data_path(), TVSHOW_FILE)
    dict_series = jsontools.load_json(read_file(fname))
    if not dict_series:
        dict_series = {}

    path = join_path(TVSHOWS_PATH, "{0} [{1}]".format(title_to_filename(serie.show.strip().lower()),
                                                      serie.channel).lower())

    if path_exists(path):
        if create_nfo:
            create_nfo_file(tvshow_id, path, "serie")

    # Si la serie no existe en el registro ...
    if tvshow_id not in dict_series:
        # ... añadir la serie al registro
        dict_series[tvshow_id] = {"name": serie.infoLabels['title'], "channels": {}}

    # Si no hay datos del canal en el registro para esta serie...
    if serie.channel not in dict_series[tvshow_id]["channels"]:
        # ... añadir canal al registro de la serie
        dict_channel = {"tvshow": serie.show.strip(), "url": serie.url, "path": path}
        dict_series[tvshow_id]["channels"][serie.channel] = dict_channel

    logger.info("dict_series {0}".format(dict_series))
    json_data = jsontools.dump_json(dict_series)
    save_file(json_data, fname)


def mark_as_watched(category, video_id=0):
    """
    marca el capitulo como visto en la libreria de Kodi
    @type category: str
    @param category: categoria "Series" o "Cine"
    @type video_id: int
    @param video_id: identificador 'episodeid' o 'movieid' en la BBDD
    """
    logger.info("streamondemand.platformcode.library mark_as_watched - category:{0}".format(category))

    logger.info("se espera 5 segundos por si falla al reproducir el fichero")
    xbmc.sleep(5000)

    if not is_compatible() or not config.get_setting("mark_as_watched") == "true":
        return

    if xbmc.Player().isPlaying():
        payload = {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}
        data = get_data(payload)

        if 'result' in data:
            payload_f = ''
            player_id = data['result'][0]["playerid"]

            if category == "Series":
                episodeid = video_id
                if episodeid == 0:
                    payload = {"jsonrpc": "2.0", "params": {"playerid": player_id,
                                                            "properties": ["season", "episode", "file", "showtitle"]},
                               "method": "Player.GetItem", "id": "libGetItem"}

                    data = get_data(payload)
                    if 'result' in data:
                        season = data['result']['item']['season']
                        episode = data['result']['item']['episode']
                        showtitle = data['result']['item']['showtitle']
                        # logger.info("titulo es {0}".format(showtitle))

                        payload = {
                            "jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes",
                            "params": {
                                "filter": {"and": [{"field": "season", "operator": "is", "value": str(season)},
                                                   {"field": "episode", "operator": "is", "value": str(episode)}]},
                                "properties": ["title", "plot", "votes", "rating", "writer", "firstaired", "playcount",
                                               "runtime", "director", "productioncode", "season", "episode",
                                               "originaltitle", "showtitle", "lastplayed", "fanart", "thumbnail",
                                               "file", "resume", "tvshowid", "dateadded", "uniqueid"]},
                            "id": 1}

                        data = get_data(payload)
                        if 'result' in data:
                            for d in data['result']['episodes']:
                                if d['showtitle'] == showtitle:
                                    episodeid = d['episodeid']
                                    break

                if episodeid != 0:
                    payload_f = {"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {
                        "episodeid": episodeid, "playcount": 1}, "id": 1}

            else:  # Categoria == 'Movies'
                movieid = video_id
                if movieid == 0:

                    payload = {"jsonrpc": "2.0", "method": "Player.GetItem",
                               "params": {"playerid": 1,
                                          "properties": ["year", "file", "title", "uniqueid", "originaltitle"]},
                               "id": "libGetItem"}

                    data = get_data(payload)
                    logger.debug(repr(data))
                    if 'result' in data:
                        title = data['result']['item']['title']
                        year = data['result']['item']['year']
                        # logger.info("titulo es {0}".format(title))

                        payload = {"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies",
                                   "params": {
                                       "filter": {"and": [{"field": "title", "operator": "is", "value": title},
                                                          {"field": "year", "operator": "is", "value": str(year)}]},
                                       "properties": ["title", "plot", "votes", "rating", "writer", "playcount",
                                                      "runtime", "director", "originaltitle", "lastplayed", "fanart",
                                                      "thumbnail", "file", "resume", "dateadded"]},
                                   "id": 1}

                        data = get_data(payload)

                        if 'result' in data:
                            for d in data['result']['movies']:
                                logger.info("title {0}".format(d['title']))
                                if d['title'] == title:
                                    movieid = d['movieid']
                                    break

                if movieid != 0:
                    payload_f = {"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {
                        "movieid": movieid, "playcount": 1}, "id": 1}

            if payload_f:
                condicion = int(config.get_setting("watched_setting"))
                payload = {"jsonrpc": "2.0", "method": "Player.GetProperties",
                           "params": {"playerid": player_id,
                                      "properties": ["time", "totaltime", "percentage"]},
                           "id": 1}

                while xbmc.Player().isPlaying():
                    data = get_data(payload)
                    # logger.debug("Player.GetProperties: {0}".format(data))
                    # 'result': {'totaltime': {'hours': 0, 'seconds': 13, 'minutes': 41, 'milliseconds': 341},
                    #            'percentage': 0.209716334939003,
                    #            'time': {'hours': 0, 'seconds': 5, 'minutes': 0, 'milliseconds': 187}}

                    if 'result' in data:
                        from datetime import timedelta
                        totaltime = data['result']['totaltime']
                        totaltime = totaltime['seconds'] + 60 * totaltime['minutes'] + 3600 * totaltime['hours']
                        tiempo_actual = data['result']['time']
                        tiempo_actual = timedelta(hours=tiempo_actual['hours'], minutes=tiempo_actual['minutes'],
                                                  seconds=tiempo_actual['seconds'])

                        if condicion == 0:  # '5 minutos'
                            mark_time = timedelta(seconds=300)
                        elif condicion == 1:  # '30%'
                            mark_time = timedelta(seconds=totaltime * 0.3)
                        elif condicion == 2:  # '50%'
                            mark_time = timedelta(seconds=totaltime * 0.5)
                        elif condicion == 3:  # '80%'
                            mark_time = timedelta(seconds=totaltime * 0.8)

                        logger.debug(str(mark_time))

                        if tiempo_actual > mark_time:
                            # Marcar como visto
                            data = get_data(payload_f)
                            if data['result'] != 'OK':
                                logger.info("ERROR al poner el contenido como visto")
                            break

                    xbmc.sleep(30000)


def get_data(payload):
    """
    obtiene la información de la llamada JSON-RPC con la información pasada en payload
    @type payload: dict
    @param payload: data
    :return:
    """
    logger.info("streamondemand.platformcode.library get_data:: payload {0}".format(payload))
    # Required header for XBMC JSON-RPC calls, otherwise you'll get a 415 HTTP response code - Unsupported media type
    headers = {'content-type': 'application/json'}

    if modo_cliente:
        try:
            req = urllib2.Request(xbmc_json_rpc_url, data=jsontools.dump_json(payload), headers=headers)
            f = urllib2.urlopen(req)
            response = f.read()
            f.close()

            logger.info("streamondemand.platformcode.library get_data:: response {0}".format(response))
            data = jsontools.load_json(response)
        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.info("streamondemand.platformcode.library get_data:: error en xbmc_json_rpc_url: {0}".format(message))
            data = ["error"]
    else:
        try:
            data = jsontools.load_json(xbmc.executeJSONRPC(jsontools.dump_json(payload)))
        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.info("streamondemand.platformcode.library get_data:: error en xbmc.executeJSONRPC: {0}".format(message))
            data = ["error"]

    logger.info("streamondemand.platformcode.library get_data:: data {0}".format(data))

    return data


def check_tvshow_xml():
    logger.info("streamondemand.platformcode.library check_tvshow_xml")
    fname = join_path(config.get_data_path(), TVSHOW_FILE_OLD)
    flag = True
    # todo soporte samba
    if not os.path.exists(fname):
        flag = False
    else:
        data = read_file(fname)
        if data == "":
            flag = False

    if flag:
        convert_xml_to_json()


def convert_xml_to_json():
    logger.info("streamondemand.platformcode.library convert_xml_to_json")
    platformtools.dialog_ok("Biblioteca: Se va a actualizar al nuevo formato",
                            "Seleccione el nombre correcto de cada serie, si no está seguro pulse 'Cancelar'.",
                            "Hay nuevas opciones en 'Biblioteca' y en la 'configuración' del addon.")

    # TODO soporte samba
    os.rename(TVSHOWS_PATH, os.path.join(config.get_library_path(), "SERIES_OLD"))
    if not path_exists(TVSHOWS_PATH):

        make_dir(TVSHOWS_PATH)
        if path_exists(TVSHOWS_PATH):
            fname = join_path(config.get_data_path(), TVSHOW_FILE_OLD)
            dict_data = {}

            # TODO compatible con samba
            if path_exists(fname):
                try:
                    with open(fname, "r") as f:
                        for line in f:
                            aux = line.rstrip('\n').split(",")
                            tvshow = aux[0].strip()
                            url = aux[1].strip()
                            channel = aux[2].strip()

                            serie = Item()
                            serie.infoLabels = {}

                            patron = "^(.+)[\s]\((\d{4})\)$"
                            matches = re.compile(patron, re.DOTALL).findall(tvshow)

                            if matches:
                                serie.infoLabels['title'] = matches[0][0]
                                serie.infoLabels['year'] = matches[0][1]
                            else:
                                serie.infoLabels['title'] = tvshow

                            create_nfo = False

                            # Abrir ventana de seleccion para identificar la serie
                            serie = get_video_id_from_scraper(serie, True)

                            if 'id_Tmdb' in serie.infoLabels:
                                tvshow_id = serie.infoLabels['id_Tmdb']
                                create_nfo = True
                            else:
                                tvshow_id = "t_{0}_[{1}]".format(tvshow.strip().replace(" ", "_"), channel)

                            path = join_path(TVSHOWS_PATH, title_to_filename("{0} [{1}]".format(
                                tvshow.strip().lower(), channel)))

                            logger.info("streamondemand.platformcode.library savelibrary Creando directorio serie:" + path)
                            try:
                                make_dir(path)
                                if create_nfo:
                                    create_nfo_file(tvshow_id, path, "serie")

                            except OSError as exception:
                                if exception.errno != errno.EEXIST:
                                    raise

                            # Si la serie no existe en el registro ...
                            if tvshow_id not in dict_data:
                                # ... añadir la serie al registro
                                dict_data[tvshow_id] = {"name": serie.infoLabels['title'], "channels": {}}

                            # Si no hay datos del canal en el registro para esta serie...
                            if channel not in dict_data[tvshow_id]["channels"]:
                                # ... añadir canal al registro de la serie
                                dict_channel = {"tvshow": tvshow.strip(), "url": url, "path": path}
                                dict_data[tvshow_id]["channels"][channel] = dict_channel

                except EnvironmentError:
                    logger.info("ERROR al leer el archivo: {0}".format(fname))
                else:
                    # todo soporte samba
                    os.rename(join_path(config.get_data_path(), TVSHOW_FILE_OLD),
                              join_path(config.get_data_path(), "series_old.xml"))

                    json_data = jsontools.dump_json(dict_data)
                    save_file(json_data, join_path(config.get_data_path(), TVSHOW_FILE))

        else:
            logger.info("ERROR, no se ha podido crear la nueva carpeta de SERIES")
    else:
        logger.info("ERROR, no se ha podido renombrar la antigua carpeta de SERIES")


def update():
    """
    actualiza la libreria
    """
    logger.info("streamondemand.platformcode.library update")
    # Se comenta la llamada normal para reutilizar 'payload' dependiendo del modo cliente
    # xbmc.executebuiltin('UpdateLibrary(video)')
    payload = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": 1}
    data = get_data(payload)
    logger.info("streamondemand.platformcode.library update data:{0}".format(data))


def create_nfo_file(video_id, path, type_video):
    """
    crea el fichero nfo con la información para scrapear la pelicula o serie
    @type video_id: str
    @param video_id: codigo identificativo del video
    @type path: str
    @param path: ruta donde se creará el fichero
    @type type_video: str
    @param type_video: tipo de video "serie" o "pelicula"
    """
    # TODO meter un parametro más "scraper" para elegir entre una lista: imdb, tvdb, etc... y con el video_id pasado de
    # esa pagina se genere el nfo especifico
    logger.info("streamondemand.platformcode.library create_nfo_file")

    if type_video == "serie":
        data = "https://www.themoviedb.org/tv/{0}".format(video_id)
        nfo_file = join_path(path, "tvshow.nfo")
    else:
        data = "https://www.themoviedb.org/movie/{0}".format(video_id)
        nfo_file = path + ".nfo"

    save_file(data, nfo_file)

def add_pelicula_to_library(item):
    logger.info("streamondemand.platformcode.library add_pelicula_to_library")

    new_item = item.clone(action="play_from_library", category="Cine")
    insertados, sobreescritos, fallidos = save_library_movie(new_item)
    itemlist = []

    if fallidos == 0:
        itemlist.append(Item(title="La pelicula se ha añadido a la biblioteca", channel=item.channel))
    else:
        itemlist.append(Item(title="ERROR, la pelicula NO se ha añadido a la biblioteca",  channel=item.channel))

    from platformcode import xbmctools
    xbmctools.renderItems(itemlist, item)

    # update()


def add_serie_to_library(item, channel):
    logger.info("streamondemand.platformcode.library add_serie_to_library, show=#"+item.show+"#")

    # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
    action = item.extra
    if "###" in item.extra:
        action = item.extra.split("###")[0]
        item.extra = item.extra.split("###")[1]

    # Obtiene el listado desde el que se llamó
    itemlist = getattr(channel, action)(item)

    insertados, sobreescritos, fallidos = save_library_tvshow(item, itemlist)

    if fallidos > -1 and (insertados + sobreescritos) > 0:
        # Guardar el registro series.json actualizado
        save_tvshow_in_file(item)

    itemlist = []
    if fallidos == -1:
        itemlist.append(Item(title="ERROR, la serie NO se ha añadido a la biblioteca",channel=item.channel))
        logger.error("streamondemand.platformcode.library La serie {0} no se ha podido añadir a la biblioteca".format(item.show))
        from platformcode import xbmctools
        xbmctools.renderItems(itemlist, item)
        return -1
    elif fallidos > 0:
        itemlist.append(Item(title="ERROR, la serie NO se ha añadido completa a la biblioteca",
                             channel=item.channel))
        logger.error("streamondemand.platformcode.library No se han podido añadir {0} episodios de la serie {1} a la biblioteca".format(fallidos,item.show))
    else:
        itemlist.append(Item(title="La serie se ha añadido a la biblioteca", channel=item.channel))
        logger.info("streamondemand.platformcode.library  Se han añadido {0} episodios de la serie {1} a la biblioteca".format(insertados,item.show))

    from platformcode import xbmctools
    xbmctools.renderItems(itemlist, item)
    # update() # TODO evitar bucle
