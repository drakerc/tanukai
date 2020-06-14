import uuid
from typing import Tuple, Optional

import cv2
import numpy as np


class SubImageNotFound(Exception):
    pass


class ImageFinder:
    # TODO: scale the smaller and larger images somehow

    def __init__(self, similarity_threshold: int = 60):
        self.similarity_threshold = similarity_threshold
        self.method = cv2.TM_CCOEFF_NORMED

    def get_marked_found_image(self, small_image: np.ndarray, large_image: np.ndarray) -> Optional[str]:
        """
        Finds a smaller image in a larger image and writes its similarity percentage on it
        and marks its bounding box.
        :return: Path to the image with bounding box
        """
        try:
            x_coordinate, y_coordinate, similarity = self.find_image(small_image, large_image)
        except SubImageNotFound as e:
            return None
        similarity_text = f'{similarity}%'

        position = (20, 80)
        cv2.putText(
            large_image,
            similarity_text,
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            2,  # font size
            (209, 80, 0, 255),  # font color
            3  # font stroke
        )

        # Get the size of the template. This is the same size as the match.
        trows, tcols = small_image.shape[:2]

        # Draw the rectangle on large_image
        cv2.rectangle(large_image, (x_coordinate, y_coordinate), (x_coordinate + tcols, y_coordinate + trows), (0, 0, 255), 2)
        unique_filename = str(uuid.uuid4())
        path = f'static/matched/{unique_filename}.jpg'
        cv2.imwrite(path, large_image)
        return path

    def find_image(self, small_image: np.ndarray, large_image: np.ndarray) -> Tuple[float, float, str]:
        """
        Finds a smaller sub-image in a larger image.
        Throws an Exception if not found.
        :return: Tuple of 3 values: x coordinate of bounding box, y coordinate and
        similarity percentage
        """
        try:
            result = cv2.matchTemplate(small_image, large_image, self.method)
        except Exception as e:
            raise SubImageNotFound  # todo: do something
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        x_coordinate, y_coordinate = max_loc

        percentage_similarity = max_val * 100
        if percentage_similarity < self.similarity_threshold:
            raise SubImageNotFound
        return x_coordinate, y_coordinate, str(format(percentage_similarity, '.2f'))
