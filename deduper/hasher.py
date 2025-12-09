"""
Image hashing and similarity comparison functionality.
"""

import imagehash
from PIL import Image
from typing import Dict, Optional


class ImageHasher:
    """Handles image hashing and similarity comparison."""
    
    def __init__(self, hash_size: int = 8):
        """
        Initialize the image hasher.
        
        Args:
            hash_size: Size of the perceptual hash (default 8x8)
        """
        self.hash_size = hash_size
        self.hashes: Dict[str, imagehash.ImageHash] = {}
    
    def compute_hash(self, image_path: str) -> Optional[imagehash.ImageHash]:
        """
        Compute perceptual hash for an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            ImageHash object or None if image cannot be processed
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                # Use difference hash (dHash) - good balance of speed and accuracy
                return imagehash.dhash(img, hash_size=self.hash_size)
        except Exception:
            # Return None on error; caller can handle logging
            return None
    
    def store_hash(self, image_path: str, hash_value: imagehash.ImageHash):
        """
        Store a computed hash for later comparison.
        
        Args:
            image_path: Path to the image file
            hash_value: Computed hash value
        """
        self.hashes[image_path] = hash_value
    
    def compute_similarity(self, hash1: imagehash.ImageHash, 
                          hash2: imagehash.ImageHash) -> float:
        """
        Compute similarity between two hashes.
        
        Args:
            hash1: First image hash
            hash2: Second image hash
            
        Returns:
            Similarity score between 0 and 1 (1 = identical)
        """
        if hash1 is None or hash2 is None:
            return 0.0
        
        # Hamming distance between hashes
        distance = hash1 - hash2
        
        # Maximum possible distance for the hash size
        max_distance = self.hash_size * self.hash_size
        
        # Convert to similarity (0-1 scale)
        similarity = 1.0 - (distance / max_distance)
        return similarity
    
    def are_similar(self, hash1: imagehash.ImageHash, 
                   hash2: imagehash.ImageHash, 
                   threshold: float) -> bool:
        """
        Check if two images are similar based on threshold.
        
        Args:
            hash1: First image hash
            hash2: Second image hash
            threshold: Similarity threshold (0-1)
            
        Returns:
            True if images are similar, False otherwise
        """
        similarity = self.compute_similarity(hash1, hash2)
        return similarity >= threshold
