# Made by MikuYoshikage

import logic
from pathlib import Path
from PIL import Image
import subprocess

def collect_track() -> logic.Track:
    
    while True:
        track_id = input("Enter track ID (lowercase separated by underscores, 50 characters max): ")
        if not logic.is_valid_id(track_id):
            print("Track ID must only contain lowercase letters and underscores. Please try again.")
            continue
        break
    while True:
        track_name = input("Enter track name: (50 characters max, English letters and spaces only, (- & ') are allowed): ")
        if not logic.is_english_text(track_name):
            print("Track name must only contain English letters and spaces. Please try again.")
            continue
        break
    while True:
        sound_path = input("Enter path to sound file (without quotes, .ogg or .mp3 only): ")
        if not Path(sound_path).exists():
            print(f"Sound file '{sound_path}' does not exist. Please try again.")
            continue
        if Path(sound_path).suffix.lower() not in [".ogg", ".mp3"]:
            print("Sound file must be in .ogg or .mp3 format. Please try again.")
            continue
        break
    while True:
        texture_path = input("Enter path to texture file (without quotes, .png only, 16x16 or 64x64 pixels): ")
        if not Path(texture_path).exists():
            print(f"Texture file '{texture_path}' does not exist. Please try again.")
            continue
        if Path(texture_path).suffix.lower() != ".png":
            print("Texture file must be in .png format. Please try again.")
            continue
        try:
            with Image.open(texture_path) as image:
                if image.size not in [(16, 16), (64, 64)]:
                    print("Texture must be 16x16 or 64x64 pixels. Please try again.")
                    continue
        except Exception:
            print("Could not open the image. Please try again.")
            continue
        break

    print("\nYou entered:")
    print(f"Track ID: {track_id}")
    print(f"Track Name: {track_name}")
    print(f"Sound Path: {sound_path}")
    print(f"Texture Path: {texture_path}")
    while True:
        confirmation = input("Is this correct? (y/n): ").strip().lower()
        if confirmation == 'y':
            break
        elif confirmation == 'n':
            print("Let's try again.")
            return collect_track()
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
            continue
    return logic.Track(id=track_id, name=track_name, sound_path=sound_path, texture_path=texture_path)

def collect_mod() -> logic.Mod:
    while True:
        mod_id = input("Enter mod ID (lowercase separated by underscores, 50 characters max): ")
        if not logic.is_valid_id(mod_id):
            print("Mod ID must only contain lowercase letters and underscores. Please try again.")
            continue
        break
    while True:
        mod_name = input("Enter mod name (50 characters max, English letters and spaces only, (- & ') are allowed): ")
        if not logic.is_english_text(mod_name):
            print("Mod name must only contain English letters and spaces. Please try again.")
            continue
        break
    print("\nYou entered:")
    print(f"Mod ID: {mod_id}")
    print(f"Mod Name: {mod_name}")
    while True:
        confirmation = input("Is this correct? (y/n): ").strip().lower()
        if confirmation == 'y':
            break
        elif confirmation == 'n':
            print("Let's try again.")
            return collect_mod()
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
            continue
    print("\nNow let's add tracks to your mod (1..128)")
    tracks = []
    while True:
        add_track = input("Do you want to add a track? (y/n): ").strip().lower()
        if add_track == 'y':
            track = collect_track()
            if not logic.is_unique_track_id(tracks, track.id):
                print(f"Track ID '{track.id}' is already used. Please enter a unique track ID.")
                continue
            tracks.append(track)
            if len(tracks) >= 128:
                print("You have reached the maximum number of tracks (128).")
                break
        elif add_track == 'n':
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
    
    if len(tracks) == 0:
        print("You must add at least one track. Let's add a track.")
        track = collect_track()
        tracks.append(track)
    return logic.Mod(id=mod_id, name=mod_name, tracks=tracks)


def main():
    print("Welcome to the Mod Maker CLI!")
    print("This tool will help you create a Minecraft forge 1.20.1 mod with custom music discs.")
    print("Please follow the prompts to create your mod.")
    mod = collect_mod()
    print("\nGenerating mod files...")
    logic.Start_Create()
    print("Changing gradle settings...")
    logic.change_property(mod)
    print("Filling Java files...")
    logic.fill_java_placeholders(mod)
    print("Moving sound files...")
    failed_sounds = logic.move_records(mod)
    if failed_sounds:
        print(f"Failed to process the following sound files: {', '.join(failed_sounds)}")
        logic.delete_failed_sounds(failed_sounds, mod)
        if not mod.tracks:
            print("All tracks failed to process. Exiting.")
            return
    print("Moving texture files...")
    logic.move_textures(mod)
    print("Generating JSON files...")
    logic.generate_en_us_json(mod)
    logic.generate_models_item_jsons(mod)
    logic.generate_music_discs_json(mod)
    logic.generate_sounds_json(mod)
    print("Building the mod...")
    build_result = logic.build_mod()
    if build_result["success"]:
        print("Mod built successfully!")
        built_jar = logic.find_built_jar()
        if built_jar:
            print(f"Built JAR: {built_jar}")
        else:
            print("Could not find the built JAR file.")
    else:
        print("Mod build failed. See details below:")
        print("--- STDOUT ---")
        print(build_result["stdout"][-2000:])
        print("--- STDERR ---")
        print(build_result["stderr"][-1500:])
    
if __name__ == "__main__":
    main()