from django.db import models

# Create your models here.

from django.db import models
from django.utils import timezone

class Instructor(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    especialidad = models.CharField(max_length=200, blank=True)
    experiencia_anios = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre

    def estudiantes_unicos_count(self):
        """
        Cuenta estudiantes únicos que han estado en cualquiera de los cursos de este instructor.
        """
        # Matriculas a través de cursos relacionados
        from django.db.models import Count
        return (
            Estudiante.objects.filter(
                matricula__curso__in=self.cursos.all()
            ).distinct().count()
        )

class Curso(models.Model):
    titulo = models.CharField(max_length=250)
    descripcion = models.TextField(blank=True)
    duracion_horas = models.PositiveIntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # relación many-to-many entre Curso e Instructor (sin through)
    instructores = models.ManyToManyField(
        Instructor, related_name='cursos', blank=True
    )

    def __str__(self):
        return self.titulo

    def inscribir_estudiante(self, estudiante, fecha_matricula=None):
        """
        Matricula (o crea) la matricula del estudiante en el curso.
        Retorna la instancia Matricula.
        """
        if fecha_matricula is None:
            fecha_matricula = timezone.now()
        matricula, created = Matricula.objects.get_or_create(
            estudiante=estudiante,
            curso=self,
            defaults={'fecha_matricula': fecha_matricula}
        )
        return matricula

    def estudiantes_activos(self):
        """
        Retorna queryset de Estudiantes con progreso > 0 y no completado en este curso.
        """
        return Estudiante.objects.filter(
            matricula__curso=self,
            matricula__progreso__gt=0,
            matricula__completado=False
        ).distinct()

    def tiempo_promedio_completado(self):
        """
        Calcula tiempo promedio (en días) entre fecha_matricula y fecha_completado
        para matriculas completadas. Retorna None si no hay completadas.
        """
        from django.db.models import Avg, F, ExpressionWrapper, DurationField
        from django.db.models.functions import Cast
        from django.utils import timezone
        # Usaremos diferencia en segundos convertida a días
        qs = Matricula.objects.filter(curso=self, completado=True, fecha_completado__isnull=False)
        if not qs.exists():
            return None
        # Promedio en segundos
        import datetime
        diffs = [
            (m.fecha_completado - m.fecha_matricula).total_seconds()
            for m in qs
            if m.fecha_completado and m.fecha_matricula
        ]
        if not diffs:
            return None
        avg_seconds = sum(diffs) / len(diffs)
        avg_days = avg_seconds / (3600 * 24)
        return avg_days

class Estudiante(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    fecha_registro = models.DateField(default=timezone.now)

    cursos = models.ManyToManyField(
        Curso,
        through='Matricula',
        related_name='estudiantes',
        blank=True
    )

    def __str__(self):
        return self.nombre

    def calcular_progreso_curso(self, curso):
        """
        Calcula el % de progreso en un curso, usando la Matricula.progreso si existe.
        Retorna None si no existe matricula.
        """
        try:
            m = Matricula.objects.get(estudiante=self, curso=curso)
            return m.progreso
        except Matricula.DoesNotExist:
            return None

    def cursos_completados_count(self):
        return Matricula.objects.filter(estudiante=self, completado=True).count()

class Matricula(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='matricula')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='matricula')
    fecha_matricula = models.DateTimeField(default=timezone.now)
    progreso = models.PositiveIntegerField(default=0)  # 0-100
    completado = models.BooleanField(default=False)
    calificacion_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('estudiante', 'curso')

    def __str__(self):
        return f"{self.estudiante} → {self.curso} ({self.progreso}%)"

class Leccion(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='lecciones')
    titulo = models.CharField(max_length=250)
    contenido = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)
    duracion_minutos = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.curso.titulo} — {self.orden} — {self.titulo}"

    def marcar_completada(self, estudiante, fecha=None):
        """
        Marca la lección como completada para un estudiante (crea o actualiza ProgresoLeccion).
        """
        if fecha is None:
            fecha = timezone.now()
        pl, created = ProgresoLeccion.objects.get_or_create(
            estudiante=estudiante,
            leccion=self,
            defaults={'completada': True, 'fecha_completado': fecha}
        )
        if not created:
            pl.completada = True
            pl.fecha_completado = fecha
            pl.save()
        return pl

class ProgresoLeccion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='progresos_leccion')
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE, related_name='progresos')
    completada = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('estudiante', 'leccion')

    def __str__(self):
        return f"{self.estudiante} — {self.leccion} — {'OK' if self.completada else 'Pendiente'}"




