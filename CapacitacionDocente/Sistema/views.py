from django.contrib.auth import authenticate, login, logout
from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse
import weasyprint
from django.http import JsonResponse
from django.db.models import Q

from .forms import (
    InscripcionForm, ListaAsistenciaForm, CriteriosSeleccionForm,
    CurriculumVitaeForm, DiagnosticoNecesidadesForm, EncuestaSatisfaccionForm,
    FichaTecnicaForm, ProgramaInstitucionalForm,
    RegistroFilaForm
)
from .models import (
    Curso, Inscripcion, FichaTecnica, CriteriosSeleccion, EncuestaSatisfaccion,
    ProgramaInstitucional, ProgramaDetalle,
    DiagnosticoNecesidades, DiagnosticoAsignatura, DiagnosticoActividad,
    CurriculumVitae, CVExperienciaLaboral, CVExperienciaDocente, CVProductoAcademico, CVParticipacionInstructor,
    ListaAsistencia, AsistenciaParticipante,
    RegistroGeneral, RegistroFila, Profesor
)

# --- 2. DICCIONARIO MAESTRO (CONFIGURACIÓN) ---
# Aquí registras cada formato. Si creas uno nuevo, solo agregas una línea aquí.
PDF_CONFIG = {
    'inscripcion': {
        'model': Inscripcion,
        'form': InscripcionForm,
        'template': 'Sistema/inscripcion/inscripcion.html'
    },
    'ficha': {
        'model': FichaTecnica,
        'form': FichaTecnicaForm,
        'template': 'Sistema/ficha/ficha.html'
    },
    'criterios': {
        'model': CriteriosSeleccion,
        'form': CriteriosSeleccionForm,
        'template': 'Sistema/criterios/criterios.html'
    },
    'cv': {
        'model': CurriculumVitae,
        'form': CurriculumVitaeForm,
        'template': 'Sistema/cv/cv.html'
    },
    'encuesta': {
        'model': EncuestaSatisfaccion,
        'form': EncuestaSatisfaccionForm,
        'template': 'Sistema/encuesta/encuesta.html'
    },
    'programa': {
        'model': ProgramaInstitucional,
        'form': ProgramaInstitucionalForm,
        'template': 'Sistema/programa/programa.html'
    },
    'diagnostico': {
        'model': DiagnosticoNecesidades,
        'form': DiagnosticoNecesidadesForm,
        'template': 'Sistema/diagnostico/diagnostico.html'
    },
    'cv': {
        'model': CurriculumVitae,
        'form': CurriculumVitaeForm,
        'template': 'Sistema/cv/cv.html'
    },
    'asistencia': {
        'model': ListaAsistencia,
        'form': ListaAsistenciaForm,
        'template': 'Sistema/asistencia/asistencia.html'
    },
    'registro': {
        'model': RegistroGeneral,
        'form': None,
        'template': 'Sistema/registro/registro.html'
    },
}


