## prompts

1. Get information

Here is what i want to do, I want to build a tool to make an audio book out of a pdf book provided

steps:

- Extract text from the PDF in very systematic way
- Split the text into chapters or sections
- Convert the text to speech using a TTS engine
- Save the audio files in a structured format
- Allow users to navigate through chapters or sections ( follow the index of the book and map it to the timestamps of the audio files, will be saved in the metadata of the audio files or a json file in the output folder)

2. Process implementation

- 1. take path of pdf as input
- 2. Move the pdf to `io/input_pool/book` folder
- 3. Convert the pdf to text using `pdfminer` and save it in `io/input_pool/book_text`
- 4. Split the text into chapters using `nltk` and save each chapter in `io/input_pool/chapter`
- 5. Convert each chapter to audio using `kokoro` and save it in `io/input_pool/chapter_audio`
- 6. Merge all chapter audio files into a single audio file using `pydub` and save it in `io/output_pool/book_audio`
- 7. Create a metadata file in `io/output_pool/metadata` with the book title, author, and other details
- 8. Create a timestamp file in `io/output_pool/timestamps` with the start and end times of each chapter
- 9. Move the final audio file and metadata file to `io/output_pool/book`
