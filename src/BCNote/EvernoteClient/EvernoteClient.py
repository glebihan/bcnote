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
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec, SyncChunkFilter
import logging
import os
from gi.repository import GLib
from ..informations import *
from NotebookList import NotebookList
from TagList import TagList
from NoteList import NoteList

DATATYPES_TO_SYNC = [
    {
        "clientProperty": "tags",
        "chunkProperty": "tags",
        "chunkExpungedProperty": "expungedTags"
    },
    {
        "clientProperty": "notebooks",
        "chunkProperty": "notebooks",
        "chunkExpungedProperty": "expungedNotebooks"
    },
    {
        "clientProperty": "notes",
        "chunkProperty": "notes",
        "chunkExpungedProperty": "expungedNotes"
    }
]

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
    
    def _get_notebooks(self):
        if not hasattr(self, "_notebooks"):
            self._notebooks = NotebookList(self, self._db)
        return self._notebooks
    notebooks = property(_get_notebooks)
    
    def _get_tags(self):
        if not hasattr(self, "_tags"):
            self._tags = TagList(self, self._db)
        return self._tags
    tags = property(_get_tags)
    
    def _get_notes(self):
        if not hasattr(self, "_notes"):
            self._notes = NoteList(self, self._db)
        return self._notes
    notes = property(_get_notes)
    
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
    
    def _get_global_data(self, key, default = None):
        data = self._db.simple_select_one("global_data", {"key": key})
        if data:
            res = data["value"]
            if type(default) == int:
                res = int(res)
            return res
        else:
            return default
    
    def _set_global_data(self, key, value):
        self._db.simple_replace("global_data", {"key": key, "value": value})
    
    @async_method(None)
    def sync(self):
        logging.debug("EvernoteClient::sync")
        
        needSync = True
        
        while needSync:
            noteStore = self._backend.get_note_store()
            syncState = noteStore.getSyncState()
            logging.debug("EvernoteClient::sync:syncState = %s" % syncState)
            
            afterUSN = self._get_global_data("updateCount", 0)
            lastSyncTime = self._get_global_data("lastSyncTime", 0)

            if syncState.fullSyncBefore > lastSyncTime:
                # The server forces us to do a full sync
                afterUSN = 0
            
            fullSync = (afterUSN == 0)
            
            # Test if there are updates on the server
            if afterUSN != syncState.updateCount:
                
                # Fetch updates from server
                chunks = []
                continue_fetching = True
                
                while continue_fetching:
                    chunkFilter = SyncChunkFilter(
                        includeNotebooks = True,
                        includeTags = True,
                        includeNotes = True,
                        includeExpunged = True
                    )
                    chunk = noteStore.getFilteredSyncChunk(afterUSN, 10, chunkFilter)
                    if chunk.chunkHighUSN and chunk.chunkHighUSN < chunk.updateCount:
                        afterUSN = chunk.chunkHighUSN
                    else:
                        continue_fetching = False
                    chunks.append(chunk)
                logging.debug("EvernoteAccount::synchronize:chunks = %s" % chunks)
                
                # Process updates
                fullRemoteGUIDList = {}
                for dataType in DATATYPES_TO_SYNC:
                    localList = getattr(self, dataType["clientProperty"])
                    for chunk in chunks:
                        items = getattr(chunk, dataType["chunkProperty"])
                        if items:
                            for remoteItem in items:
                                localItem = localList.find_match(remoteItem)
                                if localItem:
                                    if dataType["clientProperty"] ==  "notes" and remoteItem.contentHash != localItem["contentHash"]:
                                        print "jdsklqjdskqlkjqd"
                                        remoteItem.content = noteStore.getNoteContent(remoteItem.guid)
                                    localItem.update_from_remote(remoteItem)
                                else:
                                    if dataType["clientProperty"] ==  "notes":
                                        remoteItem.content = noteStore.getNoteContent(remoteItem.guid)
                                    localList.add_from_remote(remoteItem)
                                fullRemoteGUIDList.setdefault(dataType["clientProperty"], []).append(remoteItem.guid)
                    
                    # Process deletions
                    if not fullSync:
                        expungedData = getattr(chunk, dataType["chunkExpungedProperty"])
                        if expungedData:
                            for expungedItem in expungedData:
                                localList.delete_by_guid(expungedItem)
                
                # Process deletions for fullSync mode
                if fullSync:
                    for dataType in fullRemoteGUIDList:
                        getattr(self, dataType).cleanup_deleted(fullRemoteGUIDList[dataType])
                
                # Update sync status
                self._set_global_data("updateCount", syncState.updateCount)
                self._set_global_data("lastSyncTime", syncState.currentTime)
            
            # Send Changes
            needSync = False
        
        GLib.idle_add(self._trigger, "sync_complete")
