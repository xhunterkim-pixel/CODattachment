"""
Point the materials in an SDK-built bundle at the game's real shaders.

The SDK either embeds its own copy of an EFT shader (renders white in game) or points at the
SDK's own "shaders" bundle (renders purple in game). Vanilla items point at the game's shaders
bundle instead. This script rewrites each material's shader reference to the game's shader with
the same name, so your item renders like a vanilla one.

Usage (from a terminal, Python 3.9+ with UnityPy installed: pip install UnityPy):

    python fix_eft_shaders.py <your.bundle> [more.bundle ...] --game-shaders "<SPT>\\EscapeFromTarkov_Data\\StreamingAssets\\Windows\\shaders"

--game-shaders is only needed the first time (and after a game update): the shader list it reads
is cached in game_shaders.json next to this script. After that:

    python fix_eft_shaders.py <your.bundle>

The original bundle is kept as <your.bundle>.bak. Your mod's bundles.json must list "shaders" in
dependencyKeys for every bundle this script patches.
"""

import argparse
import json
import os
import shutil
import sys

import UnityPy

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_shaders.json")


def shader_name(obj):
    return obj.read_typetree()["m_ParsedForm"]["m_Name"]


def load_shader_table(bundle_path):
    """Map shader name -> (CAB name, path id) for every shader in a bundle."""
    table = {}
    env = UnityPy.load(bundle_path)
    for obj in env.objects:
        if obj.type.name == "Shader":
            table[shader_name(obj)] = (obj.assets_file.name, obj.path_id)
    return table


def game_shader_table(game_shaders):
    if game_shaders:
        print(f"Reading game shaders from {game_shaders} (this can take a minute)...")
        table = load_shader_table(game_shaders)
        with open(CACHE, "w") as f:
            json.dump(table, f, indent=1)
        print(f"Cached {len(table)} game shaders in {CACHE}")
        return {k: tuple(v) for k, v in table.items()}
    if not os.path.exists(CACHE):
        sys.exit("No game shader list yet: run once with --game-shaders pointing at the game's shaders bundle.")
    with open(CACHE) as f:
        return {k: tuple(v) for k, v in json.load(f).items()}


def sdk_shader_names(bundle_path):
    """(CAB, path id) -> shader name for the SDK's own shaders bundle next to the built bundle, if any."""
    names = {}
    sibling = os.path.join(os.path.dirname(os.path.abspath(bundle_path)), "shaders")
    if os.path.isfile(sibling):
        for name, ref in load_shader_table(sibling).items():
            names[ref] = name
    return names


def patch(bundle_path, game):
    env = UnityPy.load(bundle_path)
    objects = list(env.objects)
    sf = objects[0].assets_file
    local = {o.path_id: o for o in objects}
    sdk = sdk_shader_names(bundle_path)

    def external_index(cab):
        for i, ext in enumerate(sf.externals):
            if os.path.basename(ext.path) == cab:
                return i + 1
        ext = type(sf.externals[0]).__new__(type(sf.externals[0])) if sf.externals else None
        if ext is None:
            sys.exit("Bundle has no external table to copy; rebuild it with at least one material.")
        ext.path, ext.temp_empty, ext.guid, ext.type = f"archive:/{cab}/{cab}", "", b"\x00" * 16, 0
        sf.externals.append(ext)
        return len(sf.externals)

    game_names = {ref: name for name, ref in game.items()}
    repointed = {}
    for obj in objects:
        if obj.type.name != "Material":
            continue
        mat = obj.read_typetree()
        ref = mat["m_Shader"]
        if ref["m_FileID"] and (os.path.basename(sf.externals[ref["m_FileID"] - 1].path), ref["m_PathID"]) in game_names:
            print(f"  {mat['m_Name']}: already uses the game's shader")
            continue
        if ref["m_FileID"] == 0:
            name = shader_name(local[ref["m_PathID"]]) if ref["m_PathID"] in local else None
        else:
            cab = os.path.basename(sf.externals[ref["m_FileID"] - 1].path)
            name = sdk.get((cab, ref["m_PathID"]))
        if name is None:
            print(f"  {mat['m_Name']}: can't tell which shader it uses, left as is")
            continue
        if name not in game:
            print(f"  {mat['m_Name']}: '{name}' isn't a game shader, left as is")
            continue
        cab, path_id = game[name]
        new = {"m_FileID": external_index(cab), "m_PathID": path_id}
        if ref == new:
            print(f"  {mat['m_Name']}: already uses the game's '{name}'")
            continue
        repointed[(ref["m_FileID"], ref["m_PathID"])] = new
        mat["m_Shader"] = new
        obj.save_typetree(mat)
        print(f"  {mat['m_Name']}: now uses the game's '{name}'")

    if not repointed:
        print("Nothing to change.")
        return

    for obj in objects:
        if obj.type.name == "AssetBundle":
            ab = obj.read_typetree()
            for entry in ab["m_PreloadTable"]:
                new = repointed.get((entry["m_FileID"], entry["m_PathID"]))
                if new:
                    entry.update(new)
            for new in repointed.values():
                cab = os.path.basename(sf.externals[new["m_FileID"] - 1].path).lower()
                if cab not in ab["m_Dependencies"]:
                    ab["m_Dependencies"].append(cab)
            obj.save_typetree(ab)

    shutil.copyfile(bundle_path, bundle_path + ".bak")
    with open(bundle_path, "wb") as f:
        f.write(env.file.save(packer="lz4"))
    print(f"Saved {bundle_path} (original kept as .bak). Make sure bundles.json lists \"shaders\" in dependencyKeys.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("bundles", nargs="+", help="bundle(s) built by the SDK")
    parser.add_argument("--game-shaders", help="the game's shaders bundle (EscapeFromTarkov_Data/StreamingAssets/Windows/shaders)")
    args = parser.parse_args()

    game = game_shader_table(args.game_shaders)
    for path in args.bundles:
        print(path)
        patch(path, game)


if __name__ == "__main__":
    main()
