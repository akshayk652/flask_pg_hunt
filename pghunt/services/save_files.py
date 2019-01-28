import os, secrets
from pghunt import app


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)
    return picture_fn


def save_post_picture(form_picture, prev_file=None):
    if prev_file != 'default-paying-guest-accommodations-0.jpg' and prev_file is not None:
        prev_file_path = os.path.join(app.root_path, 'static/pg_pics', prev_file)
        os.remove(prev_file_path) 
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/pg_pics', picture_fn)
    form_picture.save(picture_path)
    return picture_fn
