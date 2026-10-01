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
└── bundles/assets/content/items/mods/foregrips/hound9gsidegrip.bundle   <- your bundle goes here
```

## Build

1. Install the **.NET 10 SDK**.
2. Copy `hound9gsidegrip.bundle` into `Hound9GSideGrip/bundles/assets/content/items/mods/foregrips/`.
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
