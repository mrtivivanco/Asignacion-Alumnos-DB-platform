from datetime import date, time

from sqlmodel import Session, select

from ..db.schema import (
    Alumno,
    AlumnoCarrera,
    Asignacion,
    Bloque,
    Carrera,
    Curso,
    Inscripcion,
    Prueba,
    Sala,
    UsoSala,
)
from .ids import require_id


def seed_demo_data(session: Session) -> None:
    """Insert deterministic academic demo data once so repeated starts are safe."""
    existing_assignment = session.exec(select(Asignacion)).first()
    if existing_assignment is not None:
        return

    carreras = [
        Carrera(nombre="Ingenieria Comercial"),
        Carrera(nombre="Ingenieria Civil Informatica"),
        Carrera(nombre="Psicologia"),
    ]
    alumnos = [
        Alumno(rut="11111111-1", nombre="Martina", apellido="Perez", email="martina.perez@uai.cl"),
        Alumno(rut="22222222-2", nombre="Diego", apellido="Soto", email="diego.soto@uai.cl"),
        Alumno(rut="33333333-3", nombre="Isidora", apellido="Rojas", email="isidora.rojas@uai.cl"),
        Alumno(rut="44444444-4", nombre="Tomas", apellido="Fuentes", email="tomas.fuentes@uai.cl"),
    ]
    cursos = [
        Curso(nombre="Calculo I", seccion="A", cupo=45),
        Curso(nombre="Base de Datos", seccion="B", cupo=35),
        Curso(nombre="Estadistica Aplicada", seccion="C", cupo=40),
    ]
    bloques = [
        Bloque(n_bloque=1, fecha=date(2026, 6, 2), dia="Martes", hora_inicio=time(18, 0), hora_fin=time(20, 0)),
        Bloque(n_bloque=2, fecha=date(2026, 6, 4), dia="Jueves", hora_inicio=time(18, 0), hora_fin=time(20, 0)),
        Bloque(n_bloque=3, fecha=date(2026, 6, 6), dia="Sabado", hora_inicio=time(9, 0), hora_fin=time(11, 0)),
        Bloque(n_bloque=4, fecha=date(2026, 6, 6), dia="Sabado", hora_inicio=time(11, 0), hora_fin=time(13, 0)),
    ]
    salas = [
        Sala(id_sala="A-101", n_sala=101, edificio="Edificio A", cupo=35),
        Sala(id_sala="B-204", n_sala=204, edificio="Edificio B", cupo=30),
        Sala(id_sala="C-310", n_sala=310, edificio="Edificio C", cupo=28),
    ]

    session.add_all([*carreras, *alumnos, *cursos, *bloques, *salas])
    session.commit()

    for item in [*carreras, *cursos]:
        session.refresh(item)

    carrera_comercial = require_id(carreras[0].id_carrera, "Carrera")
    carrera_informatica = require_id(carreras[1].id_carrera, "Carrera")
    carrera_psicologia = require_id(carreras[2].id_carrera, "Carrera")
    calculo = require_id(cursos[0].id_curso, "Curso")
    bases = require_id(cursos[1].id_curso, "Curso")
    estadistica = require_id(cursos[2].id_curso, "Curso")

    alumno_carreras = [
        AlumnoCarrera(rut_alumno="11111111-1", id_carrera=carrera_informatica),
        AlumnoCarrera(rut_alumno="22222222-2", id_carrera=carrera_comercial),
        AlumnoCarrera(rut_alumno="33333333-3", id_carrera=carrera_psicologia),
        AlumnoCarrera(rut_alumno="44444444-4", id_carrera=carrera_informatica),
    ]
    inscripciones = [
        Inscripcion(rut_alumno="11111111-1", id_curso=bases, fecha_inscripcion=date(2026, 3, 10)),
        Inscripcion(rut_alumno="22222222-2", id_curso=calculo, fecha_inscripcion=date(2026, 3, 11)),
        Inscripcion(rut_alumno="33333333-3", id_curso=estadistica, fecha_inscripcion=date(2026, 3, 12)),
        Inscripcion(rut_alumno="44444444-4", id_curso=bases, fecha_inscripcion=date(2026, 3, 13)),
    ]
    pruebas = [
        Prueba(id_curso=bases, nombre="Prueba Extraordinaria SQL", tipo="Extraordinaria", anio_creacion=2026),
        Prueba(id_curso=calculo, nombre="Prueba Extraordinaria Derivadas", tipo="Extraordinaria", anio_creacion=2026),
        Prueba(id_curso=estadistica, nombre="Prueba Extraordinaria Probabilidad", tipo="Extraordinaria", anio_creacion=2026),
    ]

    session.add_all([*alumno_carreras, *inscripciones, *pruebas])
    session.commit()

    for prueba in pruebas:
        session.refresh(prueba)

    sql = require_id(pruebas[0].id_evaluacion, "Prueba")
    derivadas = require_id(pruebas[1].id_evaluacion, "Prueba")
    probabilidad = require_id(pruebas[2].id_evaluacion, "Prueba")

    usos_sala = [
        UsoSala(id_evaluacion=sql, id_sala="A-101", n_bloque=1),
        UsoSala(id_evaluacion=derivadas, id_sala="B-204", n_bloque=2),
        UsoSala(id_evaluacion=probabilidad, id_sala="C-310", n_bloque=3),
    ]
    asignaciones = [
        Asignacion(rut_alumno="11111111-1", n_bloque=1, id_evaluacion=sql, id_sala="A-101"),
        Asignacion(rut_alumno="44444444-4", n_bloque=1, id_evaluacion=sql, id_sala="A-101"),
        Asignacion(rut_alumno="22222222-2", n_bloque=2, id_evaluacion=derivadas, id_sala="B-204"),
        Asignacion(rut_alumno="33333333-3", n_bloque=3, id_evaluacion=probabilidad, id_sala="C-310"),
    ]

    session.add_all([*usos_sala, *asignaciones])
    session.commit()
