# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# update_channels.py
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
def update_channels():
    channel_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')

    channel_files = sorted(glob.glob(channel_path))

    pool = ThreadPool(processes=10)

    # ----------------------------
    import xbmcgui
    progress = xbmcgui.DialogProgressBG()
    progress.create("Update channels list")
    # ----------------------------

    for index, channel in enumerate(channel_files):
        # ----------------------------
        percentage = index * 100 / len(channel_files)
        # ----------------------------
        channel_id = os.path.basename(channel)[:-4]
        pool.apply_async(updater.update_channel, (channel_id,))
        # ----------------------------
        progress.update(percentage, ' Update channel: ' + channel_id)
        # ----------------------------

    # ----------------------------
    progress.close()
    # ----------------------------

    pool.close()
    pool.join()


### Run
Thread(target=update_channels).start()

