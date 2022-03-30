# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

import anvil.tables.query as q
from anvil.tables import order_by


def freeze(obj):
    ob_type = type(obj)
    if ob_type in (list, tuple):
        return tuple(freeze(o) for o in obj)
    elif ob_type is dict:
        return tuple((k, freeze(v)) for k, v in sorted(obj.items()))
    else:
        return obj


def hashable(query):
    # this makes query objects cachable as keys of dictionaries
    def _mk_tuple(self):
        return tuple(freeze(param) for param in self.__dict__.values())

    def __hash__(self):
        return hash(_mk_tuple(self))

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return self.__dict__ == other.__dict__

    query.__hash__ = __hash__
    query.__eq__ = __eq__


def make_hashable():
    if q.ilike.__hash__ is not object.__hash__:
        return
    hashable(q.like)
    hashable(q.ilike)
    hashable(q.greater_than)
    hashable(q.less_than)
    hashable(q.greater_than_or_equal_to)
    hashable(q.less_than_or_equal_to)
    hashable(q.full_text_match)
    hashable(q.all_of)
    hashable(q.any_of)
    hashable(q.none_of)
    hashable(order_by)
