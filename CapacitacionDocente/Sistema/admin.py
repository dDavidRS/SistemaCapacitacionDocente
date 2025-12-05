from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Curso, Inscripcion, FichaTecnica, CriteriosSeleccion, EncuestaSatisfaccion,
    RegistroGeneral, RegistroFila,
    ProgramaInstitucional, ProgramaDetalle,
    DiagnosticoNecesidades, DiagnosticoAsignatura, DiagnosticoActividad,
    CurriculumVitae, CVExperienciaLaboral, CVExperienciaDocente,
    CVProductoAcademico, CVParticipacionInstructor,
    ListaAsistencia, AsistenciaParticipante, Profesor
)

# =======================================================
# CONFIGURACIÓN GENERAL DEL SITIO
# =======================================================
admin.site.site_header = 'Panel de Control TecNM'
admin.site.site_title = 'Administración'
admin.site.index_title = 'Gestión del Sistema'


# =======================================================
# HELPER: BOTÓN PDF
# =======================================================
def crear_boton_pdf(obj, tipo):
    if obj.pk:
        url = reverse('descargar_pdf', kwargs={'tipo': tipo, 'pk': obj.pk})
        return format_html(
            '<a href="{}" target="_blank" class="button" style="background-color:#1b396a; color:white; padding:5px 10px; border-radius:15px; font-weight:bold;">'
            '<i class="fas fa-file-pdf"></i> PDF</a>', url
        )
    return "-"


# =======================================================
# 1. CURSOS
# =======================================================
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'clave', 'instructor', 'periodo', 'estado_coloreado')
    list_filter = ('estado', 'periodo')
    search_fields = ('nombre', 'clave', 'instructor')
    list_per_page = 15

    def estado_coloreado(self, obj):
        color = 'green' if obj.estado == 'disponible' else 'orange' if obj.estado == 'pausa' else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_estado_display())

    estado_coloreado.short_description = 'Estado'


# =======================================================
# 2. INSCRIPCIÓN
# =======================================================
@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'nombre_curso', 'email', 'periodo', 'ver_pdf')
    list_filter = ('periodo', 'genero', 'grado_estudios')
    search_fields = ('nombre_completo', 'curp', 'rfc', 'email')

    def ver_pdf(self, obj): return crear_boton_pdf(obj, 'inscripcion')

    ver_pdf.short_description = 'Formato'


# =======================================================
# 3. FICHA TÉCNICA
# =======================================================
@admin.register(FichaTecnica)
class FichaTecnicaAdmin(admin.ModelAdmin):
    list_display = ('nombre_curso', 'instructor', 'desc_duracion', 'ver_pdf')
    search_fields = ('nombre_curso', 'instructor')

    def ver_pdf(self, obj): return crear_boton_pdf(obj, 'ficha')

    ver_pdf.short_description = 'Formato'


# =======================================================
# 4. CRITERIOS DE SELECCIÓN
# =======================================================
@admin.register(CriteriosSeleccion)
class CriteriosAdmin(admin.ModelAdmin):
    list_display = ('nombre_instructor', 'nombre_curso', 'total_puntaje', 'aceptado_icon', 'ver_pdf')
    list_filter = ('aceptado', 'empresa')
    search_fields = ('nombre_instructor', 'nombre_curso')

    def aceptado_icon(self, obj):
        return True if obj.aceptado == 'si' else False

    aceptado_icon.boolean = True  # Esto pone un ícono de ✔ o ✘
    aceptado_icon.short_description = 'Aceptado'

    def ver_pdf(self, obj): return crear_boton_pdf(obj, 'criterios')

    ver_pdf.short_description = 'Formato'


# =======================================================
# 5. ENCUESTA DE SATISFACCIÓN
# =======================================================
@admin.register(EncuestaSatisfaccion)
class EncuestaAdmin(admin.ModelAdmin):
    list_display = ('nombre_curso', 'facilitador', 'periodo', 'fecha', 'ver_pdf')
    list_filter = ('periodo', 'facilitador')
    search_fields = ('nombre_curso', 'facilitador')

    def ver_pdf(self, obj): return crear_boton_pdf(obj, 'encuesta')

    ver_pdf.short_description = 'Formato'


# =======================================================
# 6. PROGRAMA INSTITUCIONAL (Con Tabla Hija)
# =======================================================
class ProgramaDetalleInline(admin.TabularInline):
    model = ProgramaDetalle
    extra = 0
    min_num = 0
    fields = ('no_consecutivo', 'nombre_curso', 'instructor', 'periodo_realizacion', 'lugar', 'horas')
    can_delete = True


