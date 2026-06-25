from sqlmodel import Session, select

from ..db.dto import (
    AlumnoCarreraCreate,
    AlumnoCarreraRead,
    AlumnoCreate,
    AlumnoRead,
    AsignacionCreate,
    AsignacionRead,
    BloqueCreate,
    BloqueRead,
    CarreraCreate,
    CarreraRead,
    CursoCreate,
    CursoRead,
    InscripcionCreate,
    InscripcionRead,
    PruebaCreate,
    PruebaRead,
    SalaCreate,
    SalaRead,
    UsoSalaCreate,
    UsoSalaRead,
)
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
from ..utils.ids import require_id


def list_alumnos(session: Session) -> list[Alumno]:
    return list(session.exec(select(Alumno).order_by(Alumno.apellido, Alumno.nombre)).all())


def get_alumno(session: Session, rut: str) -> Alumno | None:
    return session.get(Alumno, rut)


def create_alumno(session: Session, data: AlumnoCreate) -> Alumno:
    alumno = Alumno.model_validate(data)
    session.add(alumno)
    session.commit()
    session.refresh(alumno)
    return alumno


def alumno_to_read(alumno: Alumno) -> AlumnoRead:
    return AlumnoRead.model_validate(alumno)


def list_carreras(session: Session) -> list[Carrera]:
    return list(session.exec(select(Carrera).order_by(Carrera.nombre)).all())


def get_carrera(session: Session, id_carrera: int) -> Carrera | None:
    return session.get(Carrera, id_carrera)


def create_carrera(session: Session, data: CarreraCreate) -> Carrera:
    carrera = Carrera.model_validate(data)
    session.add(carrera)
    session.commit()
    session.refresh(carrera)
    return carrera


def carrera_to_read(carrera: Carrera) -> CarreraRead:
    return CarreraRead(id_carrera=require_id(carrera.id_carrera, "Carrera"), nombre=carrera.nombre)


def list_alumno_carreras(session: Session) -> list[AlumnoCarrera]:
    return list(session.exec(select(AlumnoCarrera).order_by(AlumnoCarrera.rut_alumno)).all())


def get_alumno_carrera(session: Session, rut_alumno: str, id_carrera: int) -> AlumnoCarrera | None:
    return session.get(AlumnoCarrera, (rut_alumno, id_carrera))


