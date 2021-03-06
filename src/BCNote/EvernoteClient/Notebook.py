# Notebook.py
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

from EvernoteObject import EvernoteObject

class Notebook(EvernoteObject):
    TABLE = "notebooks"
    SYNC_FIELDS = [
        "guid",
        "name",
        "updateSequenceNum",
        "defaultNotebook",
        "serviceCreated",
        "serviceUpdated",
        "published",
        "stack"
    ]
    RELATIONS = {
        "guid": [
            {"table": "notes", "field": "notebookGuid"}
        ]
    }
    
    def __init__(self, client, db, localData = None, remoteObject = None):
        EvernoteObject.__init__(self, client, db, localData, remoteObject)
    
    def __repr__(self):
        return "<Notebook guid=\"%s\" name=\"%s\">" % (self["guid"], self["name"])
