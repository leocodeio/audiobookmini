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

def process_book(pdf_path, thumbnail_path, device='auto', use_amp=None, precision='auto', voice='af_heart', lang_code='a', speed=1.0, output_format='mp3'):
    """Process a PDF file into an audiobook.

    Parameters mirror CLI options so they can be overridden.
    """
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
        extract_book(
            input_book_path,
            use_toc=True,
            extract_mode="chapters",
            output_dir=book_text_dir,
            progress_callback=lambda p: print(f"Extraction progress: {p}%") if p is not None else None
        )
        print("Text extraction completed")

        # Step 4-5: Generate audio for chapters
        chapter_audio_dir = 'io/input_pool/chapter_audio'
        book_name = os.path.splitext(filename)[0]

        # Generate audio with provided voice/lang/device settings
        generated_files = generate_audiobooks_kokoro(
            input_dir=book_text_dir,
            lang_code=lang_code,
            voice=voice,
            device=device,
            output_dir=chapter_audio_dir,
            progress_callback=lambda p, f, i, t: print(f"Audio generation: {p:.2f}%") if p is not None else None,
            use_amp=use_amp,
            precision=precision,
            speed=speed
        )
        if not generated_files:
            print("No chapter audio generated; aborting output processing.")
            return False
        print("Audio generation completed")

        # Step 6: Process output (merge + metadata handled in output module)
        process_output(
            thumbnail_path,
            chapter_audio_dir,
            book_name,
            output_base_dir='io/output_pool',
            format=output_format
        )
        print("Output processing completed")

        return True

    except Exception as e:
        print(f"Error processing book: {e}")
        return False

def main():
    """Main entry point with CLI arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="Convert a PDF into an audiobook using Kokoro TTS.")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("thumbnail", help="Path to the thumbnail image for metadata/cover")
    parser.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu", "mps"], help="Computation device preference (default: auto)")
    parser.add_argument("--precision", default="auto", choices=["auto", "fp32", "fp16", "bf16"], help="Requested precision (default: auto)")

    amp_group = parser.add_mutually_exclusive_group()
    amp_group.add_argument("--amp", dest="use_amp", action="store_true", help="Force enable automatic mixed precision")
    amp_group.add_argument("--no-amp", dest="use_amp", action="store_false", help="Force disable automatic mixed precision")
    parser.set_defaults(use_amp=None)  # None => auto policy

    parser.add_argument("--voice", default="af_heart", help="Kokoro voice identifier (e.g., af_heart, am_liam)")
    parser.add_argument("--lang", default="a", help="Kokoro language code matching the voice (default: a)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed multiplier (default: 1.0)")
    parser.add_argument("--format", choices=["mp3", "wav"], default="mp3", help="Final merged audiobook audio format (default: mp3)")

    args = parser.parse_args()

    pdf_path = args.pdf
    thumbnail_path = args.thumbnail

    print(f"Processing PDF: {pdf_path}")
    print(f"Processing Thumbnail: {thumbnail_path}")
    print(f"Options: device={args.device}, precision={args.precision}, use_amp={args.use_amp}, voice={args.voice}, lang={args.lang}, speed={args.speed}, format={args.format}")

    ensure_directories()

    if process_book(
        pdf_path,
        thumbnail_path,
        device=args.device,
        use_amp=args.use_amp,
        precision=args.precision,
        voice=args.voice,
        lang_code=args.lang,
        speed=args.speed,
        output_format=args.format,
    ):
        print("Processing completed successfully")
    else:
        print("Processing failed")
        sys.exit(1)
    
    

if __name__ == "__main__":
    main()