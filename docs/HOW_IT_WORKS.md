# How it all fits together

Background for adding attachments to SPT 4.1 (Tarkov) from ripped models. Read this once;
`ADDING_A_GRIP.md` is the step-by-step checklist.

## The three pieces

A custom attachment is three things that have to agree with each other:

| Piece | What it is | Where it lives |
|---|---|---|
| **Server mod** | A C# DLL plus JSON that tells the SPT server "this item exists": its ID, stats, name, price, which slots it fits, and which model file to show. | `SPT/user/mods/<ModName>/` |
| **Bundle** | The 3D model, textures and materials, packed by Unity into a `.bundle` file. The game client loads it to draw the item. | `SPT/user/mods/<ModName>/bundles/...` |
| **`bundles.json`** | Tells the SPT server which bundle files the mod has, so it can hand them to the game, and which other bundles must be loaded first. | `SPT/user/mods/<ModName>/bundles.json` |

The server never looks inside the bundle. The game client never reads the item JSON directly.
They meet through one string, the **prefab path**: the item's `Prefab.path` in the JSON, the
`key` in `bundles.json`, and the file's location under `bundles/` must all be the same.

## Tarkov and SPT

- **SPT 4.x server mods are C# DLLs** targeting .NET 10 (4.0 dropped the old TypeScript mods).
  SPT 4.1.6 publishes its reference packages on NuGet as `SPTushonka.Server.Core`,
  `SPTushonka.DI` and `SPTushonka.Common` (the DLLs inside are still named `SPTarkov.*`).
- **WTT-ServerCommonLib** (GUID `com.wtt.commonlib`) is a library mod that turns JSON files into
  items. Our DLL only hands it the `db/CustomItems` folder; the item itself is pure JSON. Players
  need WTT-CommonLib installed too.
- **Items are cloned from vanilla items.** `itemTplToClone` copies every property of a vanilla
  item; `overrideProperties` changes only what we list (name, prefab path, stats). Anything not
  listed (ergonomics, recoil, weight, animation fields) comes from the clone.
- **Item IDs are 24 hex characters** (MongoDB style). New items need a fresh random one. Vanilla
  IDs must come from the SPT database (`SPT_Data/database/templates/items.json`) or the in-game
  handbook. Never guess them from memory: we once cloned the wrong grip that way.
- **Slots:** with `addtoModSlots: true` and `modSlot: ["mod_foregrip"]`, CommonLib adds the new
  item everywhere the cloned item can be attached.
- **Testing:** in game, send `spt give <itemId> 1` to the SPT bot in chat to receive the item.

## Unity basics

- **GameObject:** any object in a scene. On its own it's just a named point.
- **Transform:** every GameObject's position, rotation and scale, relative to its parent.
  Children move with their parent and inherit its scale.
- **Component:** something attached to a GameObject that gives it behaviour: `MeshFilter` (which
  mesh), `MeshRenderer` (draw it with which materials), `BoxCollider`, or a script.
- **Prefab:** a saved GameObject with all its children and components. The game spawns the item
  from the prefab in the bundle. Changes made in a scene only reach the prefab after
  **Overrides > Apply All**.
- **Mesh:** the 3D shape. **Material:** says how a mesh is drawn: which shader, which textures,
  which values. **Shader:** the program on the graphics card that turns material + light into
  pixels. **Texture:** an image the shader reads.
- **Imported models:** Blender and other tools use Z as "up", Unity uses Y, so imported meshes
  usually get Rotation X = -90. Models exported in centimetres get Scale 100. Both are normal.
  What matters is which way the model ends up pointing compared with the vanilla item.

## How Tarkov uses an attachment prefab

Vanilla attachment prefabs (inspect one with `tools/inspect_bundle.py`) contain more than the mesh:

| Object / component | What it does | Without it |
|---|---|---|
| Mesh objects with `MeshRenderer` | The visible model. | Nothing to see. |
| **PreviewPivot** on the root | Centre point and rotation for the inspect view, and how the icon is framed. | Inspect view is off-centre; the icon may spin forever. |
| **GripPose** on `Base HumanLPalm` objects (+ finger bones) | Where the left hand goes and how the fingers curl. | The game uses its default left-hand position. |
| LODGroup | Swaps to a simpler mesh far away. | Fine for mods; always uses the full mesh. |
| BoxCollider | Physical shape, e.g. when dropped. | Item may fall through things. |

