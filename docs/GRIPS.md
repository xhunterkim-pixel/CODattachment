# Grips

Per-grip record: what each one is based on, the values that worked, and anything still open.
Add a section for every new grip.

## Hound 9G Side Grip

| | |
|---|---|
| Item ID | `6abe08f14fea21b38607a868` |
| Cloned from | Zenit RK-1 tactical foregrip on B-25U mount, `5c1cd46f2e22164bef5cfedb` (vanilla bundle `foregrip_all_zenit_b25u_rk_1.bundle`) |
| Bundle | `assets/content/items/mods/foregrips/houndgrip.bundle`, dependency `shaders` |
| Source | Call of Duty: Modern Warfare II (2022), ported via Blender → FBX |
| Unity prefab | `Assets/Content/Weapons/Tarkov Double Sidegrip/houndgrip/houndgrip.prefab` |

**Prefab:** root `houndgrip` (rotation 0, scale 1) with children `grip` and `rail`,
Rotation **0, 0, 0**, Scale 100. The imported -90 left the grip running back along the gun
instead of out to the side like the RK-1. At 0, 0, 0 it lies in the same plane as the RK-1,
about 23° shallower.

**Materials** (both `p0/Reflective/Bumped Specular SMap`):

| | `houndgrip_grip` (polymer) | `houndgrip_rail` (metal) |
|---|---|---|
| Main Color | 193, 193, 193 | 193, 193, 193 |
| Specular Color | 217, 217, 217 | 217, 217, 217 |
| "Specularness" | 2 | 2 |
| "Glossness" | 0.6 | 1.08 |
| Reflection Color | 80, 80, 80, alpha 128 | 154, 154, 154, alpha 128 |
| Reflection Cubemap | `dots small` | `patron_cubemap_metall` |
| Spec / Diffuse Vals | 1, 0.5, 0, 0 | 1, 0.5, 0, 0 |

**Hand poses** (from `unity/AddSideGripHandPoses.cs`, then moved to fit the grip at rotation
0, 0, 0; computed from the meshes, not yet confirmed in game):

| Object | Position | Rotation |
|---|---|---|
| `Base HumanLPalm` (Alternative) | 0.176, -0.023, 0.003 | 51.9, 268.0, 250.2 |
| `Base HumanLPalm 1` (Common) | 0.139, 0.038, -0.100 | 12.3, 242.7, 157.7 |

**SDK fix needed for this project:** PathID Replacer entry `3868700100545724512 → 6014991791773097075`
(SMap), because this project's SMap builds with a different PathID than the SDK's table expects.

**History of what went wrong**, in order:

1. Cloned the wrong vanilla item (ID guessed from memory) → wrong stats and normal-grip
   animation. Fixed with the real ID from the handbook.
2. Doge box → `bundles.json` lacked the `shaders` dependency.
3. Purple → shader pointed at the SDK's `shaders` bundle; the replacer had crashed (absolute
   output path), then skipped SMap (PathID not in its table).
4. White → shader built into the bundle; no reflection cubemap.
5. Fixed by pointing SMap at the game's shader (now done by the SDK via the table entry above).
6. Off-centre inspect, spinning icon → no PreviewPivot.
7. Default hand grip → no GripPose hand poses; then hand held it oddly because the mesh
   orientation differed from the RK-1.

**Open:** confirm in game that the hand poses above sit right, and that the icon renders with
PreviewPivot. Optional: convert the COD textures for SMap (diffuse alpha is a flat specular mask
right now, so the gloss detail isn't used).
