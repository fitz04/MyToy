# 📚 프로젝트 문서 디렉토리

> **프로젝트**: AI Coding Assistant - DeepAgent + Chainlit
> **최종 업데이트**: 2025-11-14

---

## 📖 문서 읽기 순서 (권장)

### 1️⃣ 시작하기
처음 프로젝트를 이해하고 싶다면 이 순서로 읽으세요:

1. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - 설치 및 환경 설정
2. **[README.md](../README.md)** - 프로젝트 개요 (루트)
3. **[EXAMPLES.md](EXAMPLES.md)** - 사용 예제
4. **[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)** - 전체 개발 계획 (8주)

### 2️⃣ 개발 진행 상황
현재 어디까지 개발되었는지 확인하려면:

1. **[CURRENT_STATUS.md](../CURRENT_STATUS.md)** - 현재 구현 상태 (루트)
2. **[Phase 1 구현 문서](#phase-1-문서)** - 파일 쓰기, Git, TODO 시스템
3. **[Phase 2 구현 문서](#phase-2-문서)** - 에러 자동 수정

### 3️⃣ 실제 사용하기
기능을 테스트하고 사용하려면:

1. **[MANUAL_TEST_GUIDE.md](MANUAL_TEST_GUIDE.md)** - 수동 테스트 가이드
2. **[테스트 결과 문서](#테스트-문서)** - 자동 테스트 결과

---

## 📁 문서 분류

### 📘 설계 및 계획 문서

| 문서 | 설명 | 작성일 | 상태 |
|------|------|--------|------|
| [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) | 8주 개발 계획 | 2025-11-14 | ✅ 완료 |
| [ERROR_FIXER_DESIGN.md](ERROR_FIXER_DESIGN.md) | 에러 자동 수정 설계 | 2025-11-14 | ✅ 완료 |

### 📗 구현 문서 (시간순)

#### Phase 1 문서
| 문서 | 설명 | 작성일 | 버전 |
|------|------|--------|------|
| [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) | Phase 1 구현 완전 가이드<br>- 파일 쓰기 도구<br>- Git 통합<br>- TODO 계획 시스템 | 2025-11-14 | v0.1.0 |

**구현 기능**:
- ✅ 파일 쓰기/편집 (write_file, edit_file, insert_code, delete_lines)
- ✅ Git 통합 (git_status, git_commit, smart_commit)
- ✅ TODO 계획 (Task, Plan, 의존성 관리)

#### Phase 2 문서
| 문서 | 설명 | 작성일 | 버전 |
|------|------|--------|------|
| [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md) | Phase 2 초기 구현 가이드<br>- 에러 자동 수정<br>- AutoErrorFixer 클래스 | 2025-11-14 | v0.2.0 |
| [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md) | **Phase 2 완료 문서** ⭐<br>- 모든 Phase 2 기능 통합<br>- 테스트, 린팅, 리뷰, 템플릿 | 2025-11-14 | v0.2.5 |

**구현 기능**:
- ✅ 에러 자동 수정 (AutoErrorFixer)
- ✅ pytest 통합 (TestRunner)
- ✅ 린터/포매터 통합 (CodeQuality: black, flake8, pylint, isort)
- ✅ 코드 리뷰 시스템 (CodeReviewer)
- ✅ 프로젝트 템플릿 (ProjectTemplates: FastAPI, Flask, CLI, Library)

### 📙 테스트 문서

| 문서 | 설명 | 작성일 | 테스트 대상 |
|------|------|--------|-------------|
| [TEST_RESULTS.md](TEST_RESULTS.md) | Phase 1 자동 테스트 결과<br>통과율: 100% (11/11) | 2025-11-14 | Phase 1 기능 |
| [MANUAL_TEST_GUIDE.md](MANUAL_TEST_GUIDE.md) | Phase 2 수동 테스트 가이드<br>6가지 테스트 시나리오 | 2025-11-14 | Phase 2 기능 |

### 📕 사용자 가이드

| 문서 | 설명 | 대상 |
|------|------|------|
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | 설치 및 환경 설정 | 초보자 |
| [EXAMPLES.md](EXAMPLES.md) | 사용 예제 모음 | 모든 사용자 |

---

## 🔍 주제별 문서 찾기

### 파일 작업 (쓰기/편집)
- **구현 문서**: [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) > "1. 파일 쓰기 도구"
- **API 문서**: [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) > "API 문서"
- **사용 예시**: [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) > "사용 예시"
- **소스 코드**: `../tools/file_operations.py`

### Git 통합
- **구현 문서**: [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) > "2. Git 통합"
- **API 문서**: [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) > "API 문서"
- **소스 코드**: `../tools/git_operations.py`

### TODO 계획 시스템
- **구현 문서**: [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) > "3. TODO 계획 시스템"
- **API 문서**: [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) > "API 문서"
- **소스 코드**: `../agents/planner.py`

### 에러 자동 수정
- **설계 문서**: [ERROR_FIXER_DESIGN.md](ERROR_FIXER_DESIGN.md)
- **구현 문서**: [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md)
- **테스트 가이드**: [MANUAL_TEST_GUIDE.md](MANUAL_TEST_GUIDE.md)
- **소스 코드**: `../agents/error_fixer.py`

---

## 📊 문서 통계

### 전체 문서 현황
- **설계 문서**: 2개
- **구현 문서**: 3개 (Phase 1, Phase 2 초기, Phase 2 완료)
- **테스트 문서**: 3개
- **사용자 가이드**: 2개
- **총 문서**: 10개

### 코드 라인 수 (구현 문서 기준)
- **Phase 1**: ~1,200 lines (3개 모듈)
- **Phase 2**: ~2,200 lines (5개 모듈)
  - AutoErrorFixer: ~520 lines
  - TestRunner: ~480 lines
  - CodeQuality: ~430 lines
  - CodeReviewer: ~440 lines
  - ProjectTemplates: ~550 lines
- **테스트**: ~800 lines (4개 파일)

### 문서 작성 날짜
- **2025-11-14**: 모든 Phase 1, Phase 2 문서 작성

---

## 🎯 다음 문서

### 계획 중
- [ ] **PHASE2_MANUAL_TEST_RESULTS.md** - Phase 2 전체 기능 수동 테스트 결과
- [ ] **PHASE3_IMPLEMENTATION.md** - Phase 3 구현 문서 (RAG, 웹 검색 등)
- [ ] **API_REFERENCE.md** - 전체 API 레퍼런스
- [ ] **TROUBLESHOOTING.md** - 문제 해결 가이드

### 최근 완료
- [x] **PHASE2_COMPLETE.md** - Phase 2 완료 문서 (2025-11-14)
- [x] **REQUIREMENTS.md** - 의존성 관리 가이드 (2025-11-14)

---

## 📝 문서 기여 가이드

### 문서 작성 규칙
1. **파일명**: 대문자 + 언더스코어 (예: `PHASE1_IMPLEMENTATION.md`)
2. **헤더**: 이모지 + 제목 (예: `# 🛠️ Phase 1 구현`)
3. **날짜 표시**: `> **작성일**: 2025-11-14`
4. **버전 표시**: `> **버전**: v0.1.0`

### 문서 템플릿
```markdown
# 🔧 [문서 제목]

> **작성일**: YYYY-MM-DD
> **버전**: vX.Y.Z
> **상태**: ✅ 완료 / 🟡 작성 중 / 🔴 계획

## 📋 목차
1. [개요](#개요)
2. [구현된 기능](#구현된-기능)
...

## 개요
[문서 내용]
```

---

## 🔗 외부 링크

### 프로젝트 리소스
- **GitHub**: [fitz04/MyToy](https://github.com/fitz04/MyToy)
- **프로젝트 루트**: [../](../)
- **소스 코드**: [../agents/](../agents/), [../tools/](../tools/)

### 참고 자료
- **DeepAgent**: [공식 문서]
- **Chainlit**: [공식 문서]
- **LangChain**: [공식 문서]

---

**문서 관리자**: Claude AI
**마지막 업데이트**: 2025-11-14
**문의**: 프로젝트 이슈 트래커
