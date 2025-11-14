@echo off
REM AI Coding Assistant 실행 스크립트 (Windows)

echo 🤖 AI Coding Assistant 시작 중...

REM .env 파일 확인
if not exist .env (
    echo ⚠️  .env 파일이 없습니다. .env.example을 복사하여 .env를 생성하고 API 키를 설정하세요.
    echo    copy .env.example .env
    exit /b 1
)

REM 가상환경 확인 및 생성
if not exist venv (
    echo 📦 가상환경이 없습니다. 가상환경을 생성합니다...
    python -m venv venv
)

echo 🔧 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM 의존성 설치 확인
if not exist venv\.installed (
    echo 📥 의존성 설치 중...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    type nul > venv\.installed
) else (
    echo ✅ 의존성이 이미 설치되어 있습니다.
)

REM 데이터 디렉토리 생성
if not exist data mkdir data
if not exist data\vectorstore mkdir data\vectorstore

REM Chainlit 실행
echo 🚀 Chainlit 애플리케이션 시작...
chainlit run app.py -w

deactivate
