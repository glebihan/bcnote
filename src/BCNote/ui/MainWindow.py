# MainWindow.py
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

from gi.repository import Gtk
from gi.repository import WebKit
from ..informations import *
import urllib

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application, uiFile):
        Gtk.ApplicationWindow.__init__(self, application = application)
        self.set_title(APPNAME)
        
        self.set_default_size(application.configuration.getint("Display", "window_width"), application.configuration.getint("Display", "window_height"))
        if application.configuration.getboolean("Display", "window_maximized"):
            self.maximize()
        
        self._application = application
        self._uiFile = uiFile
        
        self._headerbar = Gtk.HeaderBar()
        self._headerbar.set_show_close_button(True)
        self._headerbar.props.title = APPNAME
        self.set_titlebar(self._headerbar)
        
        sw = Gtk.ScrolledWindow()
        self.add(sw)
        self._webview = WebKit.WebView()
        sw.add(self._webview)
        
        self._webview.connect("script-alert", self._on_webview_script_alert)
                
        self._webview.open(urllib.pathname2url(self._uiFile))
        
        self.connect("size-allocate", self._on_size_allocate)
    
    def _on_size_allocate(self, window, rectangle):
        if self.is_maximized():
            self._application.configuration.set("Display", "window_maximized", "true")
        else:
            self._application.configuration.set("Display", "window_maximized", "false")
            width, height = self.get_size()
            self._application.configuration.set("Display", "window_width", str(width))
            self._application.configuration.set("Display", "window_height", str(height))
    
    def _on_webview_script_alert(self, webview, frame, message):
        return self._application.handle_connector_command(message)
    
    def send_connector_command(self, command):
        self._webview.execute_script(command)
