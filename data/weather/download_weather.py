#!/usr/bin/env python3
"""Downloads the EPW weather files of the cases (the repository holds the links, not the files).

  python data/weather/download_weather.py                 download every file of weather_files.csv into data/weather/
  python data/weather/download_weather.py --only USA_NY_Buffalo.Niagara.Intl.AP.725280_TMY3.epw
  python data/weather/download_weather.py --out some/folder
  python data/weather/download_weather.py --check         only check the files that are already there

Each file is downloaded as a zip from the link, the .epw (column zip_member) is taken out of it, saved under the name of column file, and its SHA-256 is compared with the value in weather_files.csv.
A file that is already there with the right checksum is not downloaded again. A checksum that does not match is reported and the file is not kept
(use --keep-mismatch to keep it: the weather data of the provider may have been updated, and a case then simulates with other data).
Only the Python standard library is used.
"""
import argparse
import csv
import hashlib
import io
import os
import sys
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--only")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--keep-mismatch", action="store_true")
    a = ap.parse_args(argv)
    rows = list(csv.DictReader(open(os.path.join(HERE, "weather_files.csv"), encoding="utf8")))
    if a.only:
        rows = [r for r in rows if r["file"] == a.only]
        if not rows:
            print("ERROR: %s is not in weather_files.csv" % a.only)
            return 3
    os.makedirs(a.out, exist_ok=True)
    bad = 0
    for r in rows:
        dst = os.path.join(a.out, r["file"])
        if os.path.isfile(dst) and sha256_file(dst) == r["sha256"]:
            print("ok        %s (already there)" % r["file"])
            continue
        if a.check:
            print("MISSING or CHANGED  %s" % r["file"])
            bad += 1
            continue
        print("download  %s" % r["file"])
        try:
            with urllib.request.urlopen(urllib.request.Request(r["url"], headers={"User-Agent": "BEMGenBench-weather-download"}), timeout=120) as resp:
                data = resp.read()
            z = zipfile.ZipFile(io.BytesIO(data))
            want = r.get("zip_member") or r["file"]
            member = next((n for n in z.namelist() if os.path.basename(n) == want), None)
            if member is None:
                raise RuntimeError("the zip has no member %s (members: %s)" % (want, ", ".join(z.namelist())))
            epw = z.read(member)
        except Exception as e:  # noqa: BLE001
            print("FAILED    %s: %s" % (r["file"], e))
            bad += 1
            continue
        if sha256_bytes(epw) != r["sha256"]:
            print("CHECKSUM DIFFERS  %s: expected %s, got %s" % (r["file"], r["sha256"][:12], sha256_bytes(epw)[:12]))
            bad += 1
            if not a.keep_mismatch:
                continue
        open(dst, "wb").write(epw)
    print("%d of %d files need attention" % (bad, len(rows)) if bad else "all %d files are in place" % len(rows))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
