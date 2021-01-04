import os
from PIL import Image
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, UpdatePreferencesForm, Buscar
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import ipapi


def obtenerLink(link):
    link = link.split("/")
    try:
        link = link[-1].split("=")
    except:
        return link[0]
    try:
        link = link[1].split("&")
    except:
        return link[0]
    return link[0]






@app.route("/")
@app.route("/home")
def home():
    current_user.connected_lol = False
    current_user.connected_csgo = False
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)



@app.route("/desafios")
def desafios():
    current_user.connected_lol = False
    current_user.connected_csgo = False

    return render_template('desafios.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        search = request.form.get('search')
        data = ipapi.location(ip=search, output='json')
        
        if form.entrenador.data == True:
            entrenador = "(entrenador)"
        else:
            entrenador = ""

        user = User(username=form.username.data, email=form.email.data, password=hashed_password, pais=data["continent_code"], 
                lol=form.lol.data, rango_lol=form.rango_lol.data, csgo=form.csgo.data, rango_csgo=form.rango_csgo.data, 
                name_lol=form.name_lol.data, name_csgo=form.name_csgo.data, entrenador=entrenador)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created, {form.username.data}. You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


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
            flash('Login Unsuccessful. Please check your email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    current_user.connected_lol = False
    current_user.connected_csgo = False
    db.session.commit()

    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)

    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    current_user.connected_lol = False
    current_user.connected_csgo = False

    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file


        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash('Tu cuenta fue actualizada', 'success')
        return redirect(url_for('account'))
        
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    search = request.form.get('search')
    data = ipapi.location(ip=search, output='json')

    return render_template('account.html', title='Account', data=data, image_file=image_file, form=form)


@app.route("/buscando-lol", methods=['GET','POST'])
def buscandolol():
    current_user.connected_lol = False
    current_user.connected_csgo = False
    db.session.commit()

    form = Buscar()
    if form.validate_on_submit():
        current_user.connected_lol = True
        db.session.commit()
        return redirect(url_for('lol'))
    return render_template('buscandolol.html', title="Buscador LoL", form=form)


@app.route("/lol", methods=['GET','POST'])
def lol():
    lista = [] 
    for x in range(len(User.query.filter_by(pais=f'{current_user.pais}').all())):
        lista.append(User.query.filter_by(pais=f'{current_user.pais}').all()[x])
    return render_template('lol.html', title="Buscador LoL", lista = lista)
    

@app.route("/buscando-csgo", methods=['GET','POST'])
def buscandocsgo():
    current_user.connected_csgo = False
    current_user.connected_lol = False
    db.session.commit()
    form = Buscar()
    if form.validate_on_submit():
        current_user.connected_csgo = True
        db.session.commit()
        return redirect(url_for('csgo'))
    return render_template('buscandocsgo.html', title="Buscador CSGO", form=form)


@app.route("/csgo")
def csgo():
    lista = []
    for x in range(len(User.query.filter_by(pais=f'{current_user.pais}').all())):
        lista.append(User.query.filter_by(pais=f'{current_user.pais}').all()[x])
        
    return render_template('csgo.html', title="Buscador CSGO", lista=lista)


@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
    current_user.connected_lol = False
    current_user.connected_csgo = False

    form = PostForm()
    if form.validate_on_submit():

        link_video = obtenerLink(form.link_video.data)

        post = Post(title=form.title.data, content=form.content.data, author=current_user, link_video=link_video)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title="New Post", form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    current_user.connected_lol = False
    current_user.connected_csgo = False

    post= Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def update_post(post_id):
    current_user.connected_lol = False
    current_user.connected_csgo = False

    post= Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        link_video = obtenerLink(form.link_video.data)
        post.link_video = link_video
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Tu post ha sido actualizado', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':    
        form.title.data = post.title
        form.content.data = post.content
        form.link_video.data = post.link_video
    return render_template('create_post.html', title="Update Post", form=form, legend='Update Post')
    

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    current_user.connected_lol = False
    current_user.connected_csgo = False

    post= Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Tu post ha sido eliminado', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    current_user.connected_lol = False
    current_user.connected_csgo = False

    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@app.route("/user/profile/<string:username>")
def user_profile(username):
    current_user.connected_lol = False
    current_user.connected_csgo = False

    return render_template('user_profile.html', user=username)


@app.route("/preferences", methods=['GET','POST'])
@login_required
def preferences():
    current_user.connected_lol = False
    current_user.connected_csgo = False

    form = UpdatePreferencesForm()
    if form.validate_on_submit():

        current_user.lol = form.lol.data
        current_user.rango_lol = form.rango_lol.data
        current_user.csgo = form.csgo.data
        current_user.rango_csgo = form.rango_csgo.data

        current_user.name_lol = form.name_lol.data
        current_user.name_csgo = form.name_csgo.data

        db.session.commit()
        flash('Tu cuenta fue actualizada', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.name_lol.data = current_user.name_lol
        form.name_csgo.data = current_user.name_csgo

    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)

    return render_template('preferences.html', title='Preferencias', form=form, image_file=image_file)


