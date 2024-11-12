from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    from app.routes import auth, alumnos, main
    app.register_blueprint(auth.auth)
    app.register_blueprint(alumnos.alumnos)
    app.register_blueprint(main.main)

    """ # Context processor global
    @app.context_processor
    def utility_processor():
        def get_notificaciones():
            from app.models import Cuota, EstadoPago
            try:
                notificaciones_pendientes = Cuota.query.filter_by(estado=EstadoPago.RETRASADO).count()
            except:
                notificaciones_pendientes = 0
            return {'notificaciones_pendientes': notificaciones_pendientes}
        return get_notificaciones() """

    @app.context_processor
    def utility_processor():
        from app.models import Cuota, EstadoPago, obtener_notificaciones
        def get_notificaciones_count():
            notificaciones = obtener_notificaciones()
            return len(notificaciones['proximos']) + len(notificaciones['retrasados'])
        
        return dict(
            notificaciones_count=get_notificaciones_count(),
            notificaciones_pendientes=Cuota.query.filter_by(estado=EstadoPago.RETRASADO).count()
        )

    return app