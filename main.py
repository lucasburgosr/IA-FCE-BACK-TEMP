from fastapi import FastAPI, APIRouter
from controllers.alumno_controller import router as alumno_router
from controllers.asistente_controller import router as asistente_router
from controllers.evaluacion_controller import router as evaluacion_router
from controllers.materia_controller import router as materia_router
from controllers.pregunta_controller import router as pregunta_router
from controllers.profesor_controller import router as profesor_router
from controllers.tema_controller import router as subtema_router
from controllers.thread_controller import router as thread_router
from controllers.unidad_controller import router as unidad_router
from controllers.auth_controller import router as auth_router
from controllers.sesion_controller import router as sesion_router
from controllers.responses_controller import router as responses_router
from fastapi.middleware.cors import CORSMiddleware
from config.db_config import Base, engine
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación y creando tablas de la base de datos...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield

    print("Cerrando pool de conexiones de la base de datos...")
    await engine.dispose()

origins = ["http://localhost:5173", "http://179.0.136.80"]

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return {"status": "ok"}

api_router = APIRouter(prefix="/api/v2")

api_router.include_router(alumno_router)
api_router.include_router(asistente_router)
api_router.include_router(evaluacion_router)
api_router.include_router(materia_router)
api_router.include_router(pregunta_router)
api_router.include_router(profesor_router)
api_router.include_router(subtema_router)
api_router.include_router(thread_router)
api_router.include_router(unidad_router)
api_router.include_router(auth_router)
api_router.include_router(sesion_router)
api_router.include_router(responses_router)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
