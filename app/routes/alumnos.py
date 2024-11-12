import csv
from datetime import datetime, timedelta
import io
from sqlite3 import IntegrityError
from flask import Blueprint, make_response, render_template, url_for, flash, redirect, request, abort, send_file
from flask_login import current_user, login_required
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from app import db
from app.models import Alumno, Certificado, DatosFinancieros, EstadoPago, ReferenciaFamiliar, SeguimientoAcademico, Cuota, obtener_notificaciones
from app.forms import CertificadoForm, BusquedaAlumnoForm, AlumnoRegistroForm, AlumnoEdicionForm, DatosFinancierosForm, PagoCuotaForm, ReferenciaFamiliarForm, SeguimientoAcademicoForm
from app.utils import save_pdf, save_picture, generate_pdf
import os

alumnos = Blueprint('alumnos', __name__)

@alumnos.route("/alumnos/registrar", methods=['GET', 'POST'])
@login_required
def registrar_alumno():
    if current_user.rol != 'admin':
        abort(403)
    form = AlumnoRegistroForm()
    if form.validate_on_submit():
        try:
            # Save picture
            if form.foto.data:
                picture_file = save_picture(form.foto.data)
            else:
                picture_file = 'default.png'

            """ # Calcular el valor total del curso
            valor_total_curso = form.valor_curso.data - form.descuento.data

            # Calcular el valor de las cuotas
            numero_coutas = int(form.n_cuotas.data)
            if numero_coutas > 0:
                valor_cuotas = valor_total_curso / numero_coutas
            else:
                valor_cuotas = 0

            # Calcular las fechas de pago de las cuotas
            from datetime import timedelta

            fechas_pago = []
            fecha_inicio = form.fecha_ingreso.data
            for i in range(numero_coutas):
                fecha_pago = fecha_inicio + timedelta(days=30 * (i + 1))
                fechas_pago.append(fecha_pago) """

            alumno = Alumno(
                nombre=form.nombre.data,
                apellidos=form.apellidos.data,
                fecha_nacimiento=form.fecha_nacimiento.data,
                edad=form.edad.data,
                ci=form.ci.data,
                nacionalidad=form.nacionalidad.data,
                telefono_fijo=form.telefono_fijo.data,
                telefono_movil=form.telefono_movil.data,
                correo_electronico=form.correo_electronico.data,
                estado_civil=form.estado_civil.data,
                sede=form.sede.data,
                n_hijos=form.n_hijos.data,
                foto=picture_file,
                direccion=form.direccion.data,
                sector=form.sector.data,
                referencia=form.referencia.data,
                profesion=form.profesion.data,
                trabajo_actual=form.trabajo_actual.data,
                fecha_ingreso=form.fecha_ingreso.data,
                fecha_graduacion=form.fecha_graduacion.data,
                horario=form.horario.data,
                asesor=form.asesor.data,
                promocion=form.promocion.data
            )
            
            db.session.add(alumno)
            db.session.commit()

            referencia_familiar = ReferenciaFamiliar(
                alumno_id=alumno.id,
                nombres_apellidos=form.nombres_apellidos_referencia.data,
                parentesco=form.parentesco_referencia.data,
                numero_contacto=form.numero_contacto_referencia.data
            )
            db.session.add(referencia_familiar)
            db.session.commit()

            """ if form.certificados.data:
                pdf_file = save_pdf(form.certificados.data)
                certificado = Certificado(
                    alumno_id=alumno.id,
                    nombre=form.certificados.data.filename,
                    archivo=pdf_file
                )
                db.session.add(certificado)
            db.session.commit() """

            """ # Guardar las fechas de pago en la base de datos
            for fecha_pago in fechas_pago:
                cuota = Cuota(
                    alumno_id=alumno.id,
                    fecha_pago=fecha_pago,
                    valor_cuota=valor_cuotas
                )
                db.session.add(cuota)
            db.session.commit() """

            flash('El alumno ha sido registrado exitosamente.', 'success')
            return redirect(url_for('alumnos.lista_alumnos'))
        
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'error')
            return render_template('alumnos/registrar.html', form=form)
            
        except IntegrityError as e:
            db.session.rollback()
            if 'ci' in str(e.orig):
                flash('El número de Cédula ya está registrado. Por favor, ingresa otro.', 'error')
            elif 'correo_electronico' in str(e.orig):
                flash('El correo electrónico ya está registrado. Por favor, ingresa otro.', 'error')
            else:
                flash('Error al registrar alumno', 'error')
            return render_template('alumnos/registrar.html', form=form)
        
    return render_template('alumnos/registrar.html', title='Registrar Alumno', form=form)

