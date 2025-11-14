"""에러 자동 수정 기능 테스트

Phase 2 핵심 기능인 AutoErrorFixer를 테스트합니다.
"""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

print("🧪 에러 자동 수정 기능 테스트\n")
print("=" * 70)


# ========== Test 1: 에러 분석 기능 ==========
print("\n📋 Test 1: 에러 분석 (analyze_error)")
print("=" * 70)


async def test_error_analysis():
    """에러 분석 기능 단독 테스트"""
    # 직접 모듈에서 import (의존성 회피)
    import importlib.util
    spec = importlib.util.spec_from_file_location("error_fixer", "agents/error_fixer.py")
    error_fixer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(error_fixer_module)

    AutoErrorFixer = error_fixer_module.AutoErrorFixer
    ErrorInfo = error_fixer_module.ErrorInfo

    # Mock LLM Manager (분석에는 필요 없음)
    class MockLLM:
        pass

    # Mock File Ops (분석에는 필요 없음)
    class MockFileOps:
        pass

    fixer = AutoErrorFixer(MockLLM(), MockFileOps())

    # 테스트 케이스 1: NameError
    print("\n1️⃣ NameError 분석...")
    try:
        x = undefined_variable  # NameError 발생
    except NameError as e:
        code = "x = undefined_variable"
        error_info = await fixer.analyze_error(e, code)

        print(f"   에러 타입: {error_info.error_type}")
        print(f"   에러 메시지: {error_info.error_message}")
        print(f"   라인 번호: {error_info.line_number}")

        assert error_info.error_type == "NameError"
        assert "undefined_variable" in error_info.error_message
        print("   ✅ NameError 분석 성공")

    # 테스트 케이스 2: TypeError
    print("\n2️⃣ TypeError 분석...")
    try:
        result = "string" + 123  # TypeError 발생
    except TypeError as e:
        code = 'result = "string" + 123'
        error_info = await fixer.analyze_error(e, code)

        print(f"   에러 타입: {error_info.error_type}")
        print(f"   에러 메시지: {error_info.error_message}")

        assert error_info.error_type == "TypeError"
        print("   ✅ TypeError 분석 성공")

    # 테스트 케이스 3: AttributeError
    print("\n3️⃣ AttributeError 분석...")
    try:
        obj = None
        obj.some_method()  # AttributeError 발생
    except AttributeError as e:
        code = "obj = None\nobj.some_method()"
        error_info = await fixer.analyze_error(e, code)

        print(f"   에러 타입: {error_info.error_type}")
        print(f"   에러 메시지: {error_info.error_message}")

        assert error_info.error_type == "AttributeError"
        print("   ✅ AttributeError 분석 성공")

    print("\n✅ 에러 분석 기능 테스트 통과!")
    return True


# ========== Test 2: 헬퍼 함수 테스트 ==========
print("\n\n📋 Test 2: 헬퍼 함수 (is_import_error, extract_missing_module 등)")
print("=" * 70)


def test_helper_functions():
    """에러 타입 판별 헬퍼 함수 테스트"""
    # 직접 모듈에서 import
    import importlib.util
    spec = importlib.util.spec_from_file_location("error_fixer", "agents/error_fixer.py")
    error_fixer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(error_fixer_module)

    is_import_error = error_fixer_module.is_import_error
    extract_missing_module = error_fixer_module.extract_missing_module
    is_name_error = error_fixer_module.is_name_error
    extract_undefined_name = error_fixer_module.extract_undefined_name

    # 1. ImportError 테스트
    print("\n1️⃣ ImportError 헬퍼 함수...")
    try:
        import nonexistent_module
    except ImportError as e:
        assert is_import_error(e) is True
        module_name = extract_missing_module(e)
        print(f"   누락된 모듈: {module_name}")
        assert module_name == "nonexistent_module"
        print("   ✅ ImportError 헬퍼 함수 동작")

    # 2. NameError 테스트
    print("\n2️⃣ NameError 헬퍼 함수...")
    try:
        y = some_undefined_variable
    except NameError as e:
        assert is_name_error(e) is True
        name = extract_undefined_name(e)
        print(f"   미정의 변수: {name}")
        assert name == "some_undefined_variable"
        print("   ✅ NameError 헬퍼 함수 동작")

    print("\n✅ 헬퍼 함수 테스트 통과!")
    return True


# ========== Test 3: 프롬프트 생성 테스트 ==========
print("\n\n📋 Test 3: LLM 프롬프트 생성")
print("=" * 70)