def create_alumno_carrera(session: Session, data: AlumnoCarreraCreate) -> AlumnoCarrera:
    item = AlumnoCarrera.model_validate(data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def alumno_carrera_to_read(session: Session, item: AlumnoCarrera) -> AlumnoCarreraRead:
    alumno = get_required(session, Alumno, item.rut_alumno, "Alumno")
    carrera = get_required(session, Carrera, item.id_carrera, "Carrera")
    return AlumnoCarreraRead(
        rut_alumno=item.rut_alumno,
        id_carrera=item.id_carrera,
        alumno=alumno_to_read(alumno),
        carrera=carrera_to_read(carrera),
    )


def list_cursos(session: Session) -> list[Curso]:
    return list(session.exec(select(Curso).order_by(Curso.nombre, Curso.seccion)).all())


def get_curso(session: Session, id_curso: int) -> Curso | None:
    return session.get(Curso, id_curso)


def create_curso(session: Session, data: CursoCreate) -> Curso:
    curso = Curso.model_validate(data)
    session.add(curso)
    session.commit()
    session.refresh(curso)
    return curso


def curso_to_read(curso: Curso) -> CursoRead:
    return CursoRead(
        id_curso=require_id(curso.id_curso, "Curso"),
        seccion=curso.seccion,
        nombre=curso.nombre,
        cupo=curso.cupo,
        created_at=curso.created_at,
    )


def list_inscripciones(session: Session) -> list[Inscripcion]:
    return list(session.exec(select(Inscripcion).order_by(Inscripcion.rut_alumno)).all())


def get_inscripcion(session: Session, rut_alumno: str, id_curso: int) -> Inscripcion | None:
    return session.get(Inscripcion, (rut_alumno, id_curso))


def create_inscripcion(session: Session, data: InscripcionCreate) -> Inscripcion:
    inscripcion = Inscripcion.model_validate(data)
    session.add(inscripcion)
    session.commit()
    session.refresh(inscripcion)
    return inscripcion


def inscripcion_to_read(session: Session, item: Inscripcion) -> InscripcionRead:
    alumno = get_required(session, Alumno, item.rut_alumno, "Alumno")
    curso = get_required(session, Curso, item.id_curso, "Curso")
    return InscripcionRead(
        rut_alumno=item.rut_alumno,
        id_curso=item.id_curso,
        fecha_inscripcion=item.fecha_inscripcion,
        alumno=alumno_to_read(alumno),
        curso=curso_to_read(curso),
    )


def list_bloques(session: Session) -> list[Bloque]:
    return list(session.exec(select(Bloque).order_by(Bloque.n_bloque)).all())


def get_bloque(session: Session, n_bloque: int) -> Bloque | None:
    return session.get(Bloque, n_bloque)


def create_bloque(session: Session, data: BloqueCreate) -> Bloque:
    bloque = Bloque.model_validate(data)
    session.add(bloque)
    session.commit()
    session.refresh(bloque)
    return bloque


def bloque_to_read(bloque: Bloque) -> BloqueRead:
    return BloqueRead.model_validate(bloque)


def list_pruebas(session: Session) -> list[Prueba]:
    return list(session.exec(select(Prueba).order_by(Prueba.nombre)).all())


def get_prueba(session: Session, id_evaluacion: int) -> Prueba | None:
    return session.get(Prueba, id_evaluacion)


def create_prueba(session: Session, data: PruebaCreate) -> Prueba:
    prueba = Prueba.model_validate(data)
    session.add(prueba)
    session.commit()
    session.refresh(prueba)
    return prueba


def prueba_to_read(session: Session, prueba: Prueba) -> PruebaRead:
    curso = get_required(session, Curso, prueba.id_curso, "Curso")
    return PruebaRead(
        id_evaluacion=require_id(prueba.id_evaluacion, "Prueba"),
        id_curso=prueba.id_curso,
        nombre=prueba.nombre,
        tipo=prueba.tipo,
        anio_creacion=prueba.anio_creacion,
        curso=curso_to_read(curso),
    )


def list_salas(session: Session) -> list[Sala]:
    return list(session.exec(select(Sala).order_by(Sala.edificio, Sala.n_sala)).all())


def get_sala(session: Session, id_sala: str) -> Sala | None:
    return session.get(Sala, id_sala)


def create_sala(session: Session, data: SalaCreate) -> Sala:
    sala = Sala.model_validate(data)
    session.add(sala)
    session.commit()
    session.refresh(sala)
    return sala


def sala_to_read(sala: Sala) -> SalaRead:
    return SalaRead.model_validate(sala)


def list_uso_sala(session: Session) -> list[UsoSala]:
    return list(session.exec(select(UsoSala).order_by(UsoSala.n_bloque, UsoSala.id_sala)).all())


def get_uso_sala(
    session: Session,
    id_evaluacion: int,
    id_sala: str,
    n_bloque: int,
) -> UsoSala | None:
    return session.get(UsoSala, (id_evaluacion, id_sala, n_bloque))


def create_uso_sala(session: Session, data: UsoSalaCreate) -> UsoSala:
    uso = UsoSala.model_validate(data)
    session.add(uso)
    session.commit()
    session.refresh(uso)
    return uso


def uso_sala_to_read(session: Session, uso: UsoSala) -> UsoSalaRead:
    prueba = get_required(session, Prueba, uso.id_evaluacion, "Prueba")
    sala = get_required(session, Sala, uso.id_sala, "Sala")
    bloque = get_required(session, Bloque, uso.n_bloque, "Bloque")
    return UsoSalaRead(
        id_evaluacion=uso.id_evaluacion,
        id_sala=uso.id_sala,
        n_bloque=uso.n_bloque,
        created_at=uso.created_at,
        prueba=prueba_to_read(session, prueba),
        sala=sala_to_read(sala),
        bloque=bloque_to_read(bloque),
    )


def list_asignaciones(session: Session) -> list[Asignacion]:
    return list(session.exec(select(Asignacion).order_by(Asignacion.n_bloque, Asignacion.rut_alumno)).all())


def list_asignaciones_by_alumno(session: Session, rut_alumno: str) -> list[Asignacion]:
    statement = (
        select(Asignacion)
        .where(Asignacion.rut_alumno == rut_alumno)
        .order_by(Asignacion.n_bloque)
    )
    return list(session.exec(statement).all())


def get_asignacion(session: Session, rut_alumno: str, n_bloque: int) -> Asignacion | None:
    return session.get(Asignacion, (rut_alumno, n_bloque))


def create_asignacion(session: Session, data: AsignacionCreate) -> Asignacion:
    asignacion = Asignacion.model_validate(data)
    session.add(asignacion)
    session.commit()
    session.refresh(asignacion)
    return asignacion


def asignacion_to_read(session: Session, asignacion: Asignacion) -> AsignacionRead:
    alumno = get_required(session, Alumno, asignacion.rut_alumno, "Alumno")
    prueba = get_required(session, Prueba, asignacion.id_evaluacion, "Prueba")
    sala = get_required(session, Sala, asignacion.id_sala, "Sala")
    bloque = get_required(session, Bloque, asignacion.n_bloque, "Bloque")
    return AsignacionRead(
        rut_alumno=asignacion.rut_alumno,
        n_bloque=asignacion.n_bloque,
        id_evaluacion=asignacion.id_evaluacion,
        id_sala=asignacion.id_sala,
        created_at=asignacion.created_at,
        alumno=alumno_to_read(alumno),
        prueba=prueba_to_read(session, prueba),
        sala=sala_to_read(sala),
        bloque=bloque_to_read(bloque),
    )


def get_required(session: Session, model: type, key: object, label: str):
    item = session.get(model, key)
    if item is None:
        raise ValueError(f"{label} not found")
    return item
