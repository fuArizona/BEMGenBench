"""schedule_kvor.py - the schedules counted as schedules, next to the key score (annotation: nothing here is part of the key score or of any other rate).

  schedule_kvor(P, res_doc)   P = the pairing (idf_pair), res_doc = the result of kvor_doc.kvor_doc

Why: the hourly values of a schedule are many keys (one per Until and value field), so a DOE case has most of its keys in a few schedules and the long schedules weigh most. The result has two parts:

  schedules, same, rate        STRICT (A1). One unit = one schedule of the reference that has a documentary basis (Schedule:Compact with at least one clause whose Until / value fields all have it, or another
                               Schedule:* object with a documentary key). A unit is the same when its partner in the candidate has the same hourly values on every day type Sunday ... Saturday in every
                               `Through:` period (design days, holidays and custom days are not compared, as in the key score). A unit without a partner counts 0.
  rate_hours                   PARTIAL (A2). The share of the hourly values (24 per day type and period) that are the same, averaged over the units.
  rate_days                    the share of the day types (24 equal hours) that are the same, averaged over the units.
  keys, keys_same              the keys that the key score counts in the classes Schedule:* (`per_class` of kvor_doc) and how many of them are the same; share_of_keys = keys / all keys.
  rate_without_schedules       the key score without those keys: (same - keys_same) / (keys - schedule keys).

With `hourly` (schedule_8760.Hourly) the pairs that the strict comparison finds different are also compared as 8,760-hour series made by EnergyPlus (`hourly_8760`: `same_after`, `schedules_same_8760`, `rate`, `rate_hours`); a unit that is the same is not expanded, EXCEPT when the calendar of the two files differs (`calendar_differs`: holidays, start weekday ...; user decision 2026-11-22): it is then expanded too, and it stays the same while at most `tolerance` (1 %) of the hours of the year differ; above that it is a different schedule (`demoted_by_calendar`, its keys are lost). The tolerance applies only to the pairs the day types find the same (the hours that differ lie outside their `For:` day types); a pair that differs by day type is still the same only when the 8,760 hours are all equal.

The partner of a schedule is the one that the pairing found (by name, by content, by the load that names it). When the pairing found none, the schedule that the paired load of the candidate names in the same field is
used (the load of the reference that names the schedule has a paired load in the candidate). A schedule with no partner counts 0 and is counted in `unpaired`.
Without a unit (the documents give no schedule) the rates are None, not 0.
"""
import collections

import idf_pair
import idf_sched
import kvor_doc

SCHED = ("schedule:compact", "schedule:constant")


def _documentary(o):
    if o["cls"].lower() == "schedule:compact":
        cl = idf_sched.compact_clauses(o["values"])
        return bool(cl) and any(kvor_doc._clause_doc(o, c) and [d for d in c["days"] if d in kvor_doc.DOC_DAYS] for c in cl)
    return any(kvor_doc._basis(o, k) == "doc" for k, _ in idf_pair.leaves(o))


def _score(pr, pc):
    """(strict 0 / 1, share of the hours, share of the day types) of the profile pr of the reference against the profile pc of the candidate."""
    if pr is None or pc is None:
        return 0, 0.0, 0.0
    strict = 1 if idf_sched.profiles_equal(pr, pc) else 0
    hours = hours_ok = days = days_ok = 0
    for p in pr:
        for d in kvor_doc.DOC_DAYS:
            h1 = p["days"].get(d)
            if h1 is None:
                continue
            h2 = idf_sched.hours_at(pc, p["end"], d)
            hours += 24
            days += 1
            n = sum(1 for u, w in zip(h1, h2) if abs(u - w) <= max(1e-6, 0.01 * max(abs(u), abs(w)))) if h2 else 0
            hours_ok += n
            days_ok += 1 if n == 24 else 0
    return strict, (hours_ok / hours if hours else 0.0), (days_ok / days if days else 0.0)


