
from fastapi import FastAPI
from .api.routers import auth,manage,quiz
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost:1378"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(manage.router)
app.include_router(quiz.router)

@app.get('/')
def home():
    return {'status':'ok you are in home page'}

# @app2.middleware("http")
# def db_session_middleware(request: Request, call_next):
#     response = Response("Internal server error", status_code=500)
#     try:
#         database.connect()
#         print('connect',database)
#         # request.state.db = SessionLocal()
#         response = call_next(request)
#     finally:
#         # request.state.db.close()
#         database.close()
#         print('close',database)
#     return response



# if __name__ == "__main__":
#     uvicorn.run("main:app2",reload=True,port=80)