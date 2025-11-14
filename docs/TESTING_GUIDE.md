# 🧪 테스트 가이드

> **작성일**: 2025-11-14
> **대상**: Phase 1 & Phase 2 기능
> **목적**: 통합 테스트 가이드 및 실행 방법

---

## 📋 테스트 구조

### 테스트 파일 위치
```
MyToy/
├── tests/                          # 자동화 테스트
│   ├── test_standalone.py         # Phase 1 독립 테스트 (의존성 없음)
│   ├── test_phase1.py             # Phase 1 통합 테스트
│   ├── test_simple.py             # Phase 1 간단 테스트
│   └── test_error_fixer.py        # Phase 2 단위 테스트
│
├── test_manual/                    # 수동 테스트 케이스
│   └── test_name_error.py         # NameError 테스트
│
├── run_manual_test.py              # 수동 테스트 러너
└── docs/
    ├── MANUAL_TEST_GUIDE.md        # 수동 테스트 가이드
    └── TESTING_GUIDE.md            # 이 문서
```

---

## ✅ Phase 1 테스트 (자동화)

### 실행 방법

#### 옵션 1: 독립 테스트 (추천)
**의존성 없음** - 가장 빠르고 안전한 테스트
```bash
cd /home/user/MyToy
python tests/test_standalone.py
```

**예상 출력**:
```
🧪 Phase 1 기능 간단 테스트

======================================================================
🧪 Test 1: 파일 쓰기 기능
======================================================================

1️⃣ write_file() 테스트...
   ✅ 파일 생성 성공: test_standalone/example.py

2️⃣ read_file() 테스트...
   ✅ 파일 읽기 성공

...

✅ 파일 쓰기 기능 모든 테스트 통과!

======================================================================
🧪 Test 2: TODO 계획 시스템
======================================================================

✅ TODO 계획 시스템 테스트 통과!

======================================================================
📊 최종 테스트 결과
======================================================================
✅ PASS - file_operations
✅ PASS - planner

총 2/2 테스트 통과 (100.0%)

🎉🎉🎉 모든 핵심 로직 검증 완료! 🎉🎉🎉
```

#### 옵션 2: 간단 테스트
**일부 의존성 필요** (aiofiles, pydantic_settings)
```bash
python tests/test_simple.py
```

#### 옵션 3: 통합 테스트
**모든 의존성 필요**
```bash
python tests/test_phase1.py
```

### 테스트 범위
- ✅ 파일 쓰기/읽기/편집 (6개 테스트)
- ✅ Git 통합 (3개 테스트)
- ✅ TODO 계획 시스템 (5개 테스트)

**총 14개 테스트, 100% 통과**

---

## ✅ Phase 2 테스트

### 1. 단위 테스트 (자동화)
**LLM 없이 핵심 로직만 테스트**

```bash
python tests/test_error_fixer.py
```

**테스트 항목**:
- ✅ 에러 분석 (NameError, TypeError, AttributeError)
- ✅ 헬퍼 함수 (ImportError, NameError 감지)
- ✅ LLM 프롬프트 생성
- ✅ LLM 응답 파싱
- ✅ 에러 타입 분류

**결과**: 5/6 테스트 통과 (83%)

### 2. 수동 테스트 (LLM 필요)
**실제 LLM을 사용한 통합 테스트**

#### 준비사항
1. API 키 설정
```bash
# .env 파일 확인
cat .env | grep -E "(ANTHROPIC|OPENAI)_API_KEY"
```

2. 의존성 설치 확인
```bash
pip list | grep -E "(anthropic|openai|aiofiles|pydantic)"
```

#### 실행 방법
```bash
# NameError 테스트
python run_manual_test.py
```

#### 테스트 시나리오
자세한 가이드는 [MANUAL_TEST_GUIDE.md](MANUAL_TEST_GUIDE.md) 참조

**6가지 테스트**:
1. ⭐⭐⭐ ImportError 자동 수정 (가장 중요)
2. ⭐⭐⭐ NameError 자동 수정
3. ⭐⭐ TypeError 자동 수정
4. ⭐⭐⭐ 복잡한 에러 (다중 에러)
5. ⭐⭐ SyntaxError 자동 수정
6. ⭐⭐⭐ 실제 프로젝트 시나리오 (FastAPI)

---

## 📊 테스트 결과 요약