def schedule_kvor(P, res_doc, hourly=None, calendar_differs=False, tolerance=0.01):
    rs = {o["name"].lower(): o for o in P.ref if o["cls"].lower() in SCHED and o.get("name")}
    cs = {o["name"].lower(): o for o in P.cand if o["cls"].lower() in SCHED and o.get("name")}
    units = [n for n, o in rs.items() if _documentary(o)]
    partner = {}
    for n, o in rs.items():
        cu = P.pr.get(o["uid"])
        if cu is not None and P.cand[cu].get("name"):
            partner[n] = P.cand[cu]["name"].lower()
    votes = collections.defaultdict(collections.Counter)         # a schedule without a partner: the schedule that the paired load of the candidate names in the same field
    for r in P.ref:
        cu = P.pr.get(r["uid"])
        if r["cls"].lower() in SCHED or cu is None:
            continue
        cl = dict(idf_pair.leaves(P.cand[cu]))
        for k, v in idf_pair.leaves(r):
            if "schedule" in k and str(v).lower() in rs and cl.get(k) and str(cl[k]).lower() in cs:
                votes[str(v).lower()][str(cl[k]).lower()] += 1
    for n, vc in votes.items():
        partner.setdefault(n, vc.most_common(1)[0][0])
    a1 = a2h = a2d = 0.0
    unpaired = 0
    same_pairs = []                               # the pairs that are the same by day type (expanded only when the calendar of the two files differs)
    differ = []                                   # (unit, reference name, candidate name): the pairs that the comparison of the meaning finds different (they are expanded to 8,760 hours when asked)
    for n in units:
        pn = partner.get(n)
        if pn is None or pn not in cs:
            unpaired += 1
            continue
        s, h, d = _score(idf_sched.profile(rs[n]), idf_sched.profile(cs[pn]))
        a1 += s
        a2h += h
        a2d += d
        if not s:
            differ.append((rs[n]["name"], cs[pn]["name"]))
        else:
            same_pairs.append((rs[n]["name"], cs[pn]["name"]))
    k_all = sum(v[0] for v in res_doc["per_class"].values())
    k_sched = sum(v[0] for c, v in res_doc["per_class"].items() if c.lower().startswith("schedule:"))
    s_sched = sum(v[1] for c, v in res_doc["per_class"].items() if c.lower().startswith("schedule:"))
    n = len(units)
    r4 = lambda x: round(x, 4)
    hr = None
    if hourly is not None:
        hr = hourly.compare(P, differ, same_pairs if calendar_differs else (), tolerance)
        if hr["status"] == "done":
            # a unit that the comparison of the meaning finds the same counts 1 (it is not expanded); a unit it finds different counts what the 8,760 hours say; a unit without a partner counts 0
            # a pair that is the same by day type and was expanded because the calendar differs (trigger "calendar") counts 1 while the share of different hours is within the tolerance, else the share of equal hours
            cal = [r for r in hr["rows"] if r.get("trigger") == "calendar"]
            dt = [r for r in hr["rows"] if r.get("trigger") != "calendar"]
            same8 = int(a1) - len(cal) + sum(1 for r in cal if r["same"]) + sum(1 for r in dt if r["same"])
            share8 = int(a1) - len(cal) + sum(1.0 if r["same"] else r["share"] for r in cal) + sum(r["share"] for r in dt)
            hr.update(same_after=sum(1 for r in dt if r["same"]), demoted_by_calendar=sum(1 for r in cal if not r["same"]), schedules_same_8760=same8, rate=r4(same8 / n) if n else None, rate_hours=r4(share8 / n) if n else None)
    return dict(hourly_8760=hr, schedules=n, same=int(a1), rate=r4(a1 / n) if n else None, rate_hours=r4(a2h / n) if n else None, rate_days=r4(a2d / n) if n else None, unpaired=unpaired,
                keys=k_sched, keys_same=s_sched, share_of_keys=r4(k_sched / k_all) if k_all else None,
                rate_without_schedules=r4((res_doc["correct"] - s_sched) / (k_all - k_sched)) if k_all > k_sched else None,
                rule="strict: every day type Sunday ... Saturday of every period equal; partial: share of the hourly values / day types equal; a schedule without a partner counts 0; not in the key score")
