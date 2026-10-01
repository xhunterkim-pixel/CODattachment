# Tutorial: from a Call of Duty rip to a working Tarkov attachment

Every click, in order, with every fix we found on the Hound 9G. Follow it top to bottom for a new
attachment, or to redo one. Why each step matters is explained in `HOW_IT_WORKS.md`; if something
goes wrong, check the troubleshooting table in `ADDING_A_GRIP.md`.

**You need:** your COD rip (model + DDS textures), Blender, the
EscapeFromTushonka-SDK in Unity 2022.3.43f1, this repo, and (for the checks) Python 3 with
`pip install UnityPy`.

**Running the Python tools on Windows:** open Command Prompt, `cd` to the folder the `.py` files are
in (e.g. `cd %USERPROFILE%\Desktop`), and write the script name without `tools/` if it's not in a
`tools` folder. Replace `<game>` with your SPT folder, the one that contains `EscapeFromTarkov.exe`
(click the address bar in Explorer there and copy it). Keep the quotes around paths. If it says
`No module named UnityPy`, run `pip install UnityPy` once.

---

## Part 1: Pick the vanilla item to imitate

Your attachment copies a vanilla item's stats, hand pose, icon framing and material values.

1. Pick the vanilla item closest in shape and use. For a side grip: the Zenit RK-1 on B-25U mount.
2. Get its **item ID** from the in-game handbook (or `SPT_Data/database/templates/items.json`).
   Never from memory.
3. Copy its bundle from your game folder, e.g.
   `EscapeFromTarkov_Data/StreamingAssets/Windows/assets/content/items/mods/foregrips/foregrip_all_zenit_b25u_rk_1.bundle`.
4. Run `python tools/inspect_bundle.py <that bundle>` and keep the output. You'll copy values from it.

## Part 2: Textures

COD packs several maps into each image, and Tarkov's SMap shader wants a different packing. The
converter page does the whole translation, including GameImageUtil's MW splits, and reads DDS
directly. Confirmed on the Hound 9G's MW3 files.

**Which ripped file is which** (MW3 rips come as three DDS per material; names vary by ripper):

| File looks like | What it really is | Goes in |
|---|---|---|
| Dark/grey colour, partly see-through in viewers | Fused colour (albedo + specular, alpha = metal) | **Color**, with "MW fused colour" |
| Purple-ish, often named "normals" | **NOG**: gloss (R), packed normal (G and A), occlusion (B). Not a finished normal map | **NOG** (not Normal!) |
| Bright green, hard black/white shapes | Material/wear masks (B and A are opposites) | Nothing. SMap doesn't use it |

The page warns if a file goes in the wrong slot.

1. Open `tools/smap-texture-converter.html` in your browser. The same steps are in its
   "How to use" box at the top.
2. **Color** slot: the colour DDS. Under **Base color alpha**, pick **MW fused colour (spec/albedo)**.
   The Metallic slot then says "Not needed".
3. **NOG** slot: the purple-ish "normals" DDS. It fills **Roughness** (gloss), **Normal** and **AO**
   by itself and turns on **Flip green** and **AO**.
4. Settings:
   - **Metal keeps diffuse: 75%**. Tarkov paints metal with a fairly bright diffuse; low values
     give dark or black metal.
   - **Diffuse brightness:** leave **Auto** on.
   - **Flip green:** leave it on (COD normals are DirectX, Unity wants OpenGL).
5. Check the four previews: Normal must be **lavender-blue with visible relief** (never teal or pink);
   Diffuse is the real colour (polymer is dark grey; the vanilla RK-1 is darker still).
6. **Download all (zip)**. You get `<name>_diffuse.png`, `<name>_gloss.png`, `<name>_normal.png`.
7. Do this once per material (e.g. once for the grip, once for the rail).

**Alternative: GameImageUtil first.** Split the colour DDS with **CoD Specular/Albedo
(Infinite Warfare/Modern Warfare)** and the NOG with **CoD Normal/Gloss/Occlusion (Infinite
Warfare/Modern Warfare)** (output PNG), click the converter's **MW3 / MW2022 (GameImageUtil PNGs)**
preset and drop all five files (`_c`, `_s`, `_g`, `_n`, `_o`) at once. Same result.

## Part 3: The model in Blender

1. Import the ripped model and check it looks right.
2. Export **FBX**. Unity will show the meshes at **Rotation X -90** and **Scale 100**; that's
   normal (Blender is Z-up and centimetres, Unity is Y-up and metres).

## Part 4: Import into Unity

1. In the SDK project, make a folder, e.g. `Assets/Content/Weapons/<attachment>/`, and drag in the
   FBX and the converted PNGs.
