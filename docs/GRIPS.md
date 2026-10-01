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
0, 0, 0). The first positions (0.176, -0.023, 0.003 and 0.139, 0.038, -0.100) put the hand past
the end of the grip in game; they were moved 3.5 cm back along the grip axis (0.939, 0.343, 0).
Current values, **not yet confirmed in game**:

| Object | Position | Rotation |
|---|---|---|
| `Base HumanLPalm` (Alternative) | 0.143, -0.035, 0.003 | 51.9, 268.0, 250.2 |
| `Base HumanLPalm 1` (Common) | 0.106, 0.026, -0.100 | 12.3, 242.7, 157.7 |

If that overshoots, the halfway values are 0.157, -0.030, 0.003 and 0.120, 0.031, -0.100.

**PreviewPivot:** Apply Default Settings (pivot centred correctly in the inspect view, confirmed),
then Icon → Rotation **0, 245, 180** (vanilla RK-1's value; the SDK default 0, 245, 0 renders the
icon upside down/end-on). Bounds Scale 0.9.

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

8. PreviewPivot added → inspect view centred (confirmed) and icon renders, but the icon faced the
   wrong way → Icon Rotation set to vanilla's 0, 245, 180.
9. Hand in the side-grip pose but too far out past the grip end → palms moved 3.5 cm toward the gun.
10. Grip texture looks grainy/concrete-like. Same in MW3 itself, so it's the source texture.
    Options: re-rip with high-res/streamed images, lower Normal intensity (~0.5), lower
    "Specularness" (~1.5).

**Open:** confirm the moved hand poses and the icon rotation in game. Optional: convert the COD
textures for SMap (diffuse alpha is a flat specular mask right now, so the gloss detail isn't used).
