import enum
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
from sqlalchemy import event

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class EstadoPago(enum.Enum):
    PENDIENTE = "Pendiente"
    PAGADO = "Pagado"
    RETRASADO = "Retrasado"


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    nombre = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    foto = db.Column(db.String(200))
    rol = db.Column(db.String(20), nullable=False, default='alumno')
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=True)

    alumno = db.relationship('Alumno', backref=db.backref('usuario', uselist=False))

class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Datos personales
    foto = db.Column(db.String(200))
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    edad = db.Column(db.Integer)
    ci = db.Column(db.String(20), unique=True, nullable=False, 
                  info={'error_messages': {'unique_constraint': 'El número de Cédula ya está registrado. Por favor, ingresa otro.'}})
    nacionalidad = db.Column(db.String(50))
    telefono_fijo = db.Column(db.String(20))
    telefono_movil = db.Column(db.String(20))
    correo_electronico = db.Column(db.String(120), unique=True, nullable=False,
                                 info={'error_messages': {'unique_constraint': 'El Correo Electrónico ya está registrado. Por favor, ingresa otro.'}})
    estado_civil = db.Column(db.String(20))
    sede = db.Column(db.String(100))
    n_hijos = db.Column(db.Integer)
    # Domicilio
    direccion = db.Column(db.String(200))
    sector = db.Column(db.String(100))
    referencia = db.Column(db.String(200))
    # Actividad laboral
    profesion = db.Column(db.String(100))
    trabajo_actual = db.Column(db.String(100))
    # Datos académicos
    fecha_ingreso = db.Column(db.Date)
    fecha_graduacion = db.Column(db.Date)
    horario = db.Column(db.String(50))
    asesor = db.Column(db.String(100))
    promocion = db.Column(db.String(50))

    @property
    def tiene_cuotas_pendientes(self):
        if self.datos_financieros is None:
            return False
        return any(cuota.estado == EstadoPago.PENDIENTE for cuota in self.datos_financieros.cuotas)
    
    @property
    def proxima_cuota(self):
        if self.datos_financieros is None:
            return None
        cuotas_pendientes = [c for c in self.datos_financieros.cuotas if c.estado == EstadoPago.PENDIENTE]
        return min(cuotas_pendientes, key=lambda x: x.fecha_vencimiento) if cuotas_pendientes else None

    @staticmethod
    def validate_unique_fields(mapper, connection, target):
        # Check CI
        existing_ci = connection.execute(
            Alumno.__table__.select().where(Alumno.ci == target.ci)
        ).fetchone()
        if existing_ci:
            raise ValueError(target.__table__.c.ci.info['error_messages']['unique_constraint'])

        # Check email
        existing_email = connection.execute(
            Alumno.__table__.select().where(Alumno.correo_electronico == target.correo_electronico)
        ).fetchone()
        if existing_email:
            raise ValueError(target.__table__.c.correo_electronico.info['error_messages']['unique_constraint'])
    
    datos_financieros = db.relationship('DatosFinancieros', backref='alumno', lazy=True, uselist=False, cascade="all, delete-orphan")
    certificados = db.relationship('Certificado', backref='alumno', lazy=True, cascade="all, delete-orphan")
    referencias_familiares = db.relationship('ReferenciaFamiliar', backref='alumno', lazy=True, cascade="all, delete-orphan")
    seguimientos_academicos = db.relationship('SeguimientoAcademico', backref='alumno', lazy=True, cascade="all, delete-orphan")

# Register the validation event
event.listen(Alumno, 'before_insert', Alumno.validate_unique_fields)

class DatosFinancieros(db.Model):
    __tablename__ = 'datos_financieros'
    
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    
    valor_curso = db.Column(db.Float)
    descuento = db.Column(db.Float)
    valor_total_curso = db.Column(db.Float)
    inscripcion = db.Column(db.Float)
    a_financiar = db.Column(db.Float)
    derecho_grado = db.Column(db.Float)
    n_cuotas = db.Column(db.Integer)
    valor_cuotas = db.Column(db.Float)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    cuotas = db.relationship('Cuota', backref='datos_financieros', lazy=True,
                           cascade="all, delete-orphan")

    def generar_cuotas(self):
        # Eliminar cuotas existentes
        Cuota.query.filter_by(datos_financieros_id=self.id).delete()
        
        monto_cuota = self.a_financiar / self.n_cuotas
        fecha_inicial = datetime.now().date()
        
        for i in range(self.n_cuotas):
            fecha_vencimiento = fecha_inicial + timedelta(days=30 * (i + 1))
            cuota = Cuota(
                datos_financieros_id=self.id,
                numero_cuota=i + 1,
                monto=monto_cuota,
                fecha_vencimiento=fecha_vencimiento
            )
            db.session.add(cuota)

    def __repr__(self):
        return f'<DatosFinancieros {self.id}>'

def actualizar_estados_cuotas():
    """Actualizar estados de cuotas diariamente"""
    cuotas = Cuota.query.filter_by(estado=EstadoPago.PENDIENTE).all()
    for cuota in cuotas:
        if cuota.esta_retrasada():
            cuota.estado = EstadoPago.RETRASADO
    db.session.commit()

def obtener_notificaciones():
    """Obtener notificaciones de pagos"""
    hoy = datetime.now().date()
    proximos = Cuota.query.filter(
        Cuota.estado == EstadoPago.PENDIENTE,
        Cuota.fecha_vencimiento > hoy,
        Cuota.fecha_vencimiento <= hoy + timedelta(days=7)
    ).all()
    
    retrasados = Cuota.query.filter_by(estado=EstadoPago.RETRASADO).all()
    
    return {
        'proximos': proximos,
        'retrasados': retrasados
    }

class Certificado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    archivo = db.Column(db.String(200), nullable=False)
    fecha_carga = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class ReferenciaFamiliar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    nombres_apellidos = db.Column(db.String(200), nullable=False)
    parentesco = db.Column(db.String(50), nullable=False)
    numero_contacto = db.Column(db.String(20), nullable=False)

class SeguimientoAcademico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    modulo = db.Column(db.String(50))
    nota = db.Column(db.Float)

class Cuota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datos_financieros_id = db.Column(db.Integer, db.ForeignKey('datos_financieros.id'), nullable=False)
    numero_cuota = db.Column(db.Integer, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    fecha_pago = db.Column(db.Date)
    estado = db.Column(db.Enum(EstadoPago), default=EstadoPago.PENDIENTE)
    
    def esta_retrasada(self):
        return not self.fecha_pago and self.fecha_vencimiento < datetime.now().date()
