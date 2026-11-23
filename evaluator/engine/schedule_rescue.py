"""schedule_rescue.py - the 8,760-hour comparison of the schedules is the FINAL one (user decision 2026-11-21).

  rescue(cand_text, ref_text, rows)   -> (new candidate text, number of schedules replaced)

A schedule pair that the comparison by day type finds different is expanded to the hourly series of the whole run period (schedule_8760.py). When the two series are the SAME, the pair counts as the same schedule: all
the keys of that schedule are the same, and so are the keys that depend on it (the loads that name it, the objects that refer to it). To let the whole comparison (pairing, key score, Object KVOR, schedule KVOR) see
this, the candidate schedule of such a pair is replaced, for a second run of the engine, by a copy of the reference schedule under the NAME OF THE CANDIDATE: the two are then equal in every field and in every
consequence. Nothing else of the candidate changes, and the file of the user is not touched (the second run reads a copy). When the series are different, nothing is replaced: the result by day type (clause by clause)
stands. Since 2026-11-22 (user decision) it can also take keys away, but only for a pair that the day types find the same and that was expanded because the calendar of the two files differs: when more than 1 % of the hours of the year differ, the candidate schedule is replaced by `demote` with a one-value schedule (nothing of the reference matches it), so that all its documentary keys and the keys that depend on it are lost.

`rows` are the rows of `hourly_8760` (`reference`, `candidate`, `same`).
"""
import idf_flatten


def _text(objs):
    return "".join("%s,\n  %s;\n\n" % (c, ",\n  ".join(f)) for c, f in objs)


def rescue(cand_text, ref_text, rows):
    same = {(r["reference"].strip().lower(), r["candidate"].strip().lower()) for r in rows if r.get("same")}
    if not same:
        return cand_text, 0
    ref = {f[0].strip().lower(): (c, f) for c, f in idf_flatten.parse_idf(ref_text) if f and c.lower().startswith("schedule:")}
    out, n = [], 0
    by_cand = {cn: rn for rn, cn in same}
    for c, f in idf_flatten.parse_idf(cand_text):
        key = f[0].strip().lower() if f else None
        if c.lower().startswith("schedule:") and key in by_cand and by_cand[key] in ref:
            rc, rf = ref[by_cand[key]]
            out.append((rc, [f[0]] + rf[1:]))
            n += 1
        else:
            out.append((c, f))
    return _text(out), n


DEMOTED_VALUE = "987654.321"          # a value that no schedule of a benchmark case has


def demote(cand_text, names):
    """The candidate schedules (names, lower case) that the 8,760 hours find DIFFERENT although the day types are the same: each is replaced by a constant Schedule:Compact of the same name and type limits."""
    names = {n.strip().lower() for n in names}
    if not names:
        return cand_text, 0
    out, n = [], 0
    for c, f in idf_flatten.parse_idf(cand_text):
        key = f[0].strip().lower() if f else None
        if c.lower().startswith("schedule:") and key in names:
            out.append(("Schedule:Compact", [f[0], f[1] if c.lower() == "schedule:compact" and len(f) > 1 else "", "Through: 12/31", "For: AllDays", "Until: 24:00", DEMOTED_VALUE]))
            n += 1
        else:
            out.append((c, f))
    return _text(out), n
