# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork
from functools import lru_cache
from math import ceil
from operator import getitem

import anvil
from anvil.js import report_exceptions
from anvil.js.window import Promise
from anvil.server import no_loading_indicator
from anvil.tables import TableError, order_by

from ._hashable_queries import make_hashable
from ._module_helpers import AbstractModule, tabulator_module

make_hashable()


def fieldgetter(*fields, getter=None):
    getter = getter or getitem

    if len(fields) == 1:
        field = fields[0]

        def g(row, obj):
            obj[field] = getter(row, field)

    else:

        def g(row, obj):
            for field in fields[:-1]:
                if row is not None:
                    # None because of linked rows being None
                    row = getter(row, field)
                obj = obj.setdefault(field, {})

            if row is not None:
                obj[fields[-1]] = getter(row, fields[-1])

    return g


def row_id_fallback(row, _field):
    return anvil._get_live_object_id(row)


_error_to_field = {KeyError: "key", AttributeError: "attribute", TableError: "column"}


class DataIterator:
    def __init__(self, data_source, data_loader):
        self.iter = iter(data_source)
        self.len = len(data_source)
        self.cache = []
        self.id_field = data_loader.id_field
        self.id_cache = data_loader.id_cache
        self.field_getters = data_loader.field_getters
        self.index_getter = data_loader.index_getter
        self.data_loader = data_loader

    def to_dict(self, row):
        as_dict = {}
        for f in self.field_getters:
            f(row, as_dict)
        return as_dict

    def fallback_to_row_id(self):
        self.id_field = self.data_loader.id_field = "_id"
        self.data_loader.table.options.index = "_id"  # this seems ok to set dynamically
        self.index_getter = self.data_loader.index_getter = row_id_fallback

    def cache_next(self):
        pysource = next(self.iter)
        index = self.index_getter(pysource, self.id_field)
        self.id_cache.setdefault(index, pysource)
        data = self.to_dict(pysource)
        data[self.id_field] = index
        self.cache.append(data)

    def paginate(self, upto):
        for i in range(upto):
            try:
                self.cache_next()
            except StopIteration:
                return
            except (AttributeError, KeyError, TableError) as e:
                if self.id_field not in str(e):
                    raise e
                tp = type(e)

                if (
                    i == 0
                    and tp is TableError
                    and not self.data_loader.data_initialized
                ):
                    self.fallback_to_row_id()
                    return self.paginate(upto)

                field = _error_to_field.get(tp, "field")
                msg = f"{e} - each data object must have a unique value for the {field} {self.id_field!r}."
                f"You can change the required {field} by changing the tabulator 'index' property"
                raise tp(msg)

    def get_remote_data(self, page, size):
        last_page = ceil(self.len / size)

        current_index = page * size
        prev_index = current_index - size

        current_size = len(self.cache)
        self.paginate(current_index - current_size)

        data = self.cache[prev_index:current_index]
        return {"data": data, "last_page": last_page}

    def get_all_data(self):
        self.paginate(self.len)
        return self.cache


class LoadingInidcator:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


loading_indicator = LoadingInidcator()


