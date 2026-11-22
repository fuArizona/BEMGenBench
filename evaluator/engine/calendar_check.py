"""calendar_check.py - do the reference IDF and the candidate IDF simulate the same calendar? (annotation, not in any rate)

The schedules of the two files are only comparable day by day (8,760 hours, 8,784 in a leap year) when both files run the same period, with the same year or start weekday, the same holidays and the same daylight
saving rule, and the same weather file. The weather file is not in the IDF: the benchmark gives one weather file per case (case.yaml `weather`), so both files are run with it. This module checks the rest, in the
RunPeriod of the two files (EnergyPlus rules, read from the schema notes):

  - a Begin Year that is given is the year of the simulation; when it is blank EnergyPlus chooses a year to match the field Day of Week for Start Day, which is Sunday when it is blank;
  - THE ACTUAL YEAR (`actual_year`): the year that EnergyPlus simulates. It is the Begin Year when given. When it is blank, EnergyPlus takes a non-leap year in which the start date falls on the start weekday: the
    weekday of 1 January that follows from the start date and the start weekday decides the year, with the table YEAR_OF_JAN1 below. The table was found by running EnergyPlus 23.1 (the year of the Time table of the
    sql file) for each start weekday on 1 January, for a blank start weekday (= Sunday), and for a start date of 1 March; other EnergyPlus versions were not tried. A date of 29 February without a year is not resolved
    (`actual_year` is None). `hours` is the number of hours from the start date to the end date in that year (8,760 for a full non-leap year, 8,784 for a full leap year);
  - Use Weather File Holidays and Special Days, Use Weather File Daylight Saving Period: blank = Yes; Apply Weekend Holiday Rule: blank = No;
  - the number of RunPeriodControl:SpecialDays and RunPeriodControl:DaylightSavingTime objects of each file is listed as a note (they add holidays and a daylight saving period).

  calendar_check(flat_reference, flat_candidate) -> dict(status "same" | "differs" | "unknown", reference, candidate, differences [text], notes [text])
  required_year_check(calendar_check_result, run_year) -> dict: does each file simulate the run year that the case requires (`run_year` of case.yaml, also in run_conditions.txt and in the task prompt)?
      `uses_run_year` (the actual year is the required year), `same_calendar_as_run_year` (another year number with the same start weekday and leap-year status: the same calendar), for the reference and for the candidate.
      An annotation like the rest of this module: nothing here changes a score.

Two files have the same calendar when the run period, the weekday of the start day, the length (leap year or not) and the holiday and daylight saving rules agree. Different year numbers with the same weekday alignment and
length are only noted. `same` does not compare the schedules. Nothing here changes a score.
"""
import calendar as _cal
import datetime

import idf_values as V

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]      # datetime.weekday(): Monday = 0
# the non-leap year that EnergyPlus 23.1 chooses when the year is blank, by the weekday of 1 January (found by running EnergyPlus 23.1)
YEAR_OF_JAN1 = {"Sunday": 2017, "Monday": 2007, "Tuesday": 2013, "Wednesday": 2014, "Thursday": 2015, "Friday": 2010, "Saturday": 2011}


def _g(o, k):
    v = o["fields"].get(k)
    return None if V.is_blank(v) else str(v).strip()


def _int(s):
    try:
        return int(float(s))
    except (TypeError, ValueError):
        return None


def _yes(s, default):
    return default if s is None else s.strip().lower() == "yes"


def actual_year(bm, bd, by, start_weekday):
    """(year, how): the year that EnergyPlus simulates. `by` given -> by; blank -> the year of YEAR_OF_JAN1 that fits the start date and the start weekday (None when it cannot be resolved)."""
    if by:
        return by, "given"
    try:
        doy = datetime.date(2001, bm, bd).timetuple().tm_yday          # 2001: not a leap year, 29 February does not exist
        wd = WEEKDAYS.index(start_weekday)
    except (TypeError, ValueError):
        return None, "not resolved"
    jan1 = WEEKDAYS[(wd - (doy - 1)) % 7]
    return YEAR_OF_JAN1[jan1], "chosen by EnergyPlus 23.1 from the start weekday"


