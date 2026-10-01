# Tutorial: from a Call of Duty rip to a working Tarkov attachment

Every click, in order, with every fix we found on the Hound 9G. Follow it top to bottom for a new
attachment, or to redo one. Why each step matters is explained in `HOW_IT_WORKS.md`; if something
goes wrong, check the troubleshooting table in `ADDING_A_GRIP.md`.

**You need:** your COD rip (model + DDS textures), Blender, the
EscapeFromTushonka-SDK in Unity 2022.3.43f1, this repo, and (for the checks) Python 3 with
`pip install UnityPy`.

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
converter page does the whole translation, including GameImageUtil's MW splits.

1. Open `tools/smap-texture-converter.html` in your browser. It reads the ripped **DDS files
   directly** (if one uses an unusual format it tells you; then convert that one to PNG with
   GameImageUtil's **Direct Convert (Global)**).
2. You need two images per material: the **colour** image and the **green (NOG)** image. This works
   for MW2019, MW2022 and (assumed, same engine) MW3.
3. **Color** slot: the colour DDS. Under **Base color alpha**, pick **MW fused colour (spec/albedo)**.
   The Metallic slot then says "Not needed".
4. **NOG** slot: the green DDS. It fills **Roughness** (gloss), **Normal** and **AO** by itself and
   turns on **Flip green** and **AO**.
5. Settings:
   - **Metal keeps diffuse: 25%** (20–35%). At 0% metal parts show as black patches.
   - **Diffuse brightness:** leave **Auto** on.
   - **Flip green:** leave it on (COD normals are DirectX, Unity wants OpenGL).
6. **Download all (zip)**. You get `<name>_diffuse.png`, `<name>_gloss.png`, `<name>_normal.png`.
7. Do this once per material (e.g. once for the grip, once for the rail).

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
3. **Texture import settings** (click each PNG, then **Apply**):

   | Texture | Texture Type | sRGB | Flip Green Channel | Aniso Level |
   |---|---|---|---|---|
   | `_diffuse` | Default | on | n/a | 5 |
   | `_gloss` | Default | on (like vanilla) | n/a | 5 |
   | `_normal` | **Normal map** | n/a | **off** (the converter already flipped it) | 5 |

## Part 5: Materials

1. Create a material per part (Project window → right-click → Create → Material).
2. **Shader:** `p0/Reflective/Bumped Specular SMap`.
3. Textures:
   - **Base (RGB) Specular (A):** `_diffuse`
   - **GlossMap:** `_gloss`
   - **Normalmap:** `_normal`
   - **Reflection Cubemap:** pick one from the SDK (`Assets/Cubemaps/` or
     `Assets/Systems/Effects/ParticleSystems/Cubemap/`). **Never leave it empty**, or the item turns
     white.
4. Values. Start from the vanilla item's (your inspect output). The SDK's labels "Specularness" and
   "Glossness" are swapped: "Specularness" is shine strength, "Glossness" is highlight tightness.
   What the Hound 9G uses:

   | Inspector label | Polymer part | Metal part |
   |---|---|---|
   | Main Color | 193, 193, 193 | 193, 193, 193 |
   | Specular Color | 217, 217, 217 | 217, 217, 217 |
   | "Specularness" | 2 (lower to ~1.5 if too shiny) | 2 |
   | "Glossness" | 0.6 | 1.08 |
   | Reflection Color | 80, 80, 80, alpha 128 | 154, 154, 154, alpha 128 |
   | Specular Vals / Diffuse Vals | 1, 0.5, 0, 0 | 1, 0.5, 0, 0 |
   | _StencilType | Hands | Hands |

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
2. Give the cubemap file(s) you used the same label, so they're built in.
3. AssetBundles window → **Build**:
   - **Output Path: relative**, e.g. `AssetBundles` (click Reset). An absolute path crashes the
     shader replacer, giving purple items.
   - The output folder must not have the same name as your bundle.
4. One-time SDK fix: **PathID Replacer** tab: add **SDK PathID 3868700100545724512 → EFT PathID
   6014991791773097075** (SMap), then **SAVE DATA TO FILE**.
5. Build. The Console should show no `DirectoryNotFoundException`.
6. Check the result:
   - `AssetBundles/StandaloneWindows/<attachment>.bundle.manifest`: `Dependencies:` shows only
     `shaders` (or nothing).
   - `python tools/inspect_bundle.py AssetBundles/StandaloneWindows/<attachment>.bundle`: each
     material's shader = `CAB-56d919bd5479d38f741da52a6beef92f object 6014991791773097075`, and each
     mesh "normals agree with faces" close to 100%.

## Part 8: The mod and testing

1. Copy `<attachment>.bundle` (only that file) into the mod at
   `bundles/assets/content/items/mods/foregrips/<attachment>.bundle`.
2. `bundles.json` has that path as `key` with `"dependencyKeys": ["shaders"]`; the item JSON's
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
