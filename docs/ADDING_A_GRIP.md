# Adding a new grip, step by step

Checklist distilled from getting the Hound 9G side grip working. Background on every step is in
`HOW_IT_WORKS.md`; per-grip notes and values are in `GRIPS.md`.

## 0. Pick the vanilla item to copy

Choose the vanilla grip whose shape and use are closest (side grip, vertical, angled, handstop).
Get from it:

- **Its item ID**, from the in-game handbook or `SPT_Data/database/templates/items.json`.
  Don't guess IDs.
- **Its bundle**, from `EscapeFromTarkov_Data/StreamingAssets/Windows/assets/content/items/mods/foregrips/`.
- **Its values:** run `python tools/inspect_bundle.py <vanilla.bundle>` and keep the output. It
  shows hierarchy, hand poses, PreviewPivot, material values and where the model sits.

## 1. Model and textures in Unity (EscapeFromTushonka-SDK, Unity 2022.3.43f1)

1. Import the FBX and textures into their own folder, e.g. `Assets/Content/Weapons/<grip>/`.
2. FBX import settings: normals must face outward. After a build, `tools/inspect_bundle.py` prints
   "normals agree with faces" per mesh: vanilla is 100%, our COD port was 0% (flagged INVERTED).
   Best fix: reverse the normals in Blender with `tools/blender_flip_custom_normals.py`, re-export,
   and keep **Normals: Import** (Calculate causes artifacts because the normal map was baked against
   the original normals). Quick fix: **Model tab → Normals: Calculate** and **Tangents: Calculate Mikktspace** (select the FBX
   file in the Project window, not the scene object, to see the Model tab). For COD ports, Calculate
   is the sensible default. Import keeps the artist's hard/soft edges, so use it only when the check
   says the normals are fine. After Calculate, adjust Smoothing Angle if curved parts crease (raise)
   or sharp edges look rounded (lower). Inverted normals also kill the shine, so re-tune material
   values afterwards.
3. Texture import settings, matching the vanilla RK-1: normal → Texture Type **Normal map**, with
   **Flip Green Channel off** if it came from the converter (the converter already flipped it; tick
   it only for a raw COD normal); diffuse and gloss → Default with **sRGB on** (vanilla's gloss is
   sRGB too); all → **Aniso Level 5**. Click **Apply**.
4. Build the prefab: an empty root GameObject (rotation 0, scale 1) named after the grip, with the
   mesh objects as children. Imported meshes usually come in at Rotation X -90, Scale 100.
5. **Orientation:** the root's origin is where the grip clamps onto the rail. Compare your mesh
   bounds with the vanilla item's (`tools/inspect_bundle.py` on both bundles). The grip body must
   point the same way as vanilla's. For the Hound 9G that meant mesh rotation **0, 0, 0** instead
   of the imported -90.

## 2. Textures (COD rips)

1. The converter opens DDS directly (BC1–BC5, BC7, uncompressed). MW3 rips have three DDS per
   material: the fused **colour**, a purple-ish one often named "normals" that is really the
   **NOG**, and a bright green **mask** image that SMap doesn't use.
2. Open `tools/smap-texture-converter.html` in a browser. Put the colour PNG in **Color** and set
   "Base color alpha" to **MW fused colour (spec/albedo)**; put the green image in **NOG**. That fills
   Roughness (gloss), Normal (reconstructed, Flip green on) and AO, using GameImageUtil's own
   "CoD Specular/Albedo (IW/MW)" and "CoD Normal/Gloss/Occlusion (IW/MW)" math.
   (Already-split maps still work through the individual slots.)
3. Keep "Metal keeps diffuse" around 75%: Tarkov's metal diffuse is fairly bright (vanilla RK-1
   ~101/255); low values give dark or black metal.
4. Use the outputs: diffuse → `_MainTex`, gloss → `_SpecMap`, normal → `_BumpMap`.

## 3. Materials

1. Shader: **p0/Reflective/Bumped Specular SMap** (unless the vanilla item uses another).
2. Textures: `_MainTex` = diffuse (its alpha is the specular mask), `_SpecMap` = gloss,
   `_BumpMap` = normal.
