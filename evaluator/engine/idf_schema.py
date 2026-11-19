"""idf_schema.py - the epJSON schema of an EnergyPlus installation: for each class the ordered fields, the extensible group, whether the class is unique and whether it has a name.

Origin: copied on 2026-10-15 from `gbxml2idf/scripts/idf_writer.py` (functions `energyplus_root`, class `Schema`), reduced to what a comparison needs and kept INDEPENDENT of that skill on purpose
(idf_compare must work in other projects). Later changes of the original are not followed automatically.

  Schema(path=None, root=None)   reads <root>/Energy+.schema.epJSON; the root is searched in this order: the argument, the environment variable ENERGYPLUS_DIR (or ENERGYPLUS), `energyplus` on the PATH,
                                 the usual install folders (standard_install_globs)
  .canonical(cls)                the class name written as in the schema (case-insensitive lookup) or SchemaError
  .info(cls)                     dict(cls, fields (ordered schema keys), ext (the extensible group key or None), ext_fields, named, unique, group, props (field -> schema property, also the fields of the items of an extensible group))
  .version                       the schema version, e.g. "23.1.0"
"""
import json
import os
import shutil

DEFAULT_ROOTS = []

def standard_install_globs():
    """The usual install folders of EnergyPlus, built from the operating system (no machine path): <system drive>\\EnergyPlusV*, /usr/local/EnergyPlus-*, /Applications/EnergyPlus-*."""
    out = ["/usr/local/EnergyPlus-*", "/Applications/EnergyPlus-*"]
    drive = os.environ.get("SystemDrive")
    if drive:
        out.insert(0, os.path.join(drive + os.sep, "EnergyPlusV*"))
    return out


class SchemaError(ValueError):
    pass


def energyplus_root(explicit=None):
    cands = []
    if explicit:
        cands.append(explicit)
    for v in ("ENERGYPLUS_DIR", "ENERGYPLUS"):
        if os.environ.get(v):
            cands.append(os.environ[v])
    w = shutil.which("energyplus")
    if w:
        cands.append(os.path.dirname(w))
    cands += DEFAULT_ROOTS
    import glob
    for g in standard_install_globs():
        cands += sorted(glob.glob(g), reverse=True)
    for c in cands:
        if os.path.isfile(os.path.join(c, "Energy+.schema.epJSON")):
            return c
    return None


def installed_roots():
    """every EnergyPlus installation that has a schema: the roots of energyplus_root() plus the usual install folders (standard_install_globs), newest version name last"""
    import glob
    out = []
    for r in [os.environ.get("ENERGYPLUS_DIR"), os.environ.get("ENERGYPLUS"), os.path.dirname(shutil.which("energyplus") or "")] + DEFAULT_ROOTS + [x for g in standard_install_globs() for x in sorted(glob.glob(g))]:
        if r and os.path.isfile(os.path.join(r, "Energy+.schema.epJSON")) and r not in out:
            out.append(r)
    return out


def root_for_version(mm):
    """the first installation whose schema is the version `mm` ("23.1"), or None (reads only the head of the schema file: the default of Version / version_identifier)"""
    import re
    for r in installed_roots():
        with open(os.path.join(r, "Energy+.schema.epJSON"), encoding="utf8") as f:
            head = f.read(4000)
        m = re.search(r'"version_identifier"\s*:\s*\{[^{}]*?"default"\s*:\s*"?(\d+)\.(\d+)', head)
        if m and "%s.%s" % m.groups() == mm:
            return r
    return None


_CACHE = {}


class Schema:
    def __init__(self, path=None, root=None):
        if path is None:
            r = energyplus_root(root)
            if r is None:
                raise SchemaError("Energy+.schema.epJSON not found: give --energyplus <installation folder>, set ENERGYPLUS_DIR or put energyplus on the PATH")
            path = os.path.join(r, "Energy+.schema.epJSON")
        self.path = path
        if path not in _CACHE:
            _CACHE[path] = json.load(open(path, encoding="utf8"))
        self.raw = _CACHE[path]
        self.classes = self.raw["properties"]
        self.version = self.raw.get("epJSON_schema_version")
        if not self.version:      # newer schemas (26.x) have no epJSON_schema_version: the default of Version / version_identifier
            try:
                d = self.classes["Version"]["patternProperties"][".*"]["properties"]["version_identifier"]["default"]
                self.version = str(d)
            except (KeyError, TypeError):
                self.version = None
        self._low = {k.lower(): k for k in self.classes}
        self._info = {}

    def canonical(self, cls):
        k = self._low.get(str(cls).strip().lower())
        if k is None:
            raise SchemaError("unknown class %r" % cls)
        return k

    def known(self, cls):
        return str(cls).strip().lower() in self._low

    def info(self, cls):
        cls = self.canonical(cls)
        if cls in self._info:
            return self._info[cls]
        b = self.classes[cls]
        li = b["legacy_idd"]
        inner = list(b["patternProperties"].values())[0]
        props = dict(inner["properties"])
        ext = li.get("extension")
        if ext and ext in props:                      # the properties of the items of an extensible group are reachable by their own field name
            props.update(props[ext].get("items", {}).get("properties", {}))
        d = dict(cls=cls, group=b.get("group", ""), fields=list(li["fields"]), ext=ext, ext_fields=list(li.get("extensibles") or []),
                 named=b.get("name") is not None, unique=(b.get("maxProperties") == 1), props=props)
        self._info[cls] = d
        return d
