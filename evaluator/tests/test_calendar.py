#!/usr/bin/env python3
"""Tests of evaluator/engine/calendar_check.py (no EnergyPlus run): the actual year of a RunPeriod and the comparison of two calendars.
The years of the table were found by running EnergyPlus 23.1 (the Time table of the sql file).
python evaluator/tests/test_calendar.py (from the root of the repository)"""
import os
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import calendar_check as C  # noqa: E402

FAILS = []


def check(name, cond, info=""):
    print(("ok   " if cond else "FAIL ") + name + (("  " + str(info)) if (info and not cond) else ""))
    if not cond:
        FAILS.append(name)


def flat(**f):
    fields = dict(begin_month="1", begin_day_of_month="1", end_month="12", end_day_of_month="31")
    fields.update({k: v for k, v in f.items() if k not in ("special", "dst")})
    objs = [dict(cls="RunPeriod", fields=fields)] + [dict(cls="RunPeriodControl:SpecialDays", fields={}) for _ in range(f.get("special", 0))] + [dict(cls="RunPeriodControl:DaylightSavingTime", fields={}) for _ in range(f.get("dst", 0))]
    return SimpleNamespace(objects=objs)


# the year that EnergyPlus 23.1 chose for a blank year, by the start weekday (1 January)
for wd, yr in (("Sunday", 2017), ("Monday", 2007), ("Tuesday", 2013), ("Wednesday", 2014), ("Thursday", 2015), ("Friday", 2010), ("Saturday", 2011)):
    e = C.effective(flat(day_of_week_for_start_day=wd))
    check("blank year, start weekday %s -> %d (not a leap year, 8760 hours)" % (wd, yr), e["actual_year"] == yr and e["leap_year"] is False and e["hours"] == 8760, e)
check("blank year and blank weekday = Sunday -> 2017", C.effective(flat())["actual_year"] == 2017)
check("start 1 March, Sunday, blank year -> 2015 (1 March 2015 is a Sunday)", C.effective(flat(begin_month="3", day_of_week_for_start_day="Sunday"))["actual_year"] == 2015)
e = C.effective(flat(begin_year="2012", end_year="2012"))
check("a given year is the actual year; 2012 is a leap year with 8784 hours; the weekday follows the year", e["actual_year"] == 2012 and e["leap_year"] is True and e["hours"] == 8784 and e["start_weekday"] == "Sunday", e)
check("29 February without a year is not resolved", C.effective(flat(begin_month="2", begin_day_of_month="29", day_of_week_for_start_day="Sunday"))["actual_year"] is None)

same = C.calendar_check(flat(), flat())
check("two equal run periods are the same calendar", same["status"] == "same" and not same["differences"], same)
d = C.calendar_check(flat(day_of_week_for_start_day="Sunday"), flat(day_of_week_for_start_day="Friday"))
check("another start weekday differs and names both actual years", d["status"] == "differs" and any("actual year: reference 2017, candidate 2010" in x for x in d["differences"]), d)
y = C.calendar_check(flat(day_of_week_for_start_day="Sunday"), flat(begin_year="2023", end_year="2023"))
check("1 January 2023 and the blank year (2017) are both a Sunday, not a leap year: the same calendar, the other year number is a note", y["status"] == "same" and any("actual year" in x for x in y["notes"]), y)
l = C.calendar_check(flat(day_of_week_for_start_day="Sunday"), flat(begin_year="2012", end_year="2012"))
check("a leap year against a non-leap year differs", l["status"] == "differs" and any("leap year" in x for x in l["differences"]), l)
h = C.calendar_check(flat(), flat(use_weather_file_holidays_and_special_days="No"))
check("the weather file holidays switched off differs", h["status"] == "differs" and any("holidays" in x for x in h["differences"]), h)
n = C.calendar_check(flat(), flat(special=10))
check("SpecialDays objects of one file are a note, not a difference", n["status"] == "same" and any("SpecialDays" in x for x in n["notes"]), n)
u = C.calendar_check(SimpleNamespace(objects=[]), flat())
check("a file without a RunPeriod is unknown", u["status"] == "unknown", u)

# the run year that a case requires (run_year of case.yaml)
c1 = C.calendar_check(flat(day_of_week_for_start_day="Sunday"), flat(day_of_week_for_start_day="Friday"))
r1 = C.required_year_check(c1, "2017")
check("run year 2017: the reference (blank year, Sunday) uses it, the candidate (Friday = 2010) does not and has another calendar",
      r1["reference"]["uses_run_year"] is True and r1["candidate"]["actual_year"] == 2010 and r1["candidate"]["uses_run_year"] is False and r1["candidate"]["same_calendar_as_run_year"] is False, r1)
c2 = C.calendar_check(flat(begin_year="2017", end_year="2017"), flat(begin_year="2023", end_year="2023"))
r2 = C.required_year_check(c2, 2017)
check("a given year equal to the run year uses it; 2023 is another year number with the same calendar (Sunday, not a leap year)",
      r2["reference"]["uses_run_year"] is True and r2["candidate"]["uses_run_year"] is False and r2["candidate"]["same_calendar_as_run_year"] is True, r2)
r3 = C.required_year_check(C.calendar_check(flat(begin_year="2012", end_year="2012"), flat()), "2012")
check("run year 2012 (a leap year): a blank year (2017) is not the same calendar", r3["reference"]["uses_run_year"] is True and r3["candidate"]["same_calendar_as_run_year"] is False, r3)
check("a run year that is not a number gives None", C.required_year_check(c1, "abc") is None)
r4 = C.required_year_check(C.calendar_check(SimpleNamespace(objects=[]), flat()), 2017)
check("a file without a RunPeriod has no actual year", r4["reference"]["actual_year"] is None and r4["candidate"]["uses_run_year"] is True, r4)

print("\n%d failure(s)" % len(FAILS) if FAILS else "\nall tests passed")
sys.exit(1 if FAILS else 0)
