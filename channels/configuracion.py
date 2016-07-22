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
# Configuración
#------------------------------------------------------------

from core import config
from core.item import Item
from core import logger

DEBUG = True
CHANNELNAME = "configuracion"

def mainlist(item):
	logger.info("tvalacarta.channels.configuracion mainlist")

	itemlist = []
	itemlist.append( Item(channel=CHANNELNAME, title="Preferencias", action="settings", folder=False) )
	itemlist.append( Item(channel=CHANNELNAME, title="", action="", folder=False) )
	itemlist.append( Item(channel="novedades", title="Ajustes de la sección 'Novedades'", action="menu_opciones", folder=True) )
	itemlist.append( Item(channel="buscador", title="Ajustes del buscador global", action="opciones", folder=True) )
	itemlist.append( Item(channel=CHANNELNAME, title="", action="", folder=False) )
	itemlist.append( Item(channel=CHANNELNAME, title="Comprobar actualizaciones", action="check_for_updates", folder=False) )

	return itemlist

def check_for_updates(item):
	from core import updater
	updater.checkforupdates(plugin_mode=False)

def settings(item):
    config.open_settings( )
