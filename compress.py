import os
import subprocess
from PIL import Image
import re
import sys

# --- Configuration ---

# The base directory containing your media files.
# This script assumes it's run from the root of your project.
BASE_DIR = 'static/media'

# Define a backup directory. The script will save modified files here,
# preserving the original directory structure.
BACKUP_DIR = 'static/media_optimized'

# --- Media Processing Rules ---
# Each rule is a tuple: (regex_pattern, media_type, parameters)
# - regex_pattern: A regular expression to match file paths.
# - media_type: 'image' or 'video'.
# - parameters: A dictionary with settings for processing.
#   - For images: {'width': new_width_in_pixels}
#   - For videos: {'height': new_height_in_pixels, 'crf': Constant Rate Factor (23-28 is good for web)}

PROCESSING_RULES = [
    # Hero carousel thumbnails
    (r'hero/slide\d+/(src|edited)\.(png|jpe?g)$', 'image', {'width': 256}),
    
    # Hero carousel videos (resize to 720p height, good compression)
    (r'hero/slide\d+/ours\.mp4$', 'video', {'height': 720, 'crf': 28}),
    
    # Multi-View Gallery images (consistent thumbnail size)
    (r'mv-gallery/\d+/.*/.+\.(png|jpe?g)$', 'image', {'width': 300}),

    # Method overview image (larger, for detail)
    (r'method/method_fig2\.(png|jpe?g)$', 'image', {'width': 1024}),
    
    # A default rule for any other videos not matched above
    (r'.*\.mp4$', 'video', {'height': 720, 'crf': 28}),

    # A default rule for any other images not matched above
    (r'.*\.(png|jpe?g)$', 'image', {'width': 1280}),
]

def resize_image(input_path, output_path, width):
    """Resizes an image to a new width while maintaining aspect ratio."""
    try:
        with Image.open(input_path) as img:
            # Only resize if the image is wider than the target width
            if img.width > width:
                aspect_ratio = img.height / img.width
                new_height = int(width * aspect_ratio)
                
                print(f"  Resizing image to {width}x{new_height}...")
                # Note: Using Image.Resampling.LANCZOS for high-quality downscaling.
                # For older Pillow versions, this might be Image.LANCZOS.
                resized_img = img.resize((width, new_height), Image.Resampling.LANCZOS)
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Save with optimization
                if output_path.lower().endswith('.png'):
                    resized_img.save(output_path, 'PNG', optimize=True)
                else: # JPG/JPEG
                    resized_img.save(output_path, 'JPEG', quality=85, optimize=True, progressive=True)
            else:
                print("  Image is already small enough. Copying without resizing.")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                # Use a system command to copy to preserve metadata
                os.system(f'copy "{input_path}" "{output_path}"' if os.name == 'nt' else f'cp "{input_path}" "{output_path}"')

    except Exception as e:
        print(f"  Error processing image {input_path}: {e}")

        
def compress_video(input_path, output_path, height, crf):
    """Compresses and resizes a video using FFmpeg."""
    try:
        print(f"  Compressing video (target height: {height}p, CRF: {crf})...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # FFmpeg command
        # -vf "scale=-2:{height}": Resizes to the target height, width is auto-scaled to maintain aspect. '-2' ensures width is even.
        # -c:v libx264: The video codec.
        # -crf {crf}: Constant Rate Factor for quality/size balance.
        # -preset slow: A good balance of encoding time and compression efficiency.
        # -c:a aac -b:a 128k: Re-encodes audio to AAC at 128kbps.
        # -movflags +faststart: Optimizes for web streaming.
        # -y: Overwrite output file if it exists.
        command = [
            'ffmpeg',
            '-i', input_path,
            '-vf', f'scale=-2:{height}',
            '-c:v', 'libx264',
            '-crf', str(crf),
            '-preset', 'slow',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            '-y',
            output_path
        ]
        
        # Use DEVNULL for stdout/stderr to keep the console clean
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except FileNotFoundError:
        print("\n[ERROR] FFmpeg not found. Please ensure it is installed and in your system's PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print(f"  Error compressing video {input_path}. FFmpeg command failed.")
    except Exception as e:
        print(f"  An unexpected error occurred with video {input_path}: {e}")


def process_files():
    """Walks through the media directory and applies processing rules."""
    print(f"Starting media processing...")
    print(f"Source directory: '{BASE_DIR}'")
    print(f"Output directory: '{BACKUP_DIR}'\n")

    if not os.path.isdir(BASE_DIR):
        print(f"[ERROR] Source directory '{BASE_DIR}' not found. Exiting.")
        return

    processed_files = set()

    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            input_path = os.path.join(root, file)
            # Use forward slashes for regex matching, consistent across OS
            relative_path = os.path.relpath(input_path, BASE_DIR).replace('\\', '/')

            if input_path in processed_files:
                continue
            
            matched = False
            for pattern, media_type, params in PROCESSING_RULES:
                if re.match(pattern, relative_path):
                    print(f"Processing '{relative_path}' (Rule: {pattern})")
                    output_path = os.path.join(BACKUP_DIR, relative_path)

                    if media_type == 'image':
                        resize_image(input_path, output_path, **params)
                    elif media_type == 'video':
                        compress_video(input_path, output_path, **params)
                    
                    processed_files.add(input_path)
                    matched = True
                    break # Stop after the first rule matches
            
            if not matched:
                # If no rule matched, just copy the file
                print(f"Copying '{relative_path}' (No rule matched)")
                output_path = os.path.join(BACKUP_DIR, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                os.system(f'copy "{input_path}" "{output_path}"' if os.name == 'nt' else f'cp "{input_path}" "{output_path}"')


    print("\nMedia processing complete.")
    print(f"Optimized files are saved in the '{BACKUP_DIR}' directory.")
    print(f"Please review the files and then replace the original '{BASE_DIR}' directory with the new one.")


if __name__ == '__main__':
    # Add a confirmation step
    response = input(f"This script will process files from '{BASE_DIR}' and save them to '{BACKUP_DIR}'.\nDo you want to continue? (y/n): ")
    if response.lower() == 'y':
        process_files()
    else:
        print("Operation cancelled.")