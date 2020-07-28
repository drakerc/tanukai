from img_match.img_match import ImgMatch
from tanukai.services.img_match.queries.tanukai_image_queries import TanukaiImageQueries


class TanukaiImgMatch(ImgMatch):

    def __init__(self):
        super().__init__()
        self._image_queries = TanukaiImageQueries()
