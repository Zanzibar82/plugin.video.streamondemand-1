# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# update_servers.py
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import glob
import os
from threading import Thread

import time

from core import config
from core import updater

DEBUG = config.get_setting("debug")


### Procedures
def update_servers():
    server_path = os.path.join(config.get_runtime_path(), "servers", '*.xml')

    server_files = glob.glob(server_path)

    # ----------------------------
    import xbmcgui
    progress = xbmcgui.DialogProgressBG()
    progress.create("Update servers list")
    # ----------------------------

    len_server_files = len(server_files)
    for index, server in enumerate(server_files):
        # ----------------------------
        percentage = index * 100 / len_server_files
        # ----------------------------
        time.sleep(4.2 / len_server_files)

        progress.update(percentage, ' Update server: ' + os.path.basename(server)[:-4])
        # ----------------------------

    # ----------------------------
    progress.close()
    # ----------------------------

    for server in server_files:
        updater.updateserver(os.path.basename(server)[:-4])


### Run
Thread(target=update_servers).start()
