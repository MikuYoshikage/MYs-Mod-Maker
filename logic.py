# Made by MikuYoshikage

from pydantic import BaseModel, field_validator
from pathlib import Path
from typing import List
import shutil
import json
import subprocess
import re
import os

PACKAGE_NAME = "com.miku.examplemod"
OS_NAME = os.name

class Track(BaseModel):
    id: str
    name: str
    texture_path: str
    sound_path: str

class Mod(BaseModel):
    id: str
    name: str
    tracks: List[Track]

def is_unique_track_id(tracks: List[Track], track_id: str) -> bool:
    return all(track.id != track_id for track in tracks)

def is_english_text(text):
    return len(text) <= 50 and bool(
        re.fullmatch(r"[A-Za-z]+(?:[ '-][A-Za-z]+)*", text)
    )


def is_valid_id(text):
    return len(text) <= 50 and bool(
        re.fullmatch(r"[a-z_]+", text)
    )

def clear_now_making():
    destination = Path("now_making")
    destination.mkdir(exist_ok=True)
    for item in destination.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

def Start_Create():
    source = Path("example")
    destination = Path("now_making")
    clear_now_making()
    for item in source.iterdir():
        if item.is_dir():
            shutil.copytree(item, destination / item.name)
        else:
            shutil.copy2(item, destination / item.name)

def change_property(mod: Mod):
    file_path = Path("now_making") / "gradle.properties"
    text = f"org.gradle.jvmargs=-Xmx3G\norg.gradle.daemon=false\nminecraft_version=1.20.1\nminecraft_version_range=[1.20.1,1.21)\nforge_version=47.4.22\nforge_version_range=[47,)\nloader_version_range=[47,)\nmapping_channel=official\nmapping_version=1.20.1\nmod_id={mod.id}\nmod_name={mod.name}\nmod_license=All Rights Reserved\nmod_version=1.0.0\nmod_group_id={PACKAGE_NAME}\nmod_authors=MikuYoshikage\nmod_description=This mod adds records to the game"
    with open(file_path, "w") as f:
        f.write(text)

def generate_track_ids_java(tracks: List[Track]) -> str:
    lines = [f'        "{track.id}"' for track in tracks]
    return ",\n".join(lines)

def fill_java_placeholders(mod: Mod):
    target = Path("now_making")

    replacements = {
        "{{MOD_ID}}": mod.id,
        "{{PACKAGE_NAME}}": PACKAGE_NAME,
        "{{TRACK_IDS_JAVA}}": generate_track_ids_java(mod.tracks),
    }

    for java_file in target.rglob("*.java"):
        content = java_file.read_text(encoding="utf-8")
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        java_file.write_text(content, encoding="utf-8")



def generate_sounds_json(mod: Mod):
    sounds = {}
    for track in mod.tracks:
        sounds[f"record.{track.id}"] = {
            "category": "record",
            "sounds": [
                {"name": f"{mod.id}:records/{track.id}", "stream": True}
            ]
        }

    target = Path("now_making") / "src/main/resources/assets" / mod.id / "sounds.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(sounds, f, indent=2, ensure_ascii=False)

def generate_en_us_json(mod: Mod):
    lang = {
        f"itemGroup.{mod.id}.{mod.id}_tab": mod.name
    }
    for track in mod.tracks:
        lang[f"item.{mod.id}.record_{track.id}"] = "Music Disc"
        lang[f"item.{mod.id}.record_{track.id}.desc"] = track.name

    target = Path("now_making") / "src/main/resources/assets" / mod.id / "lang/en_us.json"
    target.parent.mkdir(parents=True, exist_ok=True)  # ← додано
    with open(target, "w", encoding="utf-8") as f:
        json.dump(lang, f, indent=4)

def generate_models_item_jsons(mod: Mod):
    target_dir = Path("now_making") / "src/main/resources/assets" / mod.id / "models/item"
    target_dir.mkdir(parents=True, exist_ok=True)  # ← додано

    for track in mod.tracks:
        model = {
            "parent": "minecraft:item/generated",
            "textures": {
                "layer0": f"{mod.id}:item/record_{track.id}"
            }
        }
        with open(target_dir / f"record_{track.id}.json", "w", encoding="utf-8") as f:
            json.dump(model, f, indent=4)

def generate_music_discs_json(mod: Mod):
    vals = [f"{mod.id}:record_{track.id}" for track in mod.tracks]
    mdj = {"replace": False, "values": vals}

    target = Path("now_making") / "src/main/resources/data/minecraft/tags/items/music_discs.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(mdj, f, indent=4)


def move_records(mod: Mod) -> List[str]:
    target_dir = Path("now_making") / "src/main/resources/assets" / mod.id / "sounds/records"
    target_dir.mkdir(parents=True, exist_ok=True)
    failed = []
    for track in mod.tracks:
        source_path = Path(track.sound_path)
        output_path = target_dir / f"{track.id}.ogg"

        try:
            result = subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(source_path),
                    "-vn",
                    "-ac", "1",
                    "-ar", "44100",
                    "-c:a", "libvorbis",
                    "-q:a", "4",
                    str(output_path)
                ],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                failed.append(track.id)
        except FileNotFoundError:
            raise RuntimeError("ffmpeg is not installed or not found in PATH. Please install ffmpeg to process audio files.")

    return failed

def move_textures(mod: Mod):
    target_dir = Path("now_making") / "src/main/resources/assets" / mod.id / "textures/item"
    target_dir.mkdir(parents=True, exist_ok=True)

    for track in mod.tracks:
        source_path = Path(track.texture_path)
        output_path = target_dir / f"record_{track.id}.png"
        shutil.copy2(source_path, output_path)

def delete_failed_sounds(failed: List[str], mod: Mod):
    for track_id in failed:
        mod.tracks = [track for track in mod.tracks if track.id != track_id]

def find_built_jar() -> Path | None:
    jar_dir = Path("now_making/build/libs")
    if not jar_dir.exists():
        return None

    jars = [f for f in jar_dir.glob("*.jar") if "sources" not in f.name]
    return jars[0] if jars else None

def build_mod() -> dict:
    target_dir = Path("now_making")

    global OS_NAME

    if OS_NAME != "nt":
        gradlew = target_dir / "gradlew"
        os.chmod(gradlew, 0o755)
        command = [str(gradlew), "build"]
        result = subprocess.run(
                command,
                cwd=target_dir,
                capture_output=True,
                text=True
            )
    else:
        command = ["gradlew.bat", "build"]
        result = subprocess.run(
                command,
                cwd=target_dir,
                capture_output=True,
                text=True,
                shell=True
            )

    

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }