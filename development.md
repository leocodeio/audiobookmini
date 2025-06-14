# audiobookmini

## steps

- 1. take path of pdf as input
- 2. Move the pdf to `io/input_pool/book` folder
- 3. Convert the pdf to text using `pdfminer` and save it in `io/input_pool/book_text`
- 4. Split the text into chapters using `nltk` and save each chapter in `io/input_pool/chapter`
- 5. Convert each chapter to audio using `kokoro` and save it in `io/input_pool/chapter_audio`
- 6. Merge all chapter audio files into a single audio file using `pydub` and save it in `io/output_pool/book_audio`
- 7. Create a metadata file in `io/output_pool/metadata` with the book title, author, and other details
- 8. Create a timestamp file in `io/output_pool/timestamps` with the start and end times of each chapter
- 9. Move the final audio file and metadata file to `io/output_pool/book`

## file structure

```text
audiobookmini/

├── __init__.py
├── main.py
├── core/
│   └── __init__.py
├── services/
│   └── __init__.py
├── utils/
│   └── __init__.py
├── requirements.txt
├── .gitignore
├── README.md
├── development.md
├── contributing.md
└── LICENSE.md
```
