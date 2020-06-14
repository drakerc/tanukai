from PIL import Image
from datetime import datetime
from flask import Flask, request, render_template

from img_match.img_match import ImgMatch
app = Flask(__name__)

image_match = ImgMatch()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['query_img']
        img = Image.open(file.stream)  # PIL image
        uploaded_img_path = "static/uploaded/" + datetime.now().isoformat() + "_" + file.filename
        img.save(uploaded_img_path)

        # save_image = request.form.get('save_image', 'off')
        # if save_image == 'on':
        #     image_match.add_image(uploaded_img_path)
        # results = image_match.search_by_phash(uploaded_img_path, True)
        results = image_match.search_image(uploaded_img_path, True)

        return render_template(
            'index.html',
            query_path=uploaded_img_path,
            scores=results,
        )
    else:
        return render_template('start.html')


if __name__ == "__main__":
    app.run("0.0.0.0", threaded=False)
