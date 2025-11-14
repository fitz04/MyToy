# Phase 2 완료 문서

**상태**: ✅ 완료
**날짜**: 2025-11-14
**진행도**: 95%

## 개요

Phase 2는 코드 품질 자동화 도구들을 구현하는 단계입니다. 이번 단계에서는 테스트, 린팅, 코드 리뷰, 프로젝트 생성 등의 기능을 모두 구현했습니다.

## 구현된 기능

### 1. 자동 에러 수정 (AutoErrorFixer) ✅

**파일**: `agents/error_fixer.py`

LLM을 활용하여 Python 코드의 에러를 자동으로 분석하고 수정합니다.

**주요 기능**:
- 에러 타입 분류 (ImportError, NameError, SyntaxError, TypeError 등)
- LLM 기반 에러 분석 및 수정
- 자동 수정 적용 및 검증
- 수정 이력 추적

**사용 예시**:
```python
from agents import AutoErrorFixer
from llm.manager import LLMManager

llm_manager = LLMManager()
fixer = AutoErrorFixer(llm_manager)

# 에러 자동 수정
result = await fixer.auto_fix(
    file_path="buggy_code.py",
    error_message="NameError: name 'undefined_var' is not defined",
    max_attempts=3
)

if result["success"]:
    print(f"수정 완료: {result['fixed_code']}")
```

**핵심 메서드**:
- `auto_fix()`: 에러를 자동으로 수정
- `analyze_error()`: 에러를 분석하고 수정 제안 생성
- `apply_fix()`: 수정 사항을 파일에 적용

---

### 2. pytest 통합 (TestRunner) ✅

**파일**: `tools/test_runner.py`

pytest를 통합하여 자동화된 테스트 실행 및 결과 분석을 제공합니다.

**주요 기능**:
- pytest 실행 및 출력 파싱
- 테스트 결과 구조화 (성공/실패/에러/스킵)
- 실패한 테스트 자동 수정 (AutoErrorFixer 연동)
- 커버리지 측정 지원
- 마커 기반 선택적 테스트 실행

**사용 예시**:
```python
from tools import TestRunner, run_tests

runner = TestRunner()

# 기본 테스트 실행
summary = await runner.run_tests(
    test_path="tests/",
    verbose=True,
    markers=["unit"]  # unit 테스트만 실행
)

print(f"통과: {summary.passed}, 실패: {summary.failed}")

# 자동 수정과 함께 실행
from agents import AutoErrorFixer

result = await runner.run_with_auto_fix(
    test_path="tests/test_api.py",
    error_fixer=AutoErrorFixer(llm_manager),
    max_retries=2
)

if result["all_passed"]:
    print("모든 테스트 통과!")
```

**TestResult 구조**:
```python
@dataclass
class TestResult:
    test_name: str           # 테스트 이름
    file_path: str           # 파일 경로
    status: TestStatus       # PASSED, FAILED, ERROR, SKIPPED
    duration: float          # 실행 시간
    error_message: str       # 에러 메시지 (실패 시)
    traceback: str           # 전체 traceback
    line_number: int         # 에러 발생 라인
```

**TestSummary 구조**:
```python
@dataclass
class TestSummary:
    total: int               # 전체 테스트 수
    passed: int              # 통과
    failed: int              # 실패
    error: int               # 에러
    skipped: int             # 스킵
    duration: float          # 총 실행 시간
    coverage: float          # 커버리지 (있는 경우)
    results: List[TestResult]
```

---

### 3. 린터/포매터 통합 (CodeQuality) ✅

**파일**: `tools/code_quality.py`

black, flake8, pylint, isort를 통합하여 코드 품질 검사 및 자동 수정을 제공합니다.

**주요 기능**:
- **black**: 코드 포매팅
- **flake8**: 스타일 가이드 검사
- **pylint**: 심층 정적 분석
- **isort**: import 문 정렬
- 종합 품질 검사 (check_all)
- 자동 수정 (auto_fix)