3. Assign a **Reflection Cubemap**. Without one the item renders white/washed out. Cubemaps from
   the SDK (`Assets/Cubemaps/`, `Assets/Systems/Effects/ParticleSystems/Cubemap/`) are fine; give
   the cubemap file the same AssetBundle label as the grip so it's built in.
4. Start from the vanilla item's material values (from the inspect output), then tune in game, not
   in the Unity scene. Remember the swapped labels: "Specularness" = strength, "Glossness" =
   tightness. To see what other vanilla items of the same material use (polymer, metal, rubber),
   run `tools/dump_material_values.py` on a game folder and open the CSV (see TUTORIAL Part 5).
   `docs/material_library.csv` (from `tools/build_material_library.py`) has the typical values per
   material kind.

## 4. Prefab components

1. **PreviewPivot** on the root: Add Component → PreviewPivot, then ⋮ → **Apply Default Settings**
   (ignore the NullReferenceException it logs before that). Redo it whenever the model moves.
   Then set **Icon → Rotation** to the vanilla item's value from the inspect output (the SDK
   default can render the icon flipped; the RK-1 B-25U uses 0, 245, 180).
2. **Hand poses:** generate a script from the vanilla bundle:

   ```
   python tools/make_handpose_script.py <vanilla.bundle> <ShortName> unity/Add<ShortName>HandPoses.cs
   ```

   Copy it into the SDK's `Assets/Editor/`, select the prefab root, run
   **Tools → Add <ShortName> Hand Poses**. The RK-1 B-25U one is already in `unity/AddSideGripHandPoses.cs`.
3. Copy `unity/GripPoseGizmos.cs` into `Assets/Editor/` too: it draws each hand in the Scene view
   (green = Common, orange = Alternative). Move each `Base HumanLPalm` object so the hand sits
   where vanilla's sits relative to its grip.
   Move or rotate the palm object, not the finger bones (adjust fingers only for much thicker or
   thinner grips). Compare positions with the vanilla inspect output.
4. **Overrides → Apply All** on the prefab.

## 5. Build the bundle

1. Label the grip's folder (or prefab) with AssetBundle name `<grip>` + variant `bundle`. Every
   asset you label for it needs the same name *and* variant.
2. Don't label the SMap shader. It stays in the SDK's `shaders` bundle (folder label on
   `Assets/Shaders`) and the PathID Replacer converts it to the game's shader.
3. Output path: a **relative** folder like `AssetBundles` (absolute paths crash the replacer), not
   named the same as any bundle.
4. Build. The Console must show no `DirectoryNotFoundException` from the replacer.
5. Check `<grip>.bundle.manifest`: `Assets:` lists your prefab, materials, textures, cubemap;
   `Dependencies:` lists only `shaders` (or nothing).
6. Check the bundle itself: `python tools/inspect_bundle.py AssetBundles/StandaloneWindows/<grip>.bundle`.
   Every SMap material must show `shader = CAB-56d919bd5479d38f741da52a6beef92f object 6014991791773097075`.
   If it shows another CAB or "inside this bundle", either add a PathID Replacer entry or run
   `python tools/fix_eft_shaders.py <bundle>`. Also check every mesh says "normals agree with
   faces" near 100%.

## 6. Server mod entry

1. New item ID: 24 random hex characters, e.g.
   `python -c "import secrets,time;print('%08x'%int(time.time())+secrets.token_hex(8))"`.
2. Add a JSON entry in `Hound9GSideGrip/db/CustomItems/` (copy `Hound9GSideGrip.json`): set
   `itemTplToClone` to the vanilla ID, `Prefab.path` to
   `assets/content/items/mods/foregrips/<grip>.bundle`, names in `locales`, prices.
   Leave out stats you want copied from vanilla.
3. Add the bundle to `bundles.json` with `"dependencyKeys": ["shaders"]`.
4. Put the `.bundle` at `bundles/assets/content/items/mods/foregrips/<grip>.bundle`.
5. The DLL only needs rebuilding when C# changes. JSON and bundles are read at server start.

## 7. Test

1. Copy the mod folder to `SPT/user/mods/`, delete
   `%TEMP%\Battlestate Games\EscapeFromTarkov\Icon Cache`, restart the server and game.
2. Server log: `Loaded bundles from N mods (ok, missing: 0, invalid: 0)`.
3. `spt give <newId> 1` in the SPT bot chat. Inspect it, attach it next to the vanilla item,
   compare look, direction on the gun, and the left hand in raid.
