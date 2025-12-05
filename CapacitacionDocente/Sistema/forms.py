from django import forms
from .models import (
    Curso, Inscripcion, FichaTecnica, CriteriosSeleccion, EncuestaSatisfaccion,
    ProgramaInstitucional, DiagnosticoNecesidades, CurriculumVitae, ListaAsistencia,
    RegistroGeneral, RegistroFila
)

# =======================================================
# 1. FORMULARIO DE CURSO (Para Crear/Editar Cursos)
# =======================================================
class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'clave', 'instructor', 'periodo', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'clave': forms.TextInput(attrs={'class': 'form-control'}),
            'instructor': forms.TextInput(attrs={'class': 'form-control'}),
            'periodo': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

# =======================================================
# 2. INSCRIPCIÓN
# =======================================================
class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = '__all__'
        # Opcional: Widgets para mapear tus clases CSS 'input-line', etc.
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'input-line short-input'}),
            'clave_curso': forms.TextInput(attrs={'class': 'input-line full-width'}),
            'email': forms.EmailInput(attrs={'class': 'input-line full-width'}),
            # Django intentará buscar 'nombre_completo' en el HTML.
            # Si tu HTML dice name="nombre", debes cambiarlo en el HTML a name="nombre_completo"
        }

# =======================================================
# 3. FICHA TÉCNICA
# =======================================================
class FichaTecnicaForm(forms.ModelForm):
    class Meta:
        model = FichaTecnica
        fields = '__all__'
        # (Opcional) Si quieres que los textareas se vean uniformes
        widgets = {
            'introduccion': forms.Textarea(attrs={'rows': 3, 'class': 'input-clean'}),
            'justificacion': forms.Textarea(attrs={'rows': 3, 'class': 'input-clean'}),
            'objetivo_general': forms.Textarea(attrs={'rows': 3, 'class': 'input-clean'}),
            'resultados': forms.Textarea(attrs={'rows': 3, 'class': 'input-clean'}),
            'fuentes_informacion': forms.Textarea(attrs={'rows': 3, 'class': 'input-clean'}),
        }

# =======================================================
# 4. CRITERIOS DE SELECCIÓN
# =======================================================
class CriteriosSeleccionForm(forms.ModelForm):
    # Forzamos que la fecha sea obligatoria
    fecha_evaluacion = forms.DateField(required=True)

    class Meta:
        model = CriteriosSeleccion
        fields = '__all__'

# =======================================================
# 5. ENCUESTA DE OPINIÓN
# =======================================================
class EncuestaSatisfaccionForm(forms.ModelForm):
    # Forzamos que la fecha sea obligatoria
    fecha = forms.DateField(required=True)

    class Meta:
        model = EncuestaSatisfaccion
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            # El campo de comentarios lo dejamos opcional (required=False es el default para TextFields con blank=True)
            'comentarios': forms.Textarea(attrs={'rows': 4}),
        }

# =======================================================
# 6. PROGRAMA INSTITUCIONAL (Solo Encabezado)
# =======================================================
class ProgramaInstitucionalForm(forms.ModelForm):
    # Forzamos que las fechas sean obligatorias
    elaboro_fecha = forms.DateField(required=True)
    aprobo_fecha = forms.DateField(required=True)

    class Meta:
        model = ProgramaInstitucional
        fields = ['periodo', 'elaboro_nombre', 'elaboro_fecha', 'aprobo_nombre', 'aprobo_fecha']
        widgets = {
            'elaboro_fecha': forms.DateInput(attrs={'type': 'date', 'class': 'input-line short-date'}),
            'aprobo_fecha': forms.DateInput(attrs={'type': 'date', 'class': 'input-line short-date'}),
        }

# =======================================================
# 7. DIAGNÓSTICO DE NECESIDADES (Solo Encabezado)
# =======================================================
class DiagnosticoNecesidadesForm(forms.ModelForm):
    fecha_realizacion = forms.DateField(required=True)
    fecha_concentrado = forms.DateField(required=True)

    class Meta:
        model = DiagnosticoNecesidades
        fields = [
            'departamento_academico', 'carrera', 'dept_origen', 'fecha_realizacion',
            'jefe_nombre', 'presidente_nombre', 'secretario_nombre',
            'fecha_concentrado', 'subdirector_nombre',
            # Nuevos campos
            'jefe1_nombre', 'jefe1_depto',
            'jefe2_nombre', 'jefe2_depto',
            'jefe3_nombre', 'jefe3_depto',
            'jefe4_nombre', 'jefe4_depto',
        ]
        widgets = {
            'fecha_realizacion': forms.DateInput(attrs={'type': 'date', 'class': 'input-line inline-input medium'}),
            'fecha_concentrado': forms.DateInput(attrs={'type': 'date'}),
        }

# =======================================================
# 8. CURRICULUM VITAE (Solo Datos Personales/Académicos)
# =======================================================
class CurriculumVitaeForm(forms.ModelForm):
    # Forzamos que la fecha de nacimiento sea obligatoria
    fecha_nacimiento = forms.DateField(required=True)

    class Meta:
        model = CurriculumVitae
        fields = '__all__'
        # Opcional: Si tienes widgets configurados, déjalos aquí.
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'input-line'}),
            'correo': forms.EmailInput(attrs={'class': 'input-line full-width'}),
        }

# =======================================================
# 9. LISTA DE ASISTENCIA (Solo Encabezado y Pie)
# =======================================================
class ListaAsistenciaForm(forms.ModelForm):
    # SOBRESCRIBIMOS los campos para hacerlos obligatorios (required=True)
    instructor_rfc = forms.CharField(required=True)
    instructor_curp = forms.CharField(required=True)
    coordinador_rfc = forms.CharField(required=True)
    coordinador_curp = forms.CharField(required=True)

    class Meta:
        model = ListaAsistencia
        fields = [
            'hoja_actual', 'hoja_total', 'instituto', 'clave_curso', 'folio',
            'nombre_curso', 'instructor', 'periodo', 'duracion', 'horario',
            'instructor_rfc', 'instructor_curp', 'coordinador_rfc', 'coordinador_curp'
        ]

# =======================================================
# 10. REGISTRO FORMACION
# =======================================================

class RegistroFilaForm(forms.ModelForm): # <--- CAMBIO DE NOMBRE
    # Forzamos fechas obligatorias
    fecha_inicio = forms.DateField(required=True)
    fecha_termino = forms.DateField(required=True)
    horas = forms.IntegerField(required=True)

    class Meta:
        model = RegistroFila # <--- CAMBIO DE MODELO
        # Excluimos lo que se llena automático o manual
        exclude = ['registro', 'no_consecutivo', 'es_formacion', 'es_actualizacion']