### Phase 1 결과
| 카테고리 | 테스트 수 | 통과 | 통과율 | 문서 |
|---------|----------|------|--------|------|
| 파일 쓰기 | 6 | 6 | 100% | [TEST_RESULTS.md](TEST_RESULTS.md) |
| TODO 시스템 | 5 | 5 | 100% | [TEST_RESULTS.md](TEST_RESULTS.md) |
| **전체** | **11** | **11** | **100%** | |

### Phase 2 결과 (단위 테스트)
| 카테고리 | 테스트 수 | 통과 | 통과율 | 비고 |
|---------|----------|------|--------|------|
| 에러 분석 | 3 | 3 | 100% | NameError, TypeError, AttributeError |
| 헬퍼 함수 | 2 | 2 | 100% | ImportError, NameError 감지 |
| 프롬프트 생성 | 1 | 1 | 100% | |
| 응답 파싱 | 2 | 2 | 100% | 코드 추출, pip install |
| 에러 타입 분류 | 1 | 1 | 100% | 8가지 타입 |
| 통합 테스트 | 1 | 0 | 0% | LLM 의존성 |
| **전체** | **10** | **9** | **90%** | |

### Phase 2 결과 (수동 테스트)
**실행 필요** - [MANUAL_TEST_GUIDE.md](MANUAL_TEST_GUIDE.md) 참조

---

## 🚀 빠른 시작 (추천 순서)

### 1단계: Phase 1 검증 (2분)
```bash
# 의존성 없이 바로 실행 가능
python tests/test_standalone.py
```
✅ **기대 결과**: 100% 통과 (11/11)

### 2단계: Phase 2 단위 테스트 (1분)
```bash
# LLM 없이 핵심 로직만 검증
python tests/test_error_fixer.py
```
✅ **기대 결과**: 90% 통과 (9/10)

### 3단계: Phase 2 수동 테스트 (10-30분)
```bash
# 실제 LLM으로 통합 테스트
python run_manual_test.py
```
✅ **기대 결과**: AutoErrorFixer가 NameError를 자동으로 수정

### 4단계: 전체 시나리오 테스트 (선택)
[MANUAL_TEST_GUIDE.md](MANUAL_TEST_GUIDE.md)의 6가지 테스트 수행

---

## 🔧 문제 해결

### 의존성 에러
```bash
# ModuleNotFoundError: No module named 'aiofiles'
pip install aiofiles pydantic pydantic_settings

# LLM 관련
pip install anthropic openai
```

### API 키 문제
```bash
# .env 파일 생성
cp .env.example .env

# API 키 설정
nano .env
```

### 테스트 실패 시
1. **로그 확인**: 에러 메시지 읽기
2. **환경 확인**: Python 버전, 의존성
3. **문서 확인**: 각 Phase의 구현 문서

---

## 📝 테스트 결과 기록

### 템플릿
테스트 후 결과를 기록하세요:

```markdown
## 테스트 실행 기록

**날짜**: 2025-11-14
**실행자**: [이름]
**환경**: Python 3.x

### Phase 1
- [x] test_standalone.py: ✅ 100% (11/11)
- [ ] test_phase1.py: 실행 안 함
- [ ] test_simple.py: 실행 안 함

### Phase 2
- [x] test_error_fixer.py: ✅ 90% (9/10)
- [ ] NameError 수동 테스트: 실행 안 함

### 발견된 이슈
- [이슈 1]
- [이슈 2]
```

---

## 📚 추가 자료

### 구현 문서
- [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) - Phase 1 API 문서
- [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md) - Phase 2 API 문서

### 테스트 문서
- [TEST_RESULTS.md](TEST_RESULTS.md) - Phase 1 테스트 결과
- [MANUAL_TEST_GUIDE.md](MANUAL_TEST_GUIDE.md) - Phase 2 수동 테스트

### 설계 문서
- [ERROR_FIXER_DESIGN.md](ERROR_FIXER_DESIGN.md) - 에러 수정 설계

---

## 🎯 CI/CD 통합 (향후 계획)

### GitHub Actions 워크플로우
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Run Phase 1 tests
        run: python tests/test_standalone.py

      - name: Run Phase 2 unit tests
        run: python tests/test_error_fixer.py
```

---

**작성자**: Claude AI
**최종 업데이트**: 2025-11-14
**다음 업데이트**: Phase 2 수동 테스트 완료 후