**Hand poses are not baked animations.** The game reads the palm markers while it runs and pulls
the left hand there with IK (inverse kinematics), bending the fingers to the finger bones'
rotations. Move the palm marker and the hand moves with it. Each vanilla grip has two:
`GripType` **Common** (0) and **Alternative** (1). The arm can only reach so far, so markers must
stay where a real hand could be.

**The prefab's origin is the attachment point.** For a foregrip, (0, 0, 0) is where it clamps to
the rail. The game puts that point on the weapon's `mod_foregrip` slot, so the model must point
the same way as the vanilla item it replaces.

## Bundles

A `.bundle` is Unity's container format: one or more serialized files (each with an internal name
like `CAB-56d919bd5479d38f741da52a6beef92f`), each holding objects identified by a **PathID** (a
64-bit number).

- **References between objects** are stored as (file, PathID). File 0 means "inside this
  bundle"; other numbers point into an **external file** list (other bundles' CAB names).
- **Dependencies:** if a material in your bundle points at a shader in another bundle, that
  other bundle must be loaded first. SPT does this from `dependencyKeys` in `bundles.json`
  (e.g. `"shaders"`).
- **The game's shared bundles:** vanilla items don't carry their own shaders or reflection
  cubemaps. They point into the game's shared bundles:

  | Game bundle (key in `bundles.json`) | Internal name | Example object |
  |---|---|---|
  | `shaders` | `CAB-56d919bd5479d38f741da52a6beef92f` | `p0/Reflective/Bumped Specular SMap` = PathID `6014991791773097075` |
  | `cubemaps` | `CAB-4d8a4131cf377709ee7c7e960f65d349` | cubemap used by the RK-1 = PathID `972550011776207695` |

  These are from the SPT 4.1.6 game files and may change after a game update.
- **Textures, materials and cubemaps** can safely be built into your own bundle.
  **Shaders must point at the game's own copy**; see "Shaders" below.
- **Tools:** `tools/inspect_bundle.py` prints everything above for any bundle. UnityPy (Python)
  can read and edit bundles; AssetStudio and UABEA are Windows GUI tools for the same.

## Building bundles in Unity

- **AssetBundle labels** (bottom of the Inspector) decide which bundle each asset goes into. A label
  on a folder applies to everything inside it, even though each file's own box still says None. A
  label set on a file overrides its folder's label.
- **Unlabelled assets** that a labelled prefab uses (materials, textures) are pulled into that
  prefab's bundle automatically.
- **An asset used from a different bundle** becomes a dependency, listed under `Dependencies:`
  in the `.manifest` Unity writes next to each bundle. Always check the manifest after a build:
  `Assets:` is what's inside, `Dependencies:` is what it needs.
- **Label name and variant:** our bundles use name `houndgrip` + variant `bundle`, giving
  `houndgrip.bundle`. Every asset in one bundle must use the same name *and* variant, or the build
  fails ("can't exist in the same build as ... has the variant").
- **Unity builds every labelled bundle in the project** on each build, including the SDK's
  examples. Only copy your own `.bundle` into the mod.

## The SDK (EscapeFromTushonka-SDK)

<https://github.com/S3RAPH-1M/EscapeFromTushonka-SDK>: a Unity 2022.3.43f1 project preset for
Tarkov. It contains look-alike copies of Tarkov's scripts (PreviewPivot, GripPose, ...) and
shaders, so things look right in the editor, plus a custom AssetBundles window
(Configure / Build / Inspect / PathID Replacer / CabID Replacer).

**The replacer step.** Because the SDK's shaders are copies, a fresh build points at the SDK's
`shaders` bundle, which doesn't exist in the game. After each build the SDK rewrites every
reference using two lookup tables in `Assets/Packages/Custom AssetBundles-Browser/`:

- `path_data.json`: SDK PathID -> game PathID. For SMap the SDK ships
  `4203229473038756442 -> 6014991791773097075`.
