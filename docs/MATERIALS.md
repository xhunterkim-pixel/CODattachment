# Material library

Typical SMap values of Tarkov's own weapon parts, measured from the game files (SPT 4.1.6,
`items/mods`: 2074 bundles, 1743 SMap materials) with `tools/build_material_library.py`.
Spreadsheet: [`material_library.csv`](material_library.csv) (raw tool output:
[`data/material_library_raw.csv`](data/material_library_raw.csv)). Every vanilla item's own values
(4398 materials, 2058 SMap) from `tools/dump_material_values.py`:
[`data/vanilla_materials.csv`](data/vanilla_materials.csv). Open it in Excel and filter `bundle`
(e.g. `foregrip_`) to copy one specific item.

## How to read it

In Tarkov **one material usually covers a whole item**: the RK-1's polymer grip and steel mount
share one material. So "plastic" vs "metal" is mostly decided by the **textures**, not the sliders.
The tool sorted every texture pixel by its specular value (the diffuse's alpha) into four kinds,
and for each kind reports:

- **Texture targets**: the average diffuse brightness, specular and gloss that Tarkov uses. Compare
  your converted textures with these (`dump_material_values.py --textures` on your bundle).
- **Slider values**: the most common Inspector values among items that are mostly that kind.

| Kind | Diffuse | Specular (alpha) | Gloss | "Specularness" | "Glossness" | Reflection Color | Cubemap | Sure? |
|---|---|---|---|---|---|---|---|---|
| Rubber / matte | 19 (0–25) | 11 (7–13) | 111 (72–144) | 2 | 1 | 180,180,180,128 | metall_matte | low (5 items) |
| **Polymer / plastic** | 35 (25–48) | 29 (22–36) | 137 (115–156) | **2** | **1** | 255,255,255,128 | **metall** | high (849) |
| **Coated metal** | 50 (34–71) | 62 (52–75) | 147 (130–164) | **1** | **1** | 102,102,102,128 | **metall** | high (486) |
| Bare / polished metal | 82 (46–125) | 124 (116–144) | 153 (135–173) | 1 | 1 | 0,0,0,128 | none (5/9) | low (9 items) |

Numbers are 0–255 medians, typical range (middle half of pixels) in brackets. All kinds mostly use
Main Color and Specular Color **255, 255, 255** and Specular/Diffuse Vals **1, 1, 0, 0**. The
"most used" slider values are only a majority for some columns (e.g. Main Color 255 is the most
common for polymer but only in 83 of 849 items); `mods.csv` from `dump_material_values.py` has
every item's values for a closer look.

## By attachment type

From `data/vanilla_materials.csv`, SMap materials only. Medians, "most used" for the rest. Nearly all
use Specular/Diffuse Vals **1, 1, 0, 0** and `_StencilType` Hands (2).

| Type (bundle prefix) | Items | "Specularness" | "Glossness" | Main Color | Cubemap (most → next) |
|---|---|---|---|---|---|
| **foregrip** | 59 | **1.0** | 1.0 | 221 | metall_matte 33, metall 24 |
| pistolgrip | 122 | 1.39 | 1.0 | 203 | metall_matte 73, metall 44 |
| stock | 264 | 1.5 | 1.0 | 210 | metall 137, metall_matte 115 |
| mount | 240 | 1.46 | 1.0 | 213 | metall 218 |
| handguard | 224 | 1.31 | 1.0 | 214 | metall 156, metall_matte 62 |
| mag | 228 | 1.71 | 1.0 | 202 | metall 149, metall_matte 74 |
| muzzle | 193 | 1.71 | 1.0 | 202 | metall 186 |
| barrel | 191 | 1.5 | 1.0 | 209 | metall 174 |
| sight | 122 | 1.5 | 1.0 | 202 | metall 105 |
| scope | 97 | 1.94 | 1.0 | 202 | metall 81 |
| reciever | 96 | 1.6 | 1.0 | 204 | metall 90 |
| silencer | 72 | 1.52 | 1.0 | 196 | metall 55, metall_matte 15 |
| tactical | 55 | 1.69 | 1.0 | 197 | metall_matte 28, metall 20 |
| gas block | 38 | 1.77 | 1.0 | 206 | metall 37 |

**Foregrips** in detail: half use "Specularness" 1.0 (Magpul M-LOK AFG, BCM MOD 3, Stark SE-5,
Strike Industries Cobra, Tango Down), the other half 1.3–2.0 (Zenit RK series 1.2–2.0, KAC 2.0,
HK Sturmgriff 2.0). "Glossness" 0.77–1.29, mostly 1.0. Reflection Color 89–255 (alpha 128), typical
~100–150. Specular Color 255 or ~200–220. The cubemap is always one of the SDK's: metall_matte or
metall (one uses brass_matte).

Foregrip counts (59): Specular Vals / Diffuse Vals pairs: **1,1,0,0 / 1,1,0,0 (41)**, 1,2,0,0 / 1,1,0,0
(7), 1,0.5,0,0 / 1,0.5,0,0 (5, incl. the RK-1 B-25U), 1,2,0,0 / 0.8,0.4,0,0 (5, Tango Down).
Specular Color: 255 (26), 221 (7), 204 (5), 128 (4); median 224. Reflection Color: median **129**
(alpha 128), range 89–255. What the second Vals number does exactly is unverified; the two are
nearly always set as a pair.

**Cubemaps across all 2058 SMap materials:** `patron_cubemap_metall` 1525, `patron_cubemap_metall_matte`
463, `brass_matte` 20, `brass` 9, none 19. Only 12 build their own (`patron_cubemap_studio`) and 10
use two game cubemaps the SDK doesn't have (PathIDs -6042237392288980436, -152504514492450513). So the
SDK's six cover 99% of attachments.

## What it tells us

- **The two cubemaps that matter are in the SDK**: `patron_cubemap_metall` (most polymer and
  coated-metal items) and `patron_cubemap_metall_matte` (the RK-1). No ripping needed for attachments.
- **For a material that covers both plastic and metal** (most items), use the polymer column's
  sliders; the metal parts get their shine from the texture's higher specular.
- **COD conversions are shinier in the texture than Tarkov**: GameImageUtil's non-metal specular
  floor is 0.21 = 54/255, about twice Tarkov's polymer (29). That's why the Hound 9G grip glowed
  at "Specularness" 2 and looks right at 1: 54 × 1 ≈ 29 × 2. Its gloss (94) is also lower than
  Tarkov polymer (137), so its highlight is broader.
- Single-material vanilla items like the RK-1 use **Specular/Diffuse Vals 1, 0.5, 0, 0**; the
  majority uses 1, 1, 0, 0. Unverified what the second value changes in game.

## Using it on a new attachment

1. Convert the textures (TUTORIAL Part 2).
2. Pick the row for what the material mostly is, and type its slider values into the material.
3. Compare your textures' averages with the row's targets. If your specular is about twice the
   target (typical for COD polymer), halve "Specularness" instead (2 → 1).
4. Tune in game next to a vanilla item made of the same stuff.
