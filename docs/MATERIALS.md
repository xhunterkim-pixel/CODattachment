# Material library

Typical SMap values of Tarkov's own weapon parts, measured from the game files (SPT 4.1.6,
`items/mods`: 2074 bundles, 1743 SMap materials) with `tools/build_material_library.py`.
Spreadsheet: [`material_library.csv`](material_library.csv) (raw tool output:
[`data/material_library_raw.csv`](data/material_library_raw.csv)).

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
