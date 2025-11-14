# 🤖 AI Coding Assistant

**DeepAgent + Chainlit 기반의 강력한 AI 코딩 어시스턴트**

다중 LLM 지원, 로컬 파일 분석, 웹 검색, RAG 기능을 모두 갖춘 올인원 코딩 도우미입니다.

## ✨ 주요 기능

### 🧠 다중 LLM 지원
- **Claude (Anthropic)** - 복잡한 추론과 코드 분석에 최적
- **OpenAI GPT-4** - 범용 코딩 작업에 적합
- **Groq** - 초고속 추론으로 빠른 작업에 유리
- **DeepInfra** - 비용 효율적인 대량 작업

실시간으로 원하는 LLM으로 전환 가능!

### 📁 로컬 파일 분석
- 프로젝트 파일 읽기 및 분석
- 코드베이스 구조 이해
- 코드 내 검색
- 함수/클래스 파싱 및 설명

### 🌐 웹 검색
- 공식 문서 검색
- API 레퍼런스 찾기
- 코드 예제 검색
- 튜토리얼 및 가이드 탐색

### 📚 RAG (Retrieval Augmented Generation)
- 프로젝트 문서 업로드
- API 레퍼런스 저장
- 참고 자료 관리
- 컨텍스트 기반 정확한 답변

### ⚡ 코드 실행
- Python, JavaScript, Bash 코드 실행
- 솔루션 검증
- 코드 스니펫 테스트
- 디버깅 지원

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd MyToy
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
cp .env.example .env
```

`.env` 파일을 편집하여 API 키를 설정하세요:

```env
# 최소한 하나의 LLM API 키는 필수입니다
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
DEEPINFRA_API_KEY=your_deepinfra_api_key_here

# 기본 LLM 제공자 선택 (claude, openai, groq, deepinfra)
DEFAULT_LLM_PROVIDER=claude
```

### 5. 애플리케이션 실행
```bash
chainlit run app.py -w
```

브라우저에서 http://localhost:8000 접속!

## 📖 사용 방법

### 기본 명령어

| 명령어 | 설명 |
|--------|------|
| `/switch <provider>` | LLM 제공자 전환 (claude, openai, groq, deepinfra) |
| `/analyze` | 현재 프로젝트 구조 분석 |
| `/search <query>` | 웹에서 문서 검색 |
| `/upload` | RAG용 문서 업로드 |
| `/stats` | RAG 통계 보기 |
| `/clear-docs` | 업로드된 문서 전체 삭제 |
| `/clear-chat` | 대화 기록 삭제 |
| `/current-llm` | 현재 LLM 정보 보기 |
| `/help` | 도움말 보기 |

### 사용 예시

#### 코드 리뷰
```
이 Python 함수를 리뷰하고 개선점을 제안해줘:

def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
```

#### 디버깅
```
"TypeError: 'NoneType' object is not iterable" 에러가 발생했어.
이 코드를 디버깅해줘:
[코드 붙여넣기]
```

#### 문서 검색
```
Python asyncio의 최신 문서를 검색해줘
```

#### 코드 설명
```
JavaScript의 async/await가 어떻게 작동하는지 예제와 함께 설명해줘
```

## 🏗️ 프로젝트 구조

```
MyToy/
├── app.py                      # Chainlit 메인 애플리케이션
├── requirements.txt            # Python 의존성
├── .env.example               # 환경 변수 예제
├── README.md                  # 프로젝트 문서
├── config/
│   └── settings.py            # 설정 관리
├── llm/                       # LLM 제공자
│   ├── base.py               # 베이스 LLM 인터페이스
│   ├── claude.py             # Claude API
│   ├── openai_llm.py         # OpenAI API
│   ├── groq.py               # Groq API
│   ├── deepinfra.py          # DeepInfra API
│   └── manager.py            # LLM 매니저
├── tools/                     # 도구들
│   ├── file_analyzer.py      # 로컬 파일 분석
│   ├── codebase_parser.py    # 코드베이스 파싱
│   ├── web_search.py         # 웹 검색
│   └── executor.py           # 코드 실행
├── rag/                       # RAG 시스템
│   ├── document_processor.py # 문서 처리
│   ├── vectorstore.py        # 벡터 저장소
│   └── retriever.py          # 검색기
├── agents/                    # 에이전트
│   ├── coding_agent.py       # 메인 코딩 에이전트
│   └── prompts.py            # 프롬프트 템플릿
└── utils/                     # 유틸리티
    └── helpers.py            # 헬퍼 함수
```

## 🔧 고급 설정

### 환경 변수 전체 목록

```env
# LLM API Keys
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GROQ_API_KEY=
DEEPINFRA_API_KEY=

# Default LLM Provider
DEFAULT_LLM_PROVIDER=claude

# Model Names
CLAUDE_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4-turbo-preview
GROQ_MODEL=mixtral-8x7b-32768
DEEPINFRA_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct

# RAG Settings
VECTOR_STORE_PATH=./data/vectorstore
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Application Settings
MAX_FILE_SIZE=10485760
SUPPORTED_FILE_EXTENSIONS=.py,.js,.ts,.jsx,.tsx,.java,.cpp,.c,.go,.rs,.md,.txt
MAX_CONTEXT_FILES=20

# Web Search
ENABLE_WEB_SEARCH=true
MAX_SEARCH_RESULTS=5
```

### 지원 파일 형식

#### RAG 업로드
- PDF (`.pdf`)
- Word 문서 (`.docx`, `.doc`)
- 텍스트 파일 (`.txt`, `.md`)
- 코드 파일 (`.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.cpp`, `.c`, `.go`, `.rs`)

#### 프로젝트 분석
- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`)
- Go (`.go`)
- Rust (`.rs`)
- Markdown (`.md`)

## 💡 팁

1. **LLM 선택**
   - 복잡한 코드 분석: Claude
   - 빠른 응답 필요: Groq
   - 범용 작업: OpenAI
   - 비용 절감: DeepInfra

2. **RAG 활용**
   - 프로젝트별 문서를 미리 업로드하면 더 정확한 답변을 받을 수 있습니다
   - API 문서, 내부 가이드라인 등을 업로드하세요

3. **웹 검색**
   - 최신 정보가 필요할 때 활용하세요
   - 공식 문서 링크를 빠르게 찾을 수 있습니다

4. **프로젝트 분석**
   - `/analyze` 명령으로 프로젝트 개요를 먼저 파악하세요
   - 대규모 코드베이스 작업 시 유용합니다

## 🛠️ 개발

### 테스트 실행
```bash
pytest
```

### 코드 포맷팅
```bash
black .
```

### Linting
```bash
flake8 .
```

## 📝 라이선스

MIT License

## 🤝 기여

이슈와 풀 리퀘스트는 언제나 환영합니다!

## 📧 문의

프로젝트에 대한 질문이나 제안이 있으시면 이슈를 열어주세요.

---

Made with ❤️ using DeepAgent and Chainlit
