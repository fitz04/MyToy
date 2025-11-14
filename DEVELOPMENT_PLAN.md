# 🚀 AI Coding Assistant 개발 계획

> **목표**: DeepAgent + Chainlit 기반으로 실제 코딩 작업을 자동화하는 프로덕션급 AI 코딩 에이전트 구축

> **업데이트**: 2025-11-15 - Phase 1, 2 완료! 다음은 UI/UX 개선 (Phase 3)

---

## 🎯 **최우선 과제: Phase 3 - UI/UX 개선** (2025-11-15)

### 🔴 **긴급: 프로젝트 로딩 시스템** (가장 중요!)
**현재 문제**: UI에서 프로젝트를 로드할 방법이 없어서 실제 코딩 어시스턴트 기능 사용 불가

**구현 필요사항**:
```python
# app.py에 추가
@cl.on_chat_start
async def start():
    # 1. 프로젝트 경로 입력 UI
    settings = await cl.ChatSettings(
        [
            TextInput(
                id="project_path",
                label="프로젝트 경로",
                initial="/path/to/project"
            ),
            Switch(id="auto_analyze", label="자동 분석", initial=True),
        ]
    ).send()

    # 2. 파일 트리 생성 및 표시
    # 3. 선택한 파일들 RAG 인덱싱
    # 4. 프로젝트 컨텍스트 세션에 저장
```

**타임라인**: 1-2일

---

### 🔴 **긴급: 세션 지속성** (매우 중요!)
**현재 문제**: 재시작 시 모든 분석 데이터와 RAG 인덱스 사라짐

**구현 필요사항**:
```python
# utils/session_manager.py
class SessionManager:
    """프로젝트별 세션 데이터 관리"""

    async def save_session(self, project_path: str, data: dict):
        """
        저장할 데이터:
        - 분석된 파일 목록
        - RAG 인덱스 위치
        - 대화 히스토리
        - 프로젝트 설정
        """

    async def load_session(self, project_path: str) -> dict:
        """이전 세션 복원"""
```

**저장 위치**: `.agent_cache/{project_hash}/`
**타임라인**: 1일

---

### 🟡 **중요: 다국어 지원** (한국어/영어)
**현재 문제**: 모든 응답이 영어로 나옴

**구현 필요사항**:
```python
# config/settings.py에 추가
class Settings(BaseSettings):
    language: str = "ko"  # ko, en

# agents/prompts.py 분리
PROMPTS = {
    "ko": {
        "system": "당신은 전문 코딩 어시스턴트입니다...",
        "analyze": "다음 코드를 분석해주세요...",
    },
    "en": {
        "system": "You are a professional coding assistant...",
        "analyze": "Please analyze the following code...",
    }
}
```

**타임라인**: 0.5일

---

## 📊 현재 상태 (As-Is) - 2025-11-15 업데이트

### ✅ Phase 1 완료 (Week 1-2)
- [x] **파일 쓰기 도구** (`tools/file_operations.py`) ✅
  - write_file, edit_file, insert_code, delete_lines
  - 자동 백업 시스템
  - Diff 생성
- [x] **Git 통합** (`tools/git_operations.py`) ✅
  - git_status, git_diff, git_commit
  - smart_commit
  - 브랜치 관리
- [x] **TODO 계획 시스템** (`agents/planner.py`) ✅
  - Task, Plan 데이터 모델
  - 의존성 관리
  - 진행 상황 추적

### ✅ Phase 2 완료 (Week 3-4)
- [x] **에러 자동 수정** (`agents/error_fixer.py`) ✅
  - Traceback 파싱 및 분석
  - LLM 기반 수정 제안
  - 자동 재시도 (최대 3회)
  - 8가지 에러 타입 지원
  - **실제 LLM 테스트 통과!**

### ✅ 기타 기능 (이미 구현됨)
- [x] 다중 LLM 지원 (Claude, OpenAI, Groq, DeepInfra)
- [x] LLM 전환 기능 (`/switch`)
- [x] 로컬 파일 **읽기** 및 분석
- [x] 코드베이스 파싱 (Python/JavaScript)
- [x] 웹 검색 (DuckDuckGo)
- [x] RAG 시스템 (ChromaDB + Sentence Transformers)
- [x] 문서 업로드 및 검색
- [x] 코드 실행 (Python, JavaScript, Bash)
- [x] Chainlit UI 기본 구조
- [x] 대화형 인터페이스

