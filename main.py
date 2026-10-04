import os
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

# Controllers
from controllers.users import router as UsersRouter
from controllers.donations import router as DonationRouter
from controllers.item import router as ItemRouter


app = FastAPI()

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    
    allow_methods=["*"],      
    allow_headers=["*"],       
)

app.include_router(UsersRouter, prefix='/api')
app.include_router(DonationRouter, prefix='/api')
app.include_router(ItemRouter, prefix='/api')

@app.get('/health')
def health_check():
  return {'message': 'Api is running'}