def effective(flat):
    rps = [o for o in flat.objects if o["cls"].lower() == "runperiod"]
    if not rps:
        return None
    o = rps[0]
    bm, bd, by = _int(_g(o, "begin_month")), _int(_g(o, "begin_day_of_month")), _int(_g(o, "begin_year"))
    em, ed, ey = _int(_g(o, "end_month")), _int(_g(o, "end_day_of_month")), _int(_g(o, "end_year"))
    dow = _g(o, "day_of_week_for_start_day")
    if by:
        try:
            wd = datetime.date(by, bm, bd).strftime("%A")
        except (TypeError, ValueError):
            wd = dow
        start_wd, year_text = wd, str(by)
    else:
        start_wd, year_text = (dow.capitalize() if dow else "Sunday"), "blank (chosen from the start weekday)"
    year, how = actual_year(bm, bd, by, start_wd)
    hours = None
    if year:
        try:
            hours = ((datetime.date(year, em, ed) - datetime.date(year, bm, bd)).days + 1) * 24
            if hours <= 0:
                hours = None
        except (TypeError, ValueError):
            hours = None
    sd = [x for x in flat.objects if x["cls"].lower() == "runperiodcontrol:specialdays"]
    dst = [x for x in flat.objects if x["cls"].lower() == "runperiodcontrol:daylightsavingtime"]
    return dict(period="%s/%s to %s/%s" % (bm, bd, em, ed), begin_month=bm, begin_day=bd, begin_year=by, end_year=ey, year=year_text, start_weekday=start_wd,
                actual_year=year, actual_year_how=how, leap_year=_cal.isleap(year) if year else None, hours=hours,
                weather_file_holidays=_yes(_g(o, "use_weather_file_holidays_and_special_days"), True), weather_file_daylight_saving=_yes(_g(o, "use_weather_file_daylight_saving_period"), True),
                weekend_holiday_rule=_yes(_g(o, "apply_weekend_holiday_rule"), False), special_days_objects=len(sd), daylight_saving_objects=len(dst), run_periods=len(rps))


def required_year_check(cal, run_year):
    """Does the reference / the candidate simulate the run year that the case requires? (None for a file without a RunPeriod)"""
    try:
        ry = int(run_year)
    except (TypeError, ValueError):
        return None
    out = dict(run_year=ry)
    for who in ("reference", "candidate"):
        e = (cal or {}).get(who)
        if not e or not e.get("actual_year"):
            out[who] = dict(actual_year=None, uses_run_year=None, same_calendar_as_run_year=None)
            continue
        try:
            wd = datetime.date(ry, e["begin_month"], e["begin_day"]).strftime("%A")
            same_cal = (wd == e["start_weekday"]) and (_cal.isleap(ry) == e["leap_year"])
        except (TypeError, ValueError):
            same_cal = None
        out[who] = dict(actual_year=e["actual_year"], uses_run_year=e["actual_year"] == ry, same_calendar_as_run_year=same_cal)
    return out


def calendar_check(fr, fc):
    r, c = effective(fr), effective(fc)
    if r is None or c is None:
        return dict(status="unknown", reference=r, candidate=c, differences=[], notes=["a file has no RunPeriod object: the calendar cannot be compared"])
    diff, notes = [], []
    if r["period"] != c["period"]:
        diff.append("run period: reference %s, candidate %s" % (r["period"], c["period"]))
    if r["start_weekday"] != c["start_weekday"]:
        diff.append("weekday of the start day: reference %s, candidate %s (the weekday and weekend schedules fall on other days)" % (r["start_weekday"], c["start_weekday"]))
    if r["leap_year"] is not None and c["leap_year"] is not None and r["leap_year"] != c["leap_year"]:
        diff.append("leap year: reference %s (%s), candidate %s (%s)" % ("yes" if r["leap_year"] else "no", r["actual_year"], "yes" if c["leap_year"] else "no", c["actual_year"]))
    if r["end_year"] != c["end_year"] and (r["end_year"] or c["end_year"]):
        notes.append("end year: reference %s, candidate %s" % (r["end_year"] or "blank", c["end_year"] or "blank"))
    for k, label in (("weather_file_holidays", "use of the weather file holidays"), ("weather_file_daylight_saving", "use of the weather file daylight saving period"), ("weekend_holiday_rule", "apply weekend holiday rule")):
        if r[k] != c[k]:
            diff.append("%s: reference %s, candidate %s" % (label, "yes" if r[k] else "no", "yes" if c[k] else "no"))
    if r["actual_year"] != c["actual_year"]:
        aligned = r["start_weekday"] == c["start_weekday"] and r["leap_year"] == c["leap_year"]          # another year number with the same weekday alignment and length is only a note
        (notes if aligned else diff).append("actual year: reference %s, candidate %s%s" % (r["actual_year"], c["actual_year"], " (the same weekday alignment and length)" if aligned else ""))
    if r["hours"] != c["hours"] and r["hours"] and c["hours"]:
        diff.append("hours simulated: reference %d, candidate %d" % (r["hours"], c["hours"]))
    if r["special_days_objects"] != c["special_days_objects"] or r["daylight_saving_objects"] != c["daylight_saving_objects"]:
        notes.append("RunPeriodControl objects: reference %d SpecialDays / %d DaylightSavingTime, candidate %d / %d (holidays and a daylight saving period that one file adds)" %
                     (r["special_days_objects"], r["daylight_saving_objects"], c["special_days_objects"], c["daylight_saving_objects"]))
    if r["run_periods"] != c["run_periods"]:
        notes.append("number of RunPeriod objects: reference %d, candidate %d (the first of each is compared)" % (r["run_periods"], c["run_periods"]))
    return dict(status="differs" if diff else "same", reference=r, candidate=c, differences=diff, notes=notes)
