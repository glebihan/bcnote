# EvernoteClient.py
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

from ..EventsObject import EventsObject
from ..ThreadWrapper import async_method
from LocalDb import LocalDb
import evernote.api.client
import logging
import os
from gi.repository import GLib
from ..informations import *

class EvernoteClient(EventsObject):
    def __init__(self, **kwargs):
        EventsObject.__init__(self)
        
        if "token" in kwargs:
            self._token = kwargs["token"]
        else:
            self._token = None
        if "userId" in kwargs:
            self._userId = kwargs["userId"]
        else:
            self._userId = None
        
        if self._userId == None and self._token == None:
            raise Exception("Either userId or token must be provided")
        
        if self._token == None:
            self._load_token()
        
        self._backend = evernote.api.client.EvernoteClient(token = self._token)
        
        if self._userId == None:
            self._load_user_id()
        
        self._db = LocalDb(os.path.join(self.dataPath, "db.sqlite"), kwargs["upgradeFilesPath"])
    
    def _get_dataPath(self):
        return os.path.join(os.getenv("HOME"), ".local", "share", UNIX_APPNAME, "%d" % self._userId)
    dataPath = property(_get_dataPath)
    
    def _load_token(self):
        token_filename = os.path.join(self.dataPath, "token")
        if not os.path.exists(token_filename):
            raise Exception("File not found : %s" % token_filename)
        f = open(token_filename)
        self._token = f.read()
        f.close()
    
    def _load_user_id(self):
        userStore = self._backend.get_user_store()
        user = userStore.getUser()
        self._userId = user.id
    
    @async_method(None)
    def sync(self):
        logging.debug("EvernoteClient::sync")
        
        needSync = True
        
        while needSync:
            noteStore = self._backend.get_note_store()
            syncState = noteStore.getSyncState()
            logging.debug("EvernoteClient::sync:syncState = %s" % syncState)
            
            afterUSN = self._db.updateCount
            lastSyncTime = self._db.lastSyncTime
            
            if syncState.fullSyncBefore > lastSyncTime:
                afterUSN = 0
            
            fullSync = (afterUSN == 0)
            
            # Send Changes
            needSync = False
        
        GLib.idle_add(self._trigger, "sync_complete")