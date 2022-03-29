from unittest import mock, TestCase

from elasticsearch import Elasticsearch
from milvus import Milvus


def mock_elastic_init():
    return


def mock_milvus_init():
    return


class TestImgMatch(TestCase):
    @mock.patch.object(Elasticsearch, "__init__", side_effect=mock_elastic_init)
    @mock.patch.object(Milvus, "__init__", side_effect=mock_elastic_init)
    def test_add_image_by_path(self, init_elastic):
        pass
        # TODO: implement
        # img_match = ImgMatch()
        # image_path = 'tests/static/sample_img.jpg'

    @mock.patch.object(Elasticsearch, "__init__", side_effect=mock_elastic_init)
    @mock.patch.object(Milvus, "__init__", side_effect=mock_elastic_init)
    def test_add_image_by_img_object(self, init_elastic):
        pass
        # TODO: implement
        # img_match = ImgMatch()
