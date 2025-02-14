# -*- coding: utf-8 -*-

"""Pibooth printer handling.
"""
import os

try:
    import cups
    from cups_notify import Subscriber, event
except ImportError:
    cups = None  # CUPS is optional

import tempfile
import os.path as osp

import pygame
from PIL import Image
from pibooth.utils import LOGGER
from pibooth.pictures import get_picture_factory, LANDSCAPE

PRINTER_NEW_TASK = pygame.USEREVENT + 5

PRINTER_TASKS_UPDATED = pygame.USEREVENT + 2

PRINTER_TASKS_COMPLETED = pygame.USEREVENT + 3

PAPER_FORMATS = {
    '2x6': (2, 6),      # 2x6 pouces - 5x15 cm - 51x152 mm
    '3,5x5': (3.5, 5),  # 3,5x5 pouces - 9x13 cm - 89x127 mm
    '4x6': (4, 6),      # 4x6 pouces - 10x15 cm - 101x152 mm
    '5x7': (5, 7),      # 5x7 pouces - 13x18 cm - 127x178 mm
    '6x8': (6, 8),      # 6x8 pouces - 15x20 cm - 152x203 mm
    '6x9': (6, 9),      # 6x9 pouces - 15x23 cm - 152x229 mm
}


class Printer(object):

    def __init__(self, options, name='default', max_pages=-1,counters=None):
        self._conn = cups.Connection() if cups else None
        #self._notifier = Subscriber(self._conn) if cups else None
        self.name = None
        self.max_pages = max_pages
        self.options = options
        self.count = counters
        self.job_id = None
        if not cups:
            LOGGER.warning("No printer found (pycups or pycups-notify not installed)")
            return  # CUPS is not installed

        if not name or name.lower() == 'default':
            self.name = self._conn.getDefault()
            if not self.name and self._conn.getPrinters():
                self.name = list(self._conn.getPrinters().keys())[0]  # Take first one
        elif name in self._conn.getPrinters():
            self.name = name

        if not self.name:
            if name.lower() == 'default':
                LOGGER.warning("No printer configured in CUPS (see http://localhost:631)")
            else:
                LOGGER.warning("No printer named '%s' in CUPS (see http://localhost:631)", name)
        else:
            LOGGER.info("Connected to printer '%s'", self.name)

        if not options:
            self.options = {}

    def _on_event(self, evt):
        """
        Call for each new printer event.
        """
        LOGGER.info(f"PRINTER EVENT: {evt.title} - {evt.description}")

        pygame.event.post(pygame.event.Event(PRINTER_TASKS_UPDATED, evt=evt))

    def _on_event_end_printing(self, evt):
        """
        Call for each ending printer event.
        """
        tasks = self.get_all_tasks()
        if len(tasks) == 0:
            LOGGER.info(f"END PRINTER EVENT: {evt.title} - {evt.description}")

            pygame.event.post(pygame.event.Event(PRINTER_TASKS_COMPLETED))

    def is_installed(self):
        """Return True if the CUPS server is available for printing.
        """
        return cups is not None and self.name is not None

    def is_ready(self):
        """Return False if paper/ink counter is reached or printing is disabled.
        """
        if not self.is_installed():
            return False
        if self.max_pages < 0 or self.count is None:  # No limit
            return True
        return self.count.printed < self.max_pages

    def print_file(self, app, copies=1):
        """Send a file to the CUPS server to the default printer.
        """
        filename = app.previous_picture_file
        options = self.options

        choices = app.capture_choices
        capture_nbr = app.capture_nbr or app.last_capture_nbr

        LOGGER.info(f"choices: {choices}, capture_nbr: {capture_nbr}")
        if capture_nbr != None:

            choice = choices.index(capture_nbr)

            if not isinstance(options, (list, tuple)):
                options = options
            elif len(options) >= choice:
                # Take the effect corresponding to the current capture
                options = options[choice]

            LOGGER.info(f"capture_choices: {capture_nbr}, choice: {choice}, options: {options}")
        else:
            options = {}

        if not self.name:
            raise EnvironmentError("No printer found (check config file or CUPS config)")
        if not osp.isfile(filename):
            raise IOError("No such file or directory: {}".format(filename))
        #if self._notifier and not self._notifier.is_subscribed(self._on_event):
            #self._notifier.subscribe(self._on_event, [event.CUPS_EVT_JOB_COMPLETED,
            #                                         event.CUPS_EVT_JOB_CREATED,
            #                                         event.CUPS_EVT_JOB_STOPPED,
            #                                         event.CUPS_EVT_PRINTER_STATE_CHANGED,
        #                                         event.CUPS_EVT_PRINTER_STOPPED])
        #if self._notifier and not self._notifier.is_subscribed(self._on_event_end_printing):
            #self._notifier.subscribe(self._on_event_end_printing, [event.CUPS_EVT_JOB_COMPLETED,
            #                                         event.CUPS_EVT_JOB_STOPPED,
            #                                                      event.CUPS_EVT_PRINTER_STATE_CHANGED,
        #                                         event.CUPS_EVT_PRINTER_STOPPED])

        if copies > 1:
            with tempfile.NamedTemporaryFile(suffix=osp.basename(filename)) as fp:
                picture = Image.open(filename)
                factory = get_picture_factory((picture,) * copies)
                # Don't call setup factory hook here, as the selected parameters
                # are the one necessary to render several pictures on same page.
                factory.set_margin(2)
                factory.save(fp.name)
                self.job_id = self._conn.printFile(self.name, fp.name, osp.basename(filename), options)
        else:
            self.job_id = self._conn.printFile(self.name, filename, osp.basename(filename), options)
        pygame.event.post(pygame.event.Event(PRINTER_NEW_TASK))
        LOGGER.debug("File '%s' sent to the printer with options %s", filename, options)

    def cancel_all_tasks(self):
        """Cancel all tasks in the queue.
        """
        if not self.name:
            raise EnvironmentError("No printer found (check config file or CUPS config)")
        self._conn.cancelAllJobs(self.name)

    def get_all_tasks(self):
        """Return a dict (indexed by job ID) of dicts representing all tasks
        in the queue.
        """
        if not self.name:
            return {}  # No printer found
        return self._conn.getJobs(my_jobs=True, requested_attributes=["job-id", "job-name",
                                                                      "job-uri", "job-state"])

    def quit(self):
        """Do cleanup actions.
        """
        #if self._notifier:
        #    self._notifier.unsubscribe_all()