**사용 예시**:
```python
from tools import CodeQuality, check_quality

quality = CodeQuality()

# 1. 코드 포매팅
result = await quality.format_code(
    file_path="messy_code.py",
    line_length=88
)

# 2. 린팅 검사
report = await quality.lint_code(
    file_path="my_module.py",
    max_line_length=88
)

for issue in report.issues:
    print(f"{issue.file_path}:{issue.line_number} - {issue.message}")

# 3. 자동 수정 (isort + black)
fix_result = await quality.auto_fix(
    file_path="my_module.py",
    format_code=True,
    fix_imports=True
)

# 4. 종합 품질 검사
check = await quality.check_all(
    file_path="my_module.py",
    auto_fix=True  # 자동으로 수정도 수행
)

print(f"Flake8: {len(check['flake8']['issues'])} 이슈")
print(f"Pylint 점수: {check['pylint']['score']}/10")
```

**QualityReport 구조**:
```python
@dataclass
class QualityReport:
    file_path: str
    tool: str                # black, flake8, pylint
    issues: List[CodeIssue]
    summary: str
    score: float             # 0-10 (pylint만)

@dataclass
class CodeIssue:
    file_path: str
    line_number: int
    level: IssueLevel        # ERROR, WARNING, INFO
    code: str                # E501, W503 등
    message: str
    tool: str
```

**편의 함수**:
```python
# 빠른 품질 검사
report = await check_quality(file_path="module.py")
```

---

### 4. 코드 리뷰 시스템 (CodeReviewer) ✅

**파일**: `agents/code_reviewer.py`

LLM을 활용하여 전문적인 코드 리뷰를 자동으로 수행합니다.

**주요 기능**:
- 보안, 성능, 가독성, 유지보수성 종합 리뷰
- 0-10점 코드 품질 평가
- 심각도별 코멘트 (CRITICAL, MAJOR, MINOR, SUGGESTION)
- 변경사항(diff) 리뷰
- 특정 측면 개선 제안

**사용 예시**:
```python
from agents import CodeReviewer, review_file
from llm.manager import LLMManager

llm_manager = LLMManager()
reviewer = CodeReviewer(llm_manager)

# 1. 전체 코드 리뷰
review = await reviewer.review_code(
    file_path="my_api.py",
    focus=["security", "performance"]  # 집중 검토 항목
)

print(f"점수: {review.overall_score}/10")
print(f"요약: {review.summary}")

for strength in review.strengths:
    print(f"✅ {strength}")

for weakness in review.weaknesses:
    print(f"⚠️ {weakness}")

# 상세 코멘트
for comment in review.comments:
    print(f"\n[{comment.level.value.upper()}] Line {comment.line_number}")
    print(f"이슈: {comment.issue}")
    print(f"제안: {comment.suggestion}")
    print(f"이유: {comment.reason}")

# 2. 변경사항 리뷰
diff_review = await reviewer.review_diff(
    old_code=old_version,
    new_code=new_version,
    file_path="updated_file.py"
)

print(diff_review["review"])

# 3. 개선 제안
suggestions = await reviewer.suggest_improvements(
    code=my_code,
    aspect="performance"  # performance, readability, security, all
)

for suggestion in suggestions:
    print(f"\n개선: {suggestion['title']}")
    print(f"현재: {suggestion['current']}")
    print(f"개선: {suggestion['improved']}")
    print(f"효과: {suggestion['benefit']}")
```

**CodeReview 구조**:
```python
@dataclass
class CodeReview:
    file_path: str
    overall_score: float              # 0-10
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    comments: List[ReviewComment]
    refactoring_suggestions: List[str]

@dataclass
class ReviewComment:
    level: ReviewLevel               # CRITICAL, MAJOR, MINOR, SUGGESTION
    line_number: int
    code_snippet: str
    issue: str
    suggestion: str
    reason: str
```

**편의 함수**:
```python
# 빠른 파일 리뷰
review = await review_file("my_module.py", llm_manager)

# 빠른 코드 리뷰 (요약만)
summary = await quick_review(code_string, llm_manager)
```

---

### 5. 프로젝트 템플릿 (ProjectTemplates) ✅

**파일**: `tools/project_templates.py`

다양한 프로젝트 템플릿을 통해 새 프로젝트를 빠르게 생성합니다.

