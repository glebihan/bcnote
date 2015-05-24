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

from gi.repository import Gtk, Gio, GLib
from .EvernoteClient import EvernoteClient
from .EvernoteClient.SearchCondition import SearchCondition
from .AppConfiguration import AppConfiguration
from .ui.MainWindow import MainWindow
from .Connector import Connector
import logging
import os
import sys
import json
import gettext
from .informations import *

gettext.install(UNIX_APPNAME, "/usr/share/locale")

class Application(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id = "org.bcnote", register_session = True)
        self.connect("activate", self.activate)
        self.connect("startup", self.startup)
        self.connect("shutdown", self.shutdown)
        self.connect("handle-local-options", self.handle_local_options)
        
        self.add_main_option("dev-mode", 0, GLib.OptionFlags.HIDDEN, GLib.OptionArg.NONE, _("Enable development mode"), None)
        self.add_main_option("dev-token", 0, GLib.OptionFlags.HIDDEN, GLib.OptionArg.STRING, _("Set development token"), None)
        self.add_main_option("debug-level", ord("d"), GLib.OptionFlags.NONE, GLib.OptionArg.INT, _("Set debug level"), None)
        
        self.configuration = AppConfiguration(self)
        
        self._connector = Connector(self)
    
    def startup(self, application):
        ACTIONS = {
            "quit": lambda a,e: self.quit()
        }
        for action_name in ACTIONS:
            action = Gio.SimpleAction(name = action_name)
            action.connect("activate", ACTIONS[action_name])        
            self.add_action(action)
    
    def activate(self, application):
        self.evernoteClient = EvernoteClient(token = self._devToken, upgradeFilesPath = self._upgradeFilesPath)
        self.evernoteClient.connect("sync_complete", self._on_evernote_client_sync_complete)
        
        self._window = MainWindow(self, self._mainUiFile)
        self._window.show_all()
    
    def shutdown(self, shutdown):
        pass
    
    def handle_local_options(self, application, options):
        if options.lookup_value("dev-mode"):
            self._upgradeFilesPath = os.path.join(os.path.split(os.path.split(sys.argv[0])[0])[0], "data", "db_upgrades")
            self._mainUiFile = os.path.realpath(os.path.join(os.path.split(os.path.split(sys.argv[0])[0])[0], "data", "ui", "index.html"))
        else:
            self._upgradeFilesPath = os.path.join("/usr/share", UNIX_APPNAME, "db_upgrades")
            self._mainUiFile = os.path.join("/usr/share", UNIX_APPNAME, "ui", "index.html")

        debug_level = options.lookup_value("debug-level")
        if debug_level != None:
            debug_level = debug_level.get_int32()
            if debug_level > 4:
                debug_level = 4
            if debug_level < 0:
                debug_level = 0
            
            if debug_level == 4:
                logging.getLogger().setLevel(logging.DEBUG)
            elif debug_level == 3:
                logging.getLogger().setLevel(logging.INFO)
            elif debug_level == 2:
                logging.getLogger().setLevel(logging.WARNING)
            elif debug_level == 1:
                logging.getLogger().setLevel(logging.ERROR)
            elif debug_level == 0:
                logging.getLogger().setLevel(logging.CRITICAL)
        
        self._devToken = options.lookup_value("dev-token").get_string()
        
        return -1
    
    def _on_evernote_client_sync_complete(self, client):
        logging.debug("Application::_on_evernote_client_sync_complete")
    
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
