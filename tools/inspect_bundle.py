"""
Print what's inside a Unity bundle: what it depends on, the prefab hierarchy with components,
materials (shader reference, textures, values), texture import settings and mesh positions.

Use it to compare a custom bundle with the vanilla item it should behave like:

    python inspect_bundle.py houndgrip.bundle
    python inspect_bundle.py foregrip_all_zenit_b25u_rk_1.bundle

Needs Python 3 and UnityPy (pip install UnityPy).
"""

import sys

import UnityPy

COLORS = ("_Color", "_SpecColor", "_ReflectColor", "_SpecVals", "_DefVals")
FLOATS = ("_Glossness", "_Specularness", "_StencilType")


def qrot(q, v):
    x, y, z, w = q
    ux = (x, y, z)
    dot = sum(a * b for a, b in zip(ux, v))
    cross = (y * v[2] - z * v[1], z * v[0] - x * v[2], x * v[1] - y * v[0])
    return tuple(2 * dot * u + (w * w - sum(a * a for a in ux)) * c + 2 * w * k for u, c, k in zip(ux, v, cross))


def r(values, n=3):
    return tuple(round(v, n) for v in values)


def main(path):
    env = UnityPy.load(path)
    objs = {o.path_id: o for o in env.objects}
    sf = next(iter(env.objects)).assets_file
    trees = {}

    def tree(pid):
        if pid not in trees:
            trees[pid] = objs[pid].read_typetree()
        return trees[pid]

    def ref_name(ref):
        if ref["m_FileID"] == 0:
            if ref["m_PathID"] not in objs:
                return f"missing local {ref['m_PathID']}"
            o = objs[ref["m_PathID"]]
            t = tree(ref["m_PathID"])
            name = t.get("m_Name") or t.get("m_ParsedForm", {}).get("m_Name", "")
            return f"{o.type.name} '{name}' (inside this bundle)"
        ext = sf.externals[ref["m_FileID"] - 1].path.split("/")[-1]
        return f"{ext} object {ref['m_PathID']}"

    print(f"== {path}  (Unity {sf.unity_version})")
    for o in env.objects:
        if o.type.name == "AssetBundle":
            ab = tree(o.path_id)
            print("bundle name:", ab["m_AssetBundleName"] or ab["m_Name"])
            print("depends on CABs:", ab["m_Dependencies"] or "none")
    print("external files:", [e.path.split("/")[-1] for e in sf.externals] or "none")

    print("\n-- hierarchy (local position / rotation quaternion / scale) --")
    transforms = {pid: tree(pid) for pid, o in objs.items() if o.type.name == "Transform"}

    def component_names(go):
        names = []
        for c in go["m_Component"]:
            o = objs.get(c["component"]["m_PathID"])
            if o is None or o.type.name == "Transform":
                continue
            if o.type.name == "MonoBehaviour":
                mb = tree(o.path_id)
                script = objs.get(mb["m_Script"]["m_PathID"])
                names.append(tree(script.path_id)["m_ClassName"] if script else "MonoBehaviour")
            else:
                names.append(o.type.name)
        return names

    def walk(pid, depth):
        t = transforms[pid]
        go = tree(t["m_GameObject"]["m_PathID"])
        if "Digit" not in go["m_Name"]:
            print(
                "  " * depth + go["m_Name"],
                "pos", r(t["m_LocalPosition"].values(), 4),
                "rot", r(t["m_LocalRotation"].values()),
                "scale", r(t["m_LocalScale"].values()),
                component_names(go),
            )
        for child in t["m_Children"]:
            walk(child["m_PathID"], depth + 1)

    for pid, t in transforms.items():
        if t["m_Father"]["m_PathID"] == 0:
            walk(pid, 0)

    for pid, o in objs.items():
        if o.type.name == "MonoBehaviour":
            mb = tree(pid)
            if "pivotPosition" in mb:
                print("PreviewPivot:", "pivotPosition", r(mb["pivotPosition"].values()),
                      "icon boundsScale", mb["Icon"]["boundsScale"])
            if "GripType" in mb:
                go = tree(mb["m_GameObject"]["m_PathID"])
                print(f"GripPose on '{go['m_Name']}': GripType {mb['GripType']} Hand {mb['Hand']}")

    print("\n-- materials --")
    for pid, o in objs.items():
        if o.type.name != "Material":
            continue
        m = tree(pid)
        props = m["m_SavedProperties"]
        print(f"{m['m_Name']}: shader = {ref_name(m['m_Shader'])}")
        for name, tex in props["m_TexEnvs"]:
            if tex["m_Texture"]["m_PathID"]:
                print(f"  {name}: {ref_name(tex['m_Texture'])}")
        floats = dict(props["m_Floats"])
        colors = dict(props["m_Colors"])
        print("  ", {k: round(floats[k], 3) for k in FLOATS if k in floats})
        print("  ", {k: r(colors[k].values()) for k in COLORS if k in colors})

    print("\n-- textures --")
    for pid, o in objs.items():
        if o.type.name == "Texture2D":
            t = tree(pid)
            s = t["m_TextureSettings"]
            print(f"{t['m_Name']}: {t['m_Width']}x{t['m_Height']} format {t['m_TextureFormat']} "
                  f"aniso {s['m_Aniso']} wrap {s['m_WrapU']} colorspace {t.get('m_ColorSpace')}")

    print("\n-- meshes, bounds in the prefab root's space --")
    for pid, o in objs.items():
        if o.type.name != "MeshFilter":
            continue
        mf = tree(pid)
        go = tree(mf["m_GameObject"]["m_PathID"])
        tr = next(tree(c["component"]["m_PathID"]) for c in go["m_Component"]
                  if objs[c["component"]["m_PathID"]].type.name == "Transform")
        aabb = tree(mf["m_Mesh"]["m_PathID"])["m_LocalAABB"]
        c, e = list(aabb["m_Center"].values()), list(aabb["m_Extent"].values())
        q, s, p = list(tr["m_LocalRotation"].values()), list(tr["m_LocalScale"].values()), list(tr["m_LocalPosition"].values())
        corners = []
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    v = [(c[i] + sg * e[i]) * s[i] for i, sg in enumerate((sx, sy, sz))]
                    corners.append([a + b for a, b in zip(p, qrot(q, v))])
        lo = [min(cc[i] for cc in corners) for i in range(3)]
        hi = [max(cc[i] for cc in corners) for i in range(3)]
        print(f"{go['m_Name']}: min {r(lo)} max {r(hi)} center {r([(a + b) / 2 for a, b in zip(lo, hi)])}")
        print(f"  normals agree with faces: {normals_agreement(objs[mf['m_Mesh']['m_PathID']])}")


def normals_agreement(mesh_obj):
    """Share of triangles whose stored normals face the same way as the triangle itself.
    Vanilla meshes are ~100%; ~0% means the normals are inverted (item lit inside-out)."""
    verts, normals, faces = [], [], []
    for line in mesh_obj.read().export().splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "v":
            verts.append([float(x) for x in parts[1:4]])
        elif parts[0] == "vn":
            normals.append([float(x) for x in parts[1:4]])
        elif parts[0] == "f":
            faces.append([[int(x) if x else 0 for x in corner.split("/")] for corner in parts[1:4]])
    if not normals or not faces:
        return "no normals"
    agree = total = 0
    for face in faces:
        a, b, c = (verts[corner[0] - 1] for corner in face)
        u = [b[i] - a[i] for i in range(3)]
        w = [c[i] - a[i] for i in range(3)]
        face_normal = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
        stored = [sum(normals[corner[2] - 1][i] for corner in face) for i in range(3)]
        total += 1
        agree += sum(f * n for f, n in zip(face_normal, stored)) > 0
    share = agree / total
    return f"{share:.0%}" + ("  <-- INVERTED: recalculate normals" if share < 0.5 else "")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for bundle in sys.argv[1:]:
        main(bundle)
        print()
