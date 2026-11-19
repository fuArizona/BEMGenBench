"""idf_sched.py - the MEANING of a schedule, so that two schedules written differently but with the same hourly values pair and compare as equal (aligned mode).

  profile(obj, base_dir)            obj = an object of idf_flatten (cls, values) -> a canonical profile or None (a class that is not handled); base_dir = the folder of the IDF (for a Schedule:File)
  profiles_equal(p, q, tol, abs_tol)
  is_data_key(key)                  a field that only says where / how the hourly values are held (data[n], hourly_value, the file fields of Schedule:File)

Handled: Schedule:Compact (Through / For / Until / value tokens; the day-type keywords AllDays, Weekdays, Weekends, Holidays, AllOtherDays and the single day types), Schedule:Constant and
(2026-10-28) Schedule:File when its CSV can be read: hourly (60 minutes per item, no interpolation), 8760 values, column and rows to skip as the object says, the file name taken as it stands when it is
absolute, else relative to the folder of the IDF; the same value for every day type, one set of 24 values per date of a year of 365 days. No file / another layout = no profile (the object stays unpaired, as before).
The profile is a list of periods (the end month/day of the `Through:`), each with the 24 hourly values of every one of the 12 EnergyPlus day types (the time-weighted mean of the hour when an `Until:`
is not on the hour); adjacent periods with equal values are merged. A day type that no `For:` assigns is None. Other schedule classes (Schedule:Year, Week, Day, File ...) have no profile (they pair by name
or by their other fields).
"""
import csv
import datetime
import os
import re

FILE_KEYS = {"file_name", "column_number", "rows_to_skip_at_top", "number_of_hours_of_data", "column_separator", "interpolate_to_timestep", "minutes_per_item", "adjust_schedule_for_daylight_savings"}
FILES_READ = {}       # path -> dict(values=n, ok=True) | dict(ok=False, why=...): what the last profile() calls did with Schedule:File CSV files (the driver puts it in the notes of the report)
ENABLED = True        # idf_compare --schedule-files off sets it to False


def is_data_key(k):
    return k.startswith("data[") or k == "hourly_value" or k in FILE_KEYS


_KW = re.compile(r"^\s*(through|for|until|interpolate)\b\s*:?\s*(.*)$", re.I)


def _kw(token):
    """(keyword, rest) of a Schedule:Compact field: `Through: 12/31`, `For: Weekdays`, `Until: 24:00`, `Interpolate: No`; the colon may be missing (`For AllOtherDays`): EnergyPlus reads the first letters of the keyword. (None, token) for a value."""
    m = _KW.match(token)
    return (m.group(1).lower(), m.group(2)) if m else (None, token)


DAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "holiday", "summerdesignday", "winterdesignday", "customday1", "customday2"]
KEYWORDS = {"alldays": DAYS, "weekdays": DAYS[1:6], "weekends": ["saturday", "sunday"], "holidays": ["holiday"], "allotherdays": None}


def _hours(untils):
    """untils: [(minute of the end, value)] ascending -> 24 hourly means."""
    out = []
    for h in range(24):
        a, b, s = h * 60, h * 60 + 60, 0.0
        t = 0
        for end, v in untils:
            lo, hi = max(a, t), min(b, end)
            if hi > lo:
                s += v * (hi - lo)
            t = end
        out.append(round(s / 60.0, 9))
    return tuple(out)


def _compact(tokens):
    periods, cur, days, assigned = [], None, None, None
    i = 0
    while i < len(tokens):
        t = tokens[i].strip()
        kw, rest = _kw(t)
        if kw == "through":
            m = re.match(r"\s*(\d+)\s*/\s*(\d+)", rest)
            if not m:
                return None
            cur = dict(end=(int(m.group(1)), int(m.group(2))), days={d: None for d in DAYS})
            periods.append(cur)
            assigned = set()
            i += 1
        elif kw == "for":
            if cur is None:
                return None
            names = [w.lower() for w in rest.split()]
            days = []
            for w in names:
                if w in KEYWORDS:
                    days += KEYWORDS[w] if KEYWORDS[w] is not None else [d for d in DAYS if d not in assigned and d not in days]
                elif w in DAYS:
                    days.append(w)
            untils = []
            i += 1
            while i < len(tokens) and _kw(tokens[i])[0] in ("until", "interpolate"):
                if _kw(tokens[i])[0] == "interpolate":
                    i += 1
                    continue
                m = re.match(r"\s*(\d+)\s*:\s*(\d+)", _kw(tokens[i])[1])
                if not m or i + 1 >= len(tokens):
                    return None
                try:
                    v = float(tokens[i + 1])
                except ValueError:
                    return None
                untils.append((int(m.group(1)) * 60 + int(m.group(2)), v))
                i += 2
            if not untils:
                return None
            hours = _hours(untils)
            for d in days:
                cur["days"][d] = hours
                assigned.add(d)
        else:
            i += 1
    merged = []
    for p in sorted(periods, key=lambda x: x["end"]):
        if merged and merged[-1]["days"] == p["days"]:
            merged[-1]["end"] = p["end"]
        else:
            merged.append(dict(end=p["end"], days=dict(p["days"])))
    return merged


