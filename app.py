import os
import shutil

from flask import (
    Flask, render_template, request, jsonify, redirect, session, url_for,
    make_response
)
from flask_wtf import FlaskForm as Form
from wtforms import FloatField
from wtforms.validators import NumberRange
from wtforms.widgets.core import HTMLString, html_params

from ascii_generator import generate_image


TEMP_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'temp')
if not os.path.exists(TEMP_FOLDER):
    os.mkdir(TEMP_FOLDER)

STATIC_FOLDER = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'static')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = TEMP_FOLDER


class SliderWidget:

    def __call__(self, field, **kwargs):
        kwargs.setdefault('type', 'submit')
        title = kwargs.pop('title', field.description or '')
        params = html_params(title=title, **kwargs)

        html = '<div class="slidecontainer"><input type="range" %s'\
            'class="slider"></div>'
        return HTMLString(html % params)


class ASCIIGenerationForm(Form):
    scaling_factor = FloatField(
        validators=[NumberRange(0.01, 1)],
        default=0.5,
        widget=SliderWidget()
    )
    pixel_levity = FloatField(
        validators=[NumberRange(0.1, 2)],
        default=1,
        widget=SliderWidget()
    )


def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def allowed_file(filename):
    return '.' in filename and get_extension(filename) in ALLOWED_EXTENSIONS


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        f = request.files.get('image_file')
        if f and allowed_file(f.filename):
            ext = get_extension(f.filename)
            filename = f'temp.{ext}'
            session['filename'] = filename
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)
        elif session.get('filename'):
            path = os.path.join(
                app.config['UPLOAD_FOLDER'], session['filename']
            )
        else:
            return redirect(url_for('index'))

        form = ASCIIGenerationForm(formdata=request.form)
        if form.validate_on_submit():
            image_path = generate_image(
                path,
                scaling_factor=form.scaling_factor.data,
                pixel_levity=form.pixel_levity.data
            )
            shutil.move(
                image_path, os.path.join(STATIC_FOLDER, 'ascii_art.png'))
            image_url = url_for('static', filename='ascii_art.png')
            res = make_response(
                jsonify({'image_url': image_url, 'session': True}), 200)
            res.headers['Cache-Control'] = 'no-cache, no-store,'\
                ' must-revalidate'
            return res
        else:
            errors = form.errors
            return jsonify({'detail': errors}), 400
    else:
        form = ASCIIGenerationForm()
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
