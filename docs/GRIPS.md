# Grips

Per-grip record: what each one is based on, the values that worked, and anything still open.
Add a section for every new grip.

## Hound 9G Side Grip

| | |
|---|---|
| Item ID | `6abe08f14fea21b38607a868` |
| Cloned from | Zenit RK-1 tactical foregrip on B-25U mount, `5c1cd46f2e22164bef5cfedb` (vanilla bundle `foregrip_all_zenit_b25u_rk_1.bundle`) |
| Bundle | `assets/content/items/mods/foregrips/houndgrip.bundle`, dependencies `shaders`, `cubemaps` |
| Source | Call of Duty: Modern Warfare III (2023), ported via Blender → FBX |
| Unity prefab | `Assets/Content/Weapons/Tarkov Double Sidegrip/houndgrip/houndgrip.prefab` |

**Prefab:** root `houndgrip` (rotation 0, scale 1) with children `grip` and `rail`,
Rotation **0, 0, 0**, Scale 100.

**FBX import:** Normals **Import**, Tangents **Calculate Mikktspace**, after flipping the inverted
normals by hand in Blender (history 11, 18, 24). Calculate also worked but gave artifacts.

Mesh children at Rotation 0, 0, 0: the imported -90 left the grip running back along the gun
instead of out to the side like the RK-1. At 0, 0, 0 it lies in the same plane as the RK-1,
about 23° shallower.

**Materials** (both `p0/Reflective/Bumped Specular SMap`):

| | `houndgrip_grip` (polymer) | `houndgrip_rail` (metal) |
|---|---|---|
| Main Color | 221 planned, **192 in the built bundle** (history 39) | 213 |
| Specular Color | 217, 217, 217 | 217, 217, 217 |
| "Specularness" | 1 (was 2: glowed, history 27) | 1.46 (mount median; was 1.5, before that 2) |
| "Glossness" | 1 (was 1.08, before that 0.6) | 1 |
| Reflection Color | 80, 80, 80, alpha 128 (129 suggested) | 154, 154, 154, alpha 128 |
| Reflection Cubemap | `patron_cubemap_metall_matte` (was `dots small`, history 33) | `patron_cubemap_metall` |
| Spec / Diffuse Vals | 1, 0.5, 0, 0 (1, 1, 0, 0 suggested) | 1, 1, 0, 0 |

**Hand poses** (from `unity/AddSideGripHandPoses.cs`, then moved to fit the grip at rotation
0, 0, 0). The first positions (0.176, -0.023, 0.003 and 0.139, 0.038, -0.100) put the hand past
the end of the grip in game. Moving them 3.5 cm back along the grip axis (0.939, 0.343, 0) put
the hand slightly too close, so they now sit halfway (1.9 cm back). Current values, **not yet
confirmed in game**:

| Object | Position | Rotation |
|---|---|---|
| `Base HumanLPalm` (Alternative) | 0.157, -0.030, 0.003 | 51.9, 268.0, 250.2 |
| `Base HumanLPalm 1` (Common) | 0.097, 0.028, -0.102 (user moved it; was 0.120, 0.031, -0.100) | 14.8, 249.2, 159.3 |

`unity/GripPoseGizmos.cs` draws these hands in the Scene view, so they can be lined up by eye.

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