**지원 템플릿**:
1. **FastAPI**: REST API 프로젝트
2. **Flask**: 웹 애플리케이션
3. **CLI**: 커맨드라인 도구 (typer)
4. **Library**: Python 라이브러리 패키지

**사용 예시**:
```python
from tools import ProjectTemplates, create_project

templates = ProjectTemplates()

# 사용 가능한 템플릿 목록
template_list = templates.list_templates()
for t in template_list:
    print(f"{t['name']}: {t['description']}")

# FastAPI 프로젝트 생성
result = await templates.create_project(
    template_name="fastapi",
    project_name="MyAPI",
    output_dir="./projects"
)

print(f"생성됨: {result['project_path']}")
print(f"파일 수: {result['files_created']}")

# 편의 함수 사용
result = await create_project(
    template="cli",
    name="MyCLI",
    output="."
)
```

#### FastAPI 템플릿

완전한 REST API 구조:

```
MyAPI/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱
│   ├── routers/
│   │   ├── __init__.py
│   │   └── items.py         # CRUD 라우터
│   └── models/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_main.py         # TestClient 기반 테스트
├── requirements.txt
├── README.md
└── .gitignore
```

**포함 기능**:
- FastAPI 앱 설정 (제목, 버전, 문서)
- CRUD 라우터 예시 (GET, POST, PUT, DELETE)
- Pydantic 모델
- 헬스 체크 엔드포인트
- 테스트 코드

**실행**:
```bash
cd MyAPI
pip install -r requirements.txt
uvicorn app.main:app --reload
# http://localhost:8000/docs
```

#### Flask 템플릿

웹 애플리케이션 구조 (Application Factory 패턴):

```
MyFlaskApp/
├── app/
│   ├── __init__.py          # 앱 팩토리
│   ├── routes/
│   │   ├── __init__.py
│   │   └── main.py          # Blueprint
│   └── templates/
│       └── index.html       # Jinja2 템플릿
├── tests/
├── run.py                   # 개발 서버
├── requirements.txt
└── README.md
```

**실행**:
```bash
cd MyFlaskApp
pip install -r requirements.txt
python run.py
# http://localhost:5000
```

#### CLI 템플릿

Typer 기반 커맨드라인 도구:

```
MyCLI/
├── src/
│   └── mycli/
│       ├── __init__.py
│       └── cli.py           # Typer 앱
├── tests/
├── pyproject.toml           # 패키지 설정
└── README.md
```

**포함 기능**:
- 여러 커맨드 예시
- 옵션/인자 처리
- 헬프 메시지
- 진입점 설정

**실행**:
```bash
cd MyCLI
pip install -e .
mycli --help
mycli hello Alice
mycli process -i input.txt -o output.txt -v
```

#### Library 템플릿

재사용 가능한 라이브러리 패키지:

```
MyLibrary/
├── src/
│   └── mylibrary/
│       ├── __init__.py      # __all__ 정의
│       └── core.py          # 핵심 함수
├── tests/
│   └── test_core.py
├── docs/
├── pyproject.toml
└── README.md
```

**포함 기능**:
- src 레이아웃
- 테스트 코드
- pyproject.toml 설정
- 개발 의존성 (pytest, black, flake8)

**사용**:
```bash
cd MyLibrary
pip install -e .[dev]
pytest
black src/
```

---

## 통합 사용 예시

모든 도구를 함께 사용하는 워크플로우:

```python
from llm.manager import LLMManager
from agents import AutoErrorFixer, CodeReviewer
from tools import TestRunner, CodeQuality, ProjectTemplates

# 초기화
llm_manager = LLMManager()
fixer = AutoErrorFixer(llm_manager)
reviewer = CodeReviewer(llm_manager)
test_runner = TestRunner()
quality = CodeQuality()
templates = ProjectTemplates()

# 1. 새 프로젝트 생성
project = await templates.create_project(
    template_name="fastapi",
    project_name="MyAPI",
    output_dir="."
)

# 2. 코드 품질 검사
await quality.auto_fix(
    file_path="MyAPI/app/main.py",
    format_code=True,
    fix_imports=True
)

# 3. 코드 리뷰
review = await reviewer.review_code(
    file_path="MyAPI/app/main.py"
)

if review.overall_score < 7:
    print("⚠️ 코드 개선 필요")
    for comment in review.comments:
        if comment.level == ReviewLevel.CRITICAL:
            print(f"치명적: {comment.issue}")

# 4. 테스트 실행 (자동 수정 포함)
test_result = await test_runner.run_with_auto_fix(
    test_path="MyAPI/tests",
    error_fixer=fixer,
    max_retries=2
)

if test_result["all_passed"]:
    print("✅ 모든 테스트 통과!")
else:
    print(f"❌ {test_result['remaining_failures']}개 테스트 실패")

# 5. 최종 품질 체크
final_check = await quality.check_all(
    file_path="MyAPI/app/main.py",
    auto_fix=False
)

print(f"Pylint 점수: {final_check['pylint']['score']}/10")
```

