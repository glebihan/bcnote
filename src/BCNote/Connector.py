# Connector.py
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

import json
from .ThreadWrapper import async_method

class Connector(object):
    def __init__(self, application):
        self._application = application
    
    def _send_event(self, command, *args):
        command_params = []
        for i in args:
            command_params.append(json.dumps(i))
        command_string = "app.connector._trigger(\"%s\", %s)" % (command, ", ".join(command_params))
        self._application.send_connector_command(command_string)
    
    def _on_list_notebooks_complete(self, notebooksData):
        self._send_event("reload_notebooks", notebooksData)
    
    @async_method(_on_list_notebooks_complete)
    def reload_notebooks(self):
        notebooksData = [{
            'name': n["name"],
            'guid': n["guid"],
            'stack': ['', n["stack"]][n["stack"] != None]
        } for n in self._application.evernoteClient.notebooks]
        notebooksData.sort(self._compare_notebooks)
        return notebooksData
    
    def _compare_notebooks(self, a, b):
        if a['stack']:
            if b['stack']:
                if a['stack'] != b['stack']:
                    return cmp(a['stack'].lower(), b['stack'].lower())
                else:
                    return cmp(a['name'].lower(), b['name'].lower())
            else:
                return cmp(a['stack'].lower(), b['name'].lower())
        else:
            if b['stack']:
                return cmp(a['name'].lower(), b['stack'].lower())
            else:
                return cmp(a['name'].lower(), b['name'].lower())
    
    def _on_list_tags_complete(self, tagsData):
        self._send_event("reload_tags", tagsData)
    
    @async_method(_on_list_tags_complete)
    def reload_tags(self):
        parentsMap = {}
        parentsList = []
        tagsData = []
        tags = [t for t in self._application.evernoteClient.tags]
        for t in tags:
            parentsMap[t["guid"]] = t["name"]
            if t["parentGuid"]:
                parentsList.append(t["parentGuid"])
        for t in tags:
            if not t["guid"] in parentsList:
                if t["parentGuid"]:
                    parent = parentsMap[t["parentGuid"]]
                else:
                    parent = None
                tagsData.append({
                    "guid": t["guid"],
                    "parent": parent,
                    "parentGuid": t["parentGuid"],
                    "name": t["name"]
                })
        tagsData.sort(self._compare_tags)
        print(tagsData)
        return tagsData
    
    def _compare_tags(self, a, b):
        if a['parent']:
            if b['parent']:
                if a['parent'] != b['parent']:
                    return cmp(a['parent'].lower(), b['parent'].lower())
                else:
                    return cmp(a['name'].lower(), b['name'].lower())
            else:
                return cmp(a['parent'].lower(), b['name'].lower())
        else:
            if b['parent']:
                return cmp(a['name'].lower(), b['parent'].lower())
            else:
                return cmp(a['name'].lower(), b['name'].lower())
    
    def _on_search_notes_complete(self, notesData):
        print(notesData)
    
    @async_method(_on_search_notes_complete)
    def update_search(self, params):
        notes = self._application.evernoteClient.notes
        for i in params:
            if params[i] != None:
                if i == "notebook":
                    notes = notes.where("notebookGuid", params[i])
        return [n for n in notes]
    
    def reload_notes(self, parent):
        self._application.account.list_notes(parent, self._on_list_notes_complete)
    
    def _on_list_notes_complete(self, notes):
        notes_data = [{
            'title': n.title,
            'guid': n.guid,
            'created': n.created,
            'updated': n.updated
        } for n in notes]
        notes_data.sort(lambda a,b: cmp(a['title'].lower, b['title'].lower))
        self._send_event("reload_notes", notes_data)
