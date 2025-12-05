from django.db import models
from django.contrib.auth.models import User  # <--- IMPORTANTE

# =======================================================
# 1. MODELO DE CURSO (EXISTENTE)
# =======================================================
class Curso(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('pausa', 'En Pausa'),
        ('cancelado', 'Cancelado'),
    ]
    nombre = models.CharField(max_length=200)
    clave = models.CharField(max_length=50, unique=True)
    instructor = models.CharField(max_length=200)
    periodo = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')

    def __str__(self):
        return self.nombre


# =======================================================
# 2. INSCRIPCIÓN (Cédula de Inscripción)
# =======================================================
class Inscripcion(models.Model):
    fecha = models.DateField(null=True, blank=True)
    # Datos del Curso
    clave_curso = models.CharField(max_length=50)
    nombre_curso = models.CharField(max_length=200)
    nombre_instructor = models.CharField(max_length=200)
    periodo = models.CharField(max_length=100)
    horario = models.CharField(max_length=100)
    duracion = models.CharField(max_length=50)

    # Datos Personales
    GENERO_CHOICES = [('hombre', 'Hombre'), ('mujer', 'Mujer')]
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES)
    nombre_completo = models.CharField(max_length=250)
    rfc = models.CharField(max_length=20)
    curp = models.CharField(max_length=20)
    email = models.EmailField()
    grado_estudios = models.CharField(max_length=100)
    carrera = models.CharField(max_length=200)

    # Datos Laborales
    instituto = models.CharField(max_length=200)
    area_adscripcion = models.CharField(max_length=100)
    puesto = models.CharField(max_length=100)
    jefe_inmediato = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    extension = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_completo} - {self.nombre_curso}"


# =======================================================
# 3. FICHA TÉCNICA
# =======================================================
class FichaTecnica(models.Model):
    nombre_curso = models.CharField(max_length=200)
    instructor = models.CharField(max_length=200)
    introduccion = models.TextField()
    justificacion = models.TextField()
    objetivo_general = models.TextField()

    # Descripción
    desc_duracion = models.CharField(max_length=100)
    desc_contenido = models.TextField()
    desc_materiales = models.TextField()
    desc_criterios = models.TextField()

    resultados = models.TextField()
    fuentes_informacion = models.TextField()

    def __str__(self):
        return self.nombre_curso


# =======================================================
# 4. CRITERIOS DE SELECCIÓN DE INSTRUCTOR
# =======================================================
class CriteriosSeleccion(models.Model):
    nombre_instructor = models.CharField(max_length=200)
    fecha_evaluacion = models.DateField(null=True, blank=True)
    nombre_curso = models.CharField(max_length=200)
    empresa = models.CharField(max_length=200)

    # Puntajes (1 al 5)
    criterio_1 = models.IntegerField(default=0)  # Formación
    criterio_2 = models.IntegerField(default=0)  # Experiencia
    criterio_3 = models.IntegerField(default=0)  # Materiales
    criterio_4 = models.IntegerField(default=0)  # Disponibilidad
    criterio_5 = models.IntegerField(default=0)  # Certificaciones

    total_puntaje = models.IntegerField(default=0)
    aceptado = models.CharField(max_length=5, choices=[('si', 'Sí'), ('no', 'No')])

    def __str__(self):
        return f"Evaluación de {self.nombre_instructor}"


# =======================================================
# 5. ENCUESTA DE OPINIÓN
# =======================================================
class EncuestaSatisfaccion(models.Model):
    nombre_curso = models.CharField(max_length=200)
    fecha = models.DateField(null=True, blank=True)
    clave = models.CharField(max_length=50)
    duracion = models.CharField(max_length=50)
    institucion = models.CharField(max_length=200)
    facilitador = models.CharField(max_length=200)
    periodo = models.CharField(max_length=100)
    horario = models.CharField(max_length=100)

    # Preguntas (1 al 5)
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    q4 = models.IntegerField()
    q5 = models.IntegerField()
    q6 = models.IntegerField()
    q7 = models.IntegerField()
    q8 = models.IntegerField()
    q9 = models.IntegerField()
    q10 = models.IntegerField()
    q11 = models.IntegerField()
    q12 = models.IntegerField()
    q13 = models.IntegerField()
    q14 = models.IntegerField()
    q15 = models.IntegerField()
    q16 = models.IntegerField()
    q17 = models.IntegerField()
    q18 = models.IntegerField()
    q19 = models.IntegerField()
    q20 = models.IntegerField()

    comentarios = models.TextField(blank=True, null=True)


# =======================================================
# 6. REGISTRO GENERAL DE FORMACIÓN (Filas de la tabla)
# =======================================================
class RegistroGeneral(models.Model):
    # Puedes agregar campos para identificar el documento, por ejemplo el periodo o año
    periodo = models.CharField(max_length=100, default="Periodo Actual")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Firmas (Pie de página)
    jefe_desarrollo = models.CharField(max_length=200, blank=True)
    subdirector = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Registro General - {self.periodo} ({self.fecha_creacion.strftime('%d/%m/%Y')})"


