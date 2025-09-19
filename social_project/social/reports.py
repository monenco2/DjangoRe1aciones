from social import reports
from .models import Instructor, Curso, Estudiante, Matricula, Leccion, ProgresoLeccion
from django.db.models import Count, Avg


def instructor_con_mas_estudiantes():
    return (
        Instructor.objects
        .annotate(num_estudiantes=Count("curso__matricula__estudiante", distinct=True))
        .order_by("-num_estudiantes")
        .first()
    )


def cursos_con_tasa_finalizacion(min_porcentaje=80):
    cursos = []
    for curso in Curso.objects.all():
        total = curso.matricula_set.count()
        completados = curso.matricula_set.filter(completado=True).count()
        if total > 0 and (completados / total) * 100 >= min_porcentaje:
            cursos.append(curso)
    return cursos

def estudiantes_con_tres_cursos_completos():
    return (
        Estudiante.objects
        .annotate(completos=Count("matricula", filter=Q(matricula__completado=True)))
        .filter(completos__gte=3)
    )



def tiempo_promedio_para_completar():
    return (
        Matricula.objects
        .filter(completado=True)
        .aggregate(promedio=Avg("curso__duracion_horas"))
    )["promedio"]


def lecciones_mas_dificiles():
    lecciones = []
    for leccion in Leccion.objects.all():
        total = leccion.progresoleccion_set.count()
        completadas = leccion.progresoleccion_set.filter(completada=True).count()
        if total > 0 and completadas / total < 0.5:  
            lecciones.append(leccion)
    return lecciones