@admin.register(ProgramaInstitucional)
class ProgramaInstitucionalAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'elaboro_nombre', 'fecha_creacion', 'ver_pdf')
    list_filter = ('periodo',)
    inlines = [ProgramaDetalleInline]

    def ver_pdf(self, obj): return crear_boton_pdf(obj, 'programa')

    ver_pdf.short_description = 'Formato'


# =======================================================
# 7. DIAGNÓSTICO DE NECESIDADES (Con Tablas Hijas)
# =======================================================
class DiagnosticoAsignaturaInline(admin.TabularInline):
    model = DiagnosticoAsignatura
    extra = 0
    verbose_name = "Asignatura (Tablas A y B)"
    fields = ('tipo_tabla', 'asignatura', 'num_profesores', 'instructor_propuesto')


class DiagnosticoActividadInline(admin.TabularInline):
    model = DiagnosticoActividad
    extra = 0
    verbose_name = "Actividad (Tablas C y D)"
    fields = ('tipo_tabla', 'actividad', 'fecha_evento')


@admin.register(DiagnosticoNecesidades)
class DiagnosticoNecesidadesAdmin(admin.ModelAdmin):
    list_display = ('departamento_academico', 'fecha_realizacion', 'jefe_nombre', 'ver_pdf')
    search_fields = ('departamento_academico', 'jefe_nombre')
    inlines = [DiagnosticoAsignaturaInline, DiagnosticoActividadInline]

    def ver_pdf(self, obj): return crear_boton_pdf(obj, 'diagnostico')

    ver_pdf.short_description = 'Formato'


# =======================================================
# 8. CURRICULUM VITAE (Con Tablas Hijas)
# =======================================================
class CVLaboralInline(admin.StackedInline):
    model = CVExperienciaLaboral
    extra = 0
    classes = ['collapse']


class CVDocenteInline(admin.TabularInline):
    model = CVExperienciaDocente
    extra = 0


class CVProductoInline(admin.TabularInline):
    model = CVProductoAcademico
    extra = 0


class CVInstructorInline(admin.TabularInline):
    model = CVParticipacionInstructor
    extra = 0


@admin.register(CurriculumVitae)
class CVAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'telefono', 'ver_pdf')
    search_fields = ('nombre', 'rfc', 'curp')
    inlines = [CVLaboralInline, CVDocenteInline, CVProductoInline, CVInstructorInline]

    def ver_pdf(self, obj): return crear_boton_pdf(obj, 'cv')

    ver_pdf.short_description = 'Formato'


# =======================================================
# 9. LISTA DE ASISTENCIA (Con Tabla Hija)
# =======================================================
class AsistenciaParticipanteInline(admin.TabularInline):
    model = AsistenciaParticipante
    extra = 0
    fields = ('no_consecutivo', 'nombre', 'rfc', 'asist_l', 'asist_m1', 'asist_m2', 'asist_j', 'asist_v', 'concluyo')


@admin.register(ListaAsistencia)
class ListaAsistenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre_curso', 'instructor', 'folio', 'periodo', 'ver_pdf')
    list_filter = ('periodo', 'instructor')
    search_fields = ('nombre_curso', 'folio')
    inlines = [AsistenciaParticipanteInline]

    def ver_pdf(self, obj): return crear_boton_pdf(obj, 'asistencia')

    ver_pdf.short_description = 'Formato'


# =======================================================
# 10. REGISTRO GENERAL
# =======================================================
class RegistroFilaInline(admin.TabularInline):
    model = RegistroFila
    extra = 0
    fields = ('no_consecutivo', 'nombre_curso', 'instructor', 'docentes_inscritos', 'docentes_acreditados')


@admin.register(RegistroGeneral)
class RegistroGeneralAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'fecha_creacion', 'jefe_desarrollo', 'ver_pdf')
    inlines = [RegistroFilaInline]

    def ver_pdf(self, obj): return crear_boton_pdf(obj, 'registro')

    ver_pdf.short_description = 'Formato'

# =======================================================
# 11. GESTIÓN DE PROFESORES
# =======================================================
@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    # Columnas que se verán en la lista
    list_display = ('rfc', 'nombre_completo', 'municipio', 'cct')

    # Filtros laterales
    list_filter = ('municipio',)

    # Barra de búsqueda (puedes buscar por nombre o RFC)
    search_fields = ('nombre', 'apellido_paterno', 'apellido_materno', 'rfc', 'municipio')

    # Paginación
    list_per_page = 20

    # Función auxiliar para mostrar el nombre completo en una columna
    def nombre_completo(self, obj):
        return f"{obj.apellido_paterno} {obj.apellido_materno} {obj.nombre}"

    # Permitir ordenar por la columna calculada
    nombre_completo.admin_order_field = 'apellido_paterno'