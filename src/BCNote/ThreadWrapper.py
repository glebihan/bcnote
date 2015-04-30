# ThreadWrapper.py
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
from gi.repository import GLib
from functools import wraps

def async_method(callback = None):
    def _async_method_decorator(method):
        def _async_method_decorator_inner(*args):
            if callback:
                def async_method_callback(*cb_args):
                    params = (args[0],) + cb_args
                    return callback(*params)
            else:
                async_method_callback = None
            return ThreadWrapper(method, args, async_method_callback).start()
        return wraps(method)(_async_method_decorator_inner)
    return _async_method_decorator

class ThreadWrapper(object):
    def __init__(self, target, args = (), callback = None):
        self._target = target
        self._args = args
        self._callback = callback
        
        self._thread = threading.Thread(target = self._process)
    
    def _process(self):
        result = self._target(*self._args)
        
        if self._callback:
            if type(result) == tuple:
                GLib.idle_add(self._callback, *result)
            elif result == None:
                GLib.idle_add(self._callback)
            else:
                GLib.idle_add(self._callback, result)
        
    def start(self):
        self._thread.start()
