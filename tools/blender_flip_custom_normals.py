"""
Reverse a mesh's (custom split) normals in Blender without touching its faces.

Ported COD meshes came out with correct faces but every normal pointing inward (lit inside-out).
Unity's "Normals: Calculate" fixes the direction but throws away the original smoothing, so the
baked normal map no longer matches and shows artifacts. This keeps the original normals and only
reverses them.

Use: in Blender select the mesh object(s), open the Scripting tab, paste this, click Run Script,
then export the FBX again. In Unity set the FBX's Normals back to "Import".
Check: tools/inspect_bundle.py on the built bundle should report "normals agree with faces" ~100%.
"""

import bpy

for ob in bpy.context.selected_objects:
    if ob.type != 'MESH':
        continue
    mesh = ob.data
    if hasattr(mesh, "calc_normals_split"):      # Blender 4.0 and older
        mesh.calc_normals_split()
    if hasattr(mesh, "use_auto_smooth"):         # Blender 4.0 and older need this for custom normals
        mesh.use_auto_smooth = True
    flipped = [(-l.normal[0], -l.normal[1], -l.normal[2]) for l in mesh.loops]
    mesh.normals_split_custom_set(flipped)
    mesh.update()
    print(f"Reversed normals on {ob.name} ({len(flipped)} corners)")
