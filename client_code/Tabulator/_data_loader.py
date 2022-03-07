# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork
from math import ceil

from anvil.js import report_exceptions
from anvil.js.window import Promise
from anvil.server import no_loading_indicator
from anvil.tables import order_by

from ._module_helpers import AbstractModule, tabulator_module


class CachedSearch:
    def __init__(self, search, index, index_cache, col_spec):
        self.iter = iter(search)
        self.len = len(search)
        self.cache = []
        self.index_cache = index_cache
        self.index = index
        self.col_spec = col_spec

    def row_to_dict(self, row):
        # we do 1 level deep
        as_dict = {}
        for col in self.col_spec:
            key = col["name"]
            as_dict[key] = val = row[key]
            if val is None:
                continue
            type = col["type"]
            if type == "link_single":
                as_dict[key] = {**val}
            elif type == "link_multiple":
                as_dict[key] = [{**r} for r in val]
        return as_dict

    def get_next(self):
        try:
            row = next(self.iter)
        except StopIteration:
            pass
        else:
            index = row[self.index]
            cached = self.index_cache.get(index)
            if cached is None:
                cached = self.index_cache[index] = row
            self.cache.append(self.row_to_dict(row))

    def paginate(self, upto):
        for _ in range(upto):
            self.get_next()

    def get_data(self, page, size):
        last_page = ceil(self.len / size)

        current_index = page * size
        prev_index = current_index - size

        current_size = len(self.cache)
        self.paginate(current_index - current_size)

        data = self.cache[prev_index:current_index]
        return {"data": data, "last_page": last_page}


class LoadingInidcator:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


loading_indicator = LoadingInidcator()


@tabulator_module("appTableLoader", moduleInitOrder=1)
class AppTableLoader(AbstractModule):
    def __init__(self, mod, table):
        super().__init__(mod, table)
        mod.registerTableOption("appTable", None)
        mod.registerTableOption("loadingIndicator", True)
        mod.registerTableFunction("getTableRows", self.get_table_rows)
        mod.registerComponentFunction("row", "getTableRow", self.get_table_row)
        mod.registerComponentFunction("cell", "getTableRow", self.get_table_row)
        self.db = None
        self.col_spec = None
        self.search_cache = {}
        self.index_cache = {}
        self.index = None
        self.context = None

    @report_exceptions
    def initialize(self):
        options = self.table.options
        db = options.get("appTable")
        if db is None:
            return
        elif not hasattr(db, "search"):
            raise TypeError(
                f"Expected a table as the tabulator 'app_table' options, got {type(db).__name__}"
            )
        if not options.pagination:
            raise RuntimeError("using an an 'app_table' requires pagination")
        self.db = db
        self.index = options.index
        options.paginationMode = "remote"
        options.sortMode = "remote"
        options.filterMode = "remote"
        self.mod.subscribe("data-loading", self.request_data_check)
        self.mod.subscribe("data-load", self.request_data)
        self.mod.subscribe("row-data-retrieve", self.retrieve_data)
        self.context = (
            loading_indicator
            if options.get("loadingIndicator")
            else no_loading_indicator
        )

    def refresh(self):
        self.search = None
        self.search_cache.clear()
        self.index_cache.clear()

    def get_ordering(self, params):
        sort = params.get("sort") or ()
        return tuple(order_by(s.field, s.dir == "asc") for s in sort)

    def request_data_check(self, data, params, config, silent):
        return self.db is not None

    @report_exceptions
    def request_data(self, data, params, config, silent, prev):
        if silent:
            self.refresh()

        if self.col_spec is None:
            # this will cause a server call so only do it now
            self.col_spec = self.db.list_columns()

        ordering = self.get_ordering(params)
        query = params["query"]
        cache_key = hash((ordering, query))
        search = self.search_cache.get(cache_key)
        with self.context:
            if search is None:
                search = self.db.search(*ordering, *query.args, **query.kws)
                search = CachedSearch(
                    search, self.index, self.index_cache, self.col_spec
                )
                self.search_cache[cache_key] = search
            p = Promise.resolve(search.get_data(params["page"], params["size"]))
        return p

    @report_exceptions
    def retrieve_data(self, row, transformType, prev):
        if transformType != "table_row":
            return prev or row.data
        data = row.data
        index = data[self.index]
        retrieved = self.index_cache[index]
        return retrieved

    def get_table_row(self, row_or_cell):
        row = row_or_cell.get("row", row_or_cell)
        return row.getData("table_row")

    def get_table_rows(self, active=None):
        return self.table.rowManager.getData(active, "table_row")


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
