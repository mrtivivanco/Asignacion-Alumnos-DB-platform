from datetime import date, datetime, time

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class Alumno(SQLModel, table=True):
    __tablename__ = "alumnos"

    rut: str = Field(primary_key=True, max_length=12)
    nombre: str = Field(nullable=False, max_length=80)
    apellido: str = Field(nullable=False, max_length=80)
    email: str | None = Field(default=None, max_length=160)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Carrera(SQLModel, table=True):
    __tablename__ = "carreras"

    id_carrera: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(nullable=False, unique=True, index=True, max_length=120)


class AlumnoCarrera(SQLModel, table=True):
    __tablename__ = "alumno_carreras"

    rut_alumno: str = Field(foreign_key="alumnos.rut", primary_key=True, max_length=12)
    id_carrera: int = Field(foreign_key="carreras.id_carrera", primary_key=True)


class Curso(SQLModel, table=True):
    __tablename__ = "cursos"
    __table_args__ = (UniqueConstraint("nombre", "seccion"),)

    id_curso: int | None = Field(default=None, primary_key=True)
    seccion: str = Field(nullable=False, max_length=20)
    nombre: str = Field(nullable=False, max_length=120)
    cupo: int = Field(nullable=False, ge=1)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Inscripcion(SQLModel, table=True):
    __tablename__ = "inscripciones"

    rut_alumno: str = Field(foreign_key="alumnos.rut", primary_key=True, max_length=12)
    id_curso: int = Field(foreign_key="cursos.id_curso", primary_key=True)
    fecha_inscripcion: date | None = None


class Bloque(SQLModel, table=True):
    __tablename__ = "bloques"
    __table_args__ = (UniqueConstraint("fecha", "hora_inicio", "hora_fin"),)

    n_bloque: int = Field(primary_key=True)
    fecha: date = Field(nullable=False)
    dia: str = Field(nullable=False, max_length=20)
    hora_inicio: time = Field(nullable=False)
    hora_fin: time = Field(nullable=False)


class Prueba(SQLModel, table=True):
    __tablename__ = "pruebas"
    __table_args__ = (UniqueConstraint("id_curso", "nombre", "anio_creacion"),)

    id_evaluacion: int | None = Field(default=None, primary_key=True)
    id_curso: int = Field(foreign_key="cursos.id_curso", nullable=False)
    nombre: str = Field(nullable=False, max_length=140)
    tipo: str | None = Field(default=None, max_length=60)
    anio_creacion: int | None = Field(default=None, ge=2000, le=2100)


class Sala(SQLModel, table=True):
    __tablename__ = "salas"

    id_sala: str = Field(primary_key=True, max_length=20)
    n_sala: int = Field(nullable=False)
    edificio: str = Field(nullable=False, max_length=80)
    cupo: int = Field(nullable=False, ge=1)


class UsoSala(SQLModel, table=True):
    __tablename__ = "uso_sala"
    __table_args__ = (
        UniqueConstraint("id_evaluacion", "id_sala", "n_bloque"),
        UniqueConstraint("id_sala", "n_bloque"),
    )

    id_evaluacion: int = Field(foreign_key="pruebas.id_evaluacion", primary_key=True)
    id_sala: str = Field(foreign_key="salas.id_sala", primary_key=True, max_length=20)
    n_bloque: int = Field(foreign_key="bloques.n_bloque", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Asignacion(SQLModel, table=True):
    __tablename__ = "asignaciones"
    __table_args__ = (
        UniqueConstraint("rut_alumno", "id_evaluacion"),
        Index("ix_asignaciones_id_sala_n_bloque", "id_sala", "n_bloque"),
    )

    rut_alumno: str = Field(foreign_key="alumnos.rut", primary_key=True, max_length=12)
    n_bloque: int = Field(foreign_key="bloques.n_bloque", primary_key=True)
    id_evaluacion: int = Field(foreign_key="pruebas.id_evaluacion", nullable=False)
    id_sala: str = Field(foreign_key="salas.id_sala", nullable=False, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
