from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import mqtt
from app.routes import auth, users, zones, sensors, pumps
from app.middleware import setup_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt.connect_mqtt()
    yield


app = FastAPI(
    title="Borneo Agricola API",
    description="Backend Server untuk Sistem Cerdas IoT Pertanian",
    version="1.0.0",
    lifespan=lifespan,
)

setup_middleware(app)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(zones.router)
app.include_router(sensors.router)
app.include_router(pumps.router)


@app.get("/")
def ping_server():
    return {"status": "sukses", "pesan": "Mesin Utama Borneo Agricola Berjalan Sempurna!"}
