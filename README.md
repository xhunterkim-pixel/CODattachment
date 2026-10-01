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
- **Prefab setup.** The prefab inside the bundle has to be built like a vanilla foregrip. If the
  item shows up but is invisible, or the client logs errors when you attach it, open the vanilla
  RK-1 B-25U bundle in AssetStudio and copy its hierarchy and components.
- **Stats/price.** To change stats, add fields such as `"Ergonomics"`, `"Recoil"` or `"Weight"`
  to `overrideProperties`. Any field you leave out is copied from the RK-1.

## White or purple items: point materials at the game's shaders

Bundles built with the SDK either embed the SDK's copy of an EFT shader (the item renders
**white** in game) or point at the SDK's own `shaders` bundle (it renders **purple**). Vanilla
items point at the game's `shaders` bundle. `tools/fix_eft_shaders.py` rewrites your materials to
do the same.

One-time setup: install Python 3, then `pip install UnityPy`.

```
python tools/fix_eft_shaders.py "<path>\houndgrip.bundle" --game-shaders "C:\SPT\EscapeFromTarkov_Data\StreamingAssets\Windows\shaders"
```

`--game-shaders` is only needed the first time and after a game update; the shader list is cached
in `tools/game_shaders.json`. After that, run it on each bundle you build:

```
python tools/fix_eft_shaders.py "<path>\houndgrip.bundle"
```

Run it on the bundle in the SDK's output folder, so it can also resolve references to the SDK's
`shaders` bundle sitting next to it. It keeps the original as `.bak`. The mod's `bundles.json` must
list `"shaders"` in `dependencyKeys`.
