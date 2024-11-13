import os
from flask_migrate import Migrate
from app import create_app, db
from app.models import Usuario, Alumno, Certificado, ReferenciaFamiliar, SeguimientoAcademico, Cuota, DatosFinancieros

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Usuario': Usuario, 'Alumno': Alumno, 'Certificado': Certificado, 'ReferenciaFamiliar': ReferenciaFamiliar, 'SeguimientoAcademico': SeguimientoAcademico, 'Cuota': Cuota, 'DatosFinancieros': DatosFinancieros}

# Agregar ruta de healthcheck
@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)