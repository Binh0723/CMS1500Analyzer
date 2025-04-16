from app.routes.upload import upload_router

from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi import FastAPI # type: ignore


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
@app.get("/")
async def root():
    return {"Message" : "This is CMS1500 Validator"}


