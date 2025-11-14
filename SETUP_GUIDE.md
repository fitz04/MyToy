# 📚 설치 및 설정 가이드

이 가이드는 AI Coding Assistant를 처음 사용하는 사용자를 위한 상세한 설정 방법을 제공합니다.

## 🔑 API 키 발급 방법

### Claude (Anthropic)
1. https://console.anthropic.com/ 접속
2. 계정 생성 또는 로그인
3. "API Keys" 메뉴로 이동
4. "Create Key" 버튼 클릭
5. API 키 복사 및 저장

### OpenAI
1. https://platform.openai.com/ 접속
2. 계정 생성 또는 로그인
3. "API keys" 메뉴로 이동
4. "Create new secret key" 클릭
5. API 키 복사 및 저장
6. **주의**: 키는 한 번만 표시되므로 안전하게 보관하세요

### Groq
1. https://console.groq.com/ 접속
2. 계정 생성 또는 로그인
3. "API Keys" 섹션으로 이동
4. "Create API Key" 클릭
5. API 키 복사 및 저장

### DeepInfra
1. https://deepinfra.com/ 접속
2. 계정 생성 또는 로그인
3. Dashboard에서 "API Keys" 선택
4. "Create new key" 클릭
5. API 키 복사 및 저장

## 🐍 Python 환경 설정

### Python 버전 확인
```bash
python --version
```
Python 3.9 이상이 필요합니다.

### 가상환경 생성 (권장)

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python -m venv venv
source venv/bin/activate
```

### 의존성 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## ⚙️ 환경 변수 설정

### 1. .env 파일 생성
```bash
cp .env.example .env
```

### 2. .env 파일 편집
텍스트 에디터로 `.env` 파일을 열고 API 키를 입력하세요:

```env
# 사용할 LLM의 API 키만 입력하면 됩니다
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
DEEPINFRA_API_KEY=xxxxxxxxxxxxx

# 기본으로 사용할 LLM 선택
DEFAULT_LLM_PROVIDER=claude
```

### 3. 선택적 설정

#### RAG 설정
```env
# 벡터 저장소 경로
VECTOR_STORE_PATH=./data/vectorstore

# 임베딩 모델 (기본값 사용 권장)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# 문서 청크 크기
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

#### 파일 처리 설정
```env
# 최대 파일 크기 (바이트)
MAX_FILE_SIZE=10485760  # 10MB

# 지원 파일 확장자
SUPPORTED_FILE_EXTENSIONS=.py,.js,.ts,.jsx,.tsx,.java,.cpp,.c,.go,.rs,.md,.txt

# 컨텍스트에 포함할 최대 파일 수
MAX_CONTEXT_FILES=20
```

#### 웹 검색 설정
```env
# 웹 검색 활성화
ENABLE_WEB_SEARCH=true

# 최대 검색 결과 수
MAX_SEARCH_RESULTS=5
```

## 🚀 첫 실행

### 1. 애플리케이션 시작
```bash
chainlit run app.py -w
```

`-w` 플래그는 파일 변경 시 자동 재시작을 활성화합니다.

### 2. 브라우저에서 접속
기본적으로 http://localhost:8000 에서 실행됩니다.

### 3. 포트 변경 (선택사항)
```bash
chainlit run app.py --port 8080
```

## 🧪 설치 확인

### 1. LLM 연결 테스트
애플리케이션 실행 후:
```
/current-llm
```

API 키가 올바르게 설정되었는지 확인할 수 있습니다.

### 2. 간단한 질문 테스트
```
안녕! 간단한 Python 함수를 작성해줘.
```

### 3. 파일 분석 테스트
```
/analyze
```

프로젝트 구조가 올바르게 분석되는지 확인합니다.

## 🔧 문제 해결

### ImportError 발생 시
```bash
pip install --upgrade -r requirements.txt
```

### API 키 오류 시
1. `.env` 파일의 API 키 확인
2. API 키 앞뒤 공백 제거
3. 따옴표 없이 키만 입력했는지 확인

### 포트 충돌 시
```bash
# 다른 포트 사용
chainlit run app.py --port 8080
```

### ChromaDB 오류 시
```bash
# 벡터 저장소 초기화
rm -rf data/vectorstore
```

### 권한 오류 시
```bash
# Linux/Mac
chmod +x app.py

# Windows: 관리자 권한으로 실행
```

## 📦 선택적 구성 요소

### DeepAgent 추가 설정
DeepAgent의 고급 기능을 사용하려면:

```bash
pip install deepagent[full]
```

### GPU 지원 (선택사항)
임베딩 생성 속도 향상을 위해:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 🎯 다음 단계

1. [README.md](README.md)에서 사용 방법 확인
2. `/help` 명령으로 사용 가능한 명령어 확인
3. RAG에 프로젝트 문서 업로드
4. 다양한 LLM 제공자 테스트

## 💡 프로덕션 배포

### Docker 사용 (권장)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0"]
```

### 환경 변수 주입
```bash
docker run -e ANTHROPIC_API_KEY=xxx -e OPENAI_API_KEY=yyy -p 8000:8000 ai-coding-assistant
```

## 🔒 보안 주의사항

1. **API 키 보호**
   - `.env` 파일을 절대 Git에 커밋하지 마세요
   - `.gitignore`에 `.env`가 포함되어 있는지 확인하세요

2. **파일 업로드 제한**
   - `MAX_FILE_SIZE`를 적절히 설정하세요
   - 민감한 정보가 포함된 파일 업로드 주의

3. **네트워크 보안**
   - 외부 접근이 필요하면 HTTPS 사용
   - 방화벽 설정 확인

## 📞 지원

문제가 계속되면 다음을 포함하여 이슈를 생성해주세요:

1. Python 버전
2. 운영 체제
3. 오류 메시지 전체
4. 수행한 단계

즐거운 코딩 되세요! 🎉