4. Client errors are in `BepInEx/LogOutput.log` and Unity's
   `%USERPROFILE%\AppData\LocalLow\Battlestate Games\EscapeFromTarkov\Player.log`.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Build error "conflict with the user predefined AssetBundle name" | Output folder named like a bundle | Rename the output folder |
| Build error "can't exist in the same build as ... has the variant" | One asset labelled without the `bundle` variant | Give it the same name + variant |
| `DirectoryNotFoundException` after build | Absolute output path | Use a relative path (Reset button) |
| Doge box in game | Game can't load the prefab: path mismatch, or a dependency missing from `bundles.json` | Check `Prefab.path` = `bundles.json` key = file location; add `"shaders"` |
| Purple | Shader still points at the SDK's `shaders` bundle | PathID Replacer entry for the PathID your build used, or `fix_eft_shaders.py` |
| White / washed out | SDK shader built into the bundle, or no Reflection Cubemap | Don't label the shader; assign a cubemap |
| Icon spins forever | No PreviewPivot | Add it, Apply Default Settings |
| Inspect view off-centre | No PreviewPivot / not re-applied after moving the model | Apply Default Settings again |
| Icon renders but faces the wrong way | SDK default icon rotation | Copy the vanilla item's Icon rotation; delete the icon cache |
| Hand in the right pose but beside/past the grip | Palm markers offset along the grip | Move both palms along the grip axis (a few cm at a time) |
| Normal map comes out teal/green | The green **mask** file went into NOG | Put the purple-ish "normals" file (the real NOG) in NOG; the page warns |
| Normal preview is pink or the raw purple file | A NOG went into the Normal slot | Put it in NOG instead; the page warns |
| Converted colour is very dark | AO from a misread NOG multiplied in, or the colour alpha wrongly treated as metal | Untick AO; set Base color alpha to Ignore; use the tutorial's safe route |
| Polymer looks like it glows / doesn't react to light | Converted non-metal specular is ~2× Tarkov's and COD gloss is lower (broad sheen) | "Specularness" ~1, "Glossness" 1.08; Main Color lower if still bright |
| Material shows "This texture is not marked as a normal map" | The new `_normal` PNG was imported as a plain texture (happens every time you replace it) | Click **Fix Now** (or Texture Type: Normal map), then check Flip Green Channel is off |
| Edges/facets of the item noticeable in dark or low light | Usually not low poly (check `inspect_bundle.py` triangles vs vanilla). Most often lost smoothing (mesh exported flat-shaded or the normals changed after hand-flipping faces) or the normal map not marked as one | Fix Now on the normal map first. Test: FBX Normals → Calculate, Smoothing Angle 60. If the facets go away, the FBX lost its smoothing: in Blender, Shade Smooth (or Shade Auto Smooth), export with Geometry → Smoothing **Face**, back to Import. If they stay, compare a vanilla item in the same light |
| Black patches on metal parts | Metal converted to black diffuse without the metal's shine in the specular mask | Converter: alpha is the metal mask, Metal keeps diffuse 20–35% |
| Ripped texture looks grainy/low-res | Source texture (check it in the original game) or a low-res rip | Re-rip with high-res images; lower Normal intensity |
| Default hand grip instead of side grip | No GripPose objects | Add hand poses (step 3) |
| Hand grips oddly/backwards | Palm markers don't match where the model is | Fix model orientation vs vanilla first, then move the palms |
| Grip points the wrong way on the gun | Mesh rotation differs from vanilla | Compare bounds with vanilla, rotate the mesh children |
| Looks inside-out/"reversed", lit from the wrong side, seams showing | Normals point inward (common in COD → Blender → FBX ports) | Best: fix in Blender (flip script, Recalculate Outside, or flip red faces in the Face Orientation overlay) and keep Normals: Import. Quick: Normals: Calculate (causes artifacts) |
| See-through holes after flipping normals in Blender | A face was flipped the wrong way | Face Orientation overlay: flip the red ones back to blue |
| Icon rotation reverts | PreviewPivot Apply Default Settings resets it | Set the vanilla Icon rotation again after every Apply Default |
| Wrong stats or animation | Wrong `itemTplToClone` | Look the ID up, don't guess |
