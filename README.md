# audiobookmini

A simple command-line tool to turn a PDF into a structured audiobook with chapter timestamps, merged audio, and optional video render.

## Features
- Extracts text from PDF (TOC-aware if available) and splits into chapters.
- Generates per‑chapter audio using Kokoro TTS (lightweight open model).
- Merges chapters into a single audiobook file with timestamp JSON.
- Produces metadata file (duration, chapters, creation date).
- Creates a full-length simple video with the book title overlaid (for sharing).
- Auto device + AMP selection (CUDA / MPS / CPU) with manual overrides.

## Installation
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Basic Usage
```bash
python main.py /path/to/book.pdf /path/to/thumbnail.png
```
The second argument is a thumbnail image used for the generated video.

## CLI Options
```
python main.py PDF THUMBNAIL [--device auto|cuda|cpu|mps] \
    [--precision auto|fp32|fp16|bf16] [--amp | --no-amp] \
    [--voice VOICE_ID] [--lang LANG_CODE] \
    [--speed FLOAT] [--format mp3|wav]
```

### Key Flags
- --device: Force computation device; default auto chooses best available.
- --precision: Hint for numeric precision; auto derives from device & AMP.
- --amp / --no-amp: Explicitly enable/disable mixed precision (otherwise policy decides).
- --voice: Kokoro voice (e.g. af_heart, am_liam, af_sarah...).
- --lang: Kokoro language code matching the voice (e.g. a=US English, b=UK English, j=Japanese...).
- --speed: Speech speed multiplier (1.0 = normal).
- --format: Final merged audiobook output format (mp3 or wav).

### Example
```bash
python main.py book.pdf cover.png \
  --device auto --precision auto --voice af_heart --lang a \
  --speed 1.05 --format mp3
```

## Output Structure
```
io/
  input_pool/
    book/              # Original PDFs
    book_text/         # Extracted chapter .txt files
    chapter_audio/     # Per-chapter WAV files
  output_pool/
    book_audio/        # Merged final audio (mp3 or wav)
    metadata/          # metadata JSON files
    timestamps/        # chapter timestamp JSON files
    book/              # Final packaged set per book
    # videos/ / shorts/ (optional future use)
```

## Metadata Files
- metadata: `<book_name>_metadata.json` (total duration, chapters count, creation date)
- timestamps: `<book_name>_timestamps.json` (start/end times per chapter)

## Notes
- Ensure `ffmpeg` is installed for video generation & mp3 handling.
- AMP + fp16/bf16 only active when the selected device supports it.
- If no chapters are produced (e.g. extraction failed) processing aborts safely.

## Roadmap / Ideas
- Optional retry in fp32 if AMP failure.
- Add chapter title normalization.
- Parallel chapter synthesis (batching) for speedups.
- Web UI wrapper.

## License
See LICENSE.md.
