import os

from flask import (
    Flask, render_template, request, jsonify, redirect, session, url_for
)
from flask_wtf import FlaskForm as Form
from wtforms import IntegerField
from wtforms.widgets.html5 import NumberInput

from ascii_generator import generate_image


TEMP_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'temp')
if not os.path.exists(TEMP_FOLDER):
    os.mkdir(TEMP_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = TEMP_FOLDER


class ASCIIGenerationForm(Form):
    range_width = IntegerField(
        'range width', default=25, widget=NumberInput(1, 10, 40)
    )
    desired_width = IntegerField(
        'desired width', default=120, widget=NumberInput(10, 50, 300)
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
            image_text = generate_image(
                path,
                desired_width=form.desired_width.data,
                range_width=form.range_width.data,
            )
            return jsonify({'image_text': image_text, 'session': True}), 200
        else:
            errors = form.errors
            return jsonify({'detail': errors}), 400
    else:
        form = ASCIIGenerationForm()
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
