# 🧪 Phase 2 수동 테스트 가이드

> **작성일**: 2025-11-14
> **대상**: 에러 자동 수정 기능 (AutoErrorFixer)
> **목적**: 실제 LLM을 사용한 통합 테스트 및 검증

---

## 📋 테스트 준비

### 1. 환경 설정 확인
```bash
# API 키 확인
cat .env | grep -E "(ANTHROPIC|OPENAI)_API_KEY"

# 의존성 확인
pip list | grep -E "(anthropic|openai)"
```

### 2. 테스트 디렉토리 생성
```bash
mkdir -p test_manual
cd test_manual
```

---

## ✅ 테스트 체크리스트

### Test 1: ImportError 자동 수정 ⭐⭐⭐
**난이도**: ★☆☆
**예상 시간**: 3-5분
**중요도**: 매우 높음

#### 테스트 시나리오
```python
# test_manual/test_import_error.py
import pandas as pd

df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print(df)
print("Success!")
```

#### 실행 방법
```bash
# 1. 테스트 스크립트 작성
cat > test_manual/test_import_error.py << 'EOF'
import pandas as pd

df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print(df)
print("Success!")
EOF

# 2. Python REPL에서 AutoErrorFixer 실행
python3 << 'PYTHON'
import asyncio
from agents import AutoErrorFixer
from llm import LLMManager
from tools import FileOperations

async def test():
    llm = LLMManager()
    file_ops = FileOperations()
    fixer = AutoErrorFixer(llm, file_ops, max_retries=3)

    code = open("test_manual/test_import_error.py").read()

    try:
        exec(code)
    except ImportError as e:
        print(f"❌ 에러 발생: {e}")
        print("\n🔧 자동 수정 시작...\n")

        result = await fixer.auto_fix(
            error=e,
            code=code,
            file_path="test_manual/test_import_error.py"
        )

        print(f"\n{'='*60}")
        print(f"테스트 결과: {'✅ 성공' if result['success'] else '❌ 실패'}")
        print(f"{'='*60}")

        if result['success']:
            print(f"✅ 시도 횟수: {result['attempts']}")
            print(f"✅ 설치된 패키지: {result['packages_installed']}")
            print(f"\n원인: {result['cause'][:100]}...")
            print(f"방법: {result['method'][:100]}...")

asyncio.run(test())
PYTHON
```

#### 검증 항목
- [ ] 에러가 정확하게 분석되었는가? (ModuleNotFoundError: pandas)
- [ ] LLM이 적절한 수정 방법을 제안했는가? (pip install pandas)
- [ ] 패키지가 자동으로 설치되었는가?
- [ ] 수정된 코드가 정상 실행되는가?
- [ ] 백업 파일이 생성되었는가?

#### 예상 출력
```
🔧 에러 자동 수정 시작
📄 파일: test_manual/test_import_error.py
❌ 에러: ModuleNotFoundError: No module named 'pandas'

============================================================
🔄 수정 시도 1/3
============================================================

1️⃣ 에러 분석 중...
   📍 에러 타입: ModuleNotFoundError
   📝 메시지: No module named 'pandas'

2️⃣ 수정 방법 생성 중...
   💡 원인: pandas 패키지가 설치되지 않았습니다.
   🔧 방법: pip install pandas를 실행하세요.

3️⃣ 수정 적용 중...
   📦 패키지 설치 중: pandas
   ✅ 설치 완료: pandas
   ✅ 파일 업데이트: test_manual/test_import_error.py

============================================================
테스트 결과: ✅ 성공
============================================================
```

---

### Test 2: NameError 자동 수정 ⭐⭐⭐
**난이도**: ★★☆
**예상 시간**: 3-5분
**중요도**: 높음

#### 테스트 시나리오
```python
# test_manual/test_name_error.py
def calculate_total():
    result = price * quantity  # price, quantity 미정의
    return result

total = calculate_total()
print(f"Total: {total}")
```

#### 실행 방법
```bash
cat > test_manual/test_name_error.py << 'EOF'
def calculate_total():
    result = price * quantity
    return result

total = calculate_total()
print(f"Total: {total}")
EOF

# Python REPL에서 실행 (위와 동일한 패턴)
```

#### 검증 항목
- [ ] 에러가 정확하게 분석되었는가? (NameError: price/quantity)
- [ ] LLM이 적절한 수정을 제안했는가? (변수 정의 추가)
- [ ] 수정된 코드가 논리적으로 올바른가?
- [ ] 함수가 정상 실행되는가?

