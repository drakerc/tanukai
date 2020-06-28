import pickle
from typing import Callable, Tuple
from PIL import Image
import config
from img_match.processing.image_finder import ImageFinder
from img_match.processing.phasher import PHasher
from img_match.queries.image_queries import ImageQueries
from img_match.processing.feature_extractor import FeatureExtractor
import cv2
import numpy as np

class ImgMatch:

    def __init__(self):
        self._image_queries = ImageQueries()
        self._feature_extractor = FeatureExtractor()
        self._perceptual_hasher = PHasher(config.phash_size)
        self._image_finder = ImageFinder(similarity_threshold=60)

    def add_image(
            self,
            path: str,
            img: Image = None,
            add_perceptual_hash: bool = True,
            refresh_index: bool = False,
            image_model: Callable = Image,
            partition_tag: str = None,
            **image_kwargs
    ) -> str:
        """
        :param path: path to the image (on disk/URL)
        :param img: (Optional) PIL Image object. If specified, the image from path won't be loaded
        :param add_perceptual_hash: Add a perceptual hash to the index
        :param refresh_index: Refresh (reindex) the Elastic/Milvus index after adding the image.
        That guarantees that the image will be available immediately after adding, but it's slow
        :param image_model: Elasticsearch model to be persisted
        :param partition_tag: Which Milvus partition it should search in
        :param image_kwargs: Data about the added image
        """
        if not img:
            img = Image.open(path)
        feature_vectors = self._feature_extractor.get_features(img)
        perceptual_hash = None
        if add_perceptual_hash:
            perceptual_hash = self._perceptual_hasher.get_hash(img)
        saved_id = self._image_queries.save(
            feature_vectors,
            path,
            perceptual_hash,
            refresh_index,
            partition_tag,
            image_model,
            **image_kwargs
        )
        return saved_id

    def search_image(self, path: str, mark_subimage: bool = False, pagination_from: int = 0, pagination_size: int = 10, partition_tags: list = None) -> Tuple[dict, str]:
        img = Image.open(path)
        feature_vectors = self._feature_extractor.get_features(img)
        results = self._image_queries.find(feature_vectors, pagination_from, pagination_size, partition_tags=partition_tags)
        if mark_subimage:
            self._mark_subimage(path, results)
        return results, feature_vectors.dumps()

    def search_by_phash(self, path: str, mark_subimage: bool = False, pagination_from: int = 0, pagination_size: int = 10) -> dict:
        img = Image.open(path)
        perceptual_hash = self._perceptual_hasher.get_hash(img)
        results = self._image_queries.find_by_phash(perceptual_hash, pagination_from=pagination_from, pagination_size=pagination_size)
        if mark_subimage:
            self._mark_subimage(path, results)
        return results

    def search_by_id(self, image_id, mark_subimage: bool = False, pagination_from: int = 0, pagination_size: int = 10, partition_tags: list = None) -> dict:
        results = self._image_queries.find_by_id(image_id, pagination_from=pagination_from, pagination_size=pagination_size, partition_tags=partition_tags)
        # if mark_subimage:
        #     self._mark_subimage(path, results)
        return results

    def search_by_features(self, features: np.ndarray, mark_subimage: bool = False, pagination_from: int = 0, pagination_size: int = 10, partition_tags: list = None) -> dict:
        results = self._image_queries.find(features, pagination_from, pagination_size, partition_tags=partition_tags)
        if mark_subimage:
            pass
            # self._mark_subimage(path, results)
        return results

    def get_partitions(self):
        """
        Returns dict with partition data (partition_tag and count)
        :return: dict, e.g. {'ebay': 5213, 'etsy': 1233}
        """
        return self._image_queries.get_partitions()

    def _mark_subimage(self, path: str, results: dict, stop_on_first_match: bool = True) -> None:
        """
        Finds the searched image in the images returned from the database and marks them if the
        image is a subimage of a larger image.
        :param path: Path to the searched image
        :param results: Dictionary of all results
        :param stop_on_first_match: If true, it will stop trying to find the searched image after
        the first match
        """
        small_img = cv2.imread(path)
        scale_percent = 80
        width = int(small_img.shape[1] * scale_percent / 100)
        height = int(small_img.shape[0] * scale_percent / 100)
        dsize = (width, height)
        small_img = cv2.resize(small_img, dsize)
        for res in results.values():
            large_img = cv2.imread(res['thumbnail_path'])
            marked_image = self._image_finder.get_marked_found_image(small_img, large_img)
            if marked_image:
                res['thumbnail_path'] = marked_image
                if stop_on_first_match:
                    break
