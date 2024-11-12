from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import FieldList, FormField, MultipleFileField, StringField, PasswordField, SubmitField, BooleanField, DateField, IntegerField, FloatField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import Usuario, Alumno

class RegistroForm(FlaskForm):
    """ nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Length(min=2, max=100)])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()]) """
    ci = StringField('Cédula', validators=[DataRequired(), Length(min=5, max=20)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir.')])
    # foto = FileField('Foto', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Registrar')

    def validate_ci(self, ci):
        alumno = Alumno.query.filter_by(ci=ci.data).first()
        if alumno:
            raise ValidationError('Este CI ya está registrado. Por favor, use uno diferente.')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este correo electrónico ya está en uso. Por favor, use uno diferente.')

class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class ActualizarPerfilForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    foto = FileField('', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Actualizar')

class ReferenciaFamiliarForm(FlaskForm):
    nombres_apellidos = StringField('Nombres y Apellidos', validators=[DataRequired(), Length(min=2, max=200)])
    parentesco = StringField('Parentesco', validators=[DataRequired(), Length(min=2, max=50)])
    numero_contacto = StringField('Número de Contacto', validators=[DataRequired(), Length(min=5, max=20)])

class AlumnoRegistroForm(FlaskForm):
    nombre = StringField('Información', validators=[DataRequired(), Length(min=2, max=100)], render_kw={'placeholder': 'Nombres'})
    apellidos = StringField('Apellidos', validators=[DataRequired(), Length(min=2, max=100)], render_kw={'placeholder': 'Apellidos'})
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    edad = IntegerField('Edad', validators=[DataRequired()], render_kw={'placeholder': 'Edad'})
    ci = StringField('Cédula & Correo', validators=[DataRequired(), Length(min=5, max=20)], render_kw={'placeholder': 'Cédula'})
    nacionalidad = StringField('Nacionalidad', validators=[Length(max=50)], render_kw={'placeholder': 'Nacionalidad'})
    telefono_fijo = StringField('Teléfonos', validators=[Length(max=20)],render_kw={'placeholder': 'Fijo'})
    telefono_movil = StringField('Teléfono Móvil', validators=[Length(max=20)], render_kw={'placeholder': 'Móvil'})
    correo_electronico = StringField('Correo Electrónico', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Correo Electrónico'})
    estado_civil = SelectField('Estado Civil', choices=[('soltero', 'Soltero'), ('casado', 'Casado'), ('divorciado', 'Divorciado'), ('viudo', 'Viudo')])
    sede = SelectField('Sede', choices=[('sur', 'Sur')])
    n_hijos = IntegerField('Número de Hijos', render_kw={'placeholder': 'Número de Hijos'})
    foto = FileField('Foto', validators=[FileAllowed(['jpg', 'png'])])
    # Domicilio
    direccion = StringField('Dirección', validators=[Length(max=200)])
    sector = StringField('Sector', validators=[Length(max=100)], render_kw={'placeholder': 'Sector'})
    referencia = StringField('Referencia', validators=[Length(max=200)])
    # Actividad laboral
    profesion = StringField('Profesión', validators=[Length(max=100)])
    trabajo_actual = StringField('Trabajo Actual', validators=[Length(max=100)])
    # Datos académicos
    fecha_ingreso = DateField('Fecha de Ingreso', validators=[DataRequired()])
    fecha_graduacion = DateField('Fecha de Graduación', validators=[DataRequired()])
    horario = StringField('Horario', validators=[Length(max=50)], render_kw={'placeholder': 'Horario'})
    asesor = StringField('Asesor', validators=[Length(max=100)])
    promocion = StringField('Promoción', validators=[Length(max=50)], render_kw={'placeholder': 'Promoción'})
    # Datos financieros
    """ valor_curso = FloatField('Valor del Curso', validators=[DataRequired()], render_kw={'placeholder': '0.00'})
    descuento = FloatField('Descuento', validators=[DataRequired()], render_kw={'placeholder': 'Descuento'})
    valor_total_curso = FloatField('Valor Total del Curso', render_kw={'placeholder': '0.00'})
    inscripcion = FloatField('Inscripción', validators=[DataRequired()], render_kw={'placeholder': '0.00'})
    a_financiar = FloatField('A Financiar', validators=[DataRequired()], render_kw={'placeholder': 'A Financiar'})
    derecho_grado = FloatField('Derecho de Grado', validators=[DataRequired()], render_kw={'placeholder': '0.00'})
    n_cuotas = SelectField('Número de Cuotas', choices=[(1, 1), (3, 3), (6, 6), (9, 9), (12, 12)], validators=[DataRequired()])
    valor_cuotas = FloatField('Valor de las Cuotas', render_kw={'placeholder': 'Valor de las Cuotas'})
    fecha_registro = DateField('Fecha de Registro', validators=[DataRequired()]) """

    # Campos para ReferenciaFamiliar
    nombres_apellidos_referencia = StringField('Nombres y Apellidos de la Referencia', validators=[DataRequired(), Length(min=2, max=200)])
    parentesco_referencia = StringField('Parentesco', validators=[DataRequired(), Length(min=2, max=50)])
    numero_contacto_referencia = StringField('Número de Contacto', validators=[DataRequired(), Length(min=5, max=20)])

    submit = SubmitField('Registrar')

    """ def validate_ci(self, ci):
        alumno = Alumno.query.filter_by(ci=ci.data).first()
        if alumno:
            raise ValidationError('Ese CI ya está registrado. Por favor, elige otro.')

    def validate_correo_electronico(self, correo_electronico):
        alumno = Alumno.query.filter_by(correo_electronico=correo_electronico.data).first()
        if alumno:
            raise ValidationError('Ese correo electrónico ya está registrado. Por favor, elige otro.') """

class AlumnoEdicionForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Length(min=2, max=100)])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    edad = IntegerField('Edad')
    ci = StringField('CI', validators=[DataRequired(), Length(min=5, max=20)])
    nacionalidad = StringField('Nacionalidad', validators=[Length(max=50)])
    telefono_fijo = StringField('Teléfono Fijo', validators=[Length(max=20)])
    telefono_movil = StringField('Teléfono Móvil', validators=[Length(max=20)])
    correo_electronico = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    estado_civil = SelectField('Estado Civil', choices=[('soltero', 'Soltero'), ('casado', 'Casado'), ('divorciado', 'Divorciado'), ('viudo', 'Viudo')])
    sede = SelectField('Sede', choices=[('sur', 'Sur')])
    n_hijos = IntegerField('Número de Hijos')
    foto = FileField('Foto de Perfil', validators=[FileAllowed(['jpg', 'png'])])
    # Domicilio
    direccion = StringField('Dirección', validators=[Length(max=200)])
    sector = StringField('Sector', validators=[Length(max=100)], render_kw={'placeholder': 'Sector'})
    referencia = StringField('Referencia', validators=[Length(max=200)])
    # Actividad laboral
    profesion = StringField('Profesión', validators=[Length(max=100)])
    trabajo_actual = StringField('Trabajo Actual', validators=[Length(max=100)])
    # Datos académicos
    fecha_ingreso = DateField('Fecha de Ingreso', validators=[DataRequired()])
    fecha_graduacion = DateField('Fecha de Graduación', validators=[DataRequired()])
    horario = StringField('Horario', validators=[Length(max=50)], render_kw={'placeholder': 'Horario'})
    asesor = StringField('Asesor', validators=[Length(max=100)])
    promocion = StringField('Promoción', validators=[Length(max=50)], render_kw={'placeholder': 'Promoción'})

    # Campos para ReferenciaFamiliar
    nombres_apellidos_referencia = StringField('Nombres y Apellidos de la Referencia', validators=[DataRequired(), Length(min=2, max=200)])
    parentesco_referencia = StringField('Parentesco', validators=[DataRequired(), Length(min=2, max=50)])
    numero_contacto_referencia = StringField('Número de Contacto', validators=[DataRequired(), Length(min=5, max=20)])
        
    submit = SubmitField('Actualizar')

    def validate_ci(self, ci):
        if ci.data != self.original_ci:
            alumno = Alumno.query.filter_by(ci=ci.data).first()
            if alumno:
                raise ValidationError('Ese CI ya está registrado. Por favor, elige otro.')

    def validate_correo_electronico(self, correo_electronico):
        if correo_electronico.data != self.original_correo_electronico:
            alumno = Alumno.query.filter_by(correo_electronico=correo_electronico.data).first()
            if alumno:
                raise ValidationError('Ese correo electrónico ya está registrado. Por favor, elige otro.')

    def __init__(self, original_ci, original_correo_electronico, *args, **kwargs):
        super(AlumnoEdicionForm, self).__init__(*args, **kwargs)
        self.original_ci = original_ci
        self.original_correo_electronico = original_correo_electronico

class DatosFinancierosForm(FlaskForm):
    valor_curso = FloatField('Valor del Curso', validators=[DataRequired()], render_kw={'placeholder': '0.00'})
    descuento = FloatField('Descuento', validators=[DataRequired()], render_kw={'placeholder': 'Descuento'})
    valor_total_curso = FloatField('Valor Total del Curso', render_kw={'placeholder': '0.00'})
    inscripcion = FloatField('Inscripción', validators=[DataRequired()], render_kw={'placeholder': '0.00'})
    a_financiar = FloatField('A Financiar', validators=[DataRequired()], render_kw={'placeholder': 'A Financiar'})
    derecho_grado = FloatField('Derecho de Grado', validators=[DataRequired()], render_kw={'placeholder': '0.00'})
    n_cuotas = SelectField('Número de Cuotas', choices=[(1, 1), (3, 3), (6, 6), (9, 9), (12, 12)], validators=[DataRequired()])
    valor_cuotas = FloatField('Valor de las Cuotas', render_kw={'placeholder': 'Valor de las Cuotas'})

# forms.py
class PagoCuotaForm(FlaskForm):
    fecha_pago = DateField('Fecha de Pago', validators=[DataRequired()])
    comprobante = FileField('Comprobante de Pago')

class SeguimientoAcademicoForm(FlaskForm):
    alumno_id = SelectField('Alumno', coerce=int, validators=[DataRequired()])
    fecha = DateField('Fecha', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired(), Length(min=10, max=500)])
    estado = SelectField('Estado', choices=[('pendiente', 'Pendiente'), ('completado', 'Completado')], validators=[DataRequired()])
    submit = SubmitField('Registrar Seguimiento')

    def __init__(self, *args, **kwargs):
        super(SeguimientoAcademicoForm, self).__init__(*args, **kwargs)
        self.alumno_id.choices = [(alumno.id, f"{alumno.nombre} {alumno.apellidos}") for alumno in Alumno.query.all()]

class CertificadoForm(FlaskForm):
    certificados = MultipleFileField('Certificados (PDF)', validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Subir Certificado')

class BusquedaAlumnoForm(FlaskForm):
    ci = StringField('CI', validators=[DataRequired()])
    submit = SubmitField('Buscar')

class RequestResetForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')