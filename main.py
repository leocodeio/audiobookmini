import os
import sys
from pathlib import Path
from shutil import copy2
from core.services.extract import extract_book
from core.providers.kokoro import generate_audiobooks_kokoro
from output import process_output

def ensure_directories():
    """Create required directories if they don't exist."""
    directories = [
        'io/input_pool/book',
        'io/input_pool/book_text',
        'io/input_pool/chapter',
        'io/input_pool/chapter_audio',
        'io/output_pool/book_audio',
        'io/output_pool/metadata',
        'io/output_pool/timestamps',
        'io/output_pool/book'
    ]
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)

def process_book(pdf_path, thumbnail_path):
    """Process a PDF file into an audiobook."""
    if not os.path.exists(pdf_path):
        print(f"Error: File not found - {pdf_path}")
        return False

    try:
        # Step 1 & 2: Copy PDF to input pool
        filename = os.path.basename(pdf_path)
        input_book_path = os.path.join('io/input_pool/book', filename)
        copy2(pdf_path, input_book_path)
        print(f"Copied {filename} to input pool")

        # Step 3: Extract text from PDF
        book_text_dir = 'io/input_pool/book_text'
        extract_result = extract_book(
            input_book_path,
            use_toc=True,
            extract_mode="chapters",
            output_dir=book_text_dir,
            progress_callback=lambda p: print(f"Extraction progress: {p}%") if p else None
        )
        print("Text extraction completed")

        # Step 4-5: Generate audio for chapters
        chapter_audio_dir = 'io/input_pool/chapter_audio'
        book_name = os.path.splitext(filename)[0]
        
        # Configure Kokoro TTS
        voice = "af_heart"  # Default voice
        lang_code = "a"    # English
        
        # Generate audio
        generate_audiobooks_kokoro(
            input_dir=book_text_dir,
            output_dir=chapter_audio_dir,
            voice=voice,
            lang_code=lang_code,
            progress_callback=lambda p, f, i, t: print(f"Audio generation: {p}%") if p else None
        )
        print("Audio generation completed")
        
        # Step 6: Process output
        process_output(
            thumbnail_path,
            chapter_audio_dir,
            book_name,
            output_base_dir='io/output_pool',
            format='mp3'  # or 'wav' if preferred
        )
        print("Output processing completed")   

        return True

    except Exception as e:
        print(f"Error processing book: {e}")
        return False

def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python main.py <path_to_pdf> <path_to_thumbnail>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    print(f"Processing PDF: {pdf_path}")

    thumbnail_path = sys.argv[2]
    print(f"Processing Thumbnail: {thumbnail_path}")

    # Ensure all required directories exist
    ensure_directories()

    # Process the book
    if process_book(pdf_path, thumbnail_path):
        print("Processing completed successfully")
    else:
        print("Processing failed")
        sys.exit(1)
    
    

if __name__ == "__main__":
    main()