@alumnos.route("/alumnos/editar/<int:alumno_id>", methods=['GET', 'POST'])
@login_required
def editar_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    if current_user.rol != 'admin':
        abort(403)
    form = AlumnoEdicionForm(original_ci=alumno.ci, original_correo_electronico=alumno.correo_electronico)
    if form.validate_on_submit():
        if form.foto.data:
            picture_file = save_picture(form.foto.data)
            alumno.foto = picture_file
        alumno.nombre = form.nombre.data
        alumno.apellidos = form.apellidos.data
        alumno.fecha_nacimiento = form.fecha_nacimiento.data
        alumno.edad = form.edad.data
        alumno.ci = form.ci.data
        alumno.nacionalidad = form.nacionalidad.data
        alumno.telefono_fijo = form.telefono_fijo.data
        alumno.telefono_movil = form.telefono_movil.data
        alumno.correo_electronico = form.correo_electronico.data
        alumno.estado_civil = form.estado_civil.data
        alumno.sede = form.sede.data
        alumno.n_hijos = form.n_hijos.data
        alumno.direccion = form.direccion.data
        alumno.sector = form.sector.data
        alumno.referencia = form.referencia.data
        alumno.profesion = form.profesion.data
        alumno.trabajo_actual = form.trabajo_actual.data
        alumno.fecha_ingreso = form.fecha_ingreso.data
        alumno.fecha_graduacion = form.fecha_graduacion.data
        alumno.horario = form.horario.data
        alumno.asesor = form.asesor.data
        alumno.promocion = form.promocion.data

        db.session.commit()
        
        # Actualizar referencias familiares
        referencia = ReferenciaFamiliar.query.filter_by(alumno_id=alumno.id).first()
        if referencia:
            referencia.nombres_apellidos = form.nombres_apellidos_referencia.data
            referencia.parentesco = form.parentesco_referencia.data
            referencia.numero_contacto = form.numero_contacto_referencia.data
        else:
            referencia = ReferenciaFamiliar(
                alumno_id=alumno.id,
                nombres_apellidos=form.nombres_apellidos_referencia.data,
                parentesco=form.parentesco_referencia.data,
                numero_contacto=form.numero_contacto_referencia.data
            )
            db.session.add(referencia)
        db.session.commit()

        flash('El alumno ha sido actualizado exitosamente.', 'success')
        return redirect(url_for('alumnos.editar_alumno', alumno_id=alumno.id))
    elif request.method == 'GET':
        form.nombre.data = alumno.nombre
        form.apellidos.data = alumno.apellidos
        form.fecha_nacimiento.data = alumno.fecha_nacimiento
        form.edad.data = alumno.edad
        form.ci.data = alumno.ci
        form.nacionalidad.data = alumno.nacionalidad
        form.telefono_fijo.data = alumno.telefono_fijo
        form.telefono_movil.data = alumno.telefono_movil
        form.correo_electronico.data = alumno.correo_electronico
        form.estado_civil.data = alumno.estado_civil
        form.sede.data = alumno.sede
        form.n_hijos.data = alumno.n_hijos
        form.direccion.data = alumno.direccion
        form.sector.data = alumno.sector
        form.referencia.data = alumno.referencia
        form.profesion.data = alumno.profesion
        form.trabajo_actual.data = alumno.trabajo_actual
        form.fecha_ingreso.data = alumno.fecha_ingreso
        form.fecha_graduacion.data = alumno.fecha_graduacion
        form.horario.data = alumno.horario
        form.asesor.data = alumno.asesor
        form.promocion.data = alumno.promocion
        
        referencia = ReferenciaFamiliar.query.filter_by(alumno_id=alumno.id).first()
        if referencia:
            form.nombres_apellidos_referencia.data = referencia.nombres_apellidos
            form.parentesco_referencia.data = referencia.parentesco
            form.numero_contacto_referencia.data = referencia.numero_contacto
    return render_template('alumnos/editar.html', title='Editar Alumno', form=form, alumno=alumno)

@alumnos.route('/alumno/<int:alumno_id>/datos_financieros', methods=['GET', 'POST'])
@login_required
def guardar_datos_financieros(alumno_id):
    if current_user.rol != 'admin':
        abort(403)
    alumno = Alumno.query.get_or_404(alumno_id)
    datos_financieros = alumno.datos_financieros or DatosFinancieros(alumno_id=alumno.id)
    form = DatosFinancierosForm(obj=datos_financieros)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Iniciar transacción
            if not alumno.datos_financieros:
                alumno.datos_financieros = datos_financieros
            
            # Actualizar datos financieros
            form.populate_obj(datos_financieros)
            db.session.add(datos_financieros)

            # Hacer commit para obtener el ID
            db.session.commit()
            
            # Eliminar cuotas existentes si las hay
            if datos_financieros.cuotas:
                for cuota in datos_financieros.cuotas:
                    db.session.delete(cuota)
            
            # Generar nuevas cuotas
            num_cuotas = int(datos_financieros.n_cuotas)
            monto_cuota = datos_financieros.a_financiar / num_cuotas
            fecha_actual = datetime.now().date()
            
            nuevas_cuotas = []
            for i in range(num_cuotas):
                fecha_vencimiento = fecha_actual + timedelta(days=30 * (i + 1))
                nueva_cuota = Cuota(
                    datos_financieros_id=datos_financieros.id,
                    numero_cuota=i + 1,
                    monto=round(monto_cuota, 2),
                    fecha_vencimiento=fecha_vencimiento,
                    estado=EstadoPago.PENDIENTE
                )
                nuevas_cuotas.append(nueva_cuota)
            
            # Agregar todas las cuotas
            db.session.bulk_save_objects(nuevas_cuotas)
            db.session.commit()
            flash('Datos financieros y cuotas actualizados exitosamente', 'success')
            return redirect(url_for('alumnos.lista_alumnos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar datos financieros: {str(e)}', 'error')
            return render_template('alumnos/datos_financieros.html', form=form, alumno=alumno)
    
    return render_template('alumnos/datos_financieros.html', form=form, alumno=alumno)

@alumnos.route('/cuota/<int:cuota_id>/pagar', methods=['GET', 'POST'])
@login_required
def registrar_pago(cuota_id):
    cuota = Cuota.query.get_or_404(cuota_id)
    form = PagoCuotaForm()
    
    if form.validate_on_submit():
        cuota.fecha_pago = form.fecha_pago.data
        cuota.estado = EstadoPago.PAGADO
        db.session.commit()
        flash('Pago registrado exitosamente', 'success')
        return redirect(url_for('alumnos.ver_cuotas_alumno', alumno_id=cuota.datos_financieros.alumno_id))
        
    return render_template('alumnos/registrar_pago.html', form=form, cuota=cuota)

@alumnos.route('/alumno/<int:alumno_id>/cuotas')
@login_required
def ver_cuotas_alumno(alumno_id):
    if current_user.rol != 'admin':
        abort(403)
    alumno = Alumno.query.get_or_404(alumno_id)
    if not alumno.datos_financieros:
        flash('El alumno no tiene datos financieros registrados.', 'warning')
        return redirect(url_for('alumnos.lista_alumnos'))
    return render_template('alumnos/cuotas_alumno.html', alumno=alumno)

@alumnos.route('/notificaciones')
@login_required
def ver_notificaciones():
    hoy = datetime.now().date()
    proximas_cuotas = Cuota.query.filter(
        Cuota.estado == EstadoPago.PENDIENTE,
        Cuota.fecha_vencimiento > hoy,
        Cuota.fecha_vencimiento <= hoy + timedelta(days=7)
    ).all()
    
    cuotas_atrasadas = Cuota.query.filter(
        Cuota.estado == EstadoPago.PENDIENTE,
        Cuota.fecha_vencimiento < hoy
    ).all()
    
    return render_template('alumnos/notificaciones.html',
                         proximas_cuotas=proximas_cuotas,
                         cuotas_atrasadas=cuotas_atrasadas)

@alumnos.route("/alumnos/eliminar/<int:alumno_id>", methods=['POST'])
@login_required
def eliminar_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    if current_user.rol != 'admin':
        abort(403)
    db.session.delete(alumno)
    db.session.commit()
    flash('El alumno ha sido eliminado exitosamente.', 'success')
    return redirect(url_for('alumnos.lista_alumnos'))

@alumnos.route("/alumnos")
@login_required
def lista_alumnos():
    if current_user.rol != 'admin':
        abort(403)
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'nombre', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)

    query = Alumno.query

    if search:
        query = query.filter(
            Alumno.nombre.ilike(f'%{search}%') |
            Alumno.apellidos.ilike(f'%{search}%') |
            Alumno.ci.ilike(f'%{search}%') |
            Alumno.correo_electronico.ilike(f'%{search}%') |
            Alumno.telefono_movil.ilike(f'%{search}%')
        )

    if sort_order == 'asc':
        query = query.order_by(getattr(Alumno, sort_by).asc())
    else:
        query = query.order_by(getattr(Alumno, sort_by).desc())

    alumnos = query.paginate(page=page, per_page=10)
    return render_template('alumnos/lista.html', alumnos=alumnos, sort_by=sort_by, sort_order=sort_order)

