# Instructions for AI assistants

This repo adds custom weapon attachments (ported from Call of Duty) to SPT 4.1.6 (single-player
Escape from Tarkov). The user builds bundles in Unity on Windows and tests in game; you usually
can't run either, so work from the files they upload and the tools below.

## Read first

- `docs/TUTORIAL.md`: the full step-by-step workflow (rip → textures → Unity → bundle → game). Keep it
  in sync when a step changes.
- `docs/HOW_IT_WORKS.md`: how SPT, Unity, bundles, the SDK and shaders fit together, and every
  pitfall found so far.
- `docs/ADDING_A_GRIP.md`: the step-by-step checklist and troubleshooting table.
- `docs/GRIPS.md`: per-grip record (IDs, values that worked, history, open items).

## Keep the docs current (required)

After **every** fix or new finding, before you finish your turn, update the docs in the same commit:

- the grip's section in `docs/GRIPS.md` (values that changed, a line in its history, open items),
- the checklist or troubleshooting table in `docs/ADDING_A_GRIP.md` if the fix applies to future grips,
- `docs/HOW_IT_WORKS.md` if you learned how something works,
- `docs/TUTORIAL.md` if a step of the workflow changed.

Write down what was wrong, how it showed up, and what fixed it, so it never has to be rediscovered.

## Ground rules

- **Never guess IDs, paths or values from memory.** Vanilla item IDs come from the user's handbook
  or `SPT_Data/database/templates/items.json`. Material, hierarchy and hand-pose values come from
  the vanilla bundle via `tools/inspect_bundle.py`. A remembered ID once made us clone the wrong grip.
- **Compare with the vanilla item** whenever something looks or behaves wrong. Ask the user to upload
  the vanilla bundle and their built bundle, and diff them with `tools/inspect_bundle.py`. That found
  most of the fixes so far.
- Say plainly when something is unverified (e.g. values computed from meshes but not tested in game).
- The user is learning; explain in plain terms and give exact field names and values for Unity.

## Tools (Python 3 + `pip install UnityPy`)

| Tool | Use |
|---|---|
| `tools/inspect_bundle.py <bundle>` | Dump dependencies, hierarchy + components, materials (shader references), textures, mesh bounds, inverted-normals check. |
| `tools/fix_eft_shaders.py <bundle> [--game-shaders <game shaders bundle>]` | Repoint materials at the game's shaders (fixes purple/white) when the SDK's replacer can't. |
| `tools/make_handpose_script.py <vanilla.bundle> <Name> <out.cs>` | Generate a Unity editor script that copies a vanilla item's hand poses. |
| `tools/blender_flip_custom_normals.py` | Blender script: reverse inverted normals while keeping the original smoothing. |
| `unity/AddSideGripHandPoses.cs` | Generated hand poses of the RK-1 B-25U side grip. |
| `unity/GripPoseGizmos.cs` | Draws GripPose hands (palm box + finger bones) in Unity's Scene view. |
| `tools/smap-texture-converter.html` | Browser page: COD textures → SMap diffuse (spec in alpha), gloss, normal. Reads DDS (BC1–5, BC7) or PNG. Includes GameImageUtil's MW fused-colour and NOG splits (GPL-3 port; NOG route wrong on the MW3 DDS, open) and an MW3 preset for GameImageUtil-split PNGs. |

## Key facts

- Server mod: C# on .NET 10, NuGet `SPTushonka.*` 4.1.6 + `WTT-ServerCommonLib` 3.0.6, load order
  `OnLoadOrder.Preload + 2`. Items are JSON in `db/CustomItems/`, cloned from vanilla.
- `Prefab.path` in the item JSON = `key` in `bundles.json` = file path under `bundles/`.
- Every bundle that uses SMap needs `"dependencyKeys": ["shaders"]`.
- Game SMap shader: `CAB-56d919bd5479d38f741da52a6beef92f`, PathID `6014991791773097075`.
- SDK: <https://github.com/S3RAPH-1M/EscapeFromTushonka-SDK> (Unity 2022.3.43f1). Its replacer
  needs a relative output path and a table entry for every shader PathID the build produces.
- Prefabs need PreviewPivot (inspect view, icon) and GripPose hand poses (left hand); the hand is
  placed by IK at runtime, so the palm markers decide where it goes.