### 🚧 Phase 3 미구현 (UI/UX 개선 필요)
- [ ] **프로젝트 로딩 시스템** - 가장 긴급! 🔴
- [ ] **세션 지속성** - 매우 중요! 🔴
- [ ] **다국어 지원** (한국어/영어) - 중요! 🟡

### ❌ Phase 4 이후 미구현 기능
- [ ] Docker 샌드박스
- [ ] 백그라운드 작업 큐
- [ ] 플러그인 시스템
- [ ] 멀티 에이전트
- [ ] TODO 계획 및 추적 시스템
- [ ] 에러 자동 분석 및 수정
- [ ] 코드 리뷰 및 제안
- [ ] 리팩토링 자동화
- [ ] 테스트 자동 생성 및 실행
- [ ] 프로젝트 템플릿 시스템
- [ ] Docker 샌드박스
- [ ] 백그라운드 작업 큐

### 🎯 현재의 문제점
1. **읽기 전용**: 파일을 분석만 하고 수정하지 못함
2. **Git 미통합**: 버전 관리 불가
3. **계획 부재**: 복잡한 작업을 단계별로 처리 못함
4. **검증 부족**: 생성한 코드를 테스트하지 않음
5. **DeepAgent 미활용**: 아직 도구 통합이 완전하지 않음

---

## 🎯 목표 상태 (To-Be)

### 핵심 가치 제안
> "자연어로 말하면 → 계획 수립 → 코드 작성/수정 → 테스트 실행 → Git 커밋까지 자동화"

### 사용 시나리오 예시

#### 시나리오 1: 새 기능 구현
```
사용자: FastAPI에 사용자 인증 엔드포인트를 추가해줘

에이전트:
1. [계획] 프로젝트 구조 분석
2. [계획] 필요한 파일 목록 작성
   - auth/models.py (User 모델)
   - auth/routes.py (로그인/회원가입 엔드포인트)
   - requirements.txt (passlib, python-jose 추가)
3. [실행] 파일 생성 및 코드 작성
4. [검증] pytest로 테스트 실행
5. [완료] git commit -m "feat: Add user authentication"

✅ 완료! 3개 파일 생성, 테스트 통과, 커밋됨
```

#### 시나리오 2: 버그 수정
```
사용자: TypeError in user_service.py line 42를 고쳐줘

에이전트:
1. [분석] 파일 읽기 및 에러 컨텍스트 파악
2. [진단] NoneType 체크 누락 발견
3. [수정] 방어적 코드 추가
4. [검증] 테스트 실행 - PASS
5. [완료] git commit -m "fix: Add None check in user_service"
```

#### 시나리오 3: 리팩토링
```
사용자: database.py를 클린 아키텍처 패턴으로 리팩토링해줘

에이전트:
1. [계획] 현재 구조 분석
2. [계획] 리팩토링 단계 수립
   - Repository 패턴 도입
   - 의존성 주입 구조 변경
3. [실행] 단계별 리팩토링 (5단계)
4. [검증] 각 단계마다 테스트 실행
5. [완료] 여러 개의 작은 커밋으로 분할
```

---

## 🛠️ 기능 상세 설계

### **Phase 1: 핵심 기능 (MVP)** - 1-2주

#### 1.1 파일 조작 도구 🔥 **최우선**
```python
# tools/file_operations.py

@tool
async def write_file(file_path: str, content: str, mode: str = "w") -> dict:
    """
    파일 생성 또는 덮어쓰기
    - 디렉토리 자동 생성
    - 백업 생성 (기존 파일이 있을 경우)
    - 변경사항 diff 생성
    """

@tool
async def edit_file(file_path: str,
                   old_content: str,
                   new_content: str) -> dict:
    """
    파일의 특정 부분만 수정 (정교한 편집)
    - 라인 범위 지정 가능
    - 정규식 패턴 매칭
    - 변경 전후 diff 표시
    """

@tool
async def insert_code(file_path: str,
                     after_line: int,
                     code: str) -> dict:
    """특정 라인 다음에 코드 삽입"""

@tool
async def delete_lines(file_path: str,
                      start_line: int,
                      end_line: int) -> dict:
    """특정 라인 범위 삭제"""
```

**구현 포인트**:
- ✅ 원자적 파일 쓰기 (임시 파일 → rename)
- ✅ 백업 디렉토리 (`.agent_backup/`)
- ✅ diff 생성 (`difflib`)
- ✅ 파일 잠금 (동시 수정 방지)