2. **FBX import settings.** Click the **FBX file** in the Project window (not the object in the
   scene). In the Inspector, on the **Model** tab, under Geometry:
   - **Normals: Calculate** (our COD port had every normal pointing inward, so it was lit
     inside-out and dull)
   - **Smoothing Angle: 60**
   - **Tangents: Calculate Mikktspace**
   - click **Apply**.

   If a curved part shows a hard crease, raise the Smoothing Angle; if a sharp edge looks rounded,
   lower it.

   **Better fix (no artifacts):** Calculate replaces the original smoothing that the normal map was
   baked against, which causes blotches and seams. Instead, in Blender select the mesh, run
   `tools/blender_flip_custom_normals.py` (Scripting tab → paste → Run Script), export the FBX again,
   and in Unity set **Normals: Import**. That keeps COD's normals and only turns them the right way.
   Alternatives in Blender: Edit Mode, select all, **Mesh → Normals → Recalculate Outside**; or turn on
   the **Face Orientation** overlay and flip faces until none show red (what we did on the Hound 9G).
   Afterwards check in Unity (Normals: Import) for see-through holes or dark patches.
3. **Texture import settings** (click each PNG, then **Apply**):

   | Texture | Texture Type | sRGB | Flip Green Channel | Aniso Level |
   |---|---|---|---|---|
   | `_diffuse` | Default | on | n/a | 5 |
   | `_gloss` | Default | on (like vanilla) | n/a | 5 |
   | `_normal` | **Normal map** | n/a | **off** (the converter already flipped it) | 5 |

   Every time you replace `_normal` with a new PNG, Unity imports it as a plain texture again; the
   material then says "This texture is not marked as a normal map". Click **Fix Now** and check
   Flip Green Channel is still off.

   If Unity says "Anisotropic filtering is enabled for all textures in Quality Settings", that's only
   an editor note (the SDK project forces it); keep Aniso 5, it's saved into the bundle. Always click
   **Apply** (or **Save** in the "Unapplied import settings" popup).

## Part 5: Materials

1. Create a material per part (Project window → right-click → Create → Material).
2. **Shader:** `p0/Reflective/Bumped Specular SMap`.
3. Textures:
   - **Base (RGB) Specular (A):** `_diffuse`
   - **GlossMap:** `_gloss`
   - **Normalmap:** `_normal`
   - **Reflection Cubemap:** pick one from the SDK's `Assets/Cubemaps/` (the game's own:
     `patron_cubemap_metall_matte` like the RK-1, or `patron_cubemap_metall` for shinier metal).
     **Never leave it empty**, or the item turns white. Don't use others (e.g. `dots small`): they
     aren't in the game, so they'd be copied into every bundle.
