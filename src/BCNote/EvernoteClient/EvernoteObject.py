# EvernoteObject.py
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

import logging

class EvernoteObject(object):
    def __init__(self, client, db, localData = None, remoteObject = None):
        self._client = client
        self._db = db
        self._localData = localData
        self._remoteObject = remoteObject
    
    def __getitem__(self, key):
        return self._localData[key]
    
    def update_from_remote(self, remoteObject):
        logging.debug("EvernoteObject(%s)::update_from_remote:%s" % (self.TABLE, remoteObject))
        
        query = "UPDATE `%(table)s` SET %(values_list)s WHERE `guid` = ?"
        query_format = {
            "table": self.TABLE,
            "values_list": []
        }
        query_params = []
        for i in self.SYNC_FIELDS:
            remoteValue = getattr(remoteObject, i)
            if remoteValue != None:
                query_format["values_list"].append("`%s` = ?" % i)
                query_params.append(remoteValue)
        query_format["values_list"] = ", ".join(query_format["values_list"])
        query_params.append(remoteObject.guid)
        self._db.query(query % query_format, query_params)