#### 1.2 Git 통합
```python
# tools/git_operations.py

@tool
async def git_commit(message: str, files: list[str] = None) -> dict:
    """
    스마트 커밋
    - Conventional Commit 형식 자동 적용
    - 변경사항 분석하여 메시지 자동 생성
    - 커밋 전 lint 검사 (optional)
    """

@tool
async def create_branch(branch_name: str) -> dict:
    """기능 브랜치 생성 및 전환"""

@tool
async def git_diff(file_path: str = None) -> str:
    """변경사항 확인"""

@tool
async def git_status() -> dict:
    """현재 상태 조회"""
```

#### 1.3 TODO 계획 시스템
```python
# agents/planner.py

class TaskPlanner:
    """
    복잡한 작업을 단계별로 분해
    """

    async def create_plan(self, user_request: str) -> Plan:
        """
        1. 요구사항 분석
        2. 필요한 파일/기능 식별
        3. 단계별 TODO 생성
        4. 의존성 파악
        """

    async def execute_step(self, step: Step) -> StepResult:
        """
        1. 도구 선택 및 실행
        2. 결과 검증
        3. 다음 단계로 진행 또는 재시도
        """

    async def track_progress(self) -> ProgressReport:
        """진행 상황 시각화"""
```

**UI 표시** (Chainlit):
```
📋 작업 계획
━━━━━━━━━━━━━━━━━━━━━
✅ 1. 프로젝트 구조 분석
✅ 2. models.py 생성
🔄 3. routes.py 작성 중... (50%)
⏳ 4. 테스트 실행 대기
⏳ 5. Git 커밋 대기
```

#### 1.4 코드 실행 개선
```python
# tools/executor.py (기존 개선)

class ImprovedExecutor:
    """
    - ✅ 가상환경 자동 생성
    - ✅ 의존성 자동 설치 (requirements.txt 감지)
    - ✅ 테스트 프레임워크 자동 실행 (pytest, jest 등)
    - ✅ 커버리지 리포트
    """

    async def run_tests(self, test_pattern: str = "test_*.py") -> TestResult:
        """pytest 자동 실행"""

    async def check_linting(self, files: list[str]) -> LintResult:
        """ruff/pylint 실행"""

    async def format_code(self, files: list[str]) -> None:
        """black/prettier 자동 포맷팅"""
```

---

### **Phase 2: 고급 기능** - 2-3주

#### 2.1 에러 자동 수정
```python
# agents/error_fixer.py

class AutoErrorFixer:
    """
    1. Traceback 파싱
    2. 원인 분석 (LLM)
    3. 수정 시도 (3회)
    4. 실패 시 대안 제시
    """

    async def fix_error(self, error: Exception, context: dict) -> FixResult:
        """
        - ImportError → requirements.txt 업데이트
        - TypeError → 타입 체크 추가
        - AttributeError → 메서드 존재 여부 확인
        """
```

#### 2.2 코드 리뷰 및 제안
```python
# agents/code_reviewer.py

@tool
async def review_code(file_path: str) -> ReviewResult:
    """
    - 코드 품질 분석 (복잡도, 중복 등)
    - 보안 취약점 검사
    - 성능 최적화 제안
    - Best practices 준수 여부
    """

@tool
async def suggest_refactoring(file_path: str) -> list[Suggestion]:
    """리팩토링 제안"""
```

#### 2.3 템플릿 시스템
```python
# tools/templates.py

TEMPLATES = {
    "fastapi": {
        "files": [
            "main.py",
            "models.py",
            "routes/",
            "tests/",
            "requirements.txt",
            ".env.example"
        ],
        "dependencies": ["fastapi", "uvicorn", "sqlalchemy"]
    },
    "streamlit": {...},
    "cli": {...},
}

@tool
async def generate_project(template: str, name: str) -> dict:
    """프로젝트 템플릿 생성"""
```

#### 2.4 외부 검색 강화
```python
# tools/web_search.py (기존 개선)

@tool
async def search_docs(query: str, site: str = None) -> list[SearchResult]:
    """
    - Tavily API 통합 (더 정확한 검색)
    - GitHub Code Search API
    - Stack Overflow API
    - 공식 문서 우선순위
    """

@tool
async def find_similar_code(pattern: str, language: str) -> list[CodeExample]:
    """유사 코드 검색"""
```

---

### **Phase 3: 편의 기능** - 1-2주