4. Values. Start from the vanilla item's (your inspect output). The SDK's labels "Specularness" and
   "Glossness" are swapped: "Specularness" is shine strength, "Glossness" is highlight tightness.
   What the Hound 9G uses:

   | Inspector label | Polymer part | Metal part |
   |---|---|---|
   | Main Color | 193, 193, 193 | 193, 193, 193 |
   | Specular Color | 217, 217, 217 | 217, 217, 217 |
   | "Specularness" | **1** (converted COD polymer is twice as shiny as Tarkov's; 2 glows) | **~1.2** |
   | "Glossness" | 1.08 | 1.08 |
   | Reflection Color | 80, 80, 80, alpha 128 | 154, 154, 154, alpha 128 |
   | Specular Vals / Diffuse Vals | 1, 0.5, 0, 0 | 1, 0.5, 0, 0 |
   | _StencilType | Hands | Hands |

   **Your own reference table of the game's values.** There's no public database of these; the
   accurate source is the game's own bundles. Run, on your PC:

   ```
   python tools/dump_material_values.py "<game>/EscapeFromTarkov_Data/StreamingAssets/Windows/assets/content/items/mods" mods.csv --textures
   ```

   It writes one row per vanilla material with every value above, written the way Unity shows
   them (colours 0–255 with alpha last; columns `inspector_Specularness` / `inspector_Glossness`
   use the Inspector's labels, already un-swapped), plus the cubemap and, with `--textures`, the
   average diffuse colour, specular (diffuse alpha) and gloss of its textures. Open it in Excel,
   filter the material name (e.g. a polymer grip, a steel mount) and copy that row. Compare the
   texture averages with your converted textures (same columns from your own bundle) to see if
   yours are brighter or shinier. Only rows with shader `p0/Reflective/Bumped Specular SMap` apply
   to an SMap material; "unknown <number>" is another game shader (run `fix_eft_shaders.py
   --game-shaders` once to cache the names). Start with one folder (e.g. `mods/foregrips`); the
   whole `mods` folder takes a while.

   **Material library.** `python tools/build_material_library.py "<game>/.../assets/content/items/mods" material_library.csv`
   sums this up per kind of material (rubber, polymer, coated metal, bare metal). In Tarkov one
   material covers a whole item, so plastic vs metal is decided by the **textures**: use the
   library's diffuse/specular/gloss targets to check your converted textures (compare with
   `dump_material_values.py --textures` on your bundle), and its "most used" slider values as the
   starting point. The repo's copy is `docs/material_library.csv`.

5. **Leave the shader file's AssetBundle label alone.** It belongs in the SDK's `shaders` bundle;
   building it into yours makes the item white.

## Part 6: The prefab

1. Create an empty GameObject named after the attachment (Rotation 0, 0, 0, Scale 1). This is the
   **root**; its origin is where the attachment clamps onto the rail.
2. Drag the meshes in as its children, and give each the material for that part.
3. **Point it the same way as the vanilla item.** For the Hound 9G the children needed Rotation
   **0, 0, 0** (Scale stays 100) instead of the imported -90. After your first build, compare
   `inspect_bundle.py` mesh bounds for yours and the vanilla bundle: the body must extend in the
   same direction from the origin.
4. **PreviewPivot** (inspect view and icon): select the root → **Add Component → PreviewPivot** →
   ⋮ → **Apply Default Settings** (a NullReferenceException before this is harmless). Then set
   **Icon → Rotation** to the vanilla item's value; the RK-1 B-25U uses **0, 245, 180**. Apply
   Default resets the icon rotation, so set it again whenever you re-apply.
5. **Hand poses** (side-grip animation):
   1. Copy `unity/AddSideGripHandPoses.cs` and `unity/GripPoseGizmos.cs` into `Assets/Editor/`.
      For another vanilla item, generate the first one with
      `python tools/make_handpose_script.py <vanilla.bundle> <Name> unity/Add<Name>HandPoses.cs`.
   2. Select the root → **Tools → Add RK-1 B-25U Side Grip Hand Poses**. Make sure you select the
      **root**: under a Scale 100 child the hands end up metres away.
   3. The Scene view now draws both hands (green = Common, orange = Alternative). Move each
      `Base HumanLPalm` object (not the finger bones) until the hand wraps the grip like the vanilla
      one. Hound 9G values: `Base HumanLPalm` **0.157, -0.030, 0.003**; `Base HumanLPalm 1`
      **0.120, 0.031, -0.100** (rotations as the script set them, then adjusted; see `GRIPS.md`).
6. **Overrides → Apply All** on the prefab.

## Part 7: Build the bundle

1. Label the attachment's folder (or prefab): AssetBundle name `<attachment>` + variant `bundle`.
   Every asset you label for it needs the same name **and** variant. Move other prefabs, and any
   scene, out of that folder.
2. **Don't label the cubemaps.** Leave each `Assets/Cubemaps/` file on AssetBundle `cubemaps`, no
   variant (how the SDK ships it). The build then points your materials at the game's cubemaps
   instead of copying them, the same way it handles the shader. If you relabelled one for an
   earlier grip, set it back. Unity also builds a `cubemaps` (and `shaders`) file; ignore them, the
   game has its own.
3. AssetBundles window → **Build**:
   - **Output Path: relative**, e.g. `AssetBundles` (click Reset). An absolute path crashes the
     shader replacer, giving purple items.
   - The output folder must not have the same name as your bundle.
4. One-time SDK fix: **PathID Replacer** tab: add **SDK PathID 3868700100545724512 → EFT PathID
   6014991791773097075** (SMap), then **SAVE DATA TO FILE**.
5. Build. The Console should show no `DirectoryNotFoundException`.
6. Check the result:
   - `AssetBundles/StandaloneWindows/<attachment>.bundle.manifest`: `Dependencies:` shows only
     `shaders` and `cubemaps`, and `Assets:` lists no cubemap.
   - `python tools/inspect_bundle.py AssetBundles/StandaloneWindows/<attachment>.bundle`: each
     material's shader = `CAB-56d919bd5479d38f741da52a6beef92f object 6014991791773097075`, its
     `_Cube` = `CAB-4d8a4131cf377709ee7c7e960f65d349 object ...`, and each
     mesh "normals agree with faces" close to 100%. "triangles" should be in the same range as the
     vanilla item or above (not low poly); "flat-shaded" near 100% means the smoothing was lost.

## Part 8: The mod and testing

1. Copy `<attachment>.bundle` (only that file) into the mod at
   `bundles/assets/content/items/mods/foregrips/<attachment>.bundle`.
2. `bundles.json` has that path as `key` with `"dependencyKeys": ["shaders", "cubemaps"]`; the item JSON's
   `Prefab.path` is the same path.
3. Delete `%TEMP%\Battlestate Games\EscapeFromTarkov\Icon Cache`, restart the server and game.
4. `spt give <item id> 1` in the SPT bot chat. Check: textured (not purple/white/doge), icon,
   centred inspect view, direction on the gun next to the vanilla item, left hand in raid.

---

## Redoing the Hound 9G with the new textures

1. Part 2 for the grip textures and for the rail textures (fused colour + NOG each).
2. Swap the new PNGs into `houndgrip_grip` and `houndgrip_rail` (Part 4 step 3 settings).
3. Check the FBX still has Normals: Calculate / Tangents: Calculate Mikktspace.
4. Keep everything else (prefab, hands, icon, labels) as it is.
5. Rebuild (Part 7), copy, clear the icon cache, test (Part 8). The black rail patches should be
   gone. If metal looks too dark or too bright, change **Metal keeps diffuse** and re-convert.