async def test_prompt_generation():
    """수정 제안을 위한 프롬프트 생성 테스트"""
    # 직접 모듈에서 import
    import importlib.util
    spec = importlib.util.spec_from_file_location("error_fixer", "agents/error_fixer.py")
    error_fixer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(error_fixer_module)

    AutoErrorFixer = error_fixer_module.AutoErrorFixer
    ErrorInfo = error_fixer_module.ErrorInfo

    class MockLLM:
        pass

    class MockFileOps:
        pass

    fixer = AutoErrorFixer(MockLLM(), MockFileOps())

    print("\n1️⃣ 프롬프트 생성 테스트...")

    # 에러 정보 생성
    try:
        undefined_var = missing_variable
    except NameError as e:
        code = "undefined_var = missing_variable"
        error_info = await fixer.analyze_error(e, code)

        # 프롬프트 생성 (private 메서드지만 테스트용으로 호출)
        prompt = fixer._build_fix_prompt(error_info, code)

        # 프롬프트에 필수 정보가 포함되어 있는지 확인
        assert "에러 타입" in prompt
        assert "NameError" in prompt
        assert "missing_variable" in prompt
        assert "전체 코드" in prompt
        assert "Traceback" in prompt

        print("   프롬프트 길이:", len(prompt), "chars")
        print("   프롬프트 미리보기:")
        print("   " + "\n   ".join(prompt.split("\n")[:10]))
        print("   ...")

        print("   ✅ 프롬프트 생성 성공")

    print("\n✅ 프롬프트 생성 테스트 통과!")
    return True


# ========== Test 4: 응답 파싱 테스트 ==========
print("\n\n📋 Test 4: LLM 응답 파싱")
print("=" * 70)


def test_response_parsing():
    """LLM 응답 파싱 테스트"""
    # 직접 모듈에서 import
    import importlib.util
    spec = importlib.util.spec_from_file_location("error_fixer", "agents/error_fixer.py")
    error_fixer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(error_fixer_module)

    AutoErrorFixer = error_fixer_module.AutoErrorFixer

    class MockLLM:
        pass

    class MockFileOps:
        pass

    fixer = AutoErrorFixer(MockLLM(), MockFileOps())

    print("\n1️⃣ 정상 응답 파싱...")

    # 모의 LLM 응답
    mock_response = """### 1. 원인 분석
변수 'missing_variable'이 정의되지 않아 NameError가 발생했습니다.

### 2. 수정 방법
변수를 사용하기 전에 먼저 정의해야 합니다.

### 3. 수정된 코드
```python
# 변수 정의 추가
missing_variable = "some value"
undefined_var = missing_variable
```

### 4. 추가 작업
추가 작업이 필요하지 않습니다.
"""

    parsed = fixer._parse_fix_response(mock_response)

    assert "변수 'missing_variable'" in parsed["cause"]
    assert "정의해야" in parsed["method"]
    assert "missing_variable = " in parsed["fixed_code"]
    assert len(parsed["additional_tasks"]) == 0

    print("   ✅ 원인:", parsed["cause"][:50] + "...")
    print("   ✅ 방법:", parsed["method"][:50] + "...")
    print("   ✅ 수정 코드:", len(parsed["fixed_code"]), "chars")

    print("\n2️⃣ pip install 포함 응답 파싱...")

    mock_response_with_pip = """### 1. 원인 분석
pandas 모듈이 설치되지 않았습니다.

### 2. 수정 방법
pip install로 패키지를 설치합니다.

### 3. 수정된 코드
```python
import pandas as pd
df = pd.DataFrame()
```

### 4. 추가 작업
다음 패키지를 설치하세요:
pip install pandas
pip install numpy>=1.20.0
"""

    parsed = fixer._parse_fix_response(mock_response_with_pip)

    assert len(parsed["additional_tasks"]) == 2
    assert "pandas" in parsed["additional_tasks"]
    assert "numpy>=1.20.0" in parsed["additional_tasks"]

    print("   ✅ 추가 작업:", parsed["additional_tasks"])

    print("\n✅ 응답 파싱 테스트 통과!")
    return True


# ========== Test 5: 에러 타입 분류 ==========
print("\n\n📋 Test 5: 에러 타입 분류 (ErrorType Enum)")
print("=" * 70)


