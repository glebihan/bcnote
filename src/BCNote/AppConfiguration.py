# AppConfiguration.py
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

import threading
import ConfigParser
import os
from .informations import *

DEFAULT_CONFIG = {
    "Display": {
        "window_width": 1024,
        "window_height": 768,
        "window_maximized": "false"
    }
}

class AppConfiguration(ConfigParser.ConfigParser):
    def __init__(self, application):
        ConfigParser.ConfigParser.__init__(self)
        
        self._application = application
        
        self._lock = threading.Lock()
        
        self._load()
    
    def _ensure_dir_exists(self, path):
        if not os.path.exists(path):
            self._ensure_dir_exists(os.path.split(path)[0])
            os.mkdir(path)
    
    def _load(self):
        self.read([os.path.join(os.getenv("HOME"), ".config", UNIX_APPNAME, UNIX_APPNAME + ".cfg")])
    
    def _save(self):
        self._ensure_dir_exists(os.path.join(os.getenv("HOME"), ".config", UNIX_APPNAME))
        f = open(os.path.join(os.getenv("HOME"), ".config", UNIX_APPNAME, UNIX_APPNAME + ".cfg"), "w")
        self.write(f)
        f.close()
    
    def get(self, section, option):
        if self.has_section(section) and self.has_option(section, option):
            return ConfigParser.ConfigParser.get(self, section, option)
        else:
            return DEFAULT_CONFIG.setdefault(section, {}).setdefault(option, None)
    
    def set(self, section, key, value):
        if not self.has_section(section):
            self.add_section(section)
        ConfigParser.ConfigParser.set(self, section, key, value)
        self._save()
