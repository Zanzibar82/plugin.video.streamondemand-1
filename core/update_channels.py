# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# update_channels.py
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
def update_channels():
    channel_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')

    channel_files = glob.glob(channel_path)

    # ----------------------------
    import xbmcgui
    progress = xbmcgui.DialogProgressBG()
    progress.create("Update channels list")
    # ----------------------------

    len_channel_files = len(channel_files)
    for index, channel in enumerate(channel_files):
        # ----------------------------
        percentage = index * 100 / len_channel_files
        # ----------------------------
        time.sleep(4.2 / len_channel_files)

        progress.update(percentage, ' Update channel: ' + os.path.basename(channel)[:-4])
        # ----------------------------

    # ----------------------------
    progress.close()
    # ----------------------------

    for channel in channel_files:
        updater.updatechannel(os.path.basename(channel)[:-4])


### Run
Thread(target=update_channels).start()
