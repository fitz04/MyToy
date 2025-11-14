# 📦 의존성 관리 가이드

프로젝트 의존성을 **3단계**로 분리하여 관리합니다.

---

## 🎯 의존성 레벨

### 1️⃣ Core (필수) - `requirements-core.txt`
**Phase 1 & Phase 2 핵심 기능에 필요한 최소 의존성**

```bash
pip install -r requirements-core.txt
```

**포함 패키지**:
- `anthropic`, `openai` - LLM API
- `aiofiles` - 비동기 파일 I/O
- `pydantic` - 데이터 검증
- `gitpython` - Git 통합
- `python-dotenv` - 환경 변수
- `tenacity` - 재시도 로직

**사용 가능한 기능**:
- ✅ Phase 1: 파일 쓰기/편집, Git 통합, TODO 시스템
- ✅ Phase 2: 에러 자동 수정
- ✅ LLM 기반 코드 생성
- ❌ Chainlit UI (필요 없음 - CLI로 사용)
- ❌ RAG 시스템
- ❌ 웹 검색

**장점**:
- 🚀 **빠른 설치** (~10개 패키지)
- 🔒 **의존성 충돌 최소화**
- 💡 **핵심 기능에 집중**

---

### 2️⃣ UI (Chainlit) - `requirements-ui.txt`
**웹 UI가 필요한 경우**

```bash
pip install -r requirements-ui.txt
```

**추가 패키지**:
- `chainlit` - 웹 UI 프레임워크

**사용 가능한 기능**:
- ✅ Core의 모든 기능
- ✅ 웹 기반 채팅 인터페이스
- ✅ 파일 업로드
- ✅ 스트리밍 응답

**언제 사용?**:
- 웹 브라우저로 에이전트를 사용하고 싶을 때
- 여러 사람과 공유하고 싶을 때
- 비개발자도 사용할 수 있게 하고 싶을 때

---

### 3️⃣ Full (전체 기능) - `requirements-full.txt`
**모든 기능이 필요한 경우**

```bash
pip install -r requirements-full.txt
```

**추가 패키지**:
- `langchain`, `chromadb` - RAG 시스템
- `sentence-transformers` - 임베딩 모델
- `duckduckgo-search` - 웹 검색
- `groq` - 추가 LLM
- `black`, `flake8`, `pytest` - 개발 도구

**사용 가능한 기능**:
- ✅ Core + UI의 모든 기능
- ✅ RAG (문서 업로드 및 검색)
- ✅ 웹 검색
- ✅ 다양한 LLM 선택
- ✅ 코드 품질 도구

**주의**:
- ⚠️ **설치 시간 오래 걸림** (~100개 패키지, 5-10분)
- ⚠️ **의존성 충돌 가능성**
- ⚠️ **디스크 공간 많이 사용** (~3GB, torch 포함)

**언제 사용?**:
- 문서 기반 Q&A가 필요할 때
- 웹 검색 기능이 필요할 때
- 프로덕션 배포용

---

## 🚀 빠른 시작 (권장)

### 최소 설치로 시작
```bash
# 1. Core만 설치 (가장 빠름, 안정적)
pip install -r requirements-core.txt

# 2. Phase 1, 2 테스트
python tests/test_standalone.py
python run_manual_test.py
```

### 나중에 필요하면 추가
```bash
# UI가 필요하면
pip install chainlit

# RAG가 필요하면
pip install langchain chromadb sentence-transformers

# 웹 검색이 필요하면
pip install duckduckgo-search beautifulsoup4
```

---

## 📊 의존성 비교

| 레벨 | 패키지 수 | 설치 시간 | 디스크 공간 | 충돌 위험 | 권장 용도 |
|------|----------|----------|------------|----------|----------|
| **Core** | ~10 | 1분 | ~100MB | 낮음 | 개발, 테스트 |
| **UI** | ~30 | 3분 | ~500MB | 중간 | 로컬 사용 |
| **Full** | ~100 | 10분 | ~3GB | 높음 | 프로덕션 |

---

## 🔧 의존성 업데이트

### 버전 업그레이드
```bash
# Core 패키지만 업데이트
pip install -r requirements-core.txt --upgrade

# 전체 업데이트
pip install -r requirements-full.txt --upgrade
```

### 충돌 해결
```bash
# 기존 패키지 제거 후 재설치
pip uninstall -y -r requirements-full.txt
pip install -r requirements-core.txt
```

---

## 💡 팁

### 가상환경 사용 (강력 권장)
```bash
# 가상환경 생성
python -m venv venv

# 활성화
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Core 설치
pip install -r requirements-core.txt
```

### 프로젝트별 격리
```bash
# 프로젝트 A: Core만
cd project_a
python -m venv venv
source venv/bin/activate
pip install -r requirements-core.txt

# 프로젝트 B: Full
cd ../project_b
python -m venv venv
source venv/bin/activate
pip install -r requirements-full.txt
```

---

## 🐛 문제 해결

### 설치 실패 시
```bash
# 1. pip 업그레이드
pip install --upgrade pip

# 2. 캐시 삭제
pip cache purge

# 3. 개별 설치 시도
pip install anthropic
pip install openai
# ...
```

### 의존성 충돌 시
```bash
# 충돌하는 패키지 확인
pip check

# 특정 버전 고정
pip install "anthropic==0.30.0"
```

---

## 📝 업데이트 이력

- **2025-11-14**: 3단계 분리 (core, ui, full)
  - 의존성 최소화로 안정성 향상
  - 선택적 설치 지원

---

**추천 설치 방법**: `requirements-core.txt` → 필요 시 개별 패키지 추가