#### 3.1 커맨드 팔레트
```python
# UI에서 사용할 단축 명령어

COMMANDS = {
    "/fs": "file_system_navigator",  # 파일 브라우저
    "/test": "run_all_tests",        # 전체 테스트
    "/lint": "check_code_quality",   # Linting
    "/debug": "debug_mode",          # 디버그 모드 전환
    "/plan": "show_current_plan",    # 현재 계획 표시
    "/undo": "rollback_last_change", # 마지막 변경 취소
    "/diff": "show_changes",         # 변경사항 표시
    "/commit": "smart_commit",       # 스마트 커밋
}
```

#### 3.2 설정 파일
```yaml
# .agentrc.yaml

preferences:
  model: claude-3-5-sonnet
  language: ko
  auto_commit: true
  auto_test: true
  strict_types: true  # 타입 힌팅 강제

rules:
  max_file_length: 500
  max_function_length: 50
  always_use_docstrings: true

templates:
  custom_templates_dir: ./my_templates

shortcuts:
  "/mytest": "pytest tests/unit/ -v"
  "/deploy": "docker build && docker push"
```

#### 3.3 히스토리 & 검색
```python
# tools/history.py

@tool
async def search_history(query: str) -> list[Conversation]:
    """과거 대화에서 코드 검색"""

@tool
async def replay_conversation(conversation_id: str) -> None:
    """이전 대화 재현"""
```

---

### **Phase 4: 고도화** - 2-3주

#### 4.1 Docker 샌드박스
```python
# tools/docker_executor.py

class DockerExecutor:
    """
    - 각 언어별 Docker 이미지
    - 격리된 실행 환경
    - 파일 시스템 제한
    - 리소스 제한 (CPU, Memory)
    """

    async def execute_in_container(
        self,
        code: str,
        language: str,
        timeout: int = 30
    ) -> ExecutionResult:
        """컨테이너에서 안전하게 실행"""
```

#### 4.2 백그라운드 작업
```python
# agents/background_worker.py

class BackgroundWorker:
    """
    - Celery/Temporal 통합
    - 장기 실행 작업 처리
    - 진행 상황 체크포인트
    - 완료 시 알림 (Slack, Email)
    """

    async def run_async(self, task: Task) -> str:
        """백그라운드 작업 ID 반환"""

    async def check_status(self, task_id: str) -> TaskStatus:
        """작업 상태 조회"""
```

#### 4.3 플러그인 시스템
```python
# tools/plugins.py

class PluginManager:
    """
    - tools/ 디렉토리 자동 스캔
    - @register_tool 데코레이터
    - 동적 로딩
    """

# 사용자 정의 플러그인 예시
@register_tool
def my_custom_analyzer(code: str) -> dict:
    """나만의 분석 도구"""
    return {...}
```

#### 4.4 멀티 에이전트
```python
# agents/multi_agent.py

class AgentOrchestrator:
    """
    - CodeWriterAgent: 코드 작성 전담
    - TesterAgent: 테스트 전담
    - ReviewerAgent: 리뷰 전담
    - PlannerAgent: 계획 전담

    LangGraph로 워크플로우 관리
    """
```

---

## 📅 상세 개발 일정

### **Week 1-2: Phase 1 - MVP 핵심 기능**

#### Week 1
- [x] 프로젝트 기본 구조 완성 (이미 완료)
- [ ] Day 1-2: 파일 쓰기 도구 구현
  - `write_file`, `edit_file`, `insert_code`, `delete_lines`
  - 백업 시스템
  - diff 생성
- [ ] Day 3-4: Git 통합
  - `git_commit`, `git_status`, `git_diff`
  - 커밋 메시지 자동 생성
- [ ] Day 5: TODO 계획 시스템 기본
  - `TaskPlanner` 클래스
  - 단계별 실행 로직

#### Week 2
- [ ] Day 1-2: 코드 실행 개선
  - pytest 자동 실행
  - 가상환경 관리
  - 의존성 자동 설치
- [ ] Day 3-4: DeepAgent 도구 통합
  - 모든 도구를 DeepAgent에 등록
  - 워크플로우 테스트
- [ ] Day 5: MVP 통합 테스트
  - 전체 시나리오 테스트
  - 버그 수정

**Week 2 종료 시 목표**:
✅ "FastAPI 엔드포인트 추가해줘" → 자동으로 파일 생성 + 커밋 완료

---

### **Week 3-4: Phase 2 - 고급 기능**

#### Week 3
- [ ] Day 1-2: 에러 자동 수정
  - Traceback 파싱
  - 에러 유형별 수정 로직
  - 재시도 메커니즘
- [ ] Day 3-4: 코드 리뷰 기능
  - 코드 품질 분석
  - 리팩토링 제안
