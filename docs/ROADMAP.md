# Roadmap: from side grips to a whole MW2023 gun

Goal: port a complete weapon from Call of Duty: Modern Warfare III (2023) into SPT, with its
animations and sounds. Each level adds one new thing you haven't done yet, so when something
breaks there is only one new suspect. Tick items off and record what you learned in the docs.

**Rule for every level:** pick the vanilla item closest to what you're porting, run
`tools/inspect_bundle.py` on it, and copy its structure. That rule solved almost every grip problem.

Levels 3 and up go into parts of Tarkov we haven't looked inside yet; what's written there is the
plan, **not verified**. Expect to inspect vanilla bundles first and correct these notes.

## Level 1: Finish and prove the grip workflow

- [ ] Hound 9G: flip its normals (Blender script, grip + rail), grip Main Color 221, Vals 1, 1, 0, 0.
- [ ] Tune both grips' hands in game until they match the RK-1.
- [ ] Sell both from a trader (item JSON `addtoTraders`, `traders`).
- [ ] **Challenge:** port a third side grip using only `docs/TUTORIAL.md`, without asking. Note every
  place the guide was unclear and fix the guide.

## Level 2: Other attachments that need hands or nothing new

- [ ] **Vertical foregrip** (a different hand pose). Generate the hands from a vanilla vertical grip
  with `tools/make_handpose_script.py`, clone that grip's ID.
- [ ] **Muzzle device** (no hands at all). New: `mod_muzzle` slot, and how the muzzle flash point
  sits on the model.
- [ ] **Pistol grip or stock** (right hand / shoulder). New: right-hand pose, other slot types.

## Level 3: Attachments that hold other attachments

- [ ] **Mount or handguard with its own slots** (e.g. a rail section that takes a grip).
  New: empty child objects named after the slots (`mod_foregrip`, …) in the prefab, and `Slots` in
  the item JSON listing what fits. Compare with a vanilla handguard's hierarchy and JSON.
- [ ] **Challenge:** put your Hound 9G on your own handguard on a vanilla gun.

## Level 4: Optics

- [ ] **Red dot sight.** New: the reticle (a special BSG shader/material), the aim point the camera
  lines up with, and how scopes with magnification render. Hardest attachment type; inspect a
  vanilla red dot first.

## Level 5: Magazines and ammo

- [ ] **Magazine** for a vanilla gun. New: cartridges shown in the mag, capacity, which ammo fits,
  the magazine-out/in animations of the vanilla gun must still line up with your model.

## Level 6: A whole gun, with a vanilla gun's animations

The standard way to add a gun: model is new, **animations and sounds are borrowed from a vanilla
gun of the same kind** (e.g. an AR from the M4A1).

- [ ] Inspect the vanilla gun's bundle: hierarchy (bones and `mod_*` slot points, fire port,
  ejection port, aim camera), components, which animation and sound bundles it depends on.
- [ ] Rig your MW3 gun's model to the same bone names so the vanilla animations move its parts
  (bolt, trigger, magazine, charging handle).
- [ ] Item JSON: clone the vanilla gun (caliber, fire modes, recoil, ergonomics), its slots, a preset.
- [ ] **Challenge:** fire, reload and inspect your gun in raid with the vanilla animations.

## Level 7: Sounds

- [ ] Find how a vanilla gun's sounds are set up (sound bundles, the components that pick shot /
  tail / indoor-outdoor sounds) with `inspect_bundle.py` on its audio bundles.
- [ ] Rip the MW3 gun's sounds, build your own sound bundle the same way, point your gun at it.

## Level 8: The gun's own MW3 animations

The hardest part, and the one most modders skip.

- [ ] Rip the MW3 viewmodel animations (arms + gun).
- [ ] Retarget them in Blender from COD's arm rig to Tarkov's arm rig.
- [ ] Rebuild the gun's animator so BSG's code still triggers them (fire, reload, inspect, …) and
  the animation events (mag out, mag in, bolt) fire at the right moments.

## Tools to build along the way (ask Claude)

- `inspect_bundle.py` for guns: list `mod_*` slots, animators, audio and their dependencies.
- A bundle diff: your prefab's hierarchy next to the vanilla one, highlighting missing bones.
- Hand-pose scripts for other vanilla items (`make_handpose_script.py` already does any item).
