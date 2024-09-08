from fastapi import FastAPI, HTTPException
from app.routers import user_router, external_router, place_router, visitkorea_router
from app.database import ping_mongodb
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import base_settings
from dotenv import load_dotenv
from mangum import Mangum  # Lambda 배포를 위한 패키징 모듈

load_dotenv(dotenv_path="config.env")  # .env 파일의 환경 변수를 로드합니다.


app = FastAPI()

session_key = base_settings.SERVICE_KEY
if session_key is None:
    raise ValueError("SESSION_KEY 환경 변수가 설정되어야 합니다.")

# CORS 설정
origins = [
    "http://localhost:8000",  # FastAPI 서버 주소
]
## session 관리를 위한 추가.
app.add_middleware(SessionMiddleware, secret_key=session_key)

## 다른 도메인에서 호스팅되는 리소스에 접근할 수 있도록 하기 위함.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 포함
# app.include_router(ai_rt.router) # 다른 기능 만들 때까지 정지.
app.include_router(external_router)  # 외부 API 라우터 포함
app.include_router(place_router)
app.include_router(user_router)
app.include_router(visitkorea_router)


@app.get("/ping")
def ping_mongodb_endpoint():
    if ping_mongodb():
        return {
            "message": "Pinged your deployment. You successfully connected to MongoDB!"
        }
    else:
        return HTTPException(
            status_code=500, detail={"error": "Failed to connect to MongoDB"}
        )


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}


handler = Mangum(app)
