import os

from PIL import Image

from drawsearch.drawsearch_image import DrawsearchImage

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"]="0"

import glob
import time
from elasticsearch import Elasticsearch
from milvus import Milvus, IndexType, MetricType, Status
import config
from img_match.img_match import ImgMatch
from img_match.models.image import Image as Img

# Vector parameters
_DIM = 1024  # dimension of vector
_INDEX_FILE_SIZE = 32  # max file size of stored index

milvus = Milvus(config.milvus_host, config.milvus_port, pool_size=10)
collection_name = config.milvus_collection_name
es = Elasticsearch(
            config.elasticsearch_host,
            verify_certs=config.elasticsearch_verify_certs
        )


# Img.init(using=es)
image_match = ImgMatch()


# if __name__ == '__main__':
#     # _create_index()
#     status = milvus.drop_collection(collection_name)
#     time.sleep(5)
#     status, ok = milvus.has_collection(collection_name)
#     if not ok:
#         param = {
#             'collection_name': collection_name,
#             'dimension': _DIM,
#             'index_file_size': _INDEX_FILE_SIZE,  # optional
#             'metric_type': MetricType.L2  # optional
#         }
#
#         milvus.create_collection(param)
#     images_length = len(sorted(glob.glob('static/media/kkosinski/linux/imgs/*/*/*')))
#     start = time.time()
#     for index, img_path in enumerate(sorted(glob.glob('static/media/kkosinski/linux/imgs/*/*/*'))):
#         print(f'{index} out of {images_length}')
#         try:
#             image_match.add_image(img_path)
#         except Exception as e:
#             print(e)
#             continue
#     done = time.time()
#     elapsed = done - start
#     print(elapsed)
#     # milvus.compact(collection_name=config.milvus_collection_name, timeout='1')


image_path = 'e621/c8/a1/c8a1ebcc453f8a8ed7bd20333c5610be1f7b5d1f.jpg'
pil_image = Image.open(f"{config.images_path}/full/{image_path}")
image_match.add_image(
    path=image_path,
    img=pil_image,
    image_model=DrawsearchImage,
    source_website='x',
    source_url='y',
    source_id=321321,
    source_created_at="2020-06-11T14:27:26.124000-04:00",
    source_tags={"general": [
        "abs",
        "anthro",
        "armband",
        "beach",
        "biceps",
        "biped",
        "detailed_background",
        "fur",
        "genitals",
        "green_eyes",
        "hair",
        "lifeguard",
        "long_hair",
        "male",
        "multicolored_body",
        "multicolored_fur",
        "muscular",
        "muscular_male",
        "nipples",
        "pecs",
        "penis",
        "seaside",
        "striped_body",
        "striped_fur",
        "striped_tail",
        "stripes",
        "tan_body",
        "tan_fur",
        "text",
        "two_tone_body",
        "two_tone_fur"
    ],
        "species": [
            "felid",
            "mammal",
            "pantherine",
            "tiger"
        ],
        "character": [
            "pang"
        ],
        "copyright": [
            "sdorica",
            "sdorica_sunset"
        ],
        "artist": [
            "eurobeat"
        ],
        "meta": [
            "2020",
            "absurd_res",
            "english_text",
            "hi_res"
        ]
    },
    source_rating='explicit',
    source_description='e',
    source_image_url='f'
)









