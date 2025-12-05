from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name="Inicio"),
    path('login/', views.login_view, name="Login"),
    path('logout/', views.logout_view, name="Logout"),
    path('menu/', views.menu, name="Menu"),
    path('menu_admin/', views.menu_admin, name="Menu_Admin"),
    path('menu_instructor/', views.menu_instructor, name="Menu_Instructor"),
    path('programa/', views.programa, name="Programa"),
    path('inscripcion/', views.inscripcion, name="Inscripcion"),
    path('ficha/', views.ficha, name="Ficha"),
    path('diagnostico/', views.diagnostico, name="Diagnostico"),
    path('cv/', views.cv, name="CV"),
    path('criterios/', views.criterios, name="Criterios"),
    path('mis_listas/', views.mis_listas_asistencia, name="mis_listas"),
    path('asistencia/', views.asistencia, name="Asistencia"), # Crear nueva
    path('asistencia/<int:pk>/', views.asistencia, name="editar_asistencia"),
    path('encuesta/', views.encuesta, name="Encuesta"),
    path('registro/', views.registro, name="Registro"),
    path('cursos/', views.cursos, name="gestion_cursos"),
    path('cursos/crear/', views.crear_curso, name='crear_curso'),
    path('cursos/editar/', views.editar_curso, name='editar_curso'),
    path('cursos/eliminar/', views.eliminar_curso, name='eliminar_curso'),
    path('estadisticas/', views.estadisticas, name='Estadisticas'),
    path('pdf/<str:tipo>/<int:pk>/', views.descargar_pdf_generico, name="descargar_pdf"),
    path('api/buscar-curso/', views.api_buscar_curso, name='api_buscar_curso'),
    path('api/buscar-profesor/', views.api_buscar_profesor, name='api_buscar_profesor'),
]