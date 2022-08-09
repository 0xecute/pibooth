# -*- coding: utf-8 -*-

import os
import os.path as osp
import itertools
import time
from datetime import datetime
import pibooth
from pibooth.utils import LOGGER, PoolingTimer
from pibooth.pictures import get_picture_factory
from pibooth.pictures.pool import PicturesFactoryPool


class PrintingPlugin(object):

    """Plugin to show printing in progress.
    """

    def __init__(self, plugin_manager):
        self.texts_vars = {}

    def _reset_vars(self, app):
        """Destroy final picture (can not be used anymore).
        """
        app.previous_picture_file = None


    @pibooth.hookimpl
    def state_printing_enter(self, app):
        self._reset_vars(app)

    @pibooth.hookimpl
    def state_printing_do(self, cfg, app, events):
        if app.find_print_event(events) and app.previous_picture_file and app.printer.is_installed():
            LOGGER.info("PRINTING SOMETHING")

        LOGGER.info("PRINTING DO")
        time.sleep(10)
        app.printer.cancel_all_tasks()
