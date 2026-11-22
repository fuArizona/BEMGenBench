"""schedule_rescue.py - the 8,760-hour comparison of the schedules is the FINAL one (user decision 2026-11-21).

  rescue(cand_text, ref_text, rows)   -> (new candidate text, number of schedules replaced)

A schedule pair that the comparison by day type finds different is expanded to the hourly series of the whole run period (schedule_8760.py). When the two series are the SAME, the pair counts as the same schedule: all
the keys of that schedule are the same, and so are the keys that depend on it (the loads that name it, the objects that refer to it). To let the whole comparison (pairing, key score, Object KVOR, schedule KVOR) see
this, the candidate schedule of such a pair is replaced, for a second run of the engine, by a copy of the reference schedule under the NAME OF THE CANDIDATE: the two are then equal in every field and in every
consequence. Nothing else of the candidate changes, and the file of the user is not touched (the second run reads a copy). When the series are different, nothing is replaced: the result by day type (clause by clause)
stands, so that the 8,760-hour comparison can only give keys back, never take them away.

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
