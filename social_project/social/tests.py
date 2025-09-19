from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from .models import Instructor, Curso, Estudiante, Matricula, Leccion, ProgresoLeccion

class ElearningTest(TestCase):
    def setUp(self):
        # Instructores
        self.prof1 = Instructor.objects.create(
            nombre="Ana Torres", email="ana@uni.com",
            especialidad="Python", experiencia_anios=5
        )
        self.prof2 = Instructor.objects.create(
            nombre="Luis Ramírez", email="luis@uni.com",
            especialidad="Django", experiencia_anios=8
        )

        # Cursos
        self.curso_python = Curso.objects.create(
            titulo="Programación en Python",
            descripcion="Curso básico",
            duracion_horas=40,
            precio=150
        )
        self.curso_python.instructores.add(self.prof1)

        self.curso_django = Curso.objects.create(
            titulo="Desarrollo Web con Django",
            descripcion="Curso avanzado",
            duracion_horas=60,
            precio=200
        )
        self.curso_django.instructores.add(self.prof2)

        # Estudiantes
        self.juan = Estudiante.objects.create(nombre="Juan Pérez", email="juan@email.com")
        self.maria = Estudiante.objects.create(nombre="María García", email="maria@email.com")

        # Matrículas
        Matricula.objects.create(estudiante=self.juan, curso=self.curso_python, progreso=50, completado=False)
        Matricula.objects.create(estudiante=self.maria, curso=self.curso_python, progreso=100, completado=True, calificacion_final=90)
        Matricula.objects.create(estudiante=self.juan, curso=self.curso_django, progreso=100, completado=True, calificacion_final=95)

        # Lecciones
        self.l1 = Leccion.objects.create(curso=self.curso_python, titulo="Introducción", contenido="Bienvenida", orden=1, duracion_minutos=10)
        self.l2 = Leccion.objects.create(curso=self.curso_python, titulo="Variables", contenido="Explicación de variables", orden=2, duracion_minutos=20)

        # Progreso en lecciones
        ProgresoLeccion.objects.create(estudiante=self.juan, leccion=self.l1, completada=True)
        ProgresoLeccion.objects.create(estudiante=self.juan, leccion=self.l2, completada=False)

    def test_inscribir_estudiante(self):
        nuevo = Estudiante.objects.create(nombre="Carlos Ruiz", email="carlos@email.com")
        self.curso_python.inscribir_estudiante(nuevo)
        self.assertTrue(Matricula.objects.filter(estudiante=nuevo, curso=self.curso_python).exists())

    def test_calcular_progreso_curso(self):
        progreso = self.juan.calcular_progreso_curso(self.curso_python)
        self.assertEqual(progreso, 50)

    def test_estudiantes_activos(self):
        activos = self.curso_python.estudiantes_activos()
        self.assertEqual(activos.count(), 1)
        self.assertEqual(activos.first().nombre, "Juan Pérez")

    def test_instructor_contar_estudiantes(self):
        total = self.prof1.contar_estudiantes()
        self.assertEqual(total, 2)  # Juan y María en Python

    def test_marcar_leccion_completada(self):
        self.l2.marcar_completada(self.juan)
        progreso = ProgresoLeccion.objects.get(estudiante=self.juan, leccion=self.l2)
        self.assertTrue(progreso.completada)

