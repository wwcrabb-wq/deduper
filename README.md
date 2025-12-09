# Image Deduplication Tool

A Python-based image deduplication tool with a graphical user interface (GUI) that helps you identify and remove duplicate or similar images from datasets while preserving associated label files.

## Features

- **Recursive Directory Scanning**: Automatically scans through all subdirectories to find images
- **Perceptual Hashing**: Uses difference hashing (dHash) for efficient and accurate duplicate detection
- **Label Preservation**: Maintains YOLO format label files (.txt) alongside deduplicated images
- **Folder Structure Preservation**: Maintains the exact same directory structure in output
- **Adjustable Similarity Threshold**: Control how similar images need to be to be considered duplicates
- **Real-time Progress Tracking**: Progress bar and ETA display
- **User-Friendly GUI**: Simple tkinter-based interface
- **Comprehensive Format Support**: Supports all Ultralytics-compatible image formats

## Supported Image Formats

- BMP (.bmp)
- DNG (.dng)
- JPEG (.jpeg, .jpg)
- MPO (.mpo)
- PNG (.png)
- TIFF (.tif, .tiff)
- WebP (.webp)
- PFM (.pfm)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/wwcrabb-wq/deduper.git
cd deduper
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

Launch the GUI application:

```bash
python main.py
```

### Using the GUI

1. **Select Input Folder**: Click "Browse..." next to "Input Folder" and select the directory containing your dataset with images and labels

2. **Select Output Folder**: Click "Browse..." next to "Output Folder" and choose where you want the deduplicated dataset to be saved

3. **Adjust Similarity Threshold**: Use the slider to set the similarity threshold (50-100%):
   - **95-100%**: Only removes very similar/identical images (recommended)
   - **85-95%**: Moderate similarity detection
   - **50-85%**: Aggressive deduplication (may remove variations)

4. **Start Processing**: Click "Start Deduplication" to begin

5. **Monitor Progress**: Watch the progress bar, ETA, and status log for real-time updates

6. **Stop if Needed**: Click "Stop" to cancel the operation at any time

### Example Workflow

```
Input Folder Structure:
dataset/
├── images/
│   ├── img1.jpg
│   ├── img1.txt (label)
│   ├── img2.jpg
│   ├── img2.txt (label)
│   ├── img3.jpg (duplicate of img1)
│   └── subfolder/
│       ├── img4.png
│       └── img4.txt (label)

Output Folder Structure (after deduplication):
output/
├── images/
│   ├── img1.jpg
│   ├── img1.txt (label)
│   ├── img2.jpg
│   ├── img2.txt (label)
│   └── subfolder/
│       ├── img4.png
│       └── img4.txt (label)
```

## How It Works

1. **Scanning**: The tool recursively scans the input folder for all supported image formats

2. **Hashing**: Each image is processed to create a perceptual hash using difference hashing (dHash), which captures the essential visual structure of the image

3. **Comparison**: Images are compared against each other using Hamming distance to identify duplicates

4. **Selection**: When duplicates are found, the first encountered image is kept as the representative

5. **Copying**: Unique images and their associated label files are copied to the output folder while maintaining the original directory structure

## Algorithm Details

- **Hashing Method**: Difference Hash (dHash) with 8x8 hash size
- **Similarity Metric**: Normalized Hamming distance converted to similarity score (0-1)
- **Duplicate Detection**: Images with similarity above threshold are marked as duplicates
- **Representative Selection**: First encountered image is kept when duplicates are found

## Edge Cases Handled

- Empty input folders
- Corrupted or unreadable images (skipped with error message)
- Missing label files (image is still processed)
- Nested directory structures
- Mixed image formats

## Troubleshooting

### "No images found in input directory"
- Ensure your input folder contains supported image formats
- Check that file extensions match supported formats

### "Error processing image"
- Some images may be corrupted or in an unsupported variant
- These images are skipped and logged; check the status log

### Application won't start
- Verify Python version: `python --version` (must be 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Project Structure

```
deduper/
├── main.py                 # Entry point
├── deduper/
│   ├── __init__.py        # Package initialization
│   ├── gui.py             # GUI implementation
│   ├── scanner.py         # File scanning functionality
│   ├── hasher.py          # Image hashing and comparison
│   └── deduplicator.py    # Main deduplication logic
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Requirements

See `requirements.txt` for specific versions:
- Pillow: Image processing library
- imagehash: Perceptual hashing library

## License

This project is open source and available for use.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Credits

Built using:
- [Pillow](https://python-pillow.org/) for image processing
- [imagehash](https://github.com/JohannesBuchner/imagehash) for perceptual hashing
- tkinter for GUI (included with Python)