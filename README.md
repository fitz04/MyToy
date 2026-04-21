# 🤖 AI Coding Agent

다중 LLM을 지원하는 AI 코딩 어시스턴트. 로컬 프로젝트 분석, 코드 리뷰, 테스트 자동화, RAG 기능을 제공합니다.

## 주요 기능

- **다중 LLM**: Claude, OpenAI GPT-4, Groq, DeepInfra 실시간 전환
- **프로젝트 분석**: 코드베이스 구조 파악, 파일 탐색, 함수/클래스 파싱
- **코드 품질**: black 포매팅, flake8 린팅, pylint 정적 분석, isort
- **코드 리뷰**: LLM 기반 자동 리뷰 (점수, 강점/약점, 코멘트)
- **테스트 실행**: pytest 자동화, 커버리지 측정
- **프로젝트 생성**: FastAPI / Flask / CLI / Library 템플릿
- **RAG**: 문서 업로드 및 컨텍스트 기반 답변
- **웹 검색**: 공식 문서, API 레퍼런스 검색
- **세션 관리**: 프로젝트별 세션 저장/복원

## 실행 방법

### 설치

```bash
git clone <repository-url>
cd MyToy
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-ui.txt
```

### 환경 변수

```bash
cp .env.example .env
# .env 파일에 API 키 설정 (최소 하나 필수)
```

```env
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
DEEPINFRA_API_KEY=your_key

DEFAULT_LLM_PROVIDER=claude
```

### 실행

**Chainlit UI** (채팅 중심):
```bash
chainlit run app.py -w
# http://localhost:8000
```

**Gradio UI** (고정 사이드바):
```bash
python app_gradio.py
# http://localhost:7860
```

## 프로젝트 구조

```
├── agents/             # 에이전트 (CodingAgent, CodeReviewer, ErrorFixer)
├── tools/              # 도구 (파일, Git, 테스트, 품질 검사, 웹 검색 등)
├── llm/                # LLM 관리 (Claude, OpenAI, Groq, DeepInfra)
├── rag/                # RAG (문서 처리, 벡터 저장소, 검색)
├── utils/              # 유틸리티 (세션 관리 등)
├── config/             # 설정
├── tests/              # 유닛 테스트
├── app.py              # Chainlit UI
├── app_gradio.py       # Gradio UI
└── docs/               # 문서
```

## UI 선택 가이드

| | Chainlit | Gradio |
|---|---|---|
| 버튼 위치 | 채팅 내 (매 응답마다 재표시) | 고정 사이드바 |
| 레이아웃 | 채팅 중심 | 채팅 + 도구 패널 |
| 커스터마이징 | 제한적 | 자유로움 |
| 배포 | 직접 호스팅 | HuggingFace Spaces |

## 의존성

```bash
pip install -r requirements-core.txt   # 코어만
pip install -r requirements-ui.txt     # Chainlit + Gradio 포함
pip install -r requirements-full.txt   # 전체
```
