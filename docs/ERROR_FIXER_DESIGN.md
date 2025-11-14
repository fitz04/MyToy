# 🔧 에러 자동 수정 구현 설계

## DeepAgent와의 관계

**DeepAgent의 역할**:
- LLM 호출 관리
- 도구(Tool) 등록 및 실행
- 대화 흐름 관리

**우리가 만들어야 하는 것**:
- 에러 감지 및 파싱 로직
- 에러 분석 및 수정 제안 (LLM 활용)
- 자동 수정 실행
- 재시도 메커니즘

---

## 구현 방식

### 방법 1: 순수 Python + LLM (추천)

```python
# agents/error_fixer.py

class AutoErrorFixer:
    """에러 자동 수정기 - DeepAgent 없이도 동작 가능"""

    def __init__(self, llm_manager):
        self.llm = llm_manager
        self.max_retries = 3

    async def analyze_error(self, error: Exception, code: str, context: dict):
        """
        1단계: 에러 분석
        - Python traceback 파싱
        - 에러 타입 식별
        - 관련 코드 라인 추출
        """
        import traceback

        # Traceback 정보 추출
        tb_str = ''.join(traceback.format_exception(
            type(error), error, error.__traceback__
        ))

        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': tb_str,
            'code': code,
            'line': error.__traceback__.tb_lineno if error.__traceback__ else None
        }

        return error_info

    async def generate_fix(self, error_info: dict):
        """
        2단계: LLM에게 수정 방법 요청
        - 에러 정보를 프롬프트로 구성
        - LLM이 수정 코드 생성
        """
        prompt = f"""
다음 Python 코드에서 에러가 발생했습니다:

에러 타입: {error_info['type']}
에러 메시지: {error_info['message']}

코드:
{error_info['code']}

Traceback:
{error_info['traceback']}

이 에러를 수정하는 방법을 다음 형식으로 제안해주세요:

1. 원인 분석
2. 수정 방법
3. 수정된 코드 (전체)
4. 추가 필요 사항 (예: pip install pandas)
"""

        # LLM 호출
        from llm import Message
        messages = [
            Message(role="system", content="당신은 Python 에러 수정 전문가입니다."),
            Message(role="user", content=prompt)
        ]

        response = await self.llm.generate(messages)
        return response.content

    async def apply_fix(self, fix_suggestion: str, file_path: str):
        """
        3단계: 수정 적용
        - 제안된 코드로 파일 업데이트
        """
        # LLM 응답에서 코드 추출
        code = self._extract_code_from_response(fix_suggestion)

        # 파일 업데이트
        from tools import file_ops
        result = await file_ops.write_file(file_path, code)

        return result

    async def auto_fix(self, error: Exception, file_path: str, code: str):
        """
        전체 워크플로우
        """
        for attempt in range(self.max_retries):
            print(f"\n🔧 수정 시도 {attempt + 1}/{self.max_retries}")

            # 1. 에러 분석
            error_info = await self.analyze_error(error, code, {})
            print(f"   ❌ 에러: {error_info['type']}: {error_info['message']}")

            # 2. 수정 방법 생성
            fix_suggestion = await self.generate_fix(error_info)
            print(f"   💡 수정 제안 생성됨")

            # 3. 수정 적용
            await self.apply_fix(fix_suggestion, file_path)
            print(f"   ✏️  코드 수정 완료")

            # 4. 재실행하여 검증
            try:
                from tools import CodeExecutor
                executor = CodeExecutor()
                result = await executor.execute_python(code)

                if result['status'] == 'success':
                    print(f"   ✅ 수정 성공!")
                    return True

            except Exception as e:
                error = e
                print(f"   ⚠️  여전히 에러 발생: {e}")
                continue

        print(f"\n❌ {self.max_retries}회 시도 후 실패")
        return False
```

---

### 방법 2: DeepAgent Tool로 등록 (선택적)

```python
# DeepAgent의 @tool 데코레이터 사용 (만약 DeepAgent가 제공한다면)

from deepagent import tool

@tool
async def fix_python_error(
    error_message: str,
    code: str,
    file_path: str
) -> dict:
    """
    Python 에러를 자동으로 수정합니다.

    Args:
        error_message: 에러 메시지
        code: 에러가 발생한 코드
        file_path: 파일 경로

    Returns:
        수정 결과
    """
    fixer = AutoErrorFixer(llm_manager)
    # ... 위와 동일한 로직
```

---

## 실제 구현 예시

### 시나리오: ImportError 자동 수정