- [ ] Day 5: 템플릿 시스템
  - 주요 프레임워크 템플릿 (FastAPI, Streamlit)

#### Week 4
- [ ] Day 1-2: 외부 검색 강화
  - Tavily API 통합
  - GitHub Code Search
- [ ] Day 3-4: 성능 최적화
  - LLM 호출 최소화
  - 캐싱 전략
- [ ] Day 5: 통합 테스트 및 문서화

**Week 4 종료 시 목표**:
✅ 복잡한 기능 구현 + 에러 자동 수정 + 코드 리뷰

---

### **Week 5: Phase 3 - 편의 기능**

- [ ] Day 1-2: 커맨드 팔레트
- [ ] Day 3: 설정 파일 시스템
- [ ] Day 4-5: 히스토리 검색 및 UI 개선

**Week 5 종료 시 목표**:
✅ 사용자 경험 대폭 개선

---

### **Week 6-8: Phase 4 - 고도화 (선택적)**

- Week 6: Docker 샌드박스
- Week 7: 백그라운드 작업 큐
- Week 8: 플러그인 시스템 + 멀티 에이전트

---

## 🔧 기술 스택 상세

### Core
```yaml
Framework:
  - DeepAgent: 에이전트 프레임워크
  - LangGraph: 복잡한 워크플로우 관리
  - Chainlit: UI

LLM:
  - Claude 3.5 Sonnet: 메인 모델 (복잡한 작업)
  - GPT-4 Turbo: 대안
  - Groq Mixtral: 빠른 응답용
  - DeepInfra Llama: 비용 절감용

Storage:
  - ChromaDB: 벡터 저장소 (RAG)
  - SQLite: 대화 히스토리
```

### Tools
```yaml
File Operations:
  - pathlib: 파일 경로 관리
  - aiofiles: 비동기 파일 I/O
  - difflib: diff 생성

Code Analysis:
  - tree-sitter: AST 파싱
  - ruff: Linting
  - black: 포맷팅
  - pytest: 테스트

Git:
  - GitPython: Git 조작

Search:
  - Tavily API: 웹 검색
  - DuckDuckGo (현재): 무료 대안

Execution:
  - Docker SDK: 컨테이너 관리
  - subprocess: 로컬 실행

Background:
  - Celery (선택): 작업 큐
  - Temporal (선택): 워크플로우 엔진
```

---

## 📊 성공 지표 (KPI)

### MVP (Week 2)
- [ ] 파일 생성/수정 성공률 > 95%
- [ ] Git 커밋 자동화 작동
- [ ] 단순 작업 (함수 추가) 완료 시간 < 2분
- [ ] 에러 발생률 < 10%

### Phase 2 (Week 4)
- [ ] 복잡한 작업 (API 엔드포인트 추가) 성공률 > 80%
- [ ] 에러 자동 수정률 > 60%
- [ ] 코드 리뷰 정확도 > 85%
- [ ] 평균 응답 시간 < 30초

### Phase 3 (Week 5)
- [ ] 사용자 만족도 (1-10) > 8
- [ ] 일일 활성 사용 횟수 > 10
- [ ] 커맨드 팔레트 사용률 > 50%

### Phase 4 (Week 8)
- [ ] 백그라운드 작업 완료율 > 90%
- [ ] 플러그인 시스템 사용 > 3개 이상
- [ ] 멀티 에이전트 효율성 > 단일 에이전트 대비 1.5배

---

## ⚠️ 리스크 및 대응 방안

### Risk 1: LLM 환각 (Hallucination)
**문제**: 존재하지 않는 파일/함수를 참조
**대응**:
- ✅ 파일 존재 여부 항상 확인
- ✅ 코드 실행 전 검증 단계 추가
- ✅ 사용자 확인 프롬프트 (중요 작업)

### Risk 2: 성능 저하
**문제**: LLM 호출이 너무 많아서 느림
**대응**:
- ✅ 캐싱 (동일 파일 재요청 시)
- ✅ 병렬 처리 (독립적 작업)
- ✅ 빠른 모델 사용 (단순 작업은 Groq)

### Risk 3: 보안
**문제**: 임의 코드 실행 위험
**대응**:
- ✅ Docker 샌드박스 (Phase 4)
- ✅ 파일 시스템 제한
- ✅ 위험 명령어 블랙리스트

### Risk 4: 복잡도
**문제**: 너무 많은 기능으로 관리 어려움
**대응**:
- ✅ 단계별 구현 (Phase 분리)
- ✅ MVP 먼저 완성
- ✅ 모듈화된 구조

