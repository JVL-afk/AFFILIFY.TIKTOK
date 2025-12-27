#!/usr/bin/env python3
"""
Music Assignment Helper
=======================
Automatically assigns available music files to video clips.

This script:
1. Finds all music files in music directory
2. Finds all video clips
3. Randomly assigns music to clips (can reuse same music)
4. Creates symlinks or copies with matching names

Usage:
    python3 assign_music_to_clips.py --clips-dir data/batch_output/split --music-dir data/music
"""

import os
import sys
import random
import shutil
import argparse
from pathlib import Path
from typing import List

def find_music_files(music_dir: Path) -> List[Path]:
    """Find all music files in directory."""
    extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.aac']
    music_files = []
    
    for ext in extensions:
        music_files.extend(music_dir.glob(f"*{ext}"))
    
    return sorted(music_files)

def find_clip_files(clips_dir: Path) -> List[Path]:
    """Find all video clip files."""
    return sorted(clips_dir.glob("*.mp4"))

def assign_music_to_clips(clips_dir: str, music_dir: str, method: str = "random"):
    """
    Assign music files to video clips.
    
    Args:
        clips_dir: Directory containing video clips
        music_dir: Directory containing music files
        method: Assignment method ("random", "sequential", "single")
    """
    clips_dir = Path(clips_dir)
    music_dir = Path(music_dir)
    
    # Find files
    music_files = find_music_files(music_dir)
    clip_files = find_clip_files(clips_dir)
    
    if not music_files:
        print(f"❌ ERROR: No music files found in {music_dir}")
        print(f"   Supported formats: .mp3, .wav, .m4a, .ogg, .aac")
        sys.exit(1)
    
    if not clip_files:
        print(f"❌ ERROR: No video clips found in {clips_dir}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"MUSIC ASSIGNMENT")
    print(f"{'='*70}")
    print(f"Found {len(music_files)} music files")
    print(f"Found {len(clip_files)} video clips")
    print(f"Method: {method}")
    print(f"{'='*70}\n")
    
    # Show available music
    print("Available music:")
    for i, music_file in enumerate(music_files, 1):
        print(f"  {i}. {music_file.name}")
    print()
    
    # Assign music based on method
    assignments = []
    
    if method == "single":
        # Use first music file for all clips
        music_file = music_files[0]
        print(f"Using '{music_file.name}' for ALL clips\n")
        
        for clip_file in clip_files:
            assignments.append((clip_file, music_file))
    
    elif method == "sequential":
        # Cycle through music files sequentially
        print("Assigning music sequentially...\n")
        
        for i, clip_file in enumerate(clip_files):
            music_file = music_files[i % len(music_files)]
            assignments.append((clip_file, music_file))
    
    else:  # random
        # Randomly assign music files
        print("Assigning music randomly...\n")
        
        for clip_file in clip_files:
            music_file = random.choice(music_files)
            assignments.append((clip_file, music_file))
    
    # Create copies with matching names
    print("Creating music copies with matching names...")
    success_count = 0
    
    for clip_file, music_file in assignments:
        # Create music file with same name as clip
        clip_stem = clip_file.stem
        music_ext = music_file.suffix
        target_music = music_dir / f"{clip_stem}{music_ext}"
        
        try:
            # Copy music file
            shutil.copy2(music_file, target_music)
            print(f"  ✅ {clip_file.name} → {music_file.name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {clip_file.name}: {e}")
    
    print(f"\n{'='*70}")
    print(f"ASSIGNMENT COMPLETE")
    print(f"{'='*70}")
    print(f"Successfully assigned: {success_count}/{len(clip_files)}")
    print(f"{'='*70}\n")
    
    if success_count == len(clip_files):
        print("✅ All clips now have matching music files!")
        print(f"\nNext step:")
        print(f"  python3 add_music_to_clips.py \\")
        print(f"    --clips-dir {clips_dir} \\")
        print(f"    --music-dir {music_dir} \\")
        print(f"    --output-dir data/final_clips \\")
        print(f"    --volume 0.3")
    else:
        print("⚠️  Some clips failed to get music assigned")
        sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Assign music files to video clips"
    )
    parser.add_argument(
        '--clips-dir',
        required=True,
        help='Directory containing video clips'
    )
    parser.add_argument(
        '--music-dir',
        required=True,
        help='Directory containing music files'
    )
    parser.add_argument(
        '--method',
        choices=['random', 'sequential', 'single'],
        default='random',
        help='Assignment method (default: random)'
    )
    
    args = parser.parse_args()
    
    assign_music_to_clips(
        clips_dir=args.clips_dir,
        music_dir=args.music_dir,
        method=args.method
    )

if __name__ == "__main__":
    main()