- `cab_data.json`: SDK CAB name -> game CAB name. For `shaders`:
  `1dc8d26be8722a766953ce9d8a444e8c -> 56d919bd5479d38f741da52a6beef92f`.

Quirks we hit:

- **The output path must be relative to the SDK project** (e.g. `AssetBundles`). With an absolute
  path like `C:/Users/...` the replacer crashes with `DirectoryNotFoundException` and the bundle
  stays unconverted (purple in game).
- **The output folder can't share its name with a bundle.** Unity names its index file after the
  folder, so a folder called `HoundGrip` clashes with `houndgrip.bundle`.
- **In this project, SMap builds with PathID `3868700100545724512`**, not the table's
  `4203229473038756442`, so the replacer skipped it. We added the entry
  `3868700100545724512 -> 6014991791773097075` in the PathID Replacer tab (ADD ENTRY, SAVE DATA TO
  FILE). Any other shader that comes out purple needs the same treatment; `tools/inspect_bundle.py`
  shows the PathID your build used.
- **Adding PreviewPivot logs a NullReferenceException** (`PreviewPivot.OnValidate`) until you run
  its **Apply Default Settings**. Harmless.
- **PreviewPivot's Apply Default Settings** centres the pivot correctly but sets the icon camera to
  Euler 0, 245, 0. The vanilla RK-1 uses 0, 245, 180 (same angle, rolled 180°). Copy the vanilla
  item's icon rotation. Icons are cached in `%TEMP%\Battlestate Games\EscapeFromTarkov\Icon Cache`.
- The SDK's SMap has its slider labels swapped: Inspector **"Specularness"** is `_Glossness`
  (shine strength) and **"Glossness"** is `_Specularness` (highlight tightness).

## Shaders: purple, white, right

| What you see | Why |
|---|---|
| **Purple** | The material points at a shader the game can't find, usually the SDK's `shaders` bundle that the replacer didn't convert. |
| **White / washed out** | The SDK's shader copy was built into your bundle (shader labelled into it). It runs but doesn't work with Tarkov's renderer. |
| **Doge box** | The game couldn't load the bundle or the prefab at all: path mismatch, or a dependency not in `bundles.json`. |
| **Textured, like vanilla** | Material points at the game's shader (`CAB-56d919bd...` / `6014991791773097075` for SMap) and `bundles.json` lists `"shaders"`. |

If the SDK's replacer can't be made to work, `tools/fix_eft_shaders.py` does the same conversion
by shader name, using the game's own `shaders` bundle.

## SMap material values

`p0/Reflective/Bumped Specular SMap` is the shader vanilla weapon parts use. It's a specular/gloss
shader (older than the metal/roughness shaders modern games like MW2022 use), so ripped textures
need these values tuned. Values are multipliers on the textures, not replacements for them.

| Inspector label | Property | Effect |
|---|---|---|
| Main Color | `_Color` | Multiplies the diffuse texture (overall brightness/tint). |
| Base (RGB) Specular (A) | `_MainTex` | Diffuse colour; **alpha is the specular mask**. |
| GlossMap | `_SpecMap` | Gloss texture. |
| Normalmap | `_BumpMap` | Normal map. |
| Specular Color | `_SpecColor` | Tint/brightness of the shine. |
| "Specularness" | `_Glossness` | Shine strength. |
| "Glossness" | `_Specularness` | Highlight tightness (high = sharp metal, low = soft rubber). |
| Reflection Color / Reflection Cubemap | `_ReflectColor` / `_Cube` | Reflection strength / what is reflected. **A cubemap must be assigned.** |
| Specular Vals / Diffuse Vals | `_SpecVals` / `_DefVals` | Internal tuning; copy vanilla. |
| _StencilType | `_StencilType` | Hands (2) for weapon parts. |

Vanilla RK-1 B-25U: Main Color 0.755 grey, Specular Color 0.849 grey, "Specularness" 2,
"Glossness" 1.08, Reflection Color 0.603 grey / alpha 0.5, Spec Vals and Diffuse Vals
(1, 0.5, 0, 0), textures with Aniso Level 5.

## Ripped textures (MW2022 / COD)

