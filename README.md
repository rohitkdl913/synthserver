# Subtitle Generation Server

## Overview
This project is a **FastAPI-based** server for generating subtitles from  video files. It processes media files, extracts audio, and generates subtitles using speech-to-text technology.

## Features
- Upload audio/video files for subtitle generation.
- Supports multiple file formats (MP4,WAV, etc.).
- Generates subtitles in standard formats (SRT).
- Provides an API for subtitle retrieval and download.

## Technologies Used
- **FastAPI** - Web framework for building APIs.
- **Pydantic** - Data validation and parsing.
- **FFmpeg** - Audio extraction from video files.
- **Whisper** (or any ASR model) - Speech-to-text conversion.


## Installation
### Prerequisites
- Python 3.8+
- FFmpeg installed

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/subtitle-server.git
   cd subtitle-server
   ```
2. Set up a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
### Running the Server
```sh
 fastapi run main.py
```

## License
MIT License.

## Contribution
Pull requests are welcome! Open an issue for discussions.

## Contact
For support, email: `kandelsaugat913@gmail.com`

