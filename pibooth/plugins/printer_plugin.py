# -*- coding: utf-8 -*-

import pibooth
from pibooth.utils import LOGGER


class PrinterPlugin(object):

    """Plugin to manage the printer.
    """

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.printing_status = None


    def print_picture(self, cfg, app):
        if self.printing_status != None:
            LOGGER.info("Skip the parallel printing")
            return

        self.printing_status = "Printing"
        LOGGER.info("Send final picture to printer")
        app.printer.print_file(app,
                               cfg.getint('PRINTER', 'pictures_per_page'))
        LOGGER.info("PRINTING SENT")
        app.count.printed += 1
        app.count.remaining_duplicates -= 1
        self.printing_status = None

    @pibooth.hookimpl
    def pibooth_cleanup(self, app):
        app.printer.quit()

    @pibooth.hookimpl
    def state_failsafe_enter(self, cfg, app):
        """Reset variables set in this plugin.
        """
        app.count.remaining_duplicates = cfg.getint('PRINTER', 'max_duplicates')

    @pibooth.hookimpl
    def state_wait_do(self, cfg, app, events):
        if app.find_print_event(events) and app.previous_picture_file and app.printer.is_installed():

            if app.count.remaining_duplicates <= 0:
                LOGGER.warning("Too many duplicates sent to the printer (%s max)",
                               cfg.getint('PRINTER', 'max_duplicates'))
                return

            elif not app.printer.is_ready():
                LOGGER.warning("Maximum number of printed pages reached (%s/%s max)", app.count.printed,
                               cfg.getint('PRINTER', 'max_pages'))
                return

            self.print_picture(cfg, app)
            return 'printing'

    @pibooth.hookimpl
    def state_processing_enter(self, cfg, app):
        app.count.remaining_duplicates = cfg.getint('PRINTER', 'max_duplicates')

    @pibooth.hookimpl
    def state_processing_do(self, cfg, app):
        if app.previous_picture_file and app.printer.is_ready():
            number = cfg.gettyped('PRINTER', 'auto_print')
            if number == 'max':
                number = cfg.getint('PRINTER', 'max_duplicates')
            for i in range(number):
                if app.count.remaining_duplicates > 0:
                    self.print_picture(cfg, app)

    @pibooth.hookimpl
    def state_print_do(self, cfg, app, events):
        if app.find_print_event(events) and app.previous_picture_file:
            self.print_picture(cfg, app)

