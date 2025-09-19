from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Instructor, Curso, Estudiante, Matricula

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'especialidad', 'experiencia_anios']
    search_fields = ['nombre', 'email', 'especialidad']

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'duracion_horas', 'precio', 'total_estudiantes']
    search_fields = ['titulo', 'descripcion']
    filter_horizontal = ['instructores']

    def total_estudiantes(self, obj):
        return obj.matricula.count()
    total_estudiantes.short_description = 'Matriculados'

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'fecha_registro', 'cursos_count']
    search_fields = ['nombre', 'email']
    # mostrar cursos en detalle - o usar raw_id_fields si muchos
    def cursos_count(self, obj):
        return obj.matricula.count()
    cursos_count.short_description = 'Cursos inscritos'

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'curso', 'progreso', 'completado', 'fecha_matricula']
    list_filter = ['completado']
    search_fields = ['estudiante__nombre', 'curso__titulo']

