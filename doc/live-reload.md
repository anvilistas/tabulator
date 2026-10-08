# Experimental Anvil live reload

Tabulator implements the runtime's experimental `__anvil_live_reload_state__`
property and `__anvil_live_reload_dispose__()` method. Applications do not call
these hooks during navigation.

The getter captures the initial dataset and loaded local data, including committed cell edits, sorter
fields/directions, selected row indexes, and the current pagination page. It
copies plain JavaScript objects/arrays into Python builtin containers and does
not modify the table. Local rows require stable string or numeric indexes for
selection restoration. Unsupported row values raise `TypeError`; dates, live
objects, custom instances, and cyclic data are outside this experiment.

An uninitialized table, unsupported initial dataset, or remote pagination/sorting/filtering returns `None`.
Remote sources and App Tables retain their normal loader behavior; this hook
does not turn their loaded page into a replacement local dataset. Filters,
column widths, uncommitted editors, scrolling, and edit history are not captured.

The runtime sets the property after mounting the replacement component. The
setter waits for `tableBuilt`, then restores edited rows only when the replacement's
initial dataset matches the snapshot. Changing constructor data takes effect;
changing columns with the same data preserves cell edits. It restores sorters,
selection, and page. The replacement's new columns and options remain in effect.
Restoration errors propagate to the runtime's update failure handler.

The disposal hook destroys only the retiring table's JavaScript instance. A
temporarily hidden cached Form is still owned and must not be disposed.

The methods follow the bundled Tabulator source and its public API:
[loading data](https://tabulator.info/docs/6.2/data),
[sorting](https://tabulator.info/docs/6.2/sort),
[selection](https://tabulator.info/docs/6.2/select), and
[pagination](https://tabulator.info/docs/6.2/page).