---

## 의존성 관리

Phase 2 기능들은 선택적 의존성을 사용합니다:

### 코어 의존성 (필수)
```bash
pip install -r requirements-core.txt
```

- AutoErrorFixer ✅
- 기본 LLM 기능 ✅

### UI 의존성
```bash
pip install -r requirements-ui.txt
```

- Chainlit 웹 인터페이스
- 코어 기능 포함

### 전체 의존성
```bash
pip install -r requirements-full.txt
```

- TestRunner: `pytest`, `pytest-cov`
- CodeQuality: `black`, `flake8`, `pylint`, `isort`
- CodeReviewer: LLM 기반 (코어에 포함)
- ProjectTemplates: 외부 의존성 없음

**도구별 설치**:
```bash
# 테스트 도구
pip install pytest pytest-cov

# 코드 품질 도구
pip install black flake8 pylint isort

# 템플릿 생성용 도구 (프로젝트별 요구사항)
pip install fastapi uvicorn  # FastAPI 프로젝트용
pip install flask            # Flask 프로젝트용
pip install typer            # CLI 프로젝트용
```

---

## 모범 사례

### 1. 개발 워크플로우

```bash
# 1. 코드 작성 후
python -m black my_module.py
python -m isort my_module.py

# 2. 품질 검사
python -m flake8 my_module.py
python -m pylint my_module.py

# 3. 테스트
pytest tests/ -v

# 4. 커버리지
pytest --cov=my_module tests/
```

### 2. CI/CD 통합

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: |
          pip install -r requirements-full.txt
      - name: Format check
        run: black --check .
      - name: Lint
        run: flake8 .
      - name: Tests
        run: pytest --cov=.
```

### 3. pre-commit 훅

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.0.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

---

## 다음 단계 (Phase 3)

Phase 2가 완료되었으므로 다음 단계로 진행할 수 있습니다:

### 우선순위 1: RAG 시스템
- Codebase indexing
- Semantic search
- Context-aware generation

### 우선순위 2: 웹 검색
- DuckDuckGo 통합
- StackOverflow 검색
- 문서 크롤링

### 우선순위 3: 고급 에이전트
- Multi-agent collaboration
- Tool chaining
- Self-improvement loop

---

## 문제 해결

### pytest를 찾을 수 없음
```bash
pip install pytest pytest-cov
```

### black/flake8를 찾을 수 없음
```bash
pip install black flake8 pylint isort
```

### 테스트 자동 수정이 작동하지 않음
- LLM API 키 확인 (.env 파일)
- AutoErrorFixer가 제대로 초기화되었는지 확인
- max_retries를 2-3으로 설정

### 코드 리뷰가 느림
- 큰 파일은 분할해서 리뷰
- focus 파라미터로 특정 측면만 검토
- quick_review() 사용

---

## 요약

Phase 2에서 구현된 5가지 주요 기능:

1. ✅ **AutoErrorFixer**: LLM 기반 에러 자동 수정
2. ✅ **TestRunner**: pytest 통합 및 자동 재시도
3. ✅ **CodeQuality**: black, flake8, pylint, isort 통합
4. ✅ **CodeReviewer**: LLM 기반 전문 코드 리뷰
5. ✅ **ProjectTemplates**: FastAPI, Flask, CLI, Library 템플릿

**진행도**: 95% (Phase 3 시작 준비 완료)

**다음**: 수동 테스트 수행 또는 Phase 3 개발 시작
