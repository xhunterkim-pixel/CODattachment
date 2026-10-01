"""
Build a table of the game's own material values, to copy into Unity for a new attachment.

Reads every .bundle under a folder of the game and writes one row per material: shader, Main
Color, Specular Color, "Specularness", "Glossness", Reflection Color, Specular Vals, Diffuse Vals,
Stencil, and which textures/cubemap it uses. Colours are written as the Unity colour picker shows
them (0-255, alpha last), floats as the Inspector shows them.

    python dump_material_values.py "<game>/EscapeFromTarkov_Data/StreamingAssets/Windows/assets/content/items/mods/foregrips" foregrips.csv
    python dump_material_values.py <folder> out.csv --textures

--textures also measures the average of each material's textures (diffuse RGB, specular = diffuse
alpha, gloss), so you can compare your converted textures with Tarkov's. Slower.

Open the CSV in Excel/LibreOffice/Google Sheets, sort by shader or filter by name (e.g. "polymer",
"metal", "rubber"), and copy the values of a vanilla item made of the same stuff.

Needs Python 3 and UnityPy (pip install UnityPy).
"""

import argparse
import csv
import json
import os
import sys

import UnityPy
from PIL import ImageStat

SMAP = 6014991791773097075  # p0/Reflective/Bumped Specular SMap in the game's shaders bundle
SHADER_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_shaders.json")

COLORS = [("_Color", "main_color"), ("_SpecColor", "spec_color"), ("_ReflectColor", "reflect_color"),
          ("_SpecVals", "spec_vals"), ("_DefVals", "diffuse_vals")]
# The SDK Inspector's labels for these two are swapped: "Specularness" edits _Glossness and the
# other way round. Columns are named after the Inspector labels.
FLOATS = [("_Glossness", "inspector_Specularness"), ("_Specularness", "inspector_Glossness"),
          ("_StencilType", "stencil")]
TEXTURES = [("_MainTex", "diffuse_tex"), ("_SpecMap", "gloss_tex"), ("_BumpMap", "normal_tex"), ("_Cube", "cubemap")]


def shader_names():
    names = {SMAP: "p0/Reflective/Bumped Specular SMap"}
    if os.path.exists(SHADER_CACHE):  # written by fix_eft_shaders.py --game-shaders
        with open(SHADER_CACHE) as f:
            for name, (_, pid) in json.load(f).items():
                names[pid] = name
    return names


def fmt_color(c, is_color):
    vals = [c["r"], c["g"], c["b"], c["a"]]
    if is_color:
        return " ".join(str(round(v * 255)) for v in vals)
    return " ".join(f"{v:g}" for v in (round(v, 3) for v in vals))


def texture_stats(obj, kind):
    try:
        img = obj.read().image.convert("RGBA")
    except Exception as e:  # unsupported format etc.
        return {f"{kind}_avg": f"error: {e}"}
    img.thumbnail((256, 256))
    avg = [round(v) for v in ImageStat.Stat(img).mean]
    if kind == "diffuse":
        return {"diffuse_avg_rgb": " ".join(map(str, avg[:3])), "spec_avg (diffuse alpha)": avg[3]}
    if kind == "gloss":
        return {"gloss_avg": avg[0]}
    return {}


def dump(path, names, measure):
    env = UnityPy.load(path)
    objs = {o.path_id: o for o in env.objects}
    rows = []
    for pid, o in objs.items():
        if o.type.name != "Material":
            continue
        sf = o.assets_file
        m = o.read_typetree()
        props = m["m_SavedProperties"]
        shader_pid = m["m_Shader"]["m_PathID"]
        if m["m_Shader"]["m_FileID"] == 0 and shader_pid in objs:
            shader = objs[shader_pid].read_typetree()["m_ParsedForm"]["m_Name"] + " (built in)"
        else:
            shader = names.get(shader_pid, f"unknown {shader_pid}")
        row = {"bundle": os.path.basename(path), "material": m["m_Name"], "shader": shader}
        colors, floats = dict(props["m_Colors"]), dict(props["m_Floats"])
        for key, col in COLORS:
            if key in colors:
                row[col] = fmt_color(colors[key], key in ("_Color", "_SpecColor", "_ReflectColor"))
        for key, col in FLOATS:
            if key in floats:
                row[col] = round(floats[key], 3)
        for key, col in TEXTURES:
            ref = dict(props["m_TexEnvs"]).get(key, {}).get("m_Texture")
            if not ref or not ref["m_PathID"]:
                continue
            if ref["m_FileID"] == 0 and ref["m_PathID"] in objs:
                tex = objs[ref["m_PathID"]]
                row[col] = tex.read_typetree()["m_Name"]
                if measure and key in ("_MainTex", "_SpecMap"):
                    row.update(texture_stats(tex, "diffuse" if key == "_MainTex" else "gloss"))
            else:
                ext = sf.externals[ref["m_FileID"] - 1].path.split("/")[-1]
                row[col] = f"{ext}:{ref['m_PathID']}"
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="folder to search for .bundle files (searched recursively), or one bundle")
    ap.add_argument("out", help="CSV file to write")
    ap.add_argument("--textures", action="store_true", help="also measure average diffuse/spec/gloss")
    args = ap.parse_args()

    if os.path.isfile(args.folder):
        bundles = [args.folder]
    else:
        bundles = sorted(os.path.join(d, f) for d, _, fs in os.walk(args.folder) for f in fs if f.endswith(".bundle"))
    if not bundles:
        sys.exit(f"No .bundle files under {args.folder}")

    names = shader_names()
    rows = []
    for i, b in enumerate(bundles, 1):
        print(f"[{i}/{len(bundles)}] {os.path.basename(b)}", file=sys.stderr)
        try:
            rows += dump(b, names, args.textures)
        except Exception as e:
            print(f"  skipped: {e}", file=sys.stderr)

    cols = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    smap = sum("SMap" in r["shader"] for r in rows)
    print(f"Wrote {len(rows)} materials ({smap} SMap) from {len(bundles)} bundles to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
