# Video Concatenator

A simple Python GUI application for concatenating multiple video files into a single MP4.

## Features

- Add multiple video files via a file picker dialog
- Reorder videos with Move Up / Move Down buttons or drag-and-drop
- Remove individual videos or clear the entire list
- Choose output file name and location
- Progress indicator during concatenation
- Supports common video formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM, and more

## Requirements

- Python 3.10+
- Windows, macOS, or Linux (tkinter must be available)

## Setup

```bash
# Clone the repo
git clone https://github.com/beknar/video-concatenate.git
cd video-concatenate

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/macOS

# Install dependencies
pip install moviepy
```

## Usage

```bash
python concatenate.py
```

1. Click **Add Videos** to select video files
2. Reorder them as needed using the buttons or by dragging
3. Set the output file name (defaults to `output.mp4`)
4. Click **Concatenate**

The output is encoded as H.264 video with AAC audio.

## License

MIT
