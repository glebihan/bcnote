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
from gi.repository import Gtk
import logging
import os
from informations import *

class Application(object):
    def __init__(self, cli_options):
        self.cli_options = cli_options
        self._evernote_client = EvernoteClient(token = self.cli_options.dev_token, upgradeFilesPath = self.cli_options.db_upgrades_path)
        
        self._evernote_client.connect("sync_complete", self._on_evernote_client_sync_complete)
    
    def _on_evernote_client_sync_complete(self, client):
        logging.debug("Application::_on_evernote_client_sync_complete")
        
        Gtk.main_quit()
    
    def run(self):
        self._evernote_client.sync()
        Gtk.main()