#### 예상 LLM 수정 결과
```python
def calculate_total():
    # 변수 정의 추가
    price = 100
    quantity = 3
    result = price * quantity
    return result

total = calculate_total()
print(f"Total: {total}")
```

---

### Test 3: TypeError 자동 수정 ⭐⭐
**난이도**: ★★☆
**예상 시간**: 3-5분
**중요도**: 중간

#### 테스트 시나리오
```python
# test_manual/test_type_error.py
def greet(name, age):
    message = "Hello " + name + ", you are " + age + " years old"
    return message

result = greet("Alice", 25)  # TypeError: can't concatenate str and int
print(result)
```

#### 검증 항목
- [ ] TypeError가 감지되었는가?
- [ ] LLM이 타입 변환을 제안했는가? (str(age))
- [ ] 수정된 코드가 정상 실행되는가?

---

### Test 4: 복잡한 에러 (다중 에러) ⭐⭐⭐
**난이도**: ★★★
**예상 시간**: 5-10분
**중요도**: 매우 높음

#### 테스트 시나리오
```python
# test_manual/test_complex_error.py
import requests  # ImportError
import json

def fetch_data(url):
    response = requests.get(url)
    data = json.loads(response.text)

    # 데이터 처리
    total = sum(data['items'])  # TypeError: list가 아니라 dict
    return total

result = fetch_data("https://api.example.com/data")
print(result)
```

#### 검증 항목
- [ ] 첫 번째 에러(ImportError)가 수정되었는가?
- [ ] 두 번째 에러(실제 API 호출 문제)가 감지되었는가?
- [ ] 재시도 메커니즘이 작동하는가? (최대 3회)
- [ ] 최종적으로 성공 또는 명확한 실패 메시지가 나오는가?

---

### Test 5: SyntaxError 자동 수정 ⭐⭐
**난이도**: ★☆☆
**예상 시간**: 2-3분
**중요도**: 중간

#### 테스트 시나리오
```python
# test_manual/test_syntax_error.py
def calculate(x, y)  # SyntaxError: missing colon
    return x + y

result = calculate(10, 20)
print(result)
```

#### 검증 항목
- [ ] SyntaxError가 감지되었는가?
- [ ] LLM이 콜론(:) 추가를 제안했는가?
- [ ] 수정된 코드가 정상 실행되는가?

---

### Test 6: 실제 프로젝트 시나리오 ⭐⭐⭐
**난이도**: ★★★
**예상 시간**: 10-15분
**중요도**: 매우 높음

#### 테스트 시나리오
FastAPI 엔드포인트 작성 중 에러 발생

```python
# test_manual/test_fastapi_error.py
from fastapi import FastAPI  # ImportError
from pydantic import BaseModel  # ImportError

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    total_price = item.price * item.quantity  # AttributeError
    return {"name": item.name, "total": total_price}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 검증 항목
- [ ] fastapi, pydantic 패키지가 자동 설치되었는가?
- [ ] AttributeError (quantity 미정의)가 감지되었는가?
- [ ] LLM이 Item 모델에 quantity 필드 추가를 제안했는가?
- [ ] 최종 코드가 논리적으로 올바른가?

---

## 📊 테스트 결과 기록 양식

### 테스트 결과 템플릿
각 테스트 후 다음 정보를 기록하세요:

```markdown
## Test [번호]: [테스트 이름]

**실행 날짜**: 2025-11-14
**실행자**: [이름]
**LLM 제공자**: [Claude/OpenAI/etc]
**모델**: [claude-3-5-sonnet-20241022/gpt-4-turbo/etc]

### 결과
- [ ] 성공 / [ ] 실패 / [ ] 부분 성공

### 상세 결과
- **시도 횟수**: X/3
- **설치된 패키지**: [pandas, numpy, ...]
- **실행 시간**: X초
- **백업 생성**: 예/아니오

### LLM 응답 품질
- **원인 분석 정확도**: ★★★★☆ (4/5)
- **수정 방법 적절성**: ★★★★★ (5/5)
- **코드 품질**: ★★★★☆ (4/5)

### 발견된 이슈
- [이슈 1]
- [이슈 2]

### 개선 제안
- [제안 1]
- [제안 2]

