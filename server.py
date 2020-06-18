from PIL import Image
from datetime import datetime
from flask import Flask, request, render_template

from img_match.img_match import ImgMatch
from img_match.queries.image_queries import ImageQueries

app = Flask(__name__)

image_match = ImgMatch()
image_queries = ImageQueries()


@app.route('/', methods=['GET', 'POST'])
def index():
    partitions = image_queries.get_partitions()
    if request.method == 'GET':
        return render_template('start.html', partitions=partitions)


@app.route('/search', methods=['GET', 'POST'])
def search():
    pagination_from = int(request.args.get('pagination_from', 0))
    pagination_size = int(request.args.get('pagination_size', 10))
    partition = request.form.get('partition', 'e621')
    partitions = image_queries.get_partitions()

    file = request.files.get('query_img')
    if file:
        img = Image.open(file.stream)  # PIL image
        uploaded_img_path = "static/uploaded/" + datetime.now().isoformat() + "_" + file.filename
        img.save(uploaded_img_path)
    else:
        uploaded_img_path = request.args.get('uploaded_img_path')
    results = image_match.search_image(uploaded_img_path, True, pagination_from, pagination_size, partition_tags=[partition])

    return render_template(
        'index.html',
        query_path=uploaded_img_path,
        scores=results,
        pagination_from=pagination_from,
        pagination_size=pagination_size,
        uploaded_img_path=uploaded_img_path,
        partition=partition,
        partitions=partitions
    )


@app.route('/search-by-id', methods=['GET'])
def search_by_id():
    image_id = int(request.args.get('image_id'))
    img_path = request.args.get('img_path')
    pagination_from = int(request.args.get('pagination_from', 0))
    pagination_size = int(request.args.get('pagination_size', 10))
    partition = request.form.get('partition', 'e621')
    partitions = image_queries.get_partitions()

    results = image_match.search_by_id(image_id, True, pagination_from, pagination_size, partition_tags=[partition])

    return render_template(
        'index.html',
        query_path=img_path,
        scores=results,
        pagination_from=pagination_from,
        pagination_size=pagination_size,
        uploaded_img_path=img_path,
        partition=partition,
        partitions=partitions
    )


if __name__ == "__main__":
    app.run("0.0.0.0", threaded=False)
