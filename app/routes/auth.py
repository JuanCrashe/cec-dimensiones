from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import Usuario, Alumno
from app.forms import RegistroForm, LoginForm, ActualizarPerfilForm, RequestResetForm, ResetPasswordForm
from app.utils import save_picture, save_profile_picture, send_reset_email

auth = Blueprint('auth', __name__)

@auth.route("/registro", methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistroForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        """ alumno = Alumno(nombre=form.nombre.data, apellidos=form.apellidos.data,
                        fecha_nacimiento=form.fecha_nacimiento.data, ci=form.ci.data,
                        correo_electronico=form.email.data)
        db.session.add(alumno)
        db.session.flush()  # Para obtener el ID del alumno antes de hacer commit """
        
        usuario = Usuario(username=form.ci.data, email=form.email.data, password=hashed_password,
                          rol='admin')
        db.session.add(usuario)
        
        """ if form.foto.data:
            picture_file = save_picture(form.foto.data, 'fotos_perfil')
            alumno.foto = picture_file """
        
        db.session.commit()
        flash('Tu cuenta ha sido creada. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en el campo {getattr(form, field).label.text}: {error}", 'danger')
    return render_template('auth/registro.html', title='Registro', form=form)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.password, form.password.data):
            login_user(usuario, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login fallido. Por favor, verifica el email y la contraseña', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth.route("/perfil", methods=['GET', 'POST'])
@login_required
def perfil():
    form = ActualizarPerfilForm()
    if form.validate_on_submit():
        if form.foto.data:
            picture_file = save_profile_picture(form.foto.data)
            current_user.foto = picture_file
        current_user.nombre = form.nombre.data
        current_user.apellidos = form.apellidos.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Tu perfil ha sido actualizado.', 'success')
        return redirect(url_for('auth.perfil'))
    elif request.method == 'GET':
        form.nombre.data = current_user.nombre
        form.apellidos.data = current_user.apellidos
        form.email.data = current_user.email
    imagen_perfil = url_for('static', filename='profile_pics/' + current_user.foto) if current_user.foto else url_for('static', filename='img/default.jpg')
    return render_template('auth/perfil.html', title='Perfil', form=form, imagen_perfil=imagen_perfil)

@auth.route("/recuperar_contrasena", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Se ha enviado un correo electrónico con indicaciones para recuperar su contraseña.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', title='Recuperar Contraseña', form=form)

@auth.route("/recuperar_contrasena/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = Usuario.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', title='Reset Password', form=form)