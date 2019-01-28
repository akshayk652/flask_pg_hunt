import secrets, os
from pghunt.models import User, Post, Customer
from pghunt import app, db, bcrypt, celery
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, send_file
from pghunt.forms import RegistrationForm, LoginForm, UpdateAcountForm, PostForm, BookForm
from flask_login import login_user, current_user, logout_user, login_required
from pghunt.services.download_posts import get_data
from pghunt.services.save_files import save_picture,save_post_picture


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, account_type=form.account_type.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', title="Login", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/accounts', methods=['GET', 'POST'])
@login_required
def accounts():
    form = UpdateAcountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file   
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('accounts'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('accounts.html', title='Account', image_file=image_file, form=form)


@app.route("/pgs/new", methods=['GET', 'POST'])
@login_required
def new():
    if current_user.account_type == 'pg_owner':
        form = PostForm()
        if form.validate_on_submit():
            post = Post(title=form.title.data, details=form.details.data, price=form.price.data, contact=form.contact.data, address=form.address.data, owner=current_user)
            if form.pg_picture.data:
                pg_picture_file = save_post_picture(form.pg_picture.data)
                post.pg_pic = pg_picture_file
            db.session.add(post)
            db.session.commit()
            flash('Your post is created', 'success')
            return redirect(url_for('myposts'))
        return render_template('create_post.html', title='New Post', form=form, legend='New Post')
    else:
        flash('You are not logged in as a Owner', 'danger')
        return redirect(url_for('home'))


@app.route("/pgs/<int:post_id>")
def posts(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('posts.html', title=post.title, post=post)


@app.route("/pgs/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update(post_id):
    post = Post.query.get_or_404(post_id)
    if post.owner != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.details = form.details.data
        post.price = form.price.data
        post.contact = form.contact.data
        post.address = form.address.data
        if form.pg_picture.data:
            prev_file = post.pg_pic
            pg_picture_file = save_post_picture(form.pg_picture.data, prev_file)
            post.pg_pic = pg_picture_file       
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('posts', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.details.data = post.details
        form.price.data = post.price
        form.contact.data = post.contact
        form.address.data = post.address
    return render_template('create_post.html', title='Update', form=form, legend='Update')


@app.route("/pgs/<int:post_id>/delete", methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.owner != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/pgs/<int:post_id>/book", methods=['GET', 'POST'])
@login_required
def book_pg(post_id):
    if current_user.account_type == 'customer':
        post = Post.query.get_or_404(post_id)
        if post.owner != current_user and current_user.account_type == 'owner':
            abort(403)
        form = BookForm()
        if form.validate_on_submit():
            customer = Customer(first_name=form.first_name.data, last_name=form.last_name.data, contact=form.contact.data, book_id=post_id)
            db.session.add(customer)
            db.session.commit()
            flash('Your request will be processed soon', 'success')
            return redirect(url_for('home'))
        return render_template('book_pg.html', title='Book', form=form)
    else:
        flash('Oops! What are you trying to do', 'info')
        return redirect(url_for('home'))


@app.route("/account/bookings")
@login_required
def bookings():
    if current_user.account_type == 'pg_owner':
        customers = Customer.query.all()
        posts = Post.query.all()
        return render_template('bookings.html', title='Bookings',customers=customers, posts=posts)
    else:
        flash("No Access!", "danger")
        return redirect(url_for('home'))


@app.route("/mypgs")
@login_required
def myposts():
    if current_user.account_type == 'pg_owner':
        posts = Post.query.filter_by(owner=current_user)
        return render_template('myposts.html', title="My PG's", posts=posts)
    else:
        flash("No Access!", "danger")
        return redirect(url_for('home'))


@app.route('/search')
def search():
    s = request.args.get('s')
    posts, total = Post.search(s , 1, 5)
    if total:
        flash("{} results found!".format(total), "success")
        return render_template('home.html', posts=posts)
    else:
        flash("No results found","danger")
        return redirect(url_for('home'))


@app.route("/download-posts/<int:user_id>")
@login_required
def downloads(user_id):
    if current_user.account_type == 'pg_owner':
        file_fn = current_user.username + '.csv'
        async_result = get_data.delay(user_id, file_fn)
        return render_template('download.html', id=async_result)
    else:
        flash("No Access","danger")
        return redirect(url_for('home'))


@app.route('/status')
def download_status():
    id = request.args.get('id')
    result = get_data.AsyncResult(id)
    return jsonify({"status": result.ready()})


@app.route('/download-file')
def download_file():
    file_fn = current_user.username + '.csv'
    filepath = os.path.join(app.root_path, 'static/pg_data', file_fn)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        flash("You need to create some posts first!", "info")
        return redirect(url_for('myposts'))


@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500
