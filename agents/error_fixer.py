"""에러 자동 수정 모듈

Python 코드 실행 중 발생하는 에러를 자동으로 분석하고 수정합니다.
"""

import re
import traceback
import subprocess
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from enum import Enum


class ErrorType(Enum):
    """에러 타입 분류"""
    IMPORT_ERROR = "ImportError"
    NAME_ERROR = "NameError"
    TYPE_ERROR = "TypeError"
    SYNTAX_ERROR = "SyntaxError"
    ATTRIBUTE_ERROR = "AttributeError"
    VALUE_ERROR = "ValueError"
    INDENTATION_ERROR = "IndentationError"
    UNKNOWN = "Unknown"


@dataclass
class ErrorInfo:
    """에러 정보"""
    error_type: str
    error_message: str
    traceback_text: str
    file_path: Optional[str]
    line_number: Optional[int]
    code_snippet: Optional[str]
    problematic_line: Optional[str]


class AutoErrorFixer:
    """에러 자동 수정기

    Python 에러를 분석하고 LLM을 활용해 자동으로 수정합니다.
    """

    def __init__(self, llm_manager, file_ops, max_retries: int = 3):
        """
        Args:
            llm_manager: LLM 관리자
            file_ops: 파일 작업 도구
            max_retries: 최대 재시도 횟수
        """
        self.llm = llm_manager
        self.file_ops = file_ops
        self.max_retries = max_retries

    async def analyze_error(
        self,
        error: Exception,
        code: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorInfo:
        """에러 분석

        Python 에러 객체를 분석하여 구조화된 정보를 추출합니다.

        Args:
            error: Python 예외 객체
            code: 에러가 발생한 코드
            context: 추가 컨텍스트 (파일 경로 등)

        Returns:
            ErrorInfo: 에러 정보 객체
        """
        # Traceback 텍스트 생성
        tb_lines = traceback.format_exception(
            type(error), error, error.__traceback__
        )
        tb_text = ''.join(tb_lines)

        # 에러 타입 및 메시지
        error_type = type(error).__name__
        error_message = str(error)

        # 파일 경로 및 라인 번호 추출
        file_path = None
        line_number = None

        if error.__traceback__:
            tb = error.__traceback__
            # 마지막 프레임 (실제 에러 발생 지점)
            while tb.tb_next:
                tb = tb.tb_next

            file_path = tb.tb_frame.f_code.co_filename
            line_number = tb.tb_lineno

        # 문제가 된 코드 라인 추출
        problematic_line = None
        code_snippet = None

        if line_number:
            lines = code.split('\n')
            if 0 < line_number <= len(lines):
                problematic_line = lines[line_number - 1]

                # 주변 5줄 컨텍스트
                start = max(0, line_number - 3)
                end = min(len(lines), line_number + 2)
                code_snippet = '\n'.join(
                    f"{i+1:4d}: {lines[i]}"
                    for i in range(start, end)
                )

        return ErrorInfo(
            error_type=error_type,
            error_message=error_message,
            traceback_text=tb_text,
            file_path=file_path or context.get('file_path') if context else None,
            line_number=line_number,
            code_snippet=code_snippet,
            problematic_line=problematic_line
        )

    def _build_fix_prompt(self, error_info: ErrorInfo, code: str) -> str:
        """수정 요청 프롬프트 생성"""

        prompt = f"""다음 Python 코드에서 에러가 발생했습니다. 에러를 분석하고 수정된 코드를 제공해주세요.

## 에러 정보

**에러 타입**: {error_info.error_type}
**에러 메시지**: {error_info.error_message}
"""

        if error_info.line_number:
            prompt += f"**에러 발생 위치**: Line {error_info.line_number}\n"

        if error_info.problematic_line:
            prompt += f"**문제 라인**: `{error_info.problematic_line.strip()}`\n"

        if error_info.code_snippet:
            prompt += f"\n**주변 코드**:\n```python\n{error_info.code_snippet}\n```\n"

        prompt += f"""
**전체 코드**:
```python
{code}
```

**Traceback**:
```
{error_info.traceback_text}
```

## 요청사항

다음 형식으로 응답해주세요:

### 1. 원인 분석
[에러가 발생한 근본 원인을 설명해주세요]

### 2. 수정 방법
[어떻게 수정할지 설명해주세요]

### 3. 수정된 코드
```python
[전체 수정된 코드를 제공해주세요. 주석으로 변경사항을 표시해주세요]
```

### 4. 추가 작업
[필요한 추가 작업이 있다면 설명해주세요 (예: pip install 패키지명)]
"""

        return prompt

    async def generate_fix(self, error_info: ErrorInfo, code: str) -> Dict[str, Any]:
        """LLM을 사용하여 수정 방법 생성

        Args:
            error_info: 에러 정보
            code: 원본 코드

        Returns:
            수정 제안 (원인, 방법, 수정된 코드, 추가 작업)
        """
        from llm import Message

        # 시스템 프롬프트
        system_prompt = """당신은 Python 에러 수정 전문가입니다.

에러 정보를 받으면:
1. 에러의 근본 원인을 정확하게 파악합니다
2. 가장 간단하고 효과적인 수정 방법을 제시합니다
3. 수정된 전체 코드를 제공합니다
4. 필요한 추가 작업을 알려줍니다

코드를 수정할 때는:
- 기존 코드의 구조와 스타일을 유지합니다
- 최소한의 변경으로 문제를 해결합니다
- 주석으로 변경사항을 명확히 표시합니다
- 추가 에러가 발생하지 않도록 주의합니다
"""

        # 사용자 프롬프트
        user_prompt = self._build_fix_prompt(error_info, code)

        # LLM 호출
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt)
        ]

        response = await self.llm.generate(messages)

        # 응답 파싱
        return self._parse_fix_response(response.content)

    def _parse_fix_response(self, response: str) -> Dict[str, Any]:
        """LLM 응답에서 수정 정보 추출"""

        result = {
            "cause": "",
            "method": "",
            "fixed_code": "",
            "additional_tasks": []
        }

        # 원인 분석 추출
        cause_match = re.search(
            r'### 1\. 원인 분석\s*\n(.+?)(?=###|\Z)',
            response,
            re.DOTALL
        )
        if cause_match:
            result["cause"] = cause_match.group(1).strip()

        # 수정 방법 추출
        method_match = re.search(
            r'### 2\. 수정 방법\s*\n(.+?)(?=###|\Z)',
            response,
            re.DOTALL
        )
        if method_match:
            result["method"] = method_match.group(1).strip()

        # 수정된 코드 추출
        code_match = re.search(
            r'### 3\. 수정된 코드\s*\n```python\s*\n(.+?)\n```',
            response,
            re.DOTALL
        )
        if code_match:
            result["fixed_code"] = code_match.group(1).strip()
        else:
            # 다른 형식 시도
            code_match = re.search(
                r'```python\s*\n(.+?)\n```',
                response,
                re.DOTALL
            )
            if code_match:
                result["fixed_code"] = code_match.group(1).strip()

        # 추가 작업 추출
        tasks_match = re.search(
            r'### 4\. 추가 작업\s*\n(.+?)(?=###|\Z)',
            response,
            re.DOTALL
        )
        if tasks_match:
            tasks_text = tasks_match.group(1).strip()
            # pip install 명령어 추출
            pip_commands = re.findall(r'pip install ([a-zA-Z0-9_\-\[\]>=<.,]+)', tasks_text)
            if pip_commands:
                result["additional_tasks"] = pip_commands

        return result

    async def apply_fix(
        self,
        fixed_code: str,
        file_path: str,
        additional_tasks: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """수정 적용

        Args:
            fixed_code: 수정된 코드
            file_path: 파일 경로
            additional_tasks: 추가 작업 (pip install 등)

        Returns:
            적용 결과
        """
        results = {
            "file_updated": False,
            "packages_installed": [],
            "errors": []
        }

        # 1. 추가 작업 수행 (패키지 설치)
        if additional_tasks:
            for package in additional_tasks:
                try:
                    print(f"   📦 패키지 설치 중: {package}")
                    result = subprocess.run(
                        ["pip", "install", package],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    if result.returncode == 0:
                        results["packages_installed"].append(package)
                        print(f"   ✅ 설치 완료: {package}")
                    else:
                        error_msg = f"Failed to install {package}: {result.stderr}"
                        results["errors"].append(error_msg)
                        print(f"   ❌ 설치 실패: {package}")

                except subprocess.TimeoutExpired:
                    error_msg = f"Timeout installing {package}"
                    results["errors"].append(error_msg)
                except Exception as e:
                    error_msg = f"Error installing {package}: {str(e)}"
                    results["errors"].append(error_msg)

        # 2. 파일 업데이트
        try:
            write_result = await self.file_ops.write_file(
                file_path=file_path,
                content=fixed_code,
                create_backup=True
            )

            if write_result["success"]:
                results["file_updated"] = True
                results["file_path"] = write_result["file_path"]
                results["backup_path"] = write_result.get("backup_path")
                print(f"   ✅ 파일 업데이트: {file_path}")
            else:
                error_msg = f"Failed to update file: {write_result.get('error')}"
                results["errors"].append(error_msg)
                print(f"   ❌ 파일 업데이트 실패")

        except Exception as e:
            error_msg = f"Error updating file: {str(e)}"
            results["errors"].append(error_msg)

        return results

    async def verify_fix(self, code: str, executor) -> tuple[bool, Optional[Exception]]:
        """수정 검증

        Args:
            code: 수정된 코드
            executor: 코드 실행기

        Returns:
            (성공 여부, 에러)
        """
        try:
            result = await executor.execute_python(code)

            if result.get("status") == "success":
                return True, None
            else:
                # 실행은 되었지만 에러가 있는 경우
                error_msg = result.get("error", "Unknown error")
                return False, Exception(error_msg)

        except Exception as e:
            return False, e

    async def auto_fix(
        self,
        error: Exception,
        code: str,
        file_path: str,
        executor=None
    ) -> Dict[str, Any]:
        """에러 자동 수정 전체 워크플로우

        Args:
            error: 발생한 에러
            code: 에러가 발생한 코드
            file_path: 파일 경로
            executor: 코드 실행기 (검증용, optional)

        Returns:
            수정 결과
        """
        print(f"\n🔧 에러 자동 수정 시작")
        print(f"📄 파일: {file_path}")
        print(f"❌ 에러: {type(error).__name__}: {str(error)}")

        attempt_history = []

        for attempt in range(self.max_retries):
            print(f"\n{'='*60}")
            print(f"🔄 수정 시도 {attempt + 1}/{self.max_retries}")
            print(f"{'='*60}")

            # 1. 에러 분석
            print(f"\n1️⃣ 에러 분석 중...")
            error_info = await self.analyze_error(
                error,
                code,
                {"file_path": file_path}
            )

            print(f"   📍 에러 타입: {error_info.error_type}")
            print(f"   📝 메시지: {error_info.error_message}")
            if error_info.line_number:
                print(f"   📌 위치: Line {error_info.line_number}")

            # 2. 수정 방법 생성
            print(f"\n2️⃣ 수정 방법 생성 중...")
            fix_suggestion = await self.generate_fix(error_info, code)

            print(f"   💡 원인: {fix_suggestion['cause'][:100]}...")
            print(f"   🔧 방법: {fix_suggestion['method'][:100]}...")

            if not fix_suggestion["fixed_code"]:
                print(f"   ❌ 수정 코드를 생성하지 못했습니다")
                attempt_history.append({
                    "attempt": attempt + 1,
                    "error": "No fixed code generated",
                    "success": False
                })
                continue

            # 3. 수정 적용
            print(f"\n3️⃣ 수정 적용 중...")
            apply_result = await self.apply_fix(
                fixed_code=fix_suggestion["fixed_code"],
                file_path=file_path,
                additional_tasks=fix_suggestion["additional_tasks"]
            )

            if not apply_result["file_updated"]:
                print(f"   ❌ 파일 업데이트 실패")
                attempt_history.append({
                    "attempt": attempt + 1,
                    "error": "File update failed",
                    "errors": apply_result["errors"],
                    "success": False
                })
                continue

            # 업데이트된 코드 읽기
            code = fix_suggestion["fixed_code"]

            # 4. 검증 (executor가 제공된 경우)
            if executor:
                print(f"\n4️⃣ 수정 검증 중...")
                is_fixed, verify_error = await self.verify_fix(code, executor)

                if is_fixed:
                    print(f"   ✅ 수정 성공! 코드가 정상 실행됩니다")

                    return {
                        "success": True,
                        "attempts": attempt + 1,
                        "fixed_code": code,
                        "file_path": file_path,
                        "cause": fix_suggestion["cause"],
                        "method": fix_suggestion["method"],
                        "packages_installed": apply_result["packages_installed"],
                        "history": attempt_history
                    }
                else:
                    print(f"   ⚠️  여전히 에러 발생: {verify_error}")
                    error = verify_error
                    attempt_history.append({
                        "attempt": attempt + 1,
                        "error": str(verify_error),
                        "success": False
                    })
            else:
                # 검증 없이 적용만 완료
                print(f"   ✅ 수정 적용 완료 (검증 생략)")

                return {
                    "success": True,
                    "attempts": attempt + 1,
                    "fixed_code": code,
                    "file_path": file_path,
                    "cause": fix_suggestion["cause"],
                    "method": fix_suggestion["method"],
                    "packages_installed": apply_result["packages_installed"],
                    "verified": False,
                    "history": attempt_history
                }

        # 최대 재시도 횟수 초과
        print(f"\n❌ {self.max_retries}회 시도 후 수정 실패")

        return {
            "success": False,
            "attempts": self.max_retries,
            "last_error": str(error),
            "history": attempt_history,
            "message": f"Failed to fix error after {self.max_retries} attempts"
        }


# 에러 타입별 특화 처리 헬퍼 함수들

def is_import_error(error: Exception) -> bool:
    """ImportError 또는 ModuleNotFoundError 확인"""
    return isinstance(error, (ImportError, ModuleNotFoundError))


def extract_missing_module(error: Exception) -> Optional[str]:
    """ImportError에서 누락된 모듈명 추출"""
    if not is_import_error(error):
        return None

    error_msg = str(error)

    # "No module named 'xxx'" 패턴
    match = re.search(r"No module named ['\"]([^'\"]+)['\"]", error_msg)
    if match:
        return match.group(1).split('.')[0]  # 최상위 패키지만

    return None


def is_name_error(error: Exception) -> bool:
    """NameError 확인"""
    return isinstance(error, NameError)


def extract_undefined_name(error: Exception) -> Optional[str]:
    """NameError에서 미정의 이름 추출"""
    if not is_name_error(error):
        return None

    error_msg = str(error)

    # "name 'xxx' is not defined" 패턴
    match = re.search(r"name ['\"]([^'\"]+)['\"] is not defined", error_msg)
    if match:
        return match.group(1)

    return None
