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
        Carrera(nombre="Derecho"),
        Carrera(nombre="Diseno"),
    ]
    alumnos = [
        Alumno(rut="11111111-1", nombre="Martina", apellido="Perez", email="martina.perez@alumnos.uai.cl"),
        Alumno(rut="22222222-2", nombre="Diego", apellido="Soto", email="diego.soto@alumnos.uai.cl"),
        Alumno(rut="33333333-3", nombre="Isidora", apellido="Rojas", email="isidora.rojas@alumnos.uai.cl"),
        Alumno(rut="44444444-4", nombre="Tomas", apellido="Fuentes", email="tomas.fuentes@alumnos.uai.cl"),
        Alumno(rut="55555555-5", nombre="Antonia", apellido="Morales", email="antonia.morales@alumnos.uai.cl"),
        Alumno(rut="66666666-6", nombre="Benjamin", apellido="Castro", email="benjamin.castro@alumnos.uai.cl"),
        Alumno(rut="77777777-7", nombre="Josefa", apellido="Herrera", email="josefa.herrera@alumnos.uai.cl"),
        Alumno(rut="88888888-8", nombre="Vicente", apellido="Munoz", email="vicente.munoz@alumnos.uai.cl"),
        Alumno(rut="99999999-9", nombre="Florencia", apellido="Navarro", email="florencia.navarro@alumnos.uai.cl"),
        Alumno(rut="10101010-0", nombre="Agustin", apellido="Silva", email="agustin.silva@alumnos.uai.cl"),
        Alumno(rut="12121212-2", nombre="Emilia", apellido="Vargas", email="emilia.vargas@alumnos.uai.cl"),
        Alumno(rut="13131313-3", nombre="Lucas", apellido="Reyes", email="lucas.reyes@alumnos.uai.cl"),
    ]
    cursos = [
        Curso(nombre="Calculo I", seccion="A", cupo=45),
        Curso(nombre="Base de Datos", seccion="B", cupo=35),
        Curso(nombre="Estadistica Aplicada", seccion="C", cupo=40),
        Curso(nombre="Programacion", seccion="A", cupo=32),
        Curso(nombre="Macroeconomia", seccion="B", cupo=38),
        Curso(nombre="Derecho Civil", seccion="A", cupo=30),
        Curso(nombre="Diseno de Interfaces", seccion="C", cupo=28),
    ]
    bloques = [
        Bloque(n_bloque=1, fecha=date(2026, 6, 2), dia="Martes", hora_inicio=time(18, 0), hora_fin=time(20, 0)),
        Bloque(n_bloque=2, fecha=date(2026, 6, 4), dia="Jueves", hora_inicio=time(18, 0), hora_fin=time(20, 0)),
        Bloque(n_bloque=3, fecha=date(2026, 6, 6), dia="Sabado", hora_inicio=time(9, 0), hora_fin=time(11, 0)),
        Bloque(n_bloque=4, fecha=date(2026, 6, 6), dia="Sabado", hora_inicio=time(11, 0), hora_fin=time(13, 0)),
    ]
    salas = [
        Sala(id_sala="A-101", n_sala=101, edificio="A", cupo=35),
        Sala(id_sala="A-205", n_sala=205, edificio="A", cupo=32),
        Sala(id_sala="D-101", n_sala=101, edificio="D", cupo=30),
        Sala(id_sala="D-204", n_sala=204, edificio="D", cupo=28),
        Sala(id_sala="E-110", n_sala=110, edificio="E", cupo=34),
        Sala(id_sala="E-302", n_sala=302, edificio="E", cupo=26),
        Sala(id_sala="F-201", n_sala=201, edificio="F", cupo=36),
        Sala(id_sala="F-404", n_sala=404, edificio="F", cupo=24),
    ]

    session.add_all([*carreras, *alumnos, *cursos, *bloques, *salas])
    session.commit()

    for item in [*carreras, *cursos]:
        session.refresh(item)

    carrera_comercial = require_id(carreras[0].id_carrera, "Carrera")
    carrera_informatica = require_id(carreras[1].id_carrera, "Carrera")
    carrera_psicologia = require_id(carreras[2].id_carrera, "Carrera")
    carrera_derecho = require_id(carreras[3].id_carrera, "Carrera")
    carrera_diseno = require_id(carreras[4].id_carrera, "Carrera")
    calculo = require_id(cursos[0].id_curso, "Curso")
    bases = require_id(cursos[1].id_curso, "Curso")
    estadistica = require_id(cursos[2].id_curso, "Curso")
    programacion = require_id(cursos[3].id_curso, "Curso")
    macroeconomia = require_id(cursos[4].id_curso, "Curso")
    derecho_civil = require_id(cursos[5].id_curso, "Curso")
    diseno_interfaces = require_id(cursos[6].id_curso, "Curso")

    alumno_carreras = [
        AlumnoCarrera(rut_alumno="11111111-1", id_carrera=carrera_informatica),
        AlumnoCarrera(rut_alumno="22222222-2", id_carrera=carrera_comercial),
        AlumnoCarrera(rut_alumno="33333333-3", id_carrera=carrera_psicologia),
        AlumnoCarrera(rut_alumno="44444444-4", id_carrera=carrera_informatica),
        AlumnoCarrera(rut_alumno="55555555-5", id_carrera=carrera_comercial),
        AlumnoCarrera(rut_alumno="66666666-6", id_carrera=carrera_informatica),
        AlumnoCarrera(rut_alumno="77777777-7", id_carrera=carrera_derecho),
        AlumnoCarrera(rut_alumno="88888888-8", id_carrera=carrera_diseno),
        AlumnoCarrera(rut_alumno="99999999-9", id_carrera=carrera_psicologia),
        AlumnoCarrera(rut_alumno="10101010-0", id_carrera=carrera_informatica),
        AlumnoCarrera(rut_alumno="12121212-2", id_carrera=carrera_derecho),
        AlumnoCarrera(rut_alumno="13131313-3", id_carrera=carrera_diseno),
    ]
    inscripciones = [
        Inscripcion(rut_alumno="11111111-1", id_curso=bases, fecha_inscripcion=date(2026, 3, 10)),
        Inscripcion(rut_alumno="22222222-2", id_curso=calculo, fecha_inscripcion=date(2026, 3, 11)),
        Inscripcion(rut_alumno="33333333-3", id_curso=estadistica, fecha_inscripcion=date(2026, 3, 12)),
        Inscripcion(rut_alumno="44444444-4", id_curso=bases, fecha_inscripcion=date(2026, 3, 13)),
        Inscripcion(rut_alumno="55555555-5", id_curso=macroeconomia, fecha_inscripcion=date(2026, 3, 14)),
        Inscripcion(rut_alumno="55555555-5", id_curso=estadistica, fecha_inscripcion=date(2026, 3, 14)),
        Inscripcion(rut_alumno="66666666-6", id_curso=programacion, fecha_inscripcion=date(2026, 3, 15)),
        Inscripcion(rut_alumno="66666666-6", id_curso=bases, fecha_inscripcion=date(2026, 3, 15)),
        Inscripcion(rut_alumno="77777777-7", id_curso=derecho_civil, fecha_inscripcion=date(2026, 3, 16)),
        Inscripcion(rut_alumno="88888888-8", id_curso=diseno_interfaces, fecha_inscripcion=date(2026, 3, 17)),
        Inscripcion(rut_alumno="99999999-9", id_curso=estadistica, fecha_inscripcion=date(2026, 3, 18)),
        Inscripcion(rut_alumno="10101010-0", id_curso=programacion, fecha_inscripcion=date(2026, 3, 19)),
        Inscripcion(rut_alumno="12121212-2", id_curso=derecho_civil, fecha_inscripcion=date(2026, 3, 20)),
        Inscripcion(rut_alumno="13131313-3", id_curso=diseno_interfaces, fecha_inscripcion=date(2026, 3, 21)),
    ]
    pruebas = [
        Prueba(id_curso=bases, nombre="Prueba SQL", anio_creacion=2026),
        Prueba(id_curso=bases, nombre="Prueba Modelamiento", anio_creacion=2026),
        Prueba(id_curso=calculo, nombre="Prueba Derivadas", anio_creacion=2026),
        Prueba(id_curso=calculo, nombre="Prueba Algebra", anio_creacion=2026),
        Prueba(id_curso=estadistica, nombre="Prueba Probabilidad", anio_creacion=2026),
        Prueba(id_curso=estadistica, nombre="Prueba Inferencia", anio_creacion=2026),
        Prueba(id_curso=programacion, nombre="Prueba Python", anio_creacion=2026),
        Prueba(id_curso=programacion, nombre="Prueba Estructuras de Datos", anio_creacion=2026),
        Prueba(id_curso=macroeconomia, nombre="Prueba Politica Monetaria", anio_creacion=2026),
        Prueba(id_curso=derecho_civil, nombre="Prueba Obligaciones", anio_creacion=2026),
        Prueba(id_curso=diseno_interfaces, nombre="Prueba Prototipado", anio_creacion=2026),
    ]

    session.add_all([*alumno_carreras, *inscripciones, *pruebas])
    session.commit()

    for prueba in pruebas:
        session.refresh(prueba)

    sql = require_id(pruebas[0].id_evaluacion, "Prueba")
    modelamiento = require_id(pruebas[1].id_evaluacion, "Prueba")
    derivadas = require_id(pruebas[2].id_evaluacion, "Prueba")
    algebra = require_id(pruebas[3].id_evaluacion, "Prueba")
    probabilidad = require_id(pruebas[4].id_evaluacion, "Prueba")
    inferencia = require_id(pruebas[5].id_evaluacion, "Prueba")

    usos_sala = [
        UsoSala(id_evaluacion=sql, id_sala="A-101", n_bloque=1),
        UsoSala(id_evaluacion=modelamiento, id_sala="D-101", n_bloque=1),
        UsoSala(id_evaluacion=derivadas, id_sala="F-201", n_bloque=2),
        UsoSala(id_evaluacion=algebra, id_sala="A-101", n_bloque=2),
        UsoSala(id_evaluacion=probabilidad, id_sala="E-110", n_bloque=3),
        UsoSala(id_evaluacion=inferencia, id_sala="A-101", n_bloque=4),
    ]
    asignaciones = [
        Asignacion(rut_alumno="11111111-1", n_bloque=1, id_evaluacion=sql, id_sala="A-101"),
        Asignacion(rut_alumno="44444444-4", n_bloque=1, id_evaluacion=sql, id_sala="A-101"),
        Asignacion(rut_alumno="22222222-2", n_bloque=2, id_evaluacion=derivadas, id_sala="B-204"),
        Asignacion(rut_alumno="33333333-3", n_bloque=3, id_evaluacion=probabilidad, id_sala="C-310"),
    ]

    session.add_all([*usos_sala, *asignaciones])
    session.commit()
