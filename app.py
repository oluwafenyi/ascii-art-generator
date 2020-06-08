import os
from threading import Timer

from flask import (
    Flask, render_template, request, jsonify, redirect, session, url_for)
from flask_wtf import FlaskForm as Form
from wtforms import FloatField
from wtforms.validators import NumberRange

from ascii_generator import generate_image, LOCK


TEMP_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'temp')
if not os.path.exists(TEMP_FOLDER):
    os.mkdir(TEMP_FOLDER)

STATIC_FOLDER = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'static')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = TEMP_FOLDER


class ASCIIGenerationForm(Form):
    scaling_factor = FloatField(
        validators=[NumberRange(0.01, 1)],
        default=0.5,
    )


def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def allowed_file(filename):
    return '.' in filename and get_extension(filename) in ALLOWED_EXTENSIONS


def delete_file(path):
    with LOCK:
        if os.path.exists(path):
            os.unlink(path)


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        f = request.files.get('image_file')
        if f and allowed_file(f.filename):
            filename = f.filename
            session['filename'] = filename
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            delete_upload_task = Timer(600, delete_file, (path,))
            delete_upload_task.start()
            f.save(path)
        elif session.get('filename'):
            path = os.path.join(
                app.config['UPLOAD_FOLDER'], session['filename']
            )
        else:
            return redirect(url_for('index'))

        form = ASCIIGenerationForm(formdata=request.form)
        if form.validate_on_submit():
            try:
                print('here')
                path, filename = generate_image(
                    path,
                    scaling_factor=form.scaling_factor.data,
                )
            except FileNotFoundError:
                error = 'image does not exist, please reupload'
                return jsonify({'detail': error, 'status': 404}), 404

            delete_generated_task = Timer(300, delete_file, (path,))
            delete_generated_task.start()
            image_url = url_for('static', filename=filename)
            return jsonify(
                {'image_url': image_url, 'session': True, 'status': 200}
            ), 200

        else:
            errors = form.errors
            return jsonify({'detail': errors, 'status': 400}), 400

    else:
        form = ASCIIGenerationForm()
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
