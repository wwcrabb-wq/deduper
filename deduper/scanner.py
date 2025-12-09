"""
Recursive file scanning functionality for image deduplication.
"""

import os
from pathlib import Path
from typing import List, Set, Tuple

# Supported image formats (Ultralytics-compatible)
SUPPORTED_FORMATS = {'.bmp', '.dng', '.jpeg', '.jpg', '.mpo', 
                     '.png', '.tif', '.tiff', '.webp', '.pfm'}


def scan_images(input_folder: str) -> List[Tuple[str, str]]:
    """
    Recursively scan input folder for images.
    
    Args:
        input_folder: Path to the input directory
        
    Returns:
        List of tuples containing (absolute_path, relative_path)
    """
    images = []
    input_path = Path(input_folder).resolve()
    
    if not input_path.exists():
        raise ValueError(f"Input folder does not exist: {input_folder}")
    
    for root, _, files in os.walk(input_path):
        for file in files:
            file_path = Path(root) / file
            ext = file_path.suffix.lower()
            
            if ext in SUPPORTED_FORMATS:
                abs_path = str(file_path)
                rel_path = str(file_path.relative_to(input_path))
                images.append((abs_path, rel_path))
    
    return images


def get_label_path(image_path: str) -> str:
    """
    Get the corresponding label file path for an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Path to the label file (with .txt extension)
    """
    return str(Path(image_path).with_suffix('.txt'))


def has_label_file(image_path: str) -> bool:
    """
    Check if a label file exists for the given image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        True if label file exists, False otherwise
    """
    label_path = get_label_path(image_path)
    return Path(label_path).exists()
