# SearchCondition.py
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

class SearchCondition(object):
    def __init__(self, *args):
        self._left = args[0]
        if len(args) == 3:
            self._operator = args[1]
            self._right = args[2]
        else:
            self._operator = "="
            self._right = args[1]
    
    def __and__(self, condition):
        if condition == None:
            return self
        else:
            return SearchCondition(self, "and", condition)
    
    def __or__(self, condition):
        if condition == None:
            return self
        else:
            return SearchCondition(self, "or", condition)
    
    def to_sql(self):
        if type(self._left) == SearchCondition:
            left_str, left_params = self._left.to_sql()
            right_str, right_params = self._right.to_sql()
            return "(" + left_str + ") " + self._operator + " (" + right_str + ")", left_params + right_params
        elif self._operator == "like":
            return "`%s` LIKE ?" % self._left, ["%" + self._right + "%"]
        elif self._operator == "in":
            return "`%s` IN (%s)" % (self._left, ", ".join(["?" for i in self._right])), self._right
        else:
            return "`%s` %s ?" % (self._left, self._operator), [self._right]
