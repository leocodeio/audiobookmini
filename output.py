import os
import json
from pathlib import Path
from pydub import AudioSegment
from datetime import datetime
import shutil
import subprocess
from moviepy.editor import AudioFileClip, TextClip, CompositeVideoClip, ColorClip
import math
def merge_audio_files(chapter_audio_dir, output_file, format='wav'):
    """Merge multiple audio files into a single file while tracking chapter timestamps."""
    print(f"\n--- Merging Audio Files ---")
    
    # Validate directory
    if not os.path.isdir(chapter_audio_dir):
        raise ValueError(f"Audio directory not found: {chapter_audio_dir}")
    
    # First, check for both possible formats to handle potential mismatches
    wav_files = sorted([f for f in os.listdir(chapter_audio_dir) if f.endswith('.wav')])
    mp3_files = sorted([f for f in os.listdir(chapter_audio_dir) if f.endswith('.mp3')])
    
    # Use whichever format has files
    if mp3_files and not wav_files:
        audio_files = mp3_files
        actual_format = 'mp3'
    elif wav_files and not mp3_files:
        audio_files = wav_files
        actual_format = 'wav'
    else:
        # If both or neither exist, prefer the specified format
        audio_files = wav_files if format == 'wav' else mp3_files
        actual_format = format
    
    print(f"Found {len(audio_files)} {actual_format} files to merge")
    
    # Validate we have files to merge
    if not audio_files:
        print(f"Warning: Checking directory contents:")
        print("\n".join(os.listdir(chapter_audio_dir)))
        raise ValueError(f"No audio files found in {chapter_audio_dir}")
    
    timestamps = []
    combined = None
    current_position = 0  # In milliseconds
    
    for audio_file in audio_files:
        # Extract chapter info from filename
        chapter_info = os.path.splitext(audio_file)[0]
        
        # Load the audio file
        audio_path = os.path.join(chapter_audio_dir, audio_file)
        try:
            # Let pydub detect format automatically if possible
            chapter_audio = AudioSegment.from_file(audio_path)
        except Exception as e:
            print(f"Error loading {audio_file}: {e}")
            continue
            
        # Initialize or append
        if combined is None:
            combined = chapter_audio
        else:
            combined += chapter_audio
            
        # Record timestamp
        timestamp = {
            'chapter': chapter_info,
            'start_time': current_position / 1000.0,
            'end_time': (current_position + len(chapter_audio)) / 1000.0,
            'duration': len(chapter_audio) / 1000.0
        }
        timestamps.append(timestamp)
        
        current_position += len(chapter_audio)
        print(f"Added {audio_file} - Duration: {timestamp['duration']:.2f}s")
    
    if combined is None:
        raise ValueError("No audio files were successfully loaded")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Export in requested format
    print(f"Exporting combined audio to: {output_file}")
    export_format = os.path.splitext(output_file)[1].lstrip('.')
    combined.export(output_file, format=export_format)
    
    return timestamps

def create_metadata(book_name, timestamps, output_dir):
    """
    Create metadata and timestamp files for the audiobook.
    
    Args:
        book_name (str): Name of the book
        timestamps (list): List of chapter timestamp dictionaries
        output_dir (str): Directory to save metadata files
    """
    print(f"\n--- Creating Metadata ---")
    
    # Basic metadata structure
    metadata = {
        'book_name': book_name,
        'creation_date': datetime.now().isoformat(),
        'total_chapters': len(timestamps),
        'total_duration': timestamps[-1]['end_time'] if timestamps else 0,
        'format_version': '1.0'
    }
    
    # Save metadata
    metadata_file = os.path.join(output_dir, 'metadata', f'{book_name}_metadata.json')
    os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to: {metadata_file}")
    
    # Save timestamps
    timestamp_file = os.path.join(output_dir, 'timestamps', f'{book_name}_timestamps.json')
    os.makedirs(os.path.dirname(timestamp_file), exist_ok=True)
    with open(timestamp_file, 'w', encoding='utf-8') as f:
        json.dump({'chapters': timestamps}, f, indent=2)
    print(f"Saved timestamps to: {timestamp_file}")
    
    return metadata_file, timestamp_file

