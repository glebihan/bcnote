# EvernoteObjectList.py
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
from SearchCondition import SearchCondition

class EvernoteObjectList(object):
    def __init__(self, client, db, search_condition = None):
        self._client = client
        self._db = db
        self._search_condition = search_condition
    
    def _get_instance(self, localData = None, remoteObject = None):
        return self.OBJECT_CLASS(self._client, self._db, localData = localData, remoteObject = remoteObject)
    
    def __iter__(self):
        query = "SELECT * FROM `%(table)s`" % {
            "table": self.OBJECT_CLASS.TABLE
        }
        if self._search_condition:
            search_str, query_params = self._search_condition.to_sql()
            query += " WHERE " + search_str
        else:
            query_params = []
        res = []
        for i in self._db.query(query, query_params):
            res.append(self._get_instance(localData = i))
        return iter(res)
    
    def find_match(self, remoteObject):
        logging.debug("EvernoteObjectList(%s)::find_match:%s" % (self.OBJECT_CLASS.TABLE, remoteObject))
        
        query = "SELECT * FROM `%(table)s` WHERE `guid` = ?" % {
            "table": self.OBJECT_CLASS.TABLE
        }
        res = self._db.query(query, [remoteObject.guid])
        if res:
            return self._get_instance(localData = res[0])
        else:
            return None
    
    def cleanup_deleted(self, guidList):
        logging.debug("EvernoteObjectList(%s)::cleanup_deleted:%s" % (self.OBJECT_CLASS.TABLE, guidList))
        
        query = "DELETE FROM `%(table)s` WHERE (`dirty` = 0 OR `updateSequenceNum` != 0) AND `guid` NOT IN (%(guidList)s)" % {
            "table": self.OBJECT_CLASS.TABLE,
            "guidList": ", ".join(["?" for i in guidList])
        }
        self._db.query(query, guidList)
    
    def add_from_remote(self, remoteObject):
        logging.debug("EvernoteObjectList(%s)::add_from_remote:%s" % (self.OBJECT_CLASS.TABLE, remoteObject))
        
        query = "INSERT INTO `%(table)s` (%(fields_list)s) VALUES (%(values_list)s)"
        query_format = {
            "table": self.OBJECT_CLASS.TABLE,
            "fields_list": [],
            "values_list": []
        }
        query_params = []
        for i in self.OBJECT_CLASS.SYNC_FIELDS:
            query_format["fields_list"].append("`%s`" % i)
            query_format["values_list"].append("?")
            query_params.append(getattr(remoteObject, i))
        query_format["fields_list"] = ", ".join(query_format["fields_list"])
        query_format["values_list"] = ", ".join(query_format["values_list"])
        self._db.query(query % query_format, query_params)
    
    def delete_by_guid(self, guid):
        logging.debug("EvernoteObjectList(%s)::delete_by_guid:%s" % (self.OBJECT_CLASS.TABLE, guid))
        
        self._db.query("DELETE FROM `%(table)s` WHERE `guid` = ?" % {
            "table": self.OBJECT_CLASS.TABLE
        }, [guid])
    
    def get_dirty(self):
        logging.debug("EvernoteObjectList(%s)::get_dirty" % self.OBJECT_CLASS.TABLE)
        
        res = []
        for i in self._db.query("SELECT * FROM `%(table)s` WHERE `dirty` = 1" % {
            "table": self.OBJECT_CLASS.TABLE
        }):
            res.append(self._get_instance(localData = i))
        
        return res
    
    def where(self, *args):
        if len(args) == 1 and type(args[0]) == SearchCondition:
            return type(self)(self._client, self._db, args[0])
        else:
            return type(self)(self._client, self._db, SearchCondition(*args) & self._search_condition)
