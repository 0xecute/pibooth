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
        self.timer = PoolingTimer(10)


    @pibooth.hookimpl
    def state_printing_enter(self, app):
        self.timer.start()

    @pibooth.hookimpl
    def state_printing_do(self, cfg, app, events):
        LOGGER.info("PRINTING DO")
        if app.find_print_completed_status_event(events):
            LOGGER.info("RECEIVE COMPLETED EVENT")
            return 'wait'

    def state_printing_validate(self, cfg, app, events):
        if self.timer.is_timeout():
            LOGGER.info("TIMEOUT PRINTING")
            return 'wait'

    @pibooth.hookimpl
    def state_printing_exit(self, app):
        LOGGER.info("CANCEL ALL TASKS")
        app.printer.cancel_all_tasks()
