# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# update_servers.py
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import glob
import os
from multiprocessing.pool import ThreadPool
from threading import Thread

from core import config
from core import updater

DEBUG = config.get_setting("debug")


### Procedures
def update_servers():
    server_path = os.path.join(config.get_runtime_path(), "servers", '*.xml')

    server_files = glob.glob(server_path)

    pool = ThreadPool(processes=4)

    # ----------------------------
    import xbmcgui
    progress = xbmcgui.DialogProgressBG()
    progress.create("Update servers list")
    # ----------------------------

    for index, server in enumerate(server_files):
        # ----------------------------
        percentage = index * 100 / len(server_files)
        # ----------------------------
        server_name = os.path.basename(server)[:-4]
        pool.apply_async(updater.updateserver, (server_name,))
        # ----------------------------
        progress.update(percentage, ' Update server: ' + server_name)
        # ----------------------------

    # ----------------------------
    progress.close()
    # ----------------------------

    pool.close()
    pool.join()


### Run
Thread(target=update_servers).start()
