from datetime import date, datetime, time

from sqlmodel import Field, SQLModel


class AlumnoCreate(SQLModel):
    rut: str = Field(min_length=7, max_length=12)
    nombre: str = Field(min_length=2, max_length=80)
    apellido: str = Field(min_length=2, max_length=80)
    email: str | None = Field(default=None, max_length=160)


class AlumnoRead(AlumnoCreate):
    created_at: datetime


class CarreraCreate(SQLModel):
    nombre: str = Field(min_length=2, max_length=120)


class CarreraRead(CarreraCreate):
    id_carrera: int


class AlumnoCarreraCreate(SQLModel):
    rut_alumno: str
    id_carrera: int


class AlumnoCarreraRead(AlumnoCarreraCreate):
    alumno: AlumnoRead
    carrera: CarreraRead


class CursoCreate(SQLModel):
    seccion: str = Field(min_length=1, max_length=20)
    nombre: str = Field(min_length=2, max_length=120)
    cupo: int = Field(ge=1)


class CursoRead(CursoCreate):
    id_curso: int
    created_at: datetime


class InscripcionCreate(SQLModel):
    rut_alumno: str
    id_curso: int
    fecha_inscripcion: date | None = None


class InscripcionRead(InscripcionCreate):
    alumno: AlumnoRead
    curso: CursoRead


class BloqueCreate(SQLModel):
    n_bloque: int = Field(ge=1)
    fecha: date
    dia: str = Field(min_length=2, max_length=20)
    hora_inicio: time
    hora_fin: time


class BloqueRead(BloqueCreate):
    pass


class PruebaCreate(SQLModel):
    id_curso: int
    nombre: str = Field(min_length=2, max_length=140)
    tipo: str | None = Field(default=None, max_length=60)
    anio_creacion: int | None = Field(default=None, ge=2000, le=2100)


class PruebaRead(PruebaCreate):
    id_evaluacion: int
    curso: CursoRead


class SalaCreate(SQLModel):
    id_sala: str = Field(min_length=1, max_length=20)
    n_sala: int = Field(ge=1)
    edificio: str = Field(min_length=1, max_length=80)
    cupo: int = Field(ge=1)


class SalaRead(SalaCreate):
    pass


class UsoSalaCreate(SQLModel):
    id_evaluacion: int
    id_sala: str
    n_bloque: int


class UsoSalaRead(UsoSalaCreate):
    created_at: datetime
    prueba: PruebaRead
    sala: SalaRead
    bloque: BloqueRead


class AsignacionCreate(SQLModel):
    rut_alumno: str
    n_bloque: int
    id_evaluacion: int
    id_sala: str


class AsignacionRead(AsignacionCreate):
    created_at: datetime
    alumno: AlumnoRead
    prueba: PruebaRead
    sala: SalaRead
    bloque: BloqueRead
