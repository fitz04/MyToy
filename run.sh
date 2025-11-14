#!/bin/bash

# AI Coding Assistant 실행 스크립트

echo "🤖 AI Coding Assistant 시작 중..."

# .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사하여 .env를 생성하고 API 키를 설정하세요."
    echo "   cp .env.example .env"
    exit 1
fi

# 가상환경 확인 및 활성화
if [ ! -d "venv" ]; then
    echo "📦 가상환경이 없습니다. 가상환경을 생성합니다..."
    python3 -m venv venv
fi

echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# 의존성 설치 확인
if [ ! -f "venv/.installed" ]; then
    echo "📥 의존성 설치 중..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.installed
else
    echo "✅ 의존성이 이미 설치되어 있습니다."
fi

# 데이터 디렉토리 생성
mkdir -p data/vectorstore

# Chainlit 실행
echo "🚀 Chainlit 애플리케이션 시작..."
chainlit run app.py -w

deactivate