def compact_clauses(values):
    """The `For:` clauses of a Schedule:Compact (values = the field texts of the object): [{end: (month, day) of the Through, days: [day type names], hours: 24 hourly means, idx: [item index of every
    Until and value field of the clause, counted from the first field after the type limits = the n of `data[n]`]}], or None when the object cannot be read."""
    toks = [(i, x) for i, x in enumerate(values[2:]) if x != ""]
    out, cur_end, assigned, i = [], None, set(), 0
    while i < len(toks):
        t = toks[i][1].strip()
        kw, rest = _kw(t)
        if kw == "through":
            m = re.match(r"\s*(\d+)\s*/\s*(\d+)", rest)
            if not m:
                return None
            cur_end, assigned = (int(m.group(1)), int(m.group(2))), set()
            i += 1
        elif kw == "for":
            if cur_end is None:
                return None
            days = []
            for w in [w.lower() for w in rest.split()]:
                if w in KEYWORDS:
                    days += KEYWORDS[w] if KEYWORDS[w] is not None else [d for d in DAYS if d not in assigned and d not in days]
                elif w in DAYS:
                    days.append(w)
            i += 1
            ids, untils = [], []
            while i < len(toks) and _kw(toks[i][1])[0] in ("until", "interpolate"):
                if _kw(toks[i][1])[0] == "interpolate":
                    i += 1
                    continue
                m = re.match(r"\s*(\d+)\s*:\s*(\d+)", _kw(toks[i][1])[1])
                if not m or i + 1 >= len(toks):
                    return None
                try:
                    v = float(toks[i + 1][1])
                except ValueError:
                    return None
                untils.append((int(m.group(1)) * 60 + int(m.group(2)), v))
                ids += [toks[i][0], toks[i + 1][0]]
                i += 2
            if not untils:
                return None
            out.append(dict(end=cur_end, days=days, hours=_hours(untils), idx=ids))
            assigned.update(days)
        else:
            i += 1
    return out


def hours_at(profile, end, day):
    """The 24 hourly values of a day type on the last day of a Through period (end = (month, day)) in a merged profile, or None."""
    if not profile:
        return None
    for p in profile:
        if p["end"] >= end:
            return p["days"].get(day)
    return None


_FILE_CACHE = {}


def _file_profile(v, base_dir):
    """Schedule:File (values in the order of the IDD: name, limits, file name, column, rows to skip, hours, separator, interpolate, minutes per item, daylight saving) -> a profile, or None."""
    def g(i, default=""):
        x = v[i] if len(v) > i else ""
        return x if x != "" else default
    name = g(2)
    if not ENABLED or not name:
        return None
    path = os.path.abspath(name if os.path.isabs(name) else os.path.join(base_dir or ".", name))
    try:
        column, skip, hours = int(float(g(3, "1"))), int(float(g(4, "0"))), int(float(g(5, "8760")))
    except ValueError:
        return None
    sep = {"comma": ",", "tab": "\t", "semicolon": ";", "space": " "}.get(g(6, "Comma").lower())
    why = None
    if sep is None:
        why = "column separator %s is not supported" % g(6)
    elif g(7, "No").lower() != "no" or g(8, "60") not in ("60", "60.0"):
        why = "only hourly values without interpolation are supported (interpolate %s, minutes per item %s)" % (g(7, "No"), g(8, "60"))
    elif hours != 8760:
        why = "only 8760 values are supported (the object says %d)" % hours
    elif not os.path.isfile(path):
        why = "the file does not exist"
    if why:
        FILES_READ[path] = dict(ok=False, why=why)
        return None
    key = (path, os.path.getmtime(path), column, skip, hours, sep)
    if key not in _FILE_CACHE:
        vals, why = [], None
        try:
            with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
                rows = list(csv.reader(f, delimiter=sep))[skip:]
            for i, r in enumerate(rows[:hours]):
                vals.append(round(float(r[column - 1]), 9))
        except (IndexError, ValueError, OSError):
            why = "a value in column %d of the first %d rows after the %d skipped rows is missing or not a number" % (column, hours, skip)
        if not why and len(vals) < hours:
            why = "the file has %d values, the object says %d" % (len(vals), hours)
        if why:
            _FILE_CACHE[key] = None
            FILES_READ[path] = dict(ok=False, why=why)
        else:
            periods = []
            d0 = datetime.date(2001, 1, 1)
            for d in range(365):
                day = tuple(vals[d * 24:(d + 1) * 24])
                end = d0 + datetime.timedelta(days=d)
                if periods and periods[-1]["day"] == day:
                    periods[-1]["end"] = (end.month, end.day)
                else:
                    periods.append(dict(end=(end.month, end.day), day=day))
            _FILE_CACHE[key] = [dict(end=p["end"], days={dn: p["day"] for dn in DAYS}) for p in periods]
            FILES_READ[path] = dict(ok=True, values=len(vals), periods=len(periods))
    return _FILE_CACHE[key]


def profile(obj, base_dir=None):
    c = obj["cls"].lower()
    v = obj["values"]
    if c == "schedule:file":
        return _file_profile(v, base_dir)
    if c == "schedule:compact":
        return _compact([x for x in v[2:] if x != ""])
    if c == "schedule:constant":
        try:
            val = float(v[2])
        except (IndexError, ValueError):
            return None
        return [dict(end=(12, 31), days={d: (val,) * 24 for d in DAYS})]
    return None


DOC_DAYS_ONLY = False      # idf_doc_compare sets it: two schedules are the same when Sunday ... Saturday agree (the design days, holidays and custom days are the choice of a file)


def profiles_equal(p, q, tol=0.01, abs_tol=1e-6):
    if p is None or q is None or len(p) != len(q):
        return False
    for a, b in zip(p, q):
        if a["end"] != b["end"]:
            return False
        for d in (DAYS[:7] if DOC_DAYS_ONLY else DAYS):
            x, y = a["days"][d], b["days"][d]
            if (x is None) != (y is None):
                return False
            if x is not None and any(abs(u - w) > max(abs_tol, tol * max(abs(u), abs(w))) for u, w in zip(x, y)):
                return False
    return True
