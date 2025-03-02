# Content Generator from Videos

This project is an automated tool for analyzing social media videos (TikTok, Instagram, etc.) and generating structured content from them. The system downloads videos, extracts audio, captures key frames, and uses generative AI models to analyze and create content based on these videos.

## Features

- Download videos from platforms like TikTok and Instagram
- Extract audio from videos
- Capture key frames
- Content analysis using generative AI (Gemini, OpenAI)
- Generation of summaries, transcriptions, and analysis
- Export results to Excel

## Requirements

- Python 3.8+
- FFmpeg (for audio/video processing)
- Google Gemini or OpenAI API Key

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd content-creation
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file and add your API keys.

## Usage

1. Place the video URLs in the `data/input/links.txt` file, one URL per line.

2. Run the program:
   ```
   python main.py
   ```

3. Results will be saved in the `data/output/` folder, organized by video.

## Project Structure

```
content-creation/
├── app/                    # Main application code
│   ├── controllers/        # Business logic controllers
│   ├── services/           # Services for different functionalities
│   └── models/             # Data models
├── config/                 # Application configuration
├── data/                   # Input and output data
│   ├── input/              # Input files (links.txt)
│   └── output/             # Generated results
├── jobs/                   # Main jobs and processes
├── logs/                   # Log files
├── .env.example            # Template for environment variables
├── main.py                 # Main entry point
└── requirements.txt        # Project dependencies
```

## Main Dependencies

- python-dotenv: Environment variable management
- google-generativeai: Google Gemini API
- langchain: Framework for AI applications
- ffmpeg-python: Audio and video processing
- pandas/openpyxl: Data manipulation and export

## Configuration

The `.env` file allows you to configure:
- API keys for AI models (Gemini, OpenAI)
- Selection of the AI provider to use
- Specific model to use for analysis

## License

[Specify the project license]

## Contributions

[Instructions for contributing to the project]