@alumnos.route("/alumno/<int:alumno_id>")
@login_required
def detalle_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    return render_template('alumnos/detalle.html', alumno=alumno)

@alumnos.route("/alumnos/export")
@login_required
def export_alumnos():
    if current_user.rol != 'admin':
        abort(403)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'nombre', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)

    query = Alumno.query

    if search:
        query = query.filter(
            Alumno.nombre.ilike(f'%{search}%') |
            Alumno.apellidos.ilike(f'%{search}%') |
            Alumno.ci.ilike(f'%{search}%') |
            Alumno.correo_electronico.ilike(f'%{search}%') |
            Alumno.telefono_movil.ilike(f'%{search}%')
        )

    if sort_order == 'asc':
        query = query.order_by(getattr(Alumno, sort_by).asc())
    else:
        query = query.order_by(getattr(Alumno, sort_by).desc())

    alumnos = query.all()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Nombre', 'Apellidos', 'CI', 'Correo Electrónico', 'Teléfono Móvil'])
    for alumno in alumnos:
        cw.writerow([alumno.nombre, alumno.apellidos, alumno.ci, alumno.correo_electronico, alumno.telefono_movil])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=alumnos.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@alumnos.route("/alumnos/cargar_certificados/<int:alumno_id>", methods=['GET', 'POST'])
