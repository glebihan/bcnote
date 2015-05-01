# LocalDb.py
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

from ..informations import *
import sqlite3
import logging
import os
import subprocess

class LocalDb(object):
    def __init__(self, dbFile, upgradeFilesPath):
        self._dbFile = dbFile
        self._upgradeFilesPath = upgradeFilesPath
        self._upgrade_db()
    
    def query(self, *args):
        conn = self._get_connection()
        with conn:
            cur = conn.cursor()
            cur.execute(*args)
            res = cur.fetchall()
        conn.close()
        return res
    
    def _get_version(self):
        return int(self.simple_select_one("global_data", {"key": "version"}, {"value": 0})["value"])
    version = property(_get_version)
    
    def _upgrade_db(self):
        logging.debug("LocalDb::_upgrade_db")
        
        if not os.path.exists(self._dbFile):
            folder = os.path.split(self._dbFile)[0]
            if not os.path.exists(folder):
                subprocess.call(["mkdir", "-p", folder])
        
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS `global_data` (`key` TEXT PRIMARY KEY, `value` TEXT)")
        conn.commit()
        
        version = self.version
        
        upgrade_filename = os.path.join(self._upgradeFilesPath, "%d.sql" % version)
        while os.path.exists(upgrade_filename):
            logging.debug("LocalDb::_upgrade_db:Processing DB upgrade from file : %s" % upgrade_filename)
            f = open(upgrade_filename)
            sql = f.read()
            f.close()
            cur.executescript(sql)
            version += 1
            upgrade_filename = os.path.join(self._upgradeFilesPath, "%d.sql" % version)
        conn.commit()
        
        conn.close()
        
        logging.debug("LocalDb::_upgrade_db:DB version : %d" % self.version)
    
    def _get_connection(self):
        conn = sqlite3.connect(self._dbFile)
        conn.row_factory = sqlite3.Row
        conn.text_factory = str
        return conn
    
    def simple_select(self, table, conditions = {}):
        conn = self._get_connection()
        
        with conn:
            cur = conn.cursor()
            query = "SELECT * FROM `%s`" % table
            query_params = []
            if conditions:
                query += " WHERE " + " AND ".join(["`%s` = ?" % i for i in conditions])
                query_params += [conditions[i] for i in conditions]
            cur.execute(query, query_params)
            res = cur.fetchall()
        
        conn.close()
        
        return res
    
    def simple_select_one(self, table, conditions = {}, default = None):
        data = self.simple_select(table, conditions)
        if data:
            return data[0]
        else:
            return default
    
    def simple_insert(self, table, data):
        query = "INSERT INTO `%s` (%s) VALUES (%s)" % (table, ", ".join(["`" + i + "`" for i in data]), ", ".join(["?" for i in data]))
    
        conn = sqlite3.connect(self._dbFile)
        cur = conn.cursor()
        cur.execute(query, [data[i] for i in data])
        conn.commit()
        conn.close()
        
    def simple_replace(self, table, data):
        query = "REPLACE INTO `%s` (%s) VALUES (%s)" % (table, ", ".join(["`" + i + "`" for i in data]), ", ".join(["?" for i in data]))
    
        conn = sqlite3.connect(self._dbFile)
        cur = conn.cursor()
        cur.execute(query, [data[i] for i in data])
        conn.commit()
        conn.close()
        
    def simple_update(self, table, data, conditions):
        query = "UPDATE `%s` SET %s WHERE %s" % (table, ", ".join(["`%s` = ?" % i for i in data]), " AND ".join(["`%s` = ?" % i for i in conditions]))
    
        conn = sqlite3.connect(self._dbFile)
        cur = conn.cursor()
        cur.execute(query, [data[i] for i in data] + [conditions[i] for i in conditions])
        conn.commit()
        conn.close()
    
    def simple_delete(self, table, conditions):
        query = "DELETE FROM `%s` WHERE %s" % (table, " AND ".join(["`%s` = ?" % i for i in conditions]))
        
        conn = sqlite3.connect(self._dbFile)
        cur = conn.cursor()
        cur.execute(query, [conditions[i] for i in conditions])
        conn.commit()
        conn.close()
    
    def cleanup_deleted(self, table, guidList):
        query = "DELETE FROM `%s` WHERE (`dirty` = 0 OR `updateSequenceNum` != 0) AND `guid` NOT IN (%s)" % (table, ", ".join(["?" for i in guidList]))
        
        conn = sqlite3.connect(self._dbFile)
        cur = conn.cursor()
        cur.execute(query, guidList)
        conn.commit()
        conn.close()
