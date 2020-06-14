import imagehash
from PIL.Image import Image
from img_match.processing.perceptual_hasher import PerceptualHasher


class PHasher(PerceptualHasher):
    """
    Extracts a perceptual hash using the pHash
    """

    def __init__(self, hash_size=16):
        super().__init__(hash_size)

    def get_hash(self, img: Image) -> str:
        return str(imagehash.phash(img, hash_size=self.hash_size))