# --- 3. VISTA GENÉRICA ÚNICA ---
def descargar_pdf_generico(request, tipo, pk):
    config = PDF_CONFIG.get(tipo)
    if not config: return HttpResponse("Tipo no válido.", status=404)

    if tipo == 'registro':
        # Buscamos el PADRE específico
        registro = get_object_or_404(RegistroGeneral, pk=pk)
        form = None
    else:
        registro = get_object_or_404(config['model'], pk=pk)
        form = config['form'](instance=registro)

    context = {'form': form}

    # ... (Lógica de programa, diagnostico, cv, asistencia IGUAL) ...
    if tipo == 'programa':
        detalles_db = {d.no_consecutivo: d for d in registro.detalles.all()}
        filas = []
        for i in range(1, 11):
            d = detalles_db.get(i)
            filas.append({ 'counter': i, 'nombre_curso': d.nombre_curso if d else '', 'objetivo': d.objetivo if d else '', 'periodo': d.periodo_realizacion if d else '', 'lugar': d.lugar if d else '', 'horas': d.horas if d else '', 'instructor': d.instructor if d else '', 'dirigido': d.dirigido_a if d else '', 'observaciones': d.observaciones if d else '' })
        context['tabla_filas'] = filas

    elif tipo == 'diagnostico':
        def obtener_filas(modelo, tipo_tabla, cantidad=3):
            items = list(modelo.objects.filter(diagnostico=registro, tipo_tabla=tipo_tabla))
            while len(items) < cantidad: items.append(None)
            return items
        context['tabla_a'] = obtener_filas(DiagnosticoAsignatura, 'generica')
        context['tabla_b'] = obtener_filas(DiagnosticoAsignatura, 'especialidad')
        context['tabla_c'] = obtener_filas(DiagnosticoActividad, 'docente')
        context['tabla_d'] = obtener_filas(DiagnosticoActividad, 'profesional')

    elif tipo == 'cv':
        def obtener_cv_filas(modelo, cantidad=3):
            items = list(modelo.objects.filter(cv=registro))
            while len(items) < cantidad: items.append(None)
            return items
        context['tabla_laboral'] = obtener_cv_filas(CVExperienciaLaboral)
        context['tabla_docente'] = obtener_cv_filas(CVExperienciaDocente)
        context['tabla_productos'] = obtener_cv_filas(CVProductoAcademico)
        context['tabla_instructor'] = obtener_cv_filas(CVParticipacionInstructor)

    elif tipo == 'asistencia':
        participantes_db = {p.no_consecutivo: p for p in registro.participantes.all()}
        filas = []
        for i in range(1, 24):
            p = participantes_db.get(i)
            filas.append({ 'counter': i, 'nombre': p.nombre if p else '', 'rfc': p.rfc if p else '', 'puesto': p.puesto if p else '', 'sexo': p.sexo if p else '', 'asist_l': p.asist_l if p else '', 'asist_m1': p.asist_m1 if p else '', 'asist_m2': p.asist_m2 if p else '', 'asist_j': p.asist_j if p else '', 'asist_v': p.asist_v if p else '', 'concluyo': p.concluyo if p else '' })
        context['tabla_participantes'] = filas

    # --- LÓGICA REGISTRO (NUEVO) ---
    elif tipo == 'registro':
        # Recuperamos las FILAS de este registro
        filas_db = {r.no_consecutivo: r for r in registro.filas.all()}
        filas = []
        for i in range(1, 16):
            r = filas_db.get(i)
            filas.append({
                'counter': i,
                'instituto': r.instituto if r else '',
                'nombre_curso': r.nombre_curso if r else '',
                'es_formacion': 'X' if r and r.es_formacion else '',
                'es_actualizacion': 'X' if r and r.es_actualizacion else '',
                'instructor': r.instructor if r else '',
                'fecha_inicio': r.fecha_inicio if r else '',
                'fecha_termino': r.fecha_termino if r else '',
                'horas': r.horas if r else '',
                'modalidad': r.modalidad if r else '',
                'inscritos': r.docentes_inscritos if r else '',
                'terminaron': r.docentes_terminaron if r else '',
                'acreditados': r.docentes_acreditados if r else '',
                'tipo': r.tipo if r else '',
            })
        context['tabla_registros'] = filas
    # ---------------------------------------------

    html_string = render_to_string(config['template'], context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    filename = f"{tipo}_{pk}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

# --- FUNCIONES DE AYUDA Y AUTENTICACIÓN ---

def es_admin(user):
    return user.is_superuser or user.groups.filter(name='Administradores').exists()


def inicio(request):
    return render(request, 'Sistema/inicio/inicio.html')


def login_view(request):
    if request.method == 'POST':
        username_data = request.POST.get('username')
        password_data = request.POST.get('password')
        next_url = request.POST.get('next')

        user = authenticate(request, username=username_data, password=password_data)

        if user is not None:
            login(request, user)
            return redirect(next_url if next_url else 'Inicio')
        else:
            return render(request, 'Sistema/login/login.html',
                          {'error': 'Usuario o contraseña incorrectos', 'next': next_url})

    next_url = request.GET.get('next')
    return render(request, 'Sistema/login/login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    return redirect('Inicio')


@login_required(login_url='Login')
@user_passes_test(es_admin, login_url='/')
def menu_admin(request):
    return render(request, 'Sistema/layouts/menu_admin.html')


@login_required(login_url='Login')
def menu_instructor(request):
    return render(request, 'Sistema/layouts/menu_instructor.html')


def menu(request):
    return render(request, 'Sistema/layouts/menu.html')


# =======================================================
# VISTAS DE FORMULARIOS (GUARDADO DE DATOS)
# =======================================================

# 1. INSCRIPCIÓN + PDF
def inscripcion(request):
    # 1. LEER: Revisar si venimos de un guardado exitoso para ofrecer PDF
    download_data = request.session.pop('pdf_download', None)

    if request.method == 'POST':
        # ESTO ES LO QUE VALIDA QUE NO VENGA VACÍO
        form = InscripcionForm(request.POST)

        if form.is_valid():
            # 2. GUARDAR: Guardamos y capturamos el objeto creado
            nuevo_registro = form.save()

            # 3. RECORDAR: Guardamos en sesión qué se acaba de crear
            # 'tipo': 'inscripcion' debe coincidir con la clave en tu PDF_CONFIG
            request.session['pdf_download'] = {'tipo': 'inscripcion', 'pk': nuevo_registro.pk}

            messages.success(request, 'Inscripción guardada exitosamente.')
            return redirect('Inscripcion')
        else:
            # Si form.is_valid() es False, NO se guarda nada y se muestra el error
            messages.error(request, 'Formulario incompleto. Revisa los campos rojos.')
    else:
        form = InscripcionForm()

    # Es vital pasar 'form' y 'download_data' al render
    return render(request, 'Sistema/inscripcion/inscripcion.html', {
        'form': form,
        'download_data': download_data
    })


# 2. FICHA TÉCNICA + PDF
def ficha(request):
    # 1. LEER: Revisar si venimos de un guardado exitoso para ofrecer PDF
    download_data = request.session.pop('pdf_download', None)

    if request.method == 'POST':
        form = FichaTecnicaForm(request.POST)

        if form.is_valid():
            # 2. GUARDAR: Guardamos y capturamos el objeto creado
            nuevo_registro = form.save()

            # 3. RECORDAR: Guardamos en sesión qué se acaba de crear
            request.session['pdf_download'] = {'tipo': 'ficha', 'pk': nuevo_registro.pk}

            messages.success(request, 'Ficha Técnica guardada exitosamente.')
            return redirect('Ficha')
        else:
            messages.error(request, 'El formulario está incompleto. Por favor revisa todos los campos.')
    else:
        form = FichaTecnicaForm()

    return render(request, 'Sistema/ficha/ficha.html', {
        'form': form,
        'download_data': download_data  # 4. ENVIAR: Pasamos el dato al HTML para que pinte el botón
    })


# 3. CRITERIOS DE SELECCIÓN + PDF
def criterios(request):
    # 1. LEER: Revisar si venimos de un guardado exitoso para ofrecer PDF
    download_data = request.session.pop('pdf_download', None)

    if request.method == 'POST':
        form = CriteriosSeleccionForm(request.POST)

        if form.is_valid():
            # 2. GUARDAR: Guardamos y capturamos el objeto creado
            nuevo_registro = form.save()

            # 3. RECORDAR: Guardamos en sesión qué se acaba de crear
            # 'tipo': 'criterios' debe coincidir con la clave en tu PDF_CONFIG
            request.session['pdf_download'] = {'tipo': 'criterios', 'pk': nuevo_registro.pk}

            messages.success(request, 'Criterios guardados exitosamente.')
            return redirect('Criterios')
        else:
            messages.error(request, 'Formulario incompleto. Por favor califica todos los puntos y verifica las firmas.')
    else:
        form = CriteriosSeleccionForm()

    return render(request, 'Sistema/criterios/criterios.html', {
        'form': form,
        'download_data': download_data
    })


# 4. ENCUESTA + PDF
def encuesta(request):
    # 1. LEER: Revisar si venimos de un guardado exitoso para ofrecer PDF
    download_data = request.session.pop('pdf_download', None)

    if request.method == 'POST':
        # 1. Cargar todas las respuestas en el formulario
        form = EncuestaSatisfaccionForm(request.POST)

        # 2. Validar (Candado Servidor)
        if form.is_valid():
            # GUARDAR: Guardamos y capturamos el objeto creado
            nuevo_registro = form.save()

            # RECORDAR: Guardamos en sesión qué se acaba de crear
            # 'tipo': 'encuesta' debe coincidir con la clave en tu PDF_CONFIG (que agregarás después si no está)
            # NOTA: Asegúrate de agregar 'encuesta' a tu diccionario PDF_CONFIG arriba en views.py
            request.session['pdf_download'] = {'tipo': 'encuesta', 'pk': nuevo_registro.pk}

            messages.success(request, 'Encuesta enviada correctamente.')
            return redirect('Encuesta')
        else:
            # Si faltó responder alguna pregunta
            messages.error(request,
                           'La encuesta está incompleta. Por favor asegúrate de responder todas las preguntas.')
    else:
        form = EncuestaSatisfaccionForm()

    return render(request, 'Sistema/encuesta/encuesta.html', {
        'form': form,
        'download_data': download_data
    })


# 5. PROGRAMA DE FORMACIÓN + PDF
def programa(request):
    download_data = request.session.pop('pdf_download', None)

    if request.method == 'POST':
        form = ProgramaInstitucionalForm(request.POST)

        if form.is_valid():
            prog = form.save()

            # Guardar las 10 filas (Tu lógica original intacta)
            for i in range(1, 11):
                if request.POST.get(f'curso_{i}'):
                    ProgramaDetalle.objects.create(
                        programa=prog,
                        no_consecutivo=request.POST.get(f'no_{i}'),
                        nombre_curso=request.POST.get(f'curso_{i}'),
                        objetivo=request.POST.get(f'objetivo_{i}'),
                        periodo_realizacion=request.POST.get(f'periodo_{i}'),
                        lugar=request.POST.get(f'lugar_{i}'),
                        horas=request.POST.get(f'horas_{i}') or 0,
                        instructor=request.POST.get(f'instructor_{i}'),
                        dirigido_a=request.POST.get(f'dirigido_{i}'),
                        observaciones=request.POST.get(f'observaciones_{i}')
                    )

            # Guardamos datos para descarga
            request.session['pdf_download'] = {'tipo': 'programa', 'pk': prog.pk}

            messages.success(request, 'Programa guardado exitosamente.')
            return redirect('Programa')
        else:
            messages.error(request, 'El formulario está incompleto. Por favor revisa el periodo y las firmas.')
    else:
        form = ProgramaInstitucionalForm()

    return render(request, 'Sistema/programa/programa.html', {
        'form': form,
        'download_data': download_data
    })


# 6. DIAGNÓSTICO + PDF
def diagnostico(request):
    download_data = request.session.pop('pdf_download', None)

    if request.method == 'POST':
        form = DiagnosticoNecesidadesForm(request.POST)
        if form.is_valid():
            diag = form.save()

            # Guardar Tablas A, B, C, D
            # Tabla A
            for i in range(1, 4):
                if request.POST.get(f'a_asignatura_{i}'):
                    DiagnosticoAsignatura.objects.create(
                        diagnostico=diag, tipo_tabla='generica',
                        asignatura=request.POST.get(f'a_asignatura_{i}'),
                        contenido=request.POST.get(f'a_contenido_{i}'),
                        num_profesores=request.POST.get(f'a_num_profes_{i}') or 0,
                        periodo=request.POST.get(f'a_periodo_{i}'),
                        instructor_propuesto=request.POST.get(f'a_instructor_{i}')
                    )
            # Tabla B
            for i in range(1, 4):
                if request.POST.get(f'b_asignatura_{i}'):
                    DiagnosticoAsignatura.objects.create(
                        diagnostico=diag, tipo_tabla='especialidad',
                        asignatura=request.POST.get(f'b_asignatura_{i}'),
                        contenido=request.POST.get(f'b_contenido_{i}'),
                        num_profesores=request.POST.get(f'b_num_profes_{i}') or 0,
                        periodo=request.POST.get(f'b_periodo_{i}'),
                        instructor_propuesto=request.POST.get(f'b_instructor_{i}')
                    )
            # Tabla C
            for i in range(1, 4):
                if request.POST.get(f'c_actividad_{i}'):
                    DiagnosticoActividad.objects.create(
                        diagnostico=diag, tipo_tabla='docente',
                        actividad=request.POST.get(f'c_actividad_{i}'),
                        carrera_atendida=request.POST.get(f'c_carrera_{i}'),
                        fecha_evento=request.POST.get(f'c_fecha_{i}')
                    )
            # Tabla D
            for i in range(1, 4):
                if request.POST.get(f'd_actividad_{i}'):
                    DiagnosticoActividad.objects.create(
                        diagnostico=diag, tipo_tabla='profesional',
                        actividad=request.POST.get(f'd_actividad_{i}'),
                        carrera_atendida=request.POST.get(f'd_carrera_{i}'),
                        fecha_evento=request.POST.get(f'd_fecha_{i}')
                    )

            request.session['pdf_download'] = {'tipo': 'diagnostico', 'pk': diag.pk}
            messages.success(request, 'Diagnóstico guardado exitosamente.')
            return redirect('Diagnostico')
        else:
            messages.error(request, 'Formulario incompleto.')
    else:
        form = DiagnosticoNecesidadesForm()

    return render(request, 'Sistema/diagnostico/diagnostico.html', {
        'form': form,
        'download_data': download_data
    })

# 7. CURRICULUM VITAE + PDF
def cv(request):
    download_data = request.session.pop('pdf_download', None)

    if request.method == 'POST':
        form = CurriculumVitaeForm(request.POST)
        if form.is_valid():
            curriculum = form.save()

            # Guardar Tablas Hijas
            for i in range(1, 4):
                if request.POST.get(f'exp_puesto_{i}'):
                    CVExperienciaLaboral.objects.create(
                        cv=curriculum,
                        puesto=request.POST.get(f'exp_puesto_{i}'),
                        empresa=request.POST.get(f'exp_empresa_{i}'),
                        permanencia=request.POST.get(f'exp_permanencia_{i}'),
                        actividades=request.POST.get(f'exp_actividades_{i}')
                    )
            for i in range(1, 4):
                if request.POST.get(f'doc_materia_{i}'):
                    CVExperienciaDocente.objects.create(
                        cv=curriculum,
                        materia=request.POST.get(f'doc_materia_{i}'),
                        periodo=request.POST.get(f'doc_periodo_{i}')
                    )
            for i in range(1, 4):
                if request.POST.get(f'prod_actividad_{i}'):
                    CVProductoAcademico.objects.create(
                        cv=curriculum,
                        actividad=request.POST.get(f'prod_actividad_{i}'),
                        descripcion=request.POST.get(f'prod_desc_{i}'),
                        fecha=request.POST.get(f'prod_fecha_{i}')
                    )
            for i in range(1, 4):
                if request.POST.get(f'inst_curso_{i}'):
                    CVParticipacionInstructor.objects.create(
                        cv=curriculum,
                        nombre_curso=request.POST.get(f'inst_curso_{i}'),
                        institucion=request.POST.get(f'inst_org_{i}'),
                        duracion=request.POST.get(f'inst_duracion_{i}'),
                        fecha=request.POST.get(f'inst_fecha_{i}')
                    )

            # Guardar sesión para descarga
            request.session['pdf_download'] = {'tipo': 'cv', 'pk': curriculum.pk}

            messages.success(request, 'Curriculum guardado correctamente.')
            return redirect('CV')
        else:
            messages.error(request, 'El formulario está incompleto. Por favor revisa los Datos Personales.')
    else:
        form = CurriculumVitaeForm()

    return render(request, 'Sistema/cv/cv.html', {
        'form': form,
        'download_data': download_data
    })


# 8. ASISTENCIA + PDF
# --- VISTA 1: TABLERO DE MIS LISTAS (Para que el instructor elija cuál continuar) ---
@login_required(login_url='Login')
def mis_listas_asistencia(request):
    # Filtramos solo las listas creadas por el usuario logueado
    listas = ListaAsistencia.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'Sistema/asistencia/mis_listas.html', {'listas': listas})


# --- VISTA 2: CREAR O EDITAR LISTA ---
@login_required(login_url='Login')
def asistencia(request, pk=None):
    # --- 1. LÓGICA INTELIGENTE (NUEVO) ---
    # Si entramos desde el menú (pk es None), buscamos si ya existe un borrador.
    if pk is None:
        borrador_pendiente = ListaAsistencia.objects.filter(
            usuario=request.user,
            estado='borrador'
        ).order_by('-fecha_creacion').first()

        if borrador_pendiente:
            # Si encontramos un borrador, redirigimos automáticamente a él
            return redirect('editar_asistencia', pk=borrador_pendiente.pk)
    # -------------------------------------

    # --- 2. EL RESTO DE TU CÓDIGO SIGUE IGUAL ---
    if pk:
        # MODO EDICIÓN
        lista = get_object_or_404(ListaAsistencia, pk=pk, usuario=request.user)
        participantes_db = list(lista.participantes.all().order_by('no_consecutivo'))
    else:
        # MODO CREACIÓN (Solo si no había borradores)
        lista = None
        participantes_db = []

    # ... (El resto de la vista continúa idéntico a lo que tenías) ...
    # Preparamos los datos para la plantilla...
    filas_participantes = []
    db_map = {p.no_consecutivo: p for p in participantes_db}

    for i in range(1, 24):
        p = db_map.get(i)
        filas_participantes.append({
            'counter': i,
            'nombre': p.nombre if p else '',
            'rfc': p.rfc if p else '',
            'puesto': p.puesto if p else '',
            'sexo': p.sexo if p else '',
            'asist_l': p.asist_l if p else '',
            'asist_m1': p.asist_m1 if p else '',
            'asist_m2': p.asist_m2 if p else '',
            'asist_j': p.asist_j if p else '',
            'asist_v': p.asist_v if p else '',
            'concluyo': p.concluyo if p else ''
        })

    if request.method == 'POST':
        # ... (Tu código de guardar que ya funciona) ...
        # Solo asegúrate de que este bloque esté igual al que te pasé antes
        form = ListaAsistenciaForm(request.POST, instance=lista)

        if form.is_valid():
            nueva_lista = form.save(commit=False)
            nueva_lista.usuario = request.user

            if 'btn_finalizar' in request.POST:
                nueva_lista.estado = 'finalizado'
                mensaje = 'Lista finalizada exitosamente.'
            else:
                nueva_lista.estado = 'borrador'
                mensaje = 'Progreso guardado correctamente.'

            nueva_lista.save()

            if lista:
                AsistenciaParticipante.objects.filter(lista=lista).delete()

            for i in range(1, 24):
                nombre = request.POST.get(f'nombre_{i}')
                if nombre:
                    AsistenciaParticipante.objects.create(
                        lista=nueva_lista,
                        no_consecutivo=i,
                        nombre=nombre,
                        rfc=request.POST.get(f'rfc_{i}', ''),
                        puesto=request.POST.get(f'puesto_{i}', ''),
                        sexo=request.POST.get(f'sexo_{i}', ''),
                        asist_l=request.POST.get(f'asist_l_{i}', ''),
                        asist_m1=request.POST.get(f'asist_m1_{i}', ''),
                        asist_m2=request.POST.get(f'asist_m2_{i}', ''),
                        asist_j=request.POST.get(f'asist_j_{i}', ''),
                        asist_v=request.POST.get(f'asist_v_{i}', ''),
                        concluyo=request.POST.get(f'concluyo_{i}', '')
                    )

            # Redirección
            if nueva_lista.estado == 'finalizado':
                request.session['pdf_download'] = {'tipo': 'asistencia', 'pk': nueva_lista.pk}
                # Al finalizar, redirigimos a "crear nueva" para limpiar la pantalla
                # (Como ya no es borrador, la lógica del inicio no lo abrirá)
                return redirect('Asistencia')
            else:
                messages.success(request, mensaje)
                return redirect('editar_asistencia', pk=nueva_lista.pk)

        else:
            messages.error(request, 'Error en el formulario.')
    else:
        form = ListaAsistenciaForm(instance=lista)

    return render(request, 'Sistema/asistencia/asistencia.html', {
        'form': form,
        'tabla_participantes': filas_participantes,
        'download_data': request.session.pop('pdf_download', None)
    })

# 9. REGISTRO GENERAL + PDF
def registro(request):
    download_data = request.session.pop('pdf_download', None)

    if request.method == 'POST':
        # 1. Crear el documento PADRE primero
        # (Podrías agregar inputs en el HTML para periodo, etc., por ahora usamos defaults)
        nuevo_registro = RegistroGeneral.objects.create(
            periodo="2025",
            jefe_desarrollo="Ing. Juan Perez",
            subdirector="Lic. Maria Lopez"
        )

        filas_guardadas = 0

        # 2. Guardar las HIJAS vinculadas
        for i in range(1, 16):
            nombre = request.POST.get(f'curso_{i}')
            if nombre:
                filas_guardadas += 1

                # Preparamos datos para validar con el FORMULARIO NUEVO
                data_row = {
                    'instituto': request.POST.get(f'instituto_{i}'),
                    'nombre_curso': nombre,
                    'instructor': request.POST.get(f'instructor_{i}'),
                    'fecha_inicio': request.POST.get(f'f_inicio_{i}'),
                    'fecha_termino': request.POST.get(f'f_termino_{i}'),
                    'horas': request.POST.get(f'horas_{i}'),
                    'modalidad': request.POST.get(f'modalidad_{i}'),
                    'docentes_inscritos': request.POST.get(f'inscritos_{i}'),
                    'docentes_terminaron': request.POST.get(f'terminaron_{i}'),
                    'docentes_acreditados': request.POST.get(f'acreditados_{i}'),
                    'tipo': request.POST.get(f'tipo_{i}'),
                }

                form = RegistroFilaForm(data_row)  # <--- USAMOS EL FORM NUEVO

                if form.is_valid():
                    obj = form.save(commit=False)
                    obj.registro = nuevo_registro  # Vinculamos al padre
                    obj.no_consecutivo = i
                    obj.es_formacion = True if request.POST.get(f'formacion_{i}') else False
                    obj.es_actualizacion = True if request.POST.get(f'actualizacion_{i}') else False
                    obj.save()
                else:
                    # Si hay error, borramos el padre para no dejar basura y avisamos
                    nuevo_registro.delete()
                    messages.error(request, f'Error en fila {i}: {form.errors}')
                    return redirect('Registro')

        if filas_guardadas > 0:
            request.session['pdf_download'] = {'tipo': 'registro', 'pk': nuevo_registro.pk}
            messages.success(request, 'Registro General guardado exitosamente.')
            return redirect('Registro')
        else:
            nuevo_registro.delete()
            messages.error(request, 'El formulario está vacío.')

    return render(request, 'Sistema/registro/registro.html', {
        'download_data': download_data
    })


# =======================================================
# GESTIÓN DE CURSOS (ADMIN)
# =======================================================

def cursos(request):
    cursos = Curso.objects.all().order_by('-id')
    return render(request, 'Sistema/cursos/cursos.html', {'cursos': cursos})


def crear_curso(request):
    if request.method == 'POST':
        Curso.objects.create(
            nombre=request.POST['nombre'],
            clave=request.POST['clave'],
            instructor=request.POST['instructor'],
            periodo=request.POST['periodo']
        )
        messages.success(request, 'Curso creado exitosamente.')
    return redirect('gestion_cursos')  # Asegúrate que 'gestion_cursos' es el name en urls.py, sino usa 'Cursos'


def editar_curso(request):
    if request.method == 'POST':
        curso_id = request.POST['curso_id']
        curso = Curso.objects.get(id=curso_id)
        curso.nombre = request.POST['nombre']
        curso.instructor = request.POST['instructor']
        curso.periodo = request.POST['periodo']
        curso.estado = request.POST['estado']
        curso.save()
        messages.success(request, 'Curso actualizado.')
    return redirect('gestion_cursos')


def eliminar_curso(request):
    if request.method == 'POST':
        curso_id = request.POST['curso_id']
        Curso.objects.get(id=curso_id).delete()
        messages.success(request, 'Curso eliminado.')
    return redirect('gestion_cursos')


def estadisticas(request):
    # 1. Obtener todas las encuestas base
    encuestas = EncuestaSatisfaccion.objects.all()

    # 2. Obtener listas para los filtros (valores únicos)
    periodos = EncuestaSatisfaccion.objects.values_list('periodo', flat=True).distinct()
    facilitadores = EncuestaSatisfaccion.objects.values_list('facilitador', flat=True).distinct()

    # 3. Aplicar Filtros si el usuario los seleccionó
    periodo_select = request.GET.get('periodo')
    facilitador_select = request.GET.get('facilitador')

    if periodo_select:
        encuestas = encuestas.filter(periodo=periodo_select)

    if facilitador_select:
        encuestas = encuestas.filter(facilitador=facilitador_select)

    # 4. Calcular promedios por pregunta (q1 a q20)
    # Esto genera un diccionario: {'q1__avg': 4.5, 'q2__avg': 3.8, ...}
    promedios = encuestas.aggregate(
        *[Avg(f'q{i}') for i in range(1, 21)]
    )

    # 5. Preparar datos para Chart.js (Limpiar los None si no hay datos)
    datos_grafica = []
    labels_grafica = []

    for i in range(1, 21):
        clave = f'q{i}__avg'
        valor = promedios.get(clave) or 0  # Si es None, pone 0
        datos_grafica.append(round(valor, 2))  # Redondear a 2 decimales
        labels_grafica.append(f'P{i}')  # Etiquetas P1, P2...

    context = {
        'periodos': periodos,
        'facilitadores': facilitadores,
        'datos_grafica': datos_grafica,
        'labels_grafica': labels_grafica,
        'periodo_actual': periodo_select,
        'facilitador_actual': facilitador_select
    }

    return render(request, 'Sistema/estadisticas/estadisticas.html', context)


# =======================================================
# API: AUTOCOMPLETADO
# =======================================================

def api_buscar_curso(request):
    """Busca un curso por su clave y devuelve sus datos en JSON."""
    clave = request.GET.get('clave', '').strip()
    data = {'found': False}

    if clave:
        try:
            curso = Curso.objects.get(clave=clave)
            data = {
                'found': True,
                'nombre': curso.nombre,
                'instructor': curso.instructor,
                'periodo': curso.periodo,
                # Si tienes horario en el modelo Curso, agrégalo aquí:
                # 'horario': curso.horario
            }
        except Curso.DoesNotExist:
            pass

    return JsonResponse(data)


def api_buscar_profesor(request):
    """Busca un profesor por RFC o CURP."""
    query = request.GET.get('q', '').strip()
    data = {'found': False}

    if query:
        try:
            # Buscamos si lo que escribió coincide con RFC o con CURP
            profesor = Profesor.objects.get(Q(rfc__iexact=query) | Q(curp__iexact=query))

            # Concatenamos el nombre completo
            nombre_completo = f"{profesor.nombre} {profesor.apellido_paterno} {profesor.apellido_materno}".strip()

            data = {
                'found': True,
                'nombre_completo': nombre_completo,
                'rfc': profesor.rfc,
                'curp': profesor.curp,
                #'email': profesor.email,
                #'telefono': profesor.telefono,
                # Mapeamos departamento a "area_adscripcion" si aplica
                #'area': profesor.departamento,
            }
        except (Profesor.DoesNotExist, Profesor.MultipleObjectsReturned):
            pass

    return JsonResponse(data)