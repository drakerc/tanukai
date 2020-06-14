import abc

from PIL.Image import Image


class PerceptualHasher(abc.ABC):
    """
    Extracts a perceptual hash
    """

    def __init__(self, hash_size=16):
        self.hash_size = hash_size

    @abc.abstractmethod
    def get_hash(self, img: Image) -> str:
        """
        Returns a string with a perceptual hash
        :param img: Pillow Image
        :return: perceptual hash string
        """
        pass
