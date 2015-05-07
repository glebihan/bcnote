# main.py
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-
#
# Copyright © 2015 Gwendal Le Bihan
# 
# This file is part of BCNote.
# 
# BCNote is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# BCNote is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with BCNote.  If not, see <http://www.gnu.org/licenses/>.

from EvernoteClient import EvernoteClient
from EvernoteClient.SearchCondition import SearchCondition
from ui.MainWindow import MainWindow
from Connector import Connector
from gi.repository import Gtk
import logging
import os
import sys
import json
from informations import *

class Application(object):
    def __init__(self, cliOptions):
        self.cliOptions = cliOptions
        
        if self.cliOptions.devMode:
            upgradeFilesPath = os.path.join(os.path.split(os.path.split(sys.argv[0])[0])[0], "data", "db_upgrades")
            mainUiFile = os.path.realpath(os.path.join(os.path.split(os.path.split(sys.argv[0])[0])[0], "data", "ui", "index.html"))
        else:
            upgradeFilesPath = os.path.join("/usr/share", UNIX_APPNAME, "db_upgrades")
            mainUiFile = os.path.join("/usr/share", UNIX_APPNAME, "ui", "index.html")
            
        self.evernoteClient = EvernoteClient(token = self.cliOptions.devToken, upgradeFilesPath = upgradeFilesPath)
        self.evernoteClient.connect("sync_complete", self._on_evernote_client_sync_complete)
        
        self._connector = Connector(self)
        
        self._window = MainWindow(self, mainUiFile)
        self._window.connect("delete_event", lambda w,e: Gtk.main_quit())
    
    def _on_evernote_client_sync_complete(self, client):
        logging.debug("Application::_on_evernote_client_sync_complete")
    
    def run(self):
        self._window.show_all()
        Gtk.main()
    
    def send_connector_command(self, command):
        self._window.send_connector_command(command)
    
    def handle_connector_command(self, message):
        message_parts = message.split(":")
        if message_parts and message_parts[0] == "!cmd":
            method = getattr(self._connector, message_parts[1])
            method(*json.loads(":".join(message_parts[2:])))
            return True
        else:
            return False