@tabulator_module("appTableLoader", moduleInitOrder=1)
class CustomDataLoader(AbstractModule):
    def __init__(self, mod, table):
        super().__init__(mod, table)
        mod.registerTableOption("appTable", None)
        mod.registerTableOption("getter", None)
        mod.registerTableOption("useModel", False)
        mod.registerTableOption("loadingIndicator", True)
        mod.registerTableFunction("clearAppTableCache", self.reset_cache)
        mod.registerTableFunction("getTableRows", self.get_py_sources)
        mod.registerTableFunction("getModels", self.get_py_sources)
        mod.registerComponentFunction("row", "getTableRow", self.get_py_source)
        mod.registerComponentFunction("cell", "getTableRow", self.get_py_source)
        mod.registerComponentFunction("row", "getModel", self.get_py_source)
        mod.registerComponentFunction("cell", "getModel", self.get_py_source)
        self.db = None
        self.getter = None
        self.field_getters = None
        self.index_getter = None
        self.col_spec = None
        self.auto_cols = False
        self.id_cache = {}
        self.id_field = None
        self.context = None
        self.use_model = False
        self.data_initialized = False
        # make sure this is the same function when subscribing/unsubscribing in js
        self.initial_request_complete = self.initial_request_complete

    def initialize_db(self, db, options):
        if not hasattr(db, "search"):
            msg = f"Expected a table as the tabulator 'app_table' options, got {type(db).__name__}"
            raise TypeError(msg)
        self.db = db
        options.paginationMode = "remote"
        options.sortMode = "remote"
        options.filterMode = "remote"
        self.mod.subscribe("data-loading", self.db_data_check)
        self.mod.subscribe("data-load", self.request_db_data)
        if options.get("loadingIndicator"):
            self.context = loading_indicator
        else:
            self.context = no_loading_indicator

    def initialize_model(self, options):
        modes = ("paginationMode", "filterMode", "sortMode")
        if any(options.get(mode) == "remote" for mode in modes):
            msg = "cannot use a model with remote filtering, pagination or sorting"
            raise TypeError(msg)
        self.use_model = True
        self.mod.subscribe("data-loading", self.model_data_check)
        self.mod.subscribe("data-load", self.request_model_data)

    @report_exceptions
    def initialize(self):
        options = self.table.options
        self.id_field = options.index
        db = options.get("appTable")
        if db is not None:
            self.initialize_db(db, options)
        elif options.get("useModel"):
            self.initialize_model(options)
        else:
            return
        self.mod.subscribe("row-data-retrieve", self.retrieve_data)
        self.mod.subscribe("columns-loaded", self.columns_loaded)
        self.auto_cols = options.autoColumns
        self.mod.subscribe("data-processing", self.initial_request_complete)

    def initial_request_complete(self, _data):
        self.data_initialized = True
        self.mod.unsubscribe("data-processing", self.initial_request_complete)

    def reset_cache(self):
        self.get_search_iter.cache_clear()
        self.id_cache.clear()

    @lru_cache
    def get_search_iter(self, ordering, query):
        search = self.db.search(*ordering, *query.args, **query.kws)
        return DataIterator(search, self)

    def get_ordering(self, params):
        sort = params.get("sort") or ()
        return tuple(order_by(s.field, s.dir == "asc") for s in sort)

    def db_data_check(self, data, params, config, silent):
        return self.db is not None

    def model_data_check(self, data, params, config, silent):
        return type(data) is list and self.use_model

    @report_exceptions
    def columns_loaded(self):
        cols = self.table.columnManager.columns
        field_structures = set(
            tuple(c.fieldStructure) for c in cols if c.fieldStructure
        )
        self.getter = getter = self.table.options.getter or getitem
        self.index_getter = getter
        self.field_getters = [
            fieldgetter(*fields, getter=getter) for fields in field_structures
        ]

    @report_exceptions
    def request_model_data(self, data, params, config, silent, prev):
        if self.auto_cols and self.col_spec is None and len(data):
            self.col_spec = data[0].__dict__.keys()
            self.field_getters = [
                fieldgetter(key, getter=self.getter) for key in self.col_spec
            ]

        iter_ = DataIterator(
            data, self.id_field, self.id_cache, self.field_getters, self.getter
        )
        return Promise.resolve(iter_.get_all_data())

    @report_exceptions
    def request_db_data(self, data, params, config, silent, prev):
        if self.auto_cols and self.col_spec is None:
            self.col_spec = (c["name"] for c in self.db.list_columns())
            self.field_getters = [
                fieldgetter(key, getter=self.getter) for key in self.col_spec
            ]

        ordering = self.get_ordering(params)
        query = params["query"]
        with self.context:
            iter_ = self.get_search_iter(ordering, query)
            p = Promise.resolve(iter_.get_remote_data(params["page"], params["size"]))
        return p

    @report_exceptions
    def retrieve_data(self, row, transformType, prev):
        if transformType != "py_source":
            return prev or row.data
        data = row.data
        index = data[self.id_field]
        retrieved = self.id_cache[index]
        return retrieved

    def get_py_source(self, row_or_cell):
        row = row_or_cell.get("row", row_or_cell)
        return row.getData("py_source")

    def get_py_sources(self, active=None):
        return self.table.rowManager.getData(active, "py_source")


class Query:
    def __init__(self, *args, **kws):
        self.args = args
        self.kws = {k: v if type(v) is not list else tuple(v) for k, v in kws.items()}
        self._hash = None

    def __hash__(self):
        if self._hash is None:
            try:
                self._hash = hash(self.args + tuple(sorted(self.kws.items())))
            except TypeError:
                self._hash = object.__hash__(self)
        return self._hash

    def __eq__(self, other):
        if type(other) is not Query:
            return NotImplemented
        return self.args == other.args and self.kws == other.kws


EMPTY_QUERY = Query()


@tabulator_module("query")
class QueryModule(AbstractModule):
    def __init__(self, mod, table):
        super().__init__(mod, table)
        mod.registerTableFunction("setQuery", self.set_query)
        mod.registerTableFunction("clearQuery", self.clear_query)
        self.query = EMPTY_QUERY

    def initialize(self):
        if self.table.options.get("appTable") is None:
            return
        self.mod.subscribe("data-params", self.query_params)

    def query_params(self, data, config, silent, params):
        params.query = self.query
        return params

    def set_query(self, *args, **kws):
        self.query = Query(*args, **kws)
        self.mod.reloadData()

    def clear_query(self):
        self.query = EMPTY_QUERY
        self.mod.reloadData()