def organize_final_files(book_name, audio_file, metadata_file, timestamp_file, final_dir):
    """
    Move all final files to their designated output location.
    
    Args:
        book_name (str): Name of the book
        audio_file (str): Path to the merged audio file
        metadata_file (str): Path to the metadata JSON file
        timestamp_file (str): Path to the timestamp JSON file
        final_dir (str): Final output directory
    """
    print(f"\n--- Organizing Final Files ---")
    
    # Create final directory
    book_dir = os.path.join(final_dir, book_name)
    os.makedirs(book_dir, exist_ok=True)
    
    # Copy/move files to final location
    final_paths = []
    for src_file in [audio_file, metadata_file, timestamp_file]:
        if os.path.exists(src_file):
            dest_file = os.path.join(book_dir, os.path.basename(src_file))
            shutil.copy2(src_file, dest_file)
            final_paths.append(dest_file)
            print(f"Copied: {os.path.basename(src_file)}")
    
    return book_dir
    
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def ffmpeg_run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def create_full_video(audio_file, book_name, output_dir):
    """Create full video with audio and centered text."""
    audio = AudioFileClip(audio_file)
    duration = audio.duration
    
    # Create output path with extension
    output_path = os.path.join(output_dir, f"{book_name}_full.mp4")
    
    command = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=size=1920x1080:duration={duration}:color=black",
        "-i", audio_file,
        "-vf", f"drawtext=fontfile='{FONT}':text='{book_name}':fontsize=70:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264",
        "-c:a", "aac",
        output_path
    ]
    subprocess.run(command, check=True)
    return output_path

def create_shorts(audio_file, book_name, output_dir):
    """Create vertical shorts from audio."""
    audio = AudioFileClip(audio_file)
    duration = audio.duration
    os.makedirs(output_dir, exist_ok=True)
    n = math.ceil(duration/60)
    shorts_paths = []
    
    for i in range(n):
        start = i*60
        out = os.path.join(output_dir, f"{book_name}_short_{i+1}.mp4")
        vf = (
            f"drawtext=fontfile='{FONT}':text='PART {i+1}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=200,"
            f"drawtext=fontfile='{FONT}':text='{book_name}':fontsize=70:fontcolor=white:x=(w-text_w)/2:y=400,"
            f"drawtext=fontfile='{FONT}':text='Visit channel to listen to\\ncomplete audio book':fontsize=50:fontcolor=white:x=(w-text_w)/2:y=600:enable='gte(t,50)'"
        )
        cmd = (
            f"ffmpeg -y -f lavfi -i \"color=size=1080x1920:duration=60:color=black\" "
            f"-ss {start} -i \"{audio_file}\" -t 60 -vf \"{vf}\" "
            f"-c:v libx264 -preset fast -c:a aac \"{out}\""
        )
        ffmpeg_run(cmd)
        shorts_paths.append(out)
    
    return shorts_paths

def create_full_video_with_thumbnails(audio_file, thumbnail_file, book_name, output_dir):
    """Create full video with audio, thumbnail image, and centered text."""
    audio = AudioFileClip(audio_file)
    duration = audio.duration
    
    # Create output path with extension
    output_path = os.path.join(output_dir, f"{book_name}_full_thumbnail.mp4")
    
    command = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", thumbnail_file,
        "-i", audio_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,drawtext=fontfile='{FONT}':text='{book_name}':fontsize=70:fontcolor=white:x=(w-text_w)/2:y=h-150",
        output_path
    ]
    subprocess.run(command, check=True)
    return output_path

def process_output(thumbnail_path, chapter_audio_dir, book_name, output_base_dir='io/output_pool', format='wav'):
    """
    Process the chapter audio files into the final audiobook structure.
    
    Args:
        chapter_audio_dir (str): Directory containing individual chapter audio files
        book_name (str): Name of the book
        output_base_dir (str): Base directory for all output
        format (str): Audio format to use (wav or mp3)
    
    Returns:
        str: Path to the final book directory
    """
    try:
        # 1. Merge audio files
        merged_audio_file = os.path.join(output_base_dir, 'book_audio', f'{book_name}.{format}')
        timestamps = merge_audio_files(chapter_audio_dir, merged_audio_file, format)
        
        # 2. Create metadata and timestamp files
        metadata_file, timestamp_file = create_metadata(
            book_name, timestamps, output_base_dir
        )
        
        # 3. Organize final files
        final_book_dir = organize_final_files(
            book_name,
            merged_audio_file,
            metadata_file,
            timestamp_file,
            os.path.join(output_base_dir, 'book')
        )
        
        # 4. Generate full video
        # video_dir = os.path.join(output_base_dir, 'videos')
        # os.makedirs(video_dir, exist_ok=True)
        # video_path = create_full_video(merged_audio_file, book_name, video_dir)
        
        # 5. Generate shorts
        # shorts_dir = os.path.join(output_base_dir, 'shorts')
        # os.makedirs(shorts_dir, exist_ok=True)
        # shorts_paths = create_shorts(merged_audio_file, book_name, shorts_dir)

        # 6. Generate full video with thumbnail
        video_path = create_full_video_with_thumbnails(merged_audio_file, thumbnail_path, book_name, output_base_dir)
        
        print(f"\n=== Output Processing Complete ===")
        print(f"Final book directory: {final_book_dir}")
        print(f"Full video: {video_path}")
        # print(f"Shorts generated: {len(shorts_paths)}")
        return final_book_dir
        
    except Exception as e:
        print(f"Error processing output: {e}")
        raise