from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.database import init_db
from .api import coordinates, images

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o banco de dados
init_db()

# Inclui as rotas
app.include_router(coordinates.router)
app.include_router(images.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 