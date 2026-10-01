# Hound 9G Side Grip (SPT 4.1)

Adds a new side grip cloned from the **Zenit RK-1 foregrip on B-25U mount**. It has the same stats and fits the same weapons.

Requires **WTT-ServerCommonLib 3.0.6+** (and the WTT client CommonLib it ships with).

## Layout

```
Hound9GSideGrip/
├── Hound9GSideGrip.csproj   build settings (SPT + CommonLib come from NuGet)
├── Hound9GSideGrip.cs       mod metadata + loader (hands the JSON to WTT-CommonLib)
├── db/CustomItems/Hound9GSideGrip.json   the item definition
├── bundles.json             tells SPT which bundle to serve
└── bundles/assets/content/items/mods/foregrips/houndgrip.bundle   <- your bundle goes here
```

## Build

1. Install the **.NET 10 SDK**.
2. Copy `houndgrip.bundle` into `Hound9GSideGrip/bundles/assets/content/items/mods/foregrips/`.
   You don't need the `.manifest` file.
3. Build (NuGet downloads the SPT 4.1.6 and CommonLib references automatically):
   ```
   dotnet build Hound9GSideGrip -c Release
   ```
   Or open the project in Visual Studio or Rider and build it there.
4. Copy `dist/user/mods/Hound9GSideGrip` into your SPT `user/mods` folder.

## Testing

Start the server and check the log for errors from WTT-CommonLib. In game, open the chat with
the SPT bot and send `spt give 6abe08f14fea21b38607a868 1`, then attach the grip to a weapon
that takes the RK-1 B-25U.

## Things to check

- **Clone ID.** `itemTplToClone` is `5c1cd46f2e22164bef5cfedb` (RK-1 on B-25U mount). If the
  server says it can't find it, look up the right ID in `SPT_Data/database/templates/items.json`
  (search for `b25u`).
- **Bundle path.** `Prefab.path` in the item JSON, the `key` in `bundles.json`, and the file's
  location under `bundles/` must be the same string, all lowercase.
- **Prefab setup.** The prefab needs PreviewPivot and hand poses like the vanilla grip, and its
  materials must use the game's shaders. See [`docs/ADDING_A_GRIP.md`](docs/ADDING_A_GRIP.md).
- **Stats/price.** To change stats, add fields such as `"Ergonomics"`, `"Recoil"` or `"Weight"`
  to `overrideProperties`. Any field you leave out is copied from the RK-1.

## Guides

- [`docs/TUTORIAL.md`](docs/TUTORIAL.md): every step from a COD rip to a working attachment in game.
- [`docs/HOW_IT_WORKS.md`](docs/HOW_IT_WORKS.md): how SPT, Unity, bundles, the SDK and shaders fit together.
- [`docs/ADDING_A_GRIP.md`](docs/ADDING_A_GRIP.md): step-by-step checklist for a new grip, and a troubleshooting table.
- [`docs/MATERIALS.md`](docs/MATERIALS.md): material library (Tarkov's values for rubber, polymer, coated and bare metal), with the spreadsheet `docs/material_library.csv`.
- [`docs/GRIPS.md`](docs/GRIPS.md): what each grip is based on, the values that worked, and its history.

## Tools

Python 3 with `pip install UnityPy`:

| Tool | Use |
|---|---|
| `tools/inspect_bundle.py` | Show what's in a bundle (shader references, hierarchy, hand poses, material values). Compare yours with the vanilla item. |
| `tools/dump_material_values.py` | Table (CSV) of the game's own material values for every item in a folder, to copy into Unity. |
| `tools/build_material_library.py` | Small material library (rubber, polymer, coated metal, bare metal): the game's typical texture and slider values for each. |
| `tools/fix_eft_shaders.py` | Point materials at the game's shaders when an item is purple or white. |
| `tools/make_handpose_script.py` | Turn a vanilla item's hand poses into a Unity editor script. |
| `tools/blender_flip_custom_normals.py` | Blender script that reverses inverted normals without losing the original smoothing. |
| `unity/AddSideGripHandPoses.cs` | Unity editor script with the RK-1 B-25U side-grip hand poses. |
| `unity/GripPoseGizmos.cs` | Unity editor script that draws the hand poses in the Scene view. |
| `tools/smap-texture-converter.html` | Open in a browser: converts COD textures (DDS or PNG) into SMap's diffuse/gloss/normal. |
