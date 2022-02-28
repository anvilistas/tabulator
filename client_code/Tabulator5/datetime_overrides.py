from .js_tabulator import Tabulator
from datetime import date, datetime

def dt_formatter(dt_type, name, default_format):
    def formatter(cell, formatterParams, onRendered):
        val = cell.getValue()
        if val is None:
            return ""
        if not isinstance(val, dt_type):
            raise TypeError(f"A {name} formatter expects a {name} object")
        out = formatterParams.get("format") or formatterParams.get("outputFormat", "%x")
        if dt_type is datetime:
            tz = formatterParams.get("tz") or formatterParams.get("timezone")
        else:
            tz = None
        if tz is True:
            val = val.astimezone()
        elif tz is not None:
            val = val.astimezone(tz)

        if out == "iso" or out == "isoformat":
            return val.isoformat()
        else:
            return val.strftime(out)
    return formatter


Tabulator.extendModule("format", "formatters", {
    "datetime": dt_formatter(datetime, "datetime", "%x"),
    "date": dt_formatter(date, "date", "%c"),
})


def dt_sorter(compare):
    def sorter(a, b, a_row, b_row, column, dir, params):
        align_empty_values = params.get("align_empty_values") or params.get("alignEmptyValues")
        empty_align = ""
        if a is None:
            empty_align = 0 if b is None else -1
        elif b is None:
            empty_align = 1
        else:
            return compare(a, b)
        if align_empty_values == "top" and dir == "desc" or align_empty_values == "bottom" and dir == "asc":
            empty_align *= -1
        return empty_align
    return sorter


Tabulator.extendModule("sort", "sorters", {
    "datetime": dt_sorter(lambda a, b: a.timestamp() - b.timestamp()),
    "date": dt_sorter(lambda a, b: a.toordinal() - b.toordinal()),
})



def dt_editor(x):
    def editor(cell, **properties):
        value = cell.getValue()
        


"""
//sort datetime
export default function(a, b, aRow, bRow, column, dir, params){
	var DT = window.DateTime || luxon.DateTime;
	var format = params.format || "dd/MM/yyyy HH:mm:ss",
	alignEmptyValues = params.alignEmptyValues,
	emptyAlign = 0;

	if(typeof DT != "undefined"){
		a = format === "iso" ? DT.fromISO(String(a)) : DT.fromFormat(String(a), format);
		b = format === "iso" ? DT.fromISO(String(b)) : DT.fromFormat(String(b), format);

		if(!a.isValid){
			emptyAlign = !b.isValid ? 0 : -1;
		}else if(!b.isValid){
			emptyAlign =  1;
		}else{
			//compare valid values
			return a - b;
		}

		//fix empty values in position
		if((alignEmptyValues === "top" && dir === "desc") || (alignEmptyValues === "bottom" && dir === "asc")){
			emptyAlign *= -1;
		}

		return emptyAlign;

	}else{
		console.error("Sort Error - 'datetime' sorter is dependant on luxon.js");
	}
};"""