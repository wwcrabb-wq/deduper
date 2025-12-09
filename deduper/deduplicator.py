"""
Main deduplication logic.
"""

import shutil
from pathlib import Path
from typing import List, Tuple, Callable, Optional
from .scanner import scan_images, get_label_path, has_label_file
from .hasher import ImageHasher


class Deduplicator:
    """Handles the image deduplication process."""
    
    def __init__(self, input_folder: str, output_folder: str, 
                 similarity_threshold: float = 0.95):
        """
        Initialize the deduplicator.
        
        Args:
            input_folder: Path to input directory
            output_folder: Path to output directory
            similarity_threshold: Similarity threshold (0-1)
        """
        self.input_folder = Path(input_folder).resolve()
        self.output_folder = Path(output_folder).resolve()
        self.similarity_threshold = similarity_threshold
        self.hasher = ImageHasher()
        self.stopped = False
        
    def deduplicate(self, progress_callback: Optional[Callable] = None,
                   log_callback: Optional[Callable] = None) -> dict:
        """
        Perform deduplication process.
        
        Args:
            progress_callback: Function to call with progress updates (current, total)
            log_callback: Function to call with log messages
            
        Returns:
            Dictionary with statistics about the process
        """
        self.stopped = False
        
        # Log start
        if log_callback:
            log_callback("Starting deduplication process...")
            log_callback(f"Input: {self.input_folder}")
            log_callback(f"Output: {self.output_folder}")
            log_callback(f"Threshold: {self.similarity_threshold * 100:.1f}%")
        
        # Scan for images
        if log_callback:
            log_callback("\nScanning for images...")
        
        try:
            images = scan_images(str(self.input_folder))
        except Exception as e:
            if log_callback:
                log_callback(f"Error scanning directory: {e}")
            return {'error': str(e)}
        
        if not images:
            if log_callback:
                log_callback("No images found in input directory.")
            return {'total_images': 0, 'unique_images': 0, 'duplicates_removed': 0}
        
        if log_callback:
            log_callback(f"Found {len(images)} images")
        
        # Compute hashes
        if log_callback:
            log_callback("\nComputing image hashes...")
        
        image_hashes = []
        for idx, (abs_path, rel_path) in enumerate(images):
            if self.stopped:
                if log_callback:
                    log_callback("\nProcess stopped by user.")
                return {'stopped': True}
            
            if progress_callback:
                progress_callback(idx + 1, len(images) * 2)  # First half of progress
            
            hash_value = self.hasher.compute_hash(abs_path)
            if hash_value is not None:
                image_hashes.append((abs_path, rel_path, hash_value))
        
        if log_callback:
            log_callback(f"Successfully hashed {len(image_hashes)} images")
        
        # Find duplicates
        if log_callback:
            log_callback("\nIdentifying duplicates...")
        
        unique_images = []
        duplicates = []
        
        for idx, (abs_path, rel_path, current_hash) in enumerate(image_hashes):
            if self.stopped:
                if log_callback:
                    log_callback("\nProcess stopped by user.")
                return {'stopped': True}
            
            if progress_callback:
                progress_callback(len(images) + idx + 1, len(images) * 2)  # Second half
            
            is_duplicate = False
            for _, _, unique_hash in unique_images:
                if self.hasher.are_similar(current_hash, unique_hash, 
                                          self.similarity_threshold):
                    is_duplicate = True
                    duplicates.append((abs_path, rel_path))
                    if log_callback:
                        log_callback(f"Duplicate found: {rel_path}")
                    break
            
            if not is_duplicate:
                unique_images.append((abs_path, rel_path, current_hash))
        
        # Copy unique images to output
        if log_callback:
            log_callback(f"\nCopying {len(unique_images)} unique images to output...")
        
        copied_count = 0
        for abs_path, rel_path, _ in unique_images:
            if self.stopped:
                if log_callback:
                    log_callback("\nProcess stopped by user.")
                return {'stopped': True}
            
            try:
                # Create output path maintaining directory structure
                output_path = self.output_folder / rel_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy image
                shutil.copy2(abs_path, output_path)
                copied_count += 1
                
                # Copy label file if it exists
                label_path = get_label_path(abs_path)
                if Path(label_path).exists():
                    output_label_path = get_label_path(str(output_path))
                    shutil.copy2(label_path, output_label_path)
                    if log_callback:
                        log_callback(f"Copied: {rel_path} (with label)")
                else:
                    if log_callback:
                        log_callback(f"Copied: {rel_path}")
                        
            except Exception as e:
                if log_callback:
                    log_callback(f"Error copying {rel_path}: {e}")
        
        # Summary
        stats = {
            'total_images': len(images),
            'unique_images': len(unique_images),
            'duplicates_removed': len(duplicates),
            'copied_files': copied_count
        }
        
        if log_callback:
            log_callback("\n" + "=" * 50)
            log_callback("SUMMARY")
            log_callback("=" * 50)
            log_callback(f"Total images scanned: {stats['total_images']}")
            log_callback(f"Unique images: {stats['unique_images']}")
            log_callback(f"Duplicates removed: {stats['duplicates_removed']}")
            log_callback(f"Files copied: {stats['copied_files']}")
            log_callback("=" * 50)
            log_callback("\nDeduplication complete!")
        
        return stats
    
    def stop(self):
        """Stop the deduplication process."""
        self.stopped = True