```python
# 1. 에러 발생
try:
    exec("import pandas as pd")
except ImportError as e:
    # 에러 발생!
    # ModuleNotFoundError: No module named 'pandas'

    # 2. 에러 분석
    fixer = AutoErrorFixer(llm_manager)
    error_info = await fixer.analyze_error(e, code, {})

    # 3. LLM에게 수정 요청
    fix = await fixer.generate_fix(error_info)
    # LLM 응답:
    # "이 에러는 pandas 패키지가 설치되지 않아 발생합니다.
    #  해결 방법:
    #  1. requirements.txt에 pandas 추가
    #  2. pip install pandas 실행"

    # 4. 자동 수정
    # 4-1. requirements.txt 업데이트
    await file_ops.edit_file(
        "requirements.txt",
        old_content="",
        new_content="pandas==2.0.0\n"
    )

    # 4-2. pip install 실행
    import subprocess
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

    # 5. 재실행
    exec("import pandas as pd")  # ✅ 성공!
```

---

## 에러 타입별 처리 전략

### 1. ImportError / ModuleNotFoundError
```python
async def fix_import_error(self, error, module_name):
    """
    1. requirements.txt에 모듈 추가
    2. pip install 실행
    3. 재실행
    """
    # requirements.txt 업데이트
    await file_ops.write_file(
        "requirements.txt",
        f"{module_name}\n",
        mode="a"  # append
    )

    # pip install
    subprocess.run(["pip", "install", module_name])
```

### 2. NameError (변수 미정의)
```python
async def fix_name_error(self, error, code):
    """
    LLM에게 물어보고 변수 정의 추가
    """
    prompt = f"이 코드에서 {error.name}이 정의되지 않았습니다. 정의를 추가해주세요."
    # LLM이 코드 수정 제안
```

### 3. TypeError (타입 오류)
```python
async def fix_type_error(self, error, code):
    """
    타입 체크 추가 또는 타입 변환
    """
    # LLM이 타입 힌팅 추가하거나
    # 타입 변환 코드 삽입
```

### 4. SyntaxError (문법 오류)
```python
async def fix_syntax_error(self, error, code):
    """
    LLM에게 문법 수정 요청
    """
    # LLM이 문법 오류 수정
```

---

## LLM 프롬프트 예시

### 효과적인 에러 수정 프롬프트

```python
SYSTEM_PROMPT = """
당신은 Python 에러 수정 전문가입니다.

에러 정보를 받으면:
1. 에러의 근본 원인을 파악합니다
2. 가장 간단하고 효과적인 수정 방법을 제시합니다
3. 수정된 전체 코드를 제공합니다
4. 필요한 추가 작업을 알려줍니다 (예: pip install)

응답 형식:
## 원인
[에러가 발생한 이유]

## 수정 방법
[어떻게 수정할지]

## 수정된 코드
```python
[전체 수정된 코드]
```

## 추가 작업
[pip install 등 필요한 작업]
"""

USER_PROMPT = """
에러 타입: {error_type}
에러 메시지: {error_message}

문제가 발생한 코드:
```python
{code}
```

Traceback:
{traceback}

이 에러를 수정해주세요.
"""
```

---

## 통합 사용 예시

```python
# agents/coding_agent.py에 통합

class CodingAgent:
    def __init__(self):
        self.llm_manager = LLMManager()
        self.error_fixer = AutoErrorFixer(self.llm_manager)
        self.file_ops = file_ops
        self.executor = CodeExecutor()

    async def generate_and_run_code(self, user_request: str):
        """
        코드 생성 → 실행 → 에러 발생 시 자동 수정
        """
        # 1. LLM으로 코드 생성
        code = await self._generate_code(user_request)

        # 2. 파일 저장
        await self.file_ops.write_file("generated.py", code)

        # 3. 실행
        while True:
            try:
                result = await self.executor.execute_python(code)
                print(f"✅ 실행 성공: {result}")
                break

            except Exception as e:
                print(f"❌ 에러 발생: {e}")

                # 4. 자동 수정 시도
                fixed = await self.error_fixer.auto_fix(
                    error=e,
                    file_path="generated.py",
                    code=code
                )

                if not fixed:
                    print("❌ 자동 수정 실패")
                    break

                # 수정된 코드 다시 읽기
                result = await self.file_ops.read_file("generated.py")
                code = result['content']
```

---

## 정리

**DeepAgent는**:
- ❌ 에러 수정 기능을 직접 제공하지 않음
- ✅ LLM 호출을 쉽게 만들어줌
- ✅ 우리가 만든 도구를 등록해서 사용할 수 있게 해줌

**우리가 구현할 것**:
1. **에러 파싱**: Python traceback 분석
2. **LLM 활용**: 수정 방법 생성
3. **자동 적용**: 파일 업데이트 및 재실행
4. **재시도 로직**: 최대 3회 재시도

**핵심 아이디어**:
```
코드 생성 → 실행 → 에러 발생
    ↓
에러 분석 (traceback 파싱)
    ↓
LLM에게 수정 방법 요청
    ↓
자동으로 코드 수정
    ↓
재실행 → 성공하면 종료, 실패하면 재시도
```

이제 이해가 되셨나요? 에러 자동 수정 기능을 구현해볼까요?