### Risk 5: 비용
**문제**: LLM API 호출 비용 증가
**대응**:
- ✅ 토큰 사용량 모니터링
- ✅ 저렴한 모델 활용 (DeepInfra)
- ✅ 프롬프트 최적화

---

## 🎯 우선순위 결정 원칙

### 높음 (Must Have) - Week 1-2
1. 파일 쓰기/수정
2. Git 커밋
3. 기본 계획 시스템
4. 코드 실행 및 테스트

### 중간 (Should Have) - Week 3-4
1. 에러 자동 수정
2. 코드 리뷰
3. 템플릿 시스템
4. 외부 검색 강화

### 낮음 (Nice to Have) - Week 5-8
1. Docker 샌드박스
2. 백그라운드 작업
3. 플러그인 시스템
4. 멀티 에이전트

---

## 💡 구현 팁

### 1. 도구 설계 원칙
```python
# ✅ 좋은 도구: 명확하고 단일 책임
@tool
async def write_file(path: str, content: str) -> dict:
    """파일 쓰기 - 한 가지만 잘함"""

# ❌ 나쁜 도구: 너무 많은 기능
@tool
async def handle_file(action: str, path: str, **kwargs):
    """파일 처리 - 뭘 하는지 불명확"""
```

### 2. 에러 처리
```python
# ✅ 명확한 에러 메시지
try:
    result = await write_file(path, content)
except FileNotFoundError:
    return "❌ 파일을 찾을 수 없습니다: {path}\n힌트: 디렉토리를 먼저 생성하세요."

# ❌ 모호한 에러
except Exception as e:
    return f"오류: {e}"
```

### 3. 프롬프트 최적화
```python
# ✅ 구조화된 프롬프트
SYSTEM_PROMPT = """
당신은 전문 코딩 어시스턴트입니다.

작업 순서:
1. 요구사항 분석
2. 계획 수립 (TODO 리스트)
3. 단계별 실행
4. 검증
5. 완료 보고

규칙:
- 항상 파일 존재 여부 확인
- 변경 전 백업 생성
- 테스트 실행 필수
"""

# ❌ 모호한 프롬프트
SYSTEM_PROMPT = "코드를 작성해주세요"
```

### 4. 테스트
```python
# 각 도구마다 유닛 테스트 작성
async def test_write_file():
    result = await write_file("/tmp/test.py", "print('hello')")
    assert result["success"]
    assert os.path.exists("/tmp/test.py")
```

---

## 📚 참고 자료

### DeepAgent
- 공식 문서: [DeepAgent Docs]
- 예제: [DeepAgent Examples]

### LangGraph
- 공식 문서: https://langchain-ai.github.io/langgraph/
- 멀티 에이전트 패턴

### Chainlit
- 공식 문서: https://docs.chainlit.io/
- UI 커스터마이징

### 유사 프로젝트
- Aider: https://github.com/paul-gauthier/aider
- GitHub Copilot Workspace
- Cursor IDE

---

## 🚦 시작하기

### Step 1: Phase 1 시작
```bash
# 브랜치 생성
git checkout -b feature/file-operations

# 첫 번째 도구 구현
touch tools/file_operations.py
```

### Step 2: 점진적 개선
- MVP 먼저 완성
- 사용하면서 피드백 수집
- 필요한 기능부터 추가

### Step 3: 지속적 테스트
- 매일 실제 작업에 사용
- 문제점 기록
- 빠르게 수정

---

## 📝 체크리스트

### Week 1
- [ ] `write_file` 도구 구현
- [ ] `edit_file` 도구 구현
- [ ] 백업 시스템 구현
- [ ] diff 생성 기능
- [ ] `git_commit` 구현
- [ ] `git_status` 구현

### Week 2
- [ ] `TaskPlanner` 클래스
- [ ] pytest 자동 실행
- [ ] DeepAgent 통합
- [ ] MVP 통합 테스트
- [ ] 문서 업데이트

---

## 🎉 결론

이 계획은 **실용적이고 단계적**입니다:

1. **Week 1-2**: 파일 쓰기 + Git → 바로 사용 가능!
2. **Week 3-4**: 에러 수정 + 리뷰 → 더 스마트해짐
3. **Week 5+**: 편의 기능 → 생산성 극대화

**핵심**: MVP부터 완성하고, 사용하면서 개선하기!

---

**다음 액션**: `tools/file_operations.py` 구현부터 시작! 🚀