How MW2019/MW2022 pack their textures (as split by Scobalula's GameImageUtil):

| COD image | What's in it | GameImageUtil mode |
|---|---|---|
| Colour DDS (looks partly transparent) | Albedo and specular colour fused; **alpha = metal mask**, and in metal areas the RGB is the metal's shine colour | CoD Specular/Albedo (Infinite Warfare/Modern Warfare) |
| "Green" DDS (NOG) | Normal (hemi-octahedron encoded), gloss, occlusion | CoD Normal/Gloss/Occlusion (Infinite Warfare/Modern Warfare) |

The WW2 mode splits a different layout and puts the wrong data into "AO" and "roughness".

Where COD's PBR data ends up in SMap (which has no metallic or roughness slots): metalness →
darker diffuse plus strong specular in the diffuse's alpha; specular colour → that specular value;
gloss → `_gloss` (COD already stores gloss, the inverse of roughness); normal → `_normal`;
occlusion → multiplied into the diffuse.

**MW3 (2023)**, checked on the Hound 9G's files: same packing as MW2022. Its rip had three BC7 DDS per
material: the fused colour; a NOG named "normals" (it looks purple-ish raw because R gloss ≈ 94,
G ≈ 127, B occlusion ≈ 249, but the normal is still packed in G and A); and a "green" image whose B
and A are exact complements (B + A = 255) with one grayscale map split between R and G by those
masks, a material/wear mask that SMap doesn't use.

GameImageUtil's formulas (ported into `tools/smap-texture-converter.html`), with channels 0–1:

- **Fused colour:** metal `m = clamp((A − 0.1) / 0.9)`, insulator reflectance `r = min(A, 0.1)`;
  albedo = RGB × (1 − m); specular = max(r + m × RGB, 0.21) per channel (0.21 ≈ 54/255). The
  specular can exceed 1 and must be clamped.
- **NOG:** gloss = R, occlusion = B; normal from G and A (hemi-octahedron):
  `nx = 2G − 1, ny = 2A − 1; x = (nx + ny)/2, y = (nx − ny)/2, z = 1 − |x| − |y|`, then normalise.

GameImageUtil reads DDS through DirectXTex (a native Windows library). The browser converter has
its own DDS reader instead (BC1–BC5, BC7 and uncompressed; ported from bcdec), so DDS files can be
dropped in directly. MW3 (2023) runs on the same engine as MW2022 and is assumed to pack the same way.

Converting to SMap (specular/gloss): metal has (almost) no diffuse colour and gets its colour as
specular; non-metal gets a low specular around 56/255 (4% reflectance). COD stores **gloss**, which is
what SMap wants (roughness = 1 − gloss). AO is multiplied into the diffuse. COD normals are DirectX,
so flip green. SMap's specular is a single grey value (diffuse alpha) and its reflections are dim, so
fully black metal looks like black patches; keep 20–35% of the colour on metal.

- Normal maps: set Texture Type to **Normal map**. COD uses the DirectX convention, so the green
  channel must be flipped exactly once: either in the converter (its Flip green, on by default for
  NOG) or with Unity's **Flip Green Channel**, never both.
- The vanilla RK-1's textures: diffuse sRGB, normal linear (Normal map type), **gloss sRGB**. Keep
  gloss on sRGB to match.
- Set **Aniso Level 5** like vanilla, and click Apply after changing import settings.
- COD's packed metal/roughness maps don't map one-to-one onto SMap's specular/gloss inputs; tune
  the material values in game, starting from a vanilla part made of similar material.
- If a texture looks scrambled, check the UVs. On this grip they were correct, not flipped.
- **Normals** tell the shader which way each point of the surface faces, for lighting. Separately,
  the **winding order** of each triangle decides which side is drawn (the back is culled). A port
  can end up with correct winding (looks solid) but inverted normals (lit inside-out: dark where it
  should be lit, highlights and seams in the wrong places). The Hound 9G had exactly that. Rotating
  can't fix it. Unity's Normals: Calculate fixes the direction but replaces the original smoothing,
  and a baked normal map only matches the normals it was baked against, so Calculate causes
  artifacts. Reversing the original normals (Blender, `tools/blender_flip_custom_normals.py`) keeps
  them matched.