def test_error_types():
    """에러 타입 Enum 테스트"""
    # 직접 모듈에서 import
    import importlib.util
    spec = importlib.util.spec_from_file_location("error_fixer", "agents/error_fixer.py")
    error_fixer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(error_fixer_module)

    ErrorType = error_fixer_module.ErrorType

    print("\n1️⃣ ErrorType Enum 확인...")

    error_types = [
        ErrorType.IMPORT_ERROR,
        ErrorType.NAME_ERROR,
        ErrorType.TYPE_ERROR,
        ErrorType.SYNTAX_ERROR,
        ErrorType.ATTRIBUTE_ERROR,
        ErrorType.VALUE_ERROR,
        ErrorType.INDENTATION_ERROR,
        ErrorType.UNKNOWN
    ]

    print(f"   지원하는 에러 타입: {len(error_types)}개")
    for et in error_types:
        print(f"   - {et.value}")

    assert len(error_types) == 8
    print("\n   ✅ 모든 에러 타입 정의됨")

    print("\n✅ 에러 타입 분류 테스트 통과!")
    return True


# ========== Test 6: 통합 시나리오 (Mock) ==========
print("\n\n📋 Test 6: 통합 워크플로우 (Mock LLM)")
print("=" * 70)


async def test_integration_mock():
    """모의 LLM을 사용한 통합 테스트"""
    # 직접 모듈에서 import
    import importlib.util
    spec = importlib.util.spec_from_file_location("error_fixer", "agents/error_fixer.py")
    error_fixer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(error_fixer_module)

    AutoErrorFixer = error_fixer_module.AutoErrorFixer

    # Mock LLM (항상 간단한 수정 제안 반환)
    class MockLLMManager:
        async def generate(self, messages):
            class Response:
                content = """### 1. 원인 분석
변수가 정의되지 않았습니다.

### 2. 수정 방법
변수를 정의합니다.

### 3. 수정된 코드
```python
# 변수 정의
test_var = "Hello, World!"
print(test_var)
```

### 4. 추가 작업
없음
"""
            return Response()

    # Mock File Ops
    class MockFileOps:
        async def write_file(self, file_path, content, create_backup=True):
            return {
                "success": True,
                "file_path": file_path,
                "backup_path": f"{file_path}.backup"
            }

    # Mock Executor
    class MockExecutor:
        async def execute_python(self, code):
            # 수정된 코드는 항상 성공한다고 가정
            if "test_var = " in code:
                return {"status": "success"}
            else:
                raise NameError("name 'test_var' is not defined")

    print("\n1️⃣ 통합 워크플로우 시작...")

    fixer = AutoErrorFixer(MockLLMManager(), MockFileOps(), max_retries=2)

    # 에러 생성
    try:
        print(test_var)
    except NameError as e:
        code = "print(test_var)"
        file_path = "test_output/error_test.py"

        # 자동 수정 실행
        result = await fixer.auto_fix(
            error=e,
            code=code,
            file_path=file_path,
            executor=MockExecutor()
        )

        print(f"\n   수정 결과:")
        print(f"   - 성공: {result['success']}")
        print(f"   - 시도 횟수: {result['attempts']}")
        print(f"   - 파일: {result.get('file_path')}")

        if result['success']:
            print(f"   - 원인: {result['cause'][:50]}...")
            print(f"   - 방법: {result['method'][:50]}...")
            print("\n   ✅ 통합 워크플로우 성공!")
        else:
            print(f"   ❌ 통합 워크플로우 실패: {result.get('message')}")
            return False

    print("\n✅ 통합 테스트 통과!")
    return True


# ========== 실행 ==========
async def main():
    """모든 테스트 실행"""

    results = {}

    try:
        # Test 1: 에러 분석
        results["error_analysis"] = await test_error_analysis()

        # Test 2: 헬퍼 함수
        results["helper_functions"] = test_helper_functions()

        # Test 3: 프롬프트 생성
        results["prompt_generation"] = await test_prompt_generation()

        # Test 4: 응답 파싱
        results["response_parsing"] = test_response_parsing()

        # Test 5: 에러 타입 분류
        results["error_types"] = test_error_types()

        # Test 6: 통합 테스트
        results["integration"] = await test_integration_mock()

    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 최종 결과
    print("\n" + "=" * 70)
    print("📊 최종 테스트 결과")
    print("=" * 70)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    total = len(results)
    passed = sum(results.values())
    print(f"\n총 {passed}/{total} 테스트 통과 ({passed/total*100:.1f}%)")

    if all(results.values()):
        print("\n" + "🎉" * 30)
        print("에러 자동 수정 기능 검증 완료!")
        print("Phase 2 핵심 기능이 정상 작동합니다!")
        print("🎉" * 30)
        return True
    else:
        print("\n⚠️ 일부 테스트 실패")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
