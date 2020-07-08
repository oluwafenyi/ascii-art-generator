import os
from io import BytesIO

from flask import (
    Flask, render_template, request, jsonify, redirect, url_for, Response)
from flask_wtf import FlaskForm as Form
from colour import Color
from wtforms import FloatField, StringField
from wtforms.validators import NumberRange
from werkzeug.wsgi import FileWrapper

from ascii_generator import generate_image, LOCK


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


class ColorCheck:
    def __call__(self, form, field):
        color = field.data
        try:
            Color(color)
            return True
        except ValueError:
            return False


class ASCIIGenerationForm(Form):
    scaling_factor = FloatField(
        validators=[NumberRange(0.01, 1)],
        default=0.5,
    )
    from_color = StringField(validators=[ColorCheck()], default='black')
    to_color = StringField(validators=[ColorCheck()], default='black')


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
        if not f and not allowed_file(f.filename):
            return redirect(url_for('index'))

        file_obj = BytesIO(f.read())

        form = ASCIIGenerationForm(formdata=request.form)
        if form.validate_on_submit():
            output = generate_image(
                file_obj,
                scaling_factor=form.scaling_factor.data,
                gradient=(form.from_color.data, form.to_color.data)
            )
            response = Response(
                FileWrapper(output), mimetype='image/png',
                direct_passthrough=True)
            response.headers['Content-Disposition'] = \
                'attachment; filename="ascii_art.png"'
            return response

        else:
            errors = form.errors
            return jsonify({'detail': errors, 'status': 400}), 400

    else:
        form = ASCIIGenerationForm()
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
