from fastapi import FastAPI
from routers import router

app = FastAPI(title='MedBook API')

app.include_router(router)