11. Grip looked "reversed"/inside-out, with a seam showing that MW3 hides. A half-turn rotation was
    suggested first; that was wrong (rotation can't fix this). Comparing meshes with the vanilla RK-1
    showed the real cause: the faces point outward but **every normal points inward** (vanilla:
    faces and normals agree 100%; ours: 0%), so the lighting is inverted. Fix: FBX import
    Normals → Calculate. Remember Apply Default Settings on PreviewPivot resets the icon rotation;
    set it to 0, 245, 180 again afterwards.

12. Hand at 3.5 cm back was slightly too close → halfway values. Added `unity/GripPoseGizmos.cs`
    to see the hand in Unity instead of rebuilding to check.
13. Black patches on the rail. The rail diffuse was 28% pure black with no extra specular there
    (diffuse alpha a flat 56). Cause: the textures were converted as metal → black diffuse, but
    the metal's shine never reached the specular mask, so metal rendered as flat black. MW2022
    stores the metal mask in the colour image's **alpha**, with the metal's shine colour in the RGB
    there. Fix: `tools/smap-texture-converter.html` gained "Base color alpha: It's the metal mask"
    and "Metal keeps diffuse" (default 25%), tested on sample images. Re-split the DDS files with
    GameImageUtil's MW modes (see `HOW_IT_WORKS.md`) and re-convert.

14. Ported GameImageUtil's two MW modes into the converter ("MW fused colour" + NOG slot), so
    the split happens in the page. Checked pixel-for-pixel against a Python port of GameImageUtil's
    formulas; that check caught a bug where specular above 255 wrapped around to near black
    (bright metal would have gone dark), now clamped like GameImageUtil does.

15. Docs corrected: the converter already flips the normal's green channel, so Unity's Flip Green
    Channel must stay off; and vanilla's gloss texture is sRGB, so gloss keeps sRGB on.
    Full workflow written up in `docs/TUTORIAL.md`.

16. The converter now opens DDS files itself (BC1–BC5, BC7, uncompressed), so GameImageUtil isn't
    needed at all. The decoder is a port of bcdec; checked against Pillow on random blocks of every
    format (BC7 exact, BC1–3 within 1/255) and the DDS route gives identical outputs to the PNG route.
    Source corrected to MW3 (2023); its texture packing is assumed to match MW2022 (same engine),
    not yet confirmed.

17. First real test of the converter on the MW3 rail DDS files: GameImageUtil's NOG split gave a
    proper normal map, the converter gave a flat teal one (and a different gloss). The bug is in
    the converter, most likely its DDS reading of this file's format; tests had only used
    self-made DDS files. Until fixed, use GameImageUtil's outputs. Also fixed: loading the colour
    image after the NOG could re-guess the NOG's gloss as roughness and invert it; NOG gloss is now
    always gloss. The NOG slot now warns when a file doesn't look like a packed NOG.

18. Normals: Calculate gave visible artifacts in Unity: the normal map was baked against the
    original normals, which Calculate replaces. Added `tools/blender_flip_custom_normals.py` to
    reverse the original normals in Blender instead (then Normals: Import). Not yet tested.

19. Using the converter's NOG route on the grip gave a very dark colour. Likely the NOG's AO
    (misread, like the teal normal) multiplied into the diffuse at 100%; possibly MW3's colour alpha
    isn't the metal mask. Diagnosis asked: untick AO, then set Base color alpha to Ignore. Safe
    route (GameImageUtil splits → converter) written into the tutorial.

20. Added the converter's **MW3 / MW2022 (GameImageUtil PNGs)** preset for the safe route: one
    click sets all options, and GameImageUtil's `_c/_s/_g/_n/_o` files route to the right slots.
    Tested: routing, settings and all outputs correct.

21. The converter's Normal preview showed pink/green/teal: the raw green (NOG) image had gone into
    the Normal slot (its red is gloss, the normal is packed in green/alpha). The Normal slot now
    warns when an image isn't mostly lavender-blue. The earlier teal normal may have had the same
    cause. The chat won't accept .dds attachments; rename to .bin, zip, or upload to `samples/`.

22. Solved, with the real MW3 DDS files: the converter and its DDS reader were right all along
    (decodes identical to Pillow). The rip's names were misleading: **`normals.dds` is the NOG**
    (R gloss, G/A packed normal, B occlusion), and **`green.dds` is a mask image** (R and G hold one
    grayscale map split by complementary B/A masks; not used by SMap). Putting green.dds in NOG gave
    the teal normal. With color.dds → Color (MW fused) and normals.dds → NOG, all outputs are correct.
    MW3 packing confirmed same as MW2022. The page now warns about both mix-ups.

23. Re-converted textures (color.dds → Color with MW fused colour, normals.dds → NOG) confirmed
    looking right in Unity. Unity shows "Anisotropic filtering is enabled for all textures in
    Quality Settings" when setting Aniso 5: just an editor note (the project forces aniso); keep 5.

24. Normals fixed in Blender by hand: Face Orientation overlay on, flipping faces until none were
    red, then re-exporting. Lets the FBX go back to Normals: Import (keeps the original smoothing,
    no Calculate artifacts). Not yet verified.

25. Hand-flipped FBX on Normals: Import looks right in Unity together with the re-converted
    textures (user check in the editor).

26. In game the hand uses `Base HumanLPalm 1` (GripType Common), the normal hold. `Base HumanLPalm`
    (Alternative) is kept like vanilla; when the game switches to it is not known yet.

27. In game the grip looked like it glowed and didn't react to light like the RK-1. Measured: the
    converted grip's specular (diffuse alpha) averages 54 vs the RK-1's 27 (GameImageUtil's non-metal
    floor of 0.21 is twice Tarkov's polymer), and its gloss averages 94 vs 156, so the shine is broad
    and covers the whole grip; the "Glossness" slider at 0.6 spread it further. The cubemap is not the
    cause (`dots small` averages 12/255). Fix: grip material "Specularness" 2 → 1, "Glossness"
    0.6 → 1.08; Main Color 193 → ~160 if still bright. Not yet confirmed in game.

28. Metal: the vanilla RK-1's shiniest 10% (a stand-in for its metal) has specular ~77, diffuse
    ~101 and gloss ~170, against its polymer's 22 / 37 / 155. Tarkov keeps metal diffuse fairly
    bright, so the converter's "Metal keeps diffuse" 25% was too dark; default now 75%. Rail: re-convert
    at ~75% and set "Specularness" 2 → ~1.2. Not yet measured on the rail's own textures (need its DDS).

29. Material check (user's Inspector screenshots): grip Specularness 1 / Glossness 1.08 and rail
    Specularness 1.5 / Glossness 1.08 set. The grip's new `_normal` texture showed "This texture is
    not marked as a normal map": imported as a plain texture, so the shader read the bumps wrongly
    (likely part of the flat/glowing look). Fix Now, then keep Flip Green Channel off.

30. In dark light the grip's edges/facets were noticeable ("not super but noticeably"). Not low poly:
    the grip has 3286 triangles and the rail 492, against the whole vanilla RK-1's 850 (measured on
    the earlier bundle). Likely causes, in order: the unmarked normal map (29); smoothing lost when
    the faces were flipped by hand in Blender (24), so the FBX's imported normals are flat or uneven;
    SMap's reflection catching bevel edges. `inspect_bundle.py` now prints triangle count and the
    share of flat-shaded triangles (vanilla RK-1: 40%). Test asked: Fix Now, then Normals → Calculate
    (angle 60) to see whether the facets vanish; upload the new bundle to measure. Not yet resolved.

31. Added `tools/dump_material_values.py`: tested on the RK-1 bundle. Its Main Color reads
    0.7547 = **192** (the 193 above is a rounding; either is fine). RK-1 averages: diffuse 48,
    specular 27, gloss 156.

32. Added `tools/build_material_library.py` (material library by kind). Tested on the RK-1 only:
    polymer pixels median diffuse 47 / spec 24 / gloss 162; its metal (coated class) 81 / 55 / 169.
    Needs a run over the game's `mods` folder for real numbers (asked the user).

33. Cubemaps moved to the game's shared bundle, so they aren't copied into each grip. Found in
    the SDK: its `Assets/Cubemaps/` are the game's six item cubemaps, labelled `cubemaps`, and its CAB
    and PathID tables map them to the game's `cubemaps` bundle (`CAB-4d8a...`), same as the shader.
    We had relabelled them `houndgrip`/`bundle`, which built a copy in. Fix: labels back to
    `cubemaps` (no variant), grip `dots small` (not a game cubemap) → `patron_cubemap_metall_matte`
    (the RK-1's), `bundles.json` dependencies `shaders`, `cubemaps`. Not yet built and checked.

34. Material library built from the game's `mods` folder (1743 SMap materials): see `MATERIALS.md`.
    Tarkov polymer averages specular 29 / gloss 137 at "Specularness" 2; our grip's texture is
    54 / 94, so "Specularness" 1 matches it in strength (history 27 confirmed by the data). The
    common cubemap for polymer and coated metal is `patron_cubemap_metall`, already in the SDK.

35. Every vanilla item's values added (`data/vanilla_materials.csv`). Foregrips use "Specularness"
    1.0 (half of them) to 2.0, "Glossness" ~1.0, cubemap metall_matte or metall. Our grip's
    1 / 1.08 / metall_matte is in range. The SDK's six cubemaps cover 99% of vanilla attachments.

36. Grip material set from the foregrip data: "Specularness" 1, "Glossness" 1, Main Color 221.
    Suggested to finish it: Specular/Diffuse Vals 1,1,0,0 (41 of 59 foregrips), Specular Color 255,
    Reflection Color 129,129,129,128. Not yet confirmed in game.

37. Cubemap labels checked (user screenshot): all six in `Assets/Cubemaps/` on AssetBundle `cubemaps`,
    variant None, as the SDK ships them. The Console's "custom UI ... FresnelMaterialEditor" warning
    for SMap is harmless.

38. First build with two grips failed: "AssetBundle names "cubemaps.bundle" and "cubemaps" can't
    exist in the same build". Something was still labelled `cubemaps` + variant `bundle` (left over
    from relabelling cubemaps, history 33). Fix: find it in the AssetBundles window → Configure →
    `cubemaps.bundle` and set its variant to None.

39. First build of both grips into the renamed mod `MW2023Attachment` (was `Hound9GSideGrip`; same item
    IDs, new mod GUID `com.hound.mw2023attachment`). Checked with `inspect_bundle.py`:
    - Good: dependencies `shaders` + `cubemaps` only; no cubemap copied in; SMap points at the game's
      shader; `_Cube` points at the game's cubemaps bundle `CAB-4d8a...`; rail values updated.
    - **Cubemap PathIDs not remapped**: rail `_Cube` object 4870518337489161011, grip
      4963929626472855650. The game's are -2064706391146893937 (metall) and 972550011776207695
      (metall_matte). Same cause as SMap: this project builds different PathIDs than the SDK table
      expects. Effect in game: cubemap not found (likely white/no reflection). Fix: PathID Replacer
      entries; which build PathID is which cubemap to be confirmed from the built `cubemaps` file
      (asked for it).
    - **Normals still inverted**: "normals agree with faces" 0% on grip and rail (vanilla 100%). The
      hand-flip of faces in Blender (history 24) flipped winding and normals together, so they still
      disagree; the grip is lit inside-out. Probably behind the glow (27) and the visible edges (30).
      Checked which half is wrong (direction from the mesh centre): faces/winding point outward
      78–87% (fine, RK-1 79%), stored normals point outward only 13–22% (RK-1 79%). So the faces are
      right and only the normals are inward, on the Hound grip, its rail **and the DL grip**. Blender's
      Face Orientation overlay only shows faces, so it looks all blue even when normals are inward;
      see them with Edit Mode (Tab) → Mesh Edit Mode overlay (dropdown next to Viewport Overlays) → Normals → split-normals icon (middle), Size ~0.02.
      Fix: normals only (`tools/blender_flip_custom_normals.py`, don't flip faces), or FBX Normals:
      Calculate.
    - Grip material in the bundle still has Main Color 192 and Vals 1, 0.5, 0, 0 (the 221 / 1, 1, 0, 0
      edit wasn't saved or was on the other grip).

**Open** (cleaned up; solved items removed):
- Rebuild with the cubemaps left on label `cubemaps` (history 33) and check: manifest `Dependencies:`
  `shaders`, `cubemaps`, no cubemap under `Assets:`; `inspect_bundle.py` shows `_Cube: CAB-4d8a...`.
- In game: hand poses (halfway values; `Base HumanLPalm 1`), icon rotation 0, 245, 180, shine next
  to the RK-1 with the new grip values (history 36), edges in dark light (history 30).
- Rail material still has the old values (Main 193, "Specularness" 1.5, Vals 1, 0.5, 0, 0). Vanilla
  mounts (`MATERIALS.md`): "Specularness" ~1.46, "Glossness" 1, Main ~213, Vals 1, 1, 0, 0,
  `patron_cubemap_metall`. Not changed yet.
- Not sold by any trader (`addtoTraders: false`); only `spt give` / flea.

## dlgrip (second side grip, name to come)

| | |
|---|---|
| Item ID | `6abedf70d13bed42e615da72` (`db/CustomItems/DLGrip.json`) |
| Name | **placeholder** "DL Side Grip" / "DL Side" until the user names it |
| Cloned from | RK-1 B-25U `5c1cd46f2e22164bef5cfedb` (assumed, like the Hound 9G) |
| Bundle | `assets/content/items/mods/foregrips/dlgrip.bundle`, dependencies `shaders`, `cubemaps` |
| Unity prefab | `Assets/Content/Weapons/Tarkov Double Sidegrip/dlgrip/dlgrip.prefab` |

**History:**

1. Hand poses added under the `dlgrip` root (`Base HumanLPalm`, `Base HumanLPalm 1`). The prefab
   had no mesh child yet in the user's screenshot; the grip mesh still has to go under the root.
2. Single part (one mesh, one material, folder `dlgrip/grip`), unlike the Hound 9G's grip + rail.
   Fine: the prefab just needs that one mesh child. The RK-1 it replaces includes its B-25U rail
   mount, so check in game that the grip doesn't float off the rail without a mount part.
3. The mesh ended up **on the root itself** (MeshFilter `DLGRIP`, Mesh Renderer, Box Collider on
   `dlgrip`, Scale 1) instead of a child. Vanilla (RK-1): root has only LODGroup + PreviewPivot; the
   meshes are children next to the palms. Asked to move it to a child (drag the FBX onto the root,
   set Rotation 0, 0, 0, keep Scale 100) and remove the root's MeshFilter, Mesh Renderer and Box
   Collider. Its material's Specular Color also looked black in the screenshot (kills all shine);
   asked to set 255.
4. Fixed (user screenshots): root `dlgrip` now has only Transform + PreviewPivot; child `grip` holds
   the mesh (`DLGRIP`), Mesh Renderer, a disabled Box Collider, the `grip` material; Position and
   Rotation 0, Scale **1** (this FBX shows at the right size at Scale 1, unlike the Hound's 100; check
   the size against the RK-1 after the build: RK-1 is about 0.109 × 0.047 × 0.091 m). Prefab label
   `dlgrip` / `bundle`. PreviewPivot icon Rotation still 0, 245, 0: set 0, 245, 180. The palms still
   sit at the RK-1 values and don't wrap the grip yet.

5. First build checked (`inspect_bundle.py`): structure like vanilla; size 13 × 6 × 3 cm, same
   orientation as the Hound 9G (RK-1 about 11 × 5 × 9 cm incl. mount). Problems: normals agree with
   faces **0%** (inverted, like the Hound); `_Cube` PathID 4963929626472855650 not remapped (see
   Hound history 39); **`_StencilType` 0** (vanilla: Hands, 2); Vals 1, 0.5, 0, 0. `Base HumanLPalm`
   still exactly the RK-1 value; `Base HumanLPalm 1` at 0.092, 0.049, -0.103 rot 14.0, 254.2, 152.3.
   Good: Main Color 221, Specular Color 255, Reflection 128/128, Specularness 1 / Glossness 1,
   textures 1024 aniso 5, normal map linear.

**Open:** cubemap PathID entry, normals, Stencil → Hands, icon rotation 0, 245, 180; fit the palms (`Base HumanLPalm 1` first); material values
(foregrip row in `MATERIALS.md`, Specular Color 255); size vs RK-1 after build; server item (name,
clone, trader).
