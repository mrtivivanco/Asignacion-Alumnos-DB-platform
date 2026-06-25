from collections.abc import Callable

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from ..crud import academic as crud
from ..db.config import SessionDep
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
from ..db.schema import Alumno, Bloque, Carrera, Curso, Prueba, Sala


router = APIRouter(prefix="/api", tags=["academic"])


def conflict_safe(session: SessionDep, action: Callable[[], object]):
    try:
        return action()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Record violates a unique or primary key constraint") from exc


def require_exists(session: SessionDep, model: type, key: object, label: str):
    item = session.get(model, key)
    if item is None:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return item


@router.get("/alumnos", response_model=list[AlumnoRead])
def list_alumnos(session: SessionDep):
    return [crud.alumno_to_read(alumno) for alumno in crud.list_alumnos(session)]


@router.post("/alumnos", response_model=AlumnoRead, status_code=status.HTTP_201_CREATED)
def create_alumno(alumno_data: AlumnoCreate, session: SessionDep):
    if crud.get_alumno(session, alumno_data.rut) is not None:
        raise HTTPException(status_code=409, detail="Alumno already exists")
    alumno = conflict_safe(session, lambda: crud.create_alumno(session, alumno_data))
    return crud.alumno_to_read(alumno)


@router.get("/carreras", response_model=list[CarreraRead])
def list_carreras(session: SessionDep):
    return [crud.carrera_to_read(carrera) for carrera in crud.list_carreras(session)]


@router.post("/carreras", response_model=CarreraRead, status_code=status.HTTP_201_CREATED)
def create_carrera(carrera_data: CarreraCreate, session: SessionDep):
    carrera = conflict_safe(session, lambda: crud.create_carrera(session, carrera_data))
    return crud.carrera_to_read(carrera)


@router.get("/alumno-carreras", response_model=list[AlumnoCarreraRead])
def list_alumno_carreras(session: SessionDep):
    return [crud.alumno_carrera_to_read(session, item) for item in crud.list_alumno_carreras(session)]


@router.post("/alumno-carreras", response_model=AlumnoCarreraRead, status_code=status.HTTP_201_CREATED)
def create_alumno_carrera(data: AlumnoCarreraCreate, session: SessionDep):
    require_exists(session, Alumno, data.rut_alumno, "Alumno")
    require_exists(session, Carrera, data.id_carrera, "Carrera")
    item = conflict_safe(session, lambda: crud.create_alumno_carrera(session, data))
    return crud.alumno_carrera_to_read(session, item)


@router.get("/cursos", response_model=list[CursoRead])
def list_cursos(session: SessionDep):
    return [crud.curso_to_read(curso) for curso in crud.list_cursos(session)]


@router.post("/cursos", response_model=CursoRead, status_code=status.HTTP_201_CREATED)
def create_curso(curso_data: CursoCreate, session: SessionDep):
    curso = conflict_safe(session, lambda: crud.create_curso(session, curso_data))
    return crud.curso_to_read(curso)


@router.get("/inscripciones", response_model=list[InscripcionRead])
def list_inscripciones(session: SessionDep):
    return [crud.inscripcion_to_read(session, item) for item in crud.list_inscripciones(session)]


@router.post("/inscripciones", response_model=InscripcionRead, status_code=status.HTTP_201_CREATED)
def create_inscripcion(data: InscripcionCreate, session: SessionDep):
    require_exists(session, Alumno, data.rut_alumno, "Alumno")
    require_exists(session, Curso, data.id_curso, "Curso")
    item = conflict_safe(session, lambda: crud.create_inscripcion(session, data))
    return crud.inscripcion_to_read(session, item)


@router.get("/bloques", response_model=list[BloqueRead])
def list_bloques(session: SessionDep):
    return [crud.bloque_to_read(bloque) for bloque in crud.list_bloques(session)]


@router.post("/bloques", response_model=BloqueRead, status_code=status.HTTP_201_CREATED)
def create_bloque(bloque_data: BloqueCreate, session: SessionDep):
    bloque = conflict_safe(session, lambda: crud.create_bloque(session, bloque_data))
    return crud.bloque_to_read(bloque)


@router.get("/pruebas", response_model=list[PruebaRead])
def list_pruebas(session: SessionDep):
    return [crud.prueba_to_read(session, prueba) for prueba in crud.list_pruebas(session)]


@router.post("/pruebas", response_model=PruebaRead, status_code=status.HTTP_201_CREATED)
def create_prueba(prueba_data: PruebaCreate, session: SessionDep):
    require_exists(session, Curso, prueba_data.id_curso, "Curso")
    prueba = conflict_safe(session, lambda: crud.create_prueba(session, prueba_data))
    return crud.prueba_to_read(session, prueba)


@router.get("/salas", response_model=list[SalaRead])
def list_salas(session: SessionDep):
    return [crud.sala_to_read(sala) for sala in crud.list_salas(session)]


@router.post("/salas", response_model=SalaRead, status_code=status.HTTP_201_CREATED)
def create_sala(sala_data: SalaCreate, session: SessionDep):
    sala = conflict_safe(session, lambda: crud.create_sala(session, sala_data))
    return crud.sala_to_read(sala)


@router.get("/uso-sala", response_model=list[UsoSalaRead])
def list_uso_sala(session: SessionDep):
    return [crud.uso_sala_to_read(session, uso) for uso in crud.list_uso_sala(session)]


@router.post("/uso-sala", response_model=UsoSalaRead, status_code=status.HTTP_201_CREATED)
def create_uso_sala(data: UsoSalaCreate, session: SessionDep):
    require_exists(session, Prueba, data.id_evaluacion, "Prueba")
    require_exists(session, Sala, data.id_sala, "Sala")
    require_exists(session, Bloque, data.n_bloque, "Bloque")
    uso = conflict_safe(session, lambda: crud.create_uso_sala(session, data))
    return crud.uso_sala_to_read(session, uso)


@router.get("/asignaciones", response_model=list[AsignacionRead])
def list_asignaciones(session: SessionDep):
    return [crud.asignacion_to_read(session, asignacion) for asignacion in crud.list_asignaciones(session)]


@router.post("/asignaciones", response_model=AsignacionRead, status_code=status.HTTP_201_CREATED)
def create_asignacion(data: AsignacionCreate, session: SessionDep):
    require_exists(session, Alumno, data.rut_alumno, "Alumno")
    require_exists(session, Prueba, data.id_evaluacion, "Prueba")
    require_exists(session, Sala, data.id_sala, "Sala")
    require_exists(session, Bloque, data.n_bloque, "Bloque")

    if crud.get_uso_sala(session, data.id_evaluacion, data.id_sala, data.n_bloque) is None:
        raise HTTPException(
            status_code=409,
            detail="La prueba no tiene habilitada esa sala en ese bloque",
        )

    asignacion = conflict_safe(session, lambda: crud.create_asignacion(session, data))
    return crud.asignacion_to_read(session, asignacion)


@router.get("/alumnos/{rut_alumno}/asignaciones", response_model=list[AsignacionRead])
def list_asignaciones_by_alumno(rut_alumno: str, session: SessionDep):
    require_exists(session, Alumno, rut_alumno, "Alumno")
    asignaciones = crud.list_asignaciones_by_alumno(session, rut_alumno)
    return [crud.asignacion_to_read(session, asignacion) for asignacion in asignaciones]