@login_required
def cargar_certificados(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    if current_user.rol != 'admin' and current_user.alumno_id != alumno_id:
        abort(403)
    form = CertificadoForm()
    if form.validate_on_submit():
        if form.certificados.data:
            for certificado_file in form.certificados.data:
                pdf_file = save_pdf(certificado_file)
                certificado = Certificado(
                    alumno_id=alumno.id,
                    nombre=certificado_file.filename,
                    archivo=pdf_file
                )
                db.session.add(certificado)
            db.session.commit()
            flash('Los certificados han sido subidos exitosamente.', 'success')
            return redirect(url_for('alumnos.detalle_alumno', alumno_id=alumno.id))
    return render_template('alumnos/cargar_certificados.html', alumno=alumno, form=form)

@alumnos.route("/buscar_alumno", methods=['GET', 'POST'])
@login_required
def buscar_alumno():
    if current_user.rol != 'admin':
        abort(403)
    form = BusquedaAlumnoForm()
    if form.validate_on_submit():
        alumno = Alumno.query.filter_by(ci=form.ci.data).first()
        if alumno:
            return redirect(url_for('alumnos.detalle_alumno', alumno_id=alumno.id))
        else:
            flash('No se encontró ningún alumno con ese CI.', 'danger')
    return render_template('alumnos/buscar.html', form=form)

@alumnos.route("/alumnos/generar_pdf/<int:alumno_id>")
@login_required
def generar_pdf_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    referencias = ReferenciaFamiliar.query.filter_by(alumno_id=alumno_id).all()
    seguimientos = SeguimientoAcademico.query.filter_by(alumno_id=alumno_id).all()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['BodyText']

    # Title
    elements.append(Paragraph(f"Detalle del Alumno: {alumno.nombre} {alumno.apellidos}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Imagen de Perfil
    if alumno.foto:
        image_path = os.path.join('static/profile_pics', alumno.foto)
        if os.path.exists(image_path):
            elements.append(Image(image_path, width=2 * inch, height=2 * inch))
            elements.append(Spacer(1, 0.2 * inch))

    # Personal Information
    elements.append(Paragraph("Información Personal", heading_style))
    elements.append(Spacer(1, 0.1 * inch))
    personal_info = [
        ["Fecha de Nacimiento:", alumno.fecha_nacimiento],
        ["Edad:", alumno.edad],
        ["CI:", alumno.ci],
        ["Nacionalidad:", alumno.nacionalidad],
        ["Teléfono Fijo:", alumno.telefono_fijo],
        ["Teléfono Móvil:", alumno.telefono_movil],
        ["Correo Electrónico:", alumno.correo_electronico],
        ["Estado Civil:", alumno.estado_civil],
        ["Sede:", alumno.sede],
        ["Número de Hijos:", alumno.n_hijos]
    ]
    table = Table(personal_info, colWidths=[2 * inch, 4 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))

    # Family References
    elements.append(Paragraph("Referencias Familiares", heading_style))
    elements.append(Spacer(1, 0.1 * inch))
    for referencia in referencias:
        elements.append(Paragraph(f"Nombres y Apellidos: {referencia.nombres_apellidos}", normal_style))
        elements.append(Paragraph(f"Parentesco: {referencia.parentesco}", normal_style))
        elements.append(Paragraph(f"Número de Contacto: {referencia.numero_contacto}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

    # Academic Follow-ups
    elements.append(Paragraph("Seguimientos Académicos", heading_style))
    elements.append(Spacer(1, 0.1 * inch))
    for seguimiento in seguimientos:
        elements.append(Paragraph(f"Fecha: {seguimiento.fecha}", normal_style))
        elements.append(Paragraph(f"Descripción: {seguimiento.descripcion}", normal_style))
        elements.append(Paragraph(f"Estado: {seguimiento.estado}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'alumno_{alumno.id}.pdf', mimetype='application/pdf')

@alumnos.route("/seguimiento/registrar", methods=['GET', 'POST'])
@login_required
def registrar_seguimiento():
    form = SeguimientoAcademicoForm()
    if form.validate_on_submit():
        seguimiento = SeguimientoAcademico(
            alumno_id=form.alumno_id.data,
            fecha=form.fecha.data,
            descripcion=form.descripcion.data,
            estado=form.estado.data
        )
        db.session.add(seguimiento)
        db.session.commit()
        flash('El seguimiento académico ha sido registrado exitosamente.', 'success')
        return redirect(url_for('alumnos.lista_alumnos'))
    return render_template('seguimiento/registrar.html', title='Registrar Seguimiento Académico', form=form)