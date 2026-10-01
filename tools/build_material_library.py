"""
Build a small material library (CSV) from the game's own items: typical values for rubber,
polymer, coated metal and bare metal, measured from vanilla textures and materials.

In Tarkov one SMap material usually covers a whole item (the RK-1's polymer grip and steel mount
share one material), so the difference between plastic and metal lives in the TEXTURES:
the diffuse colour, the specular mask (diffuse alpha) and the gloss map. This script looks at
every pixel of every vanilla SMap material under a folder, sorts the pixels into material classes
by their specular value, and reports per class:

  - target texture values (median and typical range of diffuse brightness, specular, gloss), to
    compare with your converted textures and to set the converter's sliders;
  - the material slider values (Main Color, Specularness, ...) most used by items that are mostly
    that class, with example items.

    python build_material_library.py "<game>/EscapeFromTarkov_Data/StreamingAssets/Windows/assets/content/items/mods" material_library.csv

The class limits (specular 0-255) are a heuristic, set from the RK-1 (polymer ~22-27, its
steel ~77); change CLASSES below if a class looks wrong. Needs Python 3 and UnityPy.
"""

import argparse
import csv
import os
import sys
from collections import Counter, defaultdict

import UnityPy

SMAP = 6014991791773097075

# (name, lowest specular, highest specular), specular = diffuse texture alpha, 0-255
CLASSES = [
    ("rubber / matte", 0, 14),
    ("polymer / plastic", 15, 44),
    ("coated metal (anodized, painted, parkerized)", 45, 109),
    ("bare / polished metal", 110, 255),
]
DOMINANT = 0.6  # an item counts as "mostly X" when this share of its pixels is X
SIZE = 256      # textures are shrunk to this before measuring


def classify(spec):
    for i, (_, lo, hi) in enumerate(CLASSES):
        if lo <= spec <= hi:
            return i
    return len(CLASSES) - 1


def color(c):
    return " ".join(str(round(c[k] * 255)) for k in "rgba")


def vec(c):
    return " ".join(f"{round(c[k], 3):g}" for k in "rgba")


def percentile(hist, p):
    total = sum(hist)
    if not total:
        return ""
    acc = 0
    for v, n in enumerate(hist):
        acc += n
        if acc >= total * p:
            return v
    return 255


def materials(path):
    """Yield (item name, slider values, diffuse image, gloss image) for each SMap material."""
    env = UnityPy.load(path)
    objs = {o.path_id: o for o in env.objects}
    for o in objs.values():
        if o.type.name != "Material":
            continue
        m = o.read_typetree()
        if m["m_Shader"]["m_PathID"] != SMAP or m["m_Shader"]["m_FileID"] == 0:
            continue
        props = m["m_SavedProperties"]
        tex = {k: v["m_Texture"] for k, v in props["m_TexEnvs"]}
        imgs = []
        for key in ("_MainTex", "_SpecMap"):
            ref = tex.get(key)
            if not ref or ref["m_FileID"] != 0 or ref["m_PathID"] not in objs:
                break
            img = objs[ref["m_PathID"]].read().image.convert("RGBA")
            img.thumbnail((SIZE, SIZE))
            imgs.append(img)
        if len(imgs) != 2:
            continue
        colors, floats = dict(props["m_Colors"]), dict(props["m_Floats"])
        cube = tex.get("_Cube")
        cube_name = ""
        if cube and cube["m_PathID"]:
            if cube["m_FileID"] == 0 and cube["m_PathID"] in objs:
                cube_name = objs[cube["m_PathID"]].read_typetree()["m_Name"]
            else:
                cube_name = f"{o.assets_file.externals[cube['m_FileID'] - 1].path.split('/')[-1]}:{cube['m_PathID']}"
        sliders = {
            "Main Color": color(colors.get("_Color", {"r": 1, "g": 1, "b": 1, "a": 1})),
            "Specular Color": color(colors["_SpecColor"]) if "_SpecColor" in colors else "",
            '"Specularness" (Inspector)': round(floats.get("_Glossness", 0), 2),
            '"Glossness" (Inspector)': round(floats.get("_Specularness", 0), 2),
            "Reflection Color": color(colors["_ReflectColor"]) if "_ReflectColor" in colors else "",
            "Specular Vals": vec(colors["_SpecVals"]) if "_SpecVals" in colors else "",
            "Diffuse Vals": vec(colors["_DefVals"]) if "_DefVals" in colors else "",
            "Cubemap": cube_name,
        }
        yield os.path.basename(path).replace(".bundle", ""), sliders, imgs[0], imgs[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="game folder to search for .bundle files (recursively), or one bundle")
    ap.add_argument("out", help="CSV file to write")
    args = ap.parse_args()

    if os.path.isfile(args.folder):
        bundles = [args.folder]
    else:
        bundles = sorted(os.path.join(d, f) for d, _, fs in os.walk(args.folder) for f in fs if f.endswith(".bundle"))

    n = len(CLASSES)
    hist = {k: [[0] * 256 for _ in range(n)] for k in ("diffuse", "spec", "gloss")}
    pixels = [0] * n
    items = [set() for _ in range(n)]
    dominant_sliders = [defaultdict(Counter) for _ in range(n)]
    dominant_items = [[] for _ in range(n)]
    measured = 0

    for i, b in enumerate(bundles, 1):
        print(f"[{i}/{len(bundles)}] {os.path.basename(b)}", file=sys.stderr)
        try:
            for item, sliders, diffuse, gloss in materials(b):
                if gloss.size != diffuse.size:
                    gloss = gloss.resize(diffuse.size)
                measured += 1
                counts = [0] * n
                for (r, g, bl, a), gl in zip(diffuse.getdata(), gloss.getdata()):
                    c = classify(a)
                    counts[c] += 1
                    hist["diffuse"][c][(r + g + bl) // 3] += 1
                    hist["spec"][c][a] += 1
                    hist["gloss"][c][gl[0]] += 1
                total = sum(counts)
                for c in range(n):
                    pixels[c] += counts[c]
                    if counts[c] > total * 0.05:
                        items[c].add(item)
                    if counts[c] >= total * DOMINANT:
                        dominant_items[c].append(item)
                        for k, v in sliders.items():
                            dominant_sliders[c][k][v] += 1
        except Exception as e:
            print(f"  skipped: {e}", file=sys.stderr)

    rows = []
    for c, (name, lo, hi) in enumerate(CLASSES):
        row = {"material class": name, "specular range used to sort": f"{lo}-{hi}",
               "items containing it": len(items[c]), "items mostly this": len(dominant_items[c])}
        for k, label in (("diffuse", "diffuse brightness"), ("spec", "specular (diffuse alpha)"), ("gloss", "gloss")):
            h = hist[k][c]
            row[f"{label} median"] = percentile(h, 0.5)
            row[f"{label} typical range"] = f"{percentile(h, 0.25)}-{percentile(h, 0.75)}" if sum(h) else ""
        for k, counter in dominant_sliders[c].items():
            value, count = counter.most_common(1)[0]
            row[f"{k} (most used)"] = f"{value}  ({count}/{len(dominant_items[c])})"
        row["example items"] = "; ".join(dominant_items[c][:5] or sorted(items[c])[:5])
        rows.append(row)

    cols = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"Measured {measured} SMap materials from {len(bundles)} bundles -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