### 스크린샷/로그
```
[실제 출력 로그 붙여넣기]
```
```

---

## 🎯 테스트 진행 순서

### Phase 1: 기본 테스트 (필수)
1. ✅ Test 1: ImportError
2. ✅ Test 2: NameError
3. ✅ Test 5: SyntaxError

**예상 소요 시간**: 10-15분
**목표**: 기본 에러 타입 처리 검증

### Phase 2: 고급 테스트 (권장)
4. ✅ Test 3: TypeError
5. ✅ Test 4: 복잡한 에러

**예상 소요 시간**: 10-15분
**목표**: 복잡한 시나리오 처리 검증

### Phase 3: 실전 테스트 (선택)
6. ✅ Test 6: 실제 프로젝트 시나리오

**예상 소요 시간**: 10-15분
**목표**: 실제 사용 시나리오 검증

---

## 🔧 테스트 환경 설정

### 옵션 1: 대화형 Python REPL
```python
import asyncio
from agents import AutoErrorFixer
from llm import LLMManager
from tools import FileOperations

async def run_test(code_file):
    llm = LLMManager()
    file_ops = FileOperations()
    fixer = AutoErrorFixer(llm, file_ops, max_retries=3)

    code = open(code_file).read()

    try:
        exec(code)
    except Exception as e:
        result = await fixer.auto_fix(
            error=e,
            code=code,
            file_path=code_file
        )
        return result

# 사용법
result = asyncio.run(run_test("test_manual/test_import_error.py"))
print(result)
```

### 옵션 2: 테스트 스크립트 작성
```python
# test_runner.py
import asyncio
from agents import AutoErrorFixer
from llm import LLMManager
from tools import FileOperations

async def main():
    test_files = [
        "test_manual/test_import_error.py",
        "test_manual/test_name_error.py",
        "test_manual/test_type_error.py",
    ]

    llm = LLMManager()
    file_ops = FileOperations()
    fixer = AutoErrorFixer(llm, file_ops)

    results = []
    for test_file in test_files:
        print(f"\n{'='*60}")
        print(f"Testing: {test_file}")
        print(f"{'='*60}\n")

        code = open(test_file).read()

        try:
            exec(code)
            print(f"✅ {test_file}: 에러 없음")
        except Exception as e:
            result = await fixer.auto_fix(
                error=e,
                code=code,
                file_path=test_file
            )
            results.append({
                "file": test_file,
                "success": result["success"],
                "attempts": result["attempts"]
            })

    # 최종 결과
    print("\n" + "="*60)
    print("최종 결과")
    print("="*60)
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"{status} {r['file']}: {r['attempts']}회 시도")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📝 테스트 후 작업

### 1. 결과 문서화
```bash
# 테스트 결과를 문서로 저장
cat > docs/PHASE2_MANUAL_TEST_RESULTS.md << 'EOF'
# Phase 2 수동 테스트 결과

## 테스트 환경
- 날짜: 2025-11-14
- LLM: Claude 3.5 Sonnet
- Python: 3.x

## 테스트 결과
[여기에 테스트 결과 기록]
EOF
```

### 2. 이슈 리포트
발견된 문제점을 GitHub Issues 또는 문서로 정리:
- 에러 분석 정확도
- LLM 응답 품질
- 수정 코드 품질
- 성능 (응답 시간)

### 3. 개선 사항 제안
- 프롬프트 개선
- 에러 타입별 특화 처리
- 재시도 전략 최적화

---

## 🚨 문제 해결

### LLM API 호출 실패
```python
# API 키 확인
import os
print(os.getenv("ANTHROPIC_API_KEY"))
print(os.getenv("OPENAI_API_KEY"))
```

### 패키지 설치 실패
```bash
# pip 권한 확인
pip install --user pandas

# 가상환경 확인
which python
which pip
```

### 파일 권한 문제
```bash
# 테스트 디렉토리 권한 확인
ls -la test_manual/

# 권한 부여
chmod +w test_manual/*.py
```

---

## 📚 참고 자료

- [PHASE2_IMPLEMENTATION.md](docs/PHASE2_IMPLEMENTATION.md) - API 문서
- [ERROR_FIXER_DESIGN.md](docs/ERROR_FIXER_DESIGN.md) - 설계 문서
- [agents/error_fixer.py](agents/error_fixer.py) - 소스 코드

---

**작성자**: Claude AI
**최종 업데이트**: 2025-11-14
**다음 업데이트**: 수동 테스트 완료 후