# --- MODELO HIJO (Antes RegistroFormacion) ---
class RegistroFila(models.Model):
    registro = models.ForeignKey(RegistroGeneral, on_delete=models.CASCADE, related_name='filas')
    no_consecutivo = models.IntegerField()

    instituto = models.CharField(max_length=200, blank=True)
    nombre_curso = models.TextField(blank=True)

    es_formacion = models.BooleanField(default=False)
    es_actualizacion = models.BooleanField(default=False)

    instructor = models.TextField(blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_termino = models.DateField(null=True, blank=True)
    horas = models.IntegerField(null=True, blank=True)
    modalidad = models.CharField(max_length=50, blank=True)

    docentes_inscritos = models.IntegerField(default=0)
    docentes_terminaron = models.IntegerField(default=0)
    docentes_acreditados = models.IntegerField(default=0)
    tipo = models.CharField(max_length=10, blank=True)


# =======================================================
# 7. PROGRAMA DE FORMACIÓN (Documento y Detalles)
# =======================================================
class ProgramaInstitucional(models.Model):
    periodo = models.CharField(max_length=100)
    elaboro_nombre = models.CharField(max_length=200)
    elaboro_fecha = models.DateField(null=True, blank=True)
    aprobo_nombre = models.CharField(max_length=200)
    aprobo_fecha = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Programa {self.periodo}"


class ProgramaDetalle(models.Model):
    programa = models.ForeignKey(ProgramaInstitucional, on_delete=models.CASCADE, related_name='detalles')
    no_consecutivo = models.IntegerField()
    nombre_curso = models.TextField()
    objetivo = models.TextField()
    periodo_realizacion = models.TextField()
    lugar = models.TextField()
    horas = models.IntegerField(null=True, blank=True)
    instructor = models.TextField()
    dirigido_a = models.TextField()
    observaciones = models.TextField(blank=True, null=True)


# =======================================================
# 8. DIAGNÓSTICO DE NECESIDADES (Documento y Detalles)
# =======================================================
class DiagnosticoNecesidades(models.Model):
    departamento_academico = models.CharField(max_length=200)
    carrera = models.CharField(max_length=200)
    dept_origen = models.CharField(max_length=200)
    fecha_realizacion = models.DateField(null=True, blank=True)

    # Firmas Parte 1
    jefe_nombre = models.CharField(max_length=200)
    presidente_nombre = models.CharField(max_length=200)
    secretario_nombre = models.CharField(max_length=200)

    # Concentrado
    fecha_concentrado = models.DateField(null=True, blank=True)
    subdirector_nombre = models.CharField(max_length=200)

    # --- NUEVOS CAMPOS PARA LA ÚLTIMA TABLA (JEFES) ---
    jefe1_nombre = models.CharField(max_length=200, blank=True)
    jefe1_depto = models.CharField(max_length=200, blank=True)

    jefe2_nombre = models.CharField(max_length=200, blank=True)
    jefe2_depto = models.CharField(max_length=200, blank=True)

    jefe3_nombre = models.CharField(max_length=200, blank=True)
    jefe3_depto = models.CharField(max_length=200, blank=True)

    jefe4_nombre = models.CharField(max_length=200, blank=True)
    jefe4_depto = models.CharField(max_length=200, blank=True)

    # Fecha de registro en sistema
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnóstico {self.departamento_academico}"


class DiagnosticoAsignatura(models.Model):
    """Para las tablas a) Genéricas y b) Especialidad"""
    TIPO_CHOICES = [('generica', 'Genérica'), ('especialidad', 'Especialidad')]

    diagnostico = models.ForeignKey(DiagnosticoNecesidades, on_delete=models.CASCADE, related_name='asignaturas')
    tipo_tabla = models.CharField(max_length=20, choices=TIPO_CHOICES)

    asignatura = models.TextField()
    contenido = models.TextField()
    num_profesores = models.IntegerField(null=True, blank=True)
    periodo = models.CharField(max_length=100)
    instructor_propuesto = models.TextField()


class DiagnosticoActividad(models.Model):
    """Para las tablas del concentrado: c) Docente y d) Profesional"""
    TIPO_CHOICES = [('docente', 'Formación Docente'), ('profesional', 'Formación Profesional')]

    diagnostico = models.ForeignKey(DiagnosticoNecesidades, on_delete=models.CASCADE, related_name='actividades')
    tipo_tabla = models.CharField(max_length=20, choices=TIPO_CHOICES)

    actividad = models.CharField(max_length=255)
    carrera_atendida = models.CharField(max_length=255)
    fecha_evento = models.CharField(max_length=100)


# =======================================================
# 9. CURRICULUM VITAE (CV)
# =======================================================
class CurriculumVitae(models.Model):
    # Datos Personales
    nombre = models.CharField(max_length=200)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    curp = models.CharField(max_length=20)
    rfc = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()

    # Formación Académica (Campos fijos)
    lic_institucion = models.CharField(max_length=200, blank=True)
    lic_titulacion = models.CharField(max_length=100, blank=True)
    lic_cedula = models.CharField(max_length=50, blank=True)

    maestria_institucion = models.CharField(max_length=200, blank=True)
    maestria_titulacion = models.CharField(max_length=100, blank=True)
    maestria_cedula = models.CharField(max_length=50, blank=True)

    doc_institucion = models.CharField(max_length=200, blank=True)
    doc_titulacion = models.CharField(max_length=100, blank=True)
    doc_cedula = models.CharField(max_length=50, blank=True)

    esp_institucion = models.CharField(max_length=200, blank=True)
    esp_titulacion = models.CharField(max_length=100, blank=True)
    esp_cedula = models.CharField(max_length=50, blank=True)

    otros_institucion = models.CharField(max_length=200, blank=True)
    otros_titulacion = models.CharField(max_length=100, blank=True)
    otros_cedula = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.nombre


# Tablas del CV
class CVExperienciaLaboral(models.Model):
    cv = models.ForeignKey(CurriculumVitae, on_delete=models.CASCADE)
    puesto = models.CharField(max_length=200)
    empresa = models.CharField(max_length=200)
    permanencia = models.CharField(max_length=100)
    actividades = models.TextField()


class CVExperienciaDocente(models.Model):
    cv = models.ForeignKey(CurriculumVitae, on_delete=models.CASCADE)
    materia = models.CharField(max_length=200)
    periodo = models.CharField(max_length=100)


class CVProductoAcademico(models.Model):
    cv = models.ForeignKey(CurriculumVitae, on_delete=models.CASCADE)
    actividad = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.CharField(max_length=100)


class CVParticipacionInstructor(models.Model):
    cv = models.ForeignKey(CurriculumVitae, on_delete=models.CASCADE)
    nombre_curso = models.CharField(max_length=200)
    institucion = models.CharField(max_length=200)
    duracion = models.CharField(max_length=50)
    fecha = models.CharField(max_length=100)


# =======================================================
# 10. LISTA DE ASISTENCIA
# =======================================================
class ListaAsistencia(models.Model):
    # --- NUEVOS CAMPOS ---
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[('borrador', 'Borrador'), ('finalizado', 'Finalizado')],
                              default='borrador')

    # --- TUS CAMPOS EXISTENTES ---
    hoja_actual = models.CharField(max_length=10, default="1")
    hoja_total = models.CharField(max_length=10, default="1")
    instituto = models.CharField(max_length=200, default="REYNOSA")
    clave_curso = models.CharField(max_length=50)
    folio = models.CharField(max_length=50)
    nombre_curso = models.CharField(max_length=200)
    instructor = models.CharField(max_length=200)
    periodo = models.CharField(max_length=100)
    duracion = models.CharField(max_length=50)
    horario = models.CharField(max_length=100)

    # Pie de página
    instructor_rfc = models.CharField(max_length=20, blank=True)
    instructor_curp = models.CharField(max_length=20, blank=True)
    coordinador_rfc = models.CharField(max_length=20, blank=True)
    coordinador_curp = models.CharField(max_length=20, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lista: {self.nombre_curso} ({self.estado})"


class AsistenciaParticipante(models.Model):
    lista = models.ForeignKey(ListaAsistencia, on_delete=models.CASCADE, related_name='participantes')
    no_consecutivo = models.IntegerField()
    nombre = models.CharField(max_length=200, blank=True)
    rfc = models.CharField(max_length=20, blank=True)
    puesto = models.CharField(max_length=100, blank=True)
    sexo = models.CharField(max_length=10, blank=True)  # H/M

    # Asistencias (Marcas, ej: "X", "/" o "1")
    asist_l = models.CharField(max_length=5, blank=True)
    asist_m1 = models.CharField(max_length=5, blank=True)
    asist_m2 = models.CharField(max_length=5, blank=True)
    asist_j = models.CharField(max_length=5, blank=True)
    asist_v = models.CharField(max_length=5, blank=True)

    concluyo = models.CharField(max_length=10, blank=True)  # SI/NO


# =======================================================
# 11. MODELO DE PROFESORES
# =======================================================
class Profesor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True)
    rfc = models.CharField(max_length=13, unique=True, verbose_name="RFC.")
    curp = models.CharField(max_length=18, blank=True, verbose_name="CURP")
    cct = models.CharField(max_length=20, blank=True, verbose_name="CCT")
    municipio = models.CharField(max_length=200, verbose_name="Municipio")
    #email = models.EmailField(verbose_name="Correo Electrónico")
    #telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")

    def __str__(self):
        return f"{self.apellido_paterno} {self.apellido_materno} {self.nombre}"

    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"
        ordering = ['apellido_paterno', 'apellido_materno']