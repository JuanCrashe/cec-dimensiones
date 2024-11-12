from flask import Blueprint, render_template, url_for
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template('home.html')

@main.route("/perfil")
@login_required
def perfil():
    return render_template('auth/perfil.html', usuario=current_user)