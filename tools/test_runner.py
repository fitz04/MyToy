"""테스트 실행 및 관리 도구

pytest를 자동으로 실행하고 결과를 파싱합니다.
실패한 테스트는 AutoErrorFixer와 연동하여 자동 수정할 수 있습니다.
"""

import asyncio
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class TestStatus(Enum):
    """테스트 상태"""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TestResult:
    """개별 테스트 결과"""
    test_name: str
    file_path: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class TestSummary:
    """전체 테스트 요약"""
    total: int
    passed: int
    failed: int
    error: int
    skipped: int
    duration: float
    results: List[TestResult]


class TestRunner:
    """pytest 실행 및 결과 관리

    pytest를 실행하고 결과를 파싱하여 구조화된 정보를 제공합니다.
    """

    def __init__(self, project_path: str = "."):
        """
        Args:
            project_path: 프로젝트 루트 경로
        """
        self.project_path = Path(project_path)

    async def run_tests(
        self,
        test_path: Optional[str] = None,
        verbose: bool = True,
        capture: bool = True,
        markers: Optional[List[str]] = None,
        timeout: int = 300
    ) -> TestSummary:
        """테스트 실행

        Args:
            test_path: 테스트 파일/디렉토리 경로 (None이면 전체)
            verbose: 상세 출력
            capture: 출력 캡처 (False면 실시간 출력)
            markers: pytest 마커 필터 (예: ["slow", "unit"])
            timeout: 타임아웃 (초)

        Returns:
            TestSummary: 테스트 결과 요약
        """
        # pytest 명령어 구성
        cmd = ["pytest"]

        if test_path:
            cmd.append(str(test_path))

        # 옵션
        if verbose:
            cmd.append("-v")

        if not capture:
            cmd.append("-s")

        # 마커 필터
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])

        # JSON 리포트 출력 (파싱용)
        cmd.append("--tb=short")
        cmd.append("--color=no")

        print(f"🧪 테스트 실행: {' '.join(cmd)}")

        # pytest 실행
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=timeout
            )

            stdout = result.stdout
            stderr = result.stderr
            returncode = result.returncode

        except subprocess.TimeoutExpired:
            print(f"⏱️  테스트 타임아웃 ({timeout}초)")
            return TestSummary(
                total=0, passed=0, failed=0, error=1, skipped=0,
                duration=timeout,
                results=[TestResult(
                    test_name="timeout",
                    file_path="",
                    status=TestStatus.ERROR,
                    duration=timeout,
                    error_message=f"Test execution timed out after {timeout} seconds"
                )]
            )

        # 결과 파싱
        summary = self._parse_pytest_output(stdout, stderr, returncode)

        return summary

    def _parse_pytest_output(
        self,
        stdout: str,
        stderr: str,
        returncode: int
    ) -> TestSummary:
        """pytest 출력 파싱"""

        results = []

        # 개별 테스트 결과 파싱
        # 패턴: test_file.py::test_name PASSED [10%]
        test_pattern = r'([^\s]+\.py)::([^\s]+)\s+(PASSED|FAILED|ERROR|SKIPPED)'

        for match in re.finditer(test_pattern, stdout):
            file_path = match.group(1)
            test_name = match.group(2)
            status_str = match.group(3)

            status = TestStatus[status_str]

            # 실패한 테스트의 에러 메시지 추출
            error_message = None
            traceback = None
            line_number = None

            if status in [TestStatus.FAILED, TestStatus.ERROR]:
                error_info = self._extract_error_info(stdout, test_name)
                error_message = error_info.get("message")
                traceback = error_info.get("traceback")
                line_number = error_info.get("line_number")

            results.append(TestResult(
                test_name=test_name,
                file_path=file_path,
                status=status,
                duration=0.0,  # pytest verbose 모드에서 추출 가능
                error_message=error_message,
                traceback=traceback,
                line_number=line_number
            ))

        # 요약 정보 파싱
        # 패턴: === 1 failed, 2 passed in 0.50s ===
        summary_pattern = r'(?:(\d+)\s+failed)?.*?(?:(\d+)\s+passed)?.*?(?:(\d+)\s+error)?.*?(?:(\d+)\s+skipped)?.*?in\s+([\d.]+)s'

        summary_match = re.search(summary_pattern, stdout)

        if summary_match:
            failed = int(summary_match.group(1) or 0)
            passed = int(summary_match.group(2) or 0)
            error = int(summary_match.group(3) or 0)
            skipped = int(summary_match.group(4) or 0)
            duration = float(summary_match.group(5))
        else:
            # 파싱 실패 시 기본값
            passed = len([r for r in results if r.status == TestStatus.PASSED])
            failed = len([r for r in results if r.status == TestStatus.FAILED])
            error = len([r for r in results if r.status == TestStatus.ERROR])
            skipped = len([r for r in results if r.status == TestStatus.SKIPPED])
            duration = 0.0

        total = passed + failed + error + skipped

        return TestSummary(
            total=total,
            passed=passed,
            failed=failed,
            error=error,
            skipped=skipped,
            duration=duration,
            results=results
        )

    def _extract_error_info(self, output: str, test_name: str) -> Dict[str, Any]:
        """실패한 테스트의 에러 정보 추출"""

        # 테스트 이름 이후의 내용에서 에러 정보 찾기
        test_section_pattern = f'{test_name}.*?(?=\n[A-Z_]+|$)'
        test_section = re.search(test_section_pattern, output, re.DOTALL)

        if not test_section:
            return {}

        section_text = test_section.group(0)

        # 에러 메시지 추출
        error_message = None
        error_match = re.search(r'E\s+(.+)', section_text)
        if error_match:
            error_message = error_match.group(1).strip()

        # Traceback 추출
        traceback = None
        tb_match = re.search(r'(Traceback.*?)(?=\n[A-Z_]+|$)', section_text, re.DOTALL)
        if tb_match:
            traceback = tb_match.group(1).strip()

        # 라인 번호 추출
        line_number = None
        line_match = re.search(r':(\d+):', section_text)
        if line_match:
            line_number = int(line_match.group(1))

        return {
            "message": error_message,
            "traceback": traceback,
            "line_number": line_number
        }

    async def run_with_auto_fix(
        self,
        test_path: Optional[str] = None,
        error_fixer=None,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """테스트 실행 및 실패 시 자동 수정

        Args:
            test_path: 테스트 경로
            error_fixer: AutoErrorFixer 인스턴스
            max_retries: 최대 재시도 횟수

        Returns:
            결과 딕셔너리
        """
        if not error_fixer:
            from agents import AutoErrorFixer
            from llm import LLMManager
            from tools import FileOperations

            error_fixer = AutoErrorFixer(
                LLMManager(),
                FileOperations(),
                max_retries=max_retries
            )

        attempt = 0
        fix_history = []

        while attempt <= max_retries:
            print(f"\n{'='*60}")
            print(f"🔄 테스트 시도 {attempt + 1}/{max_retries + 1}")
            print(f"{'='*60}\n")

            # 테스트 실행
            summary = await self.run_tests(test_path)

            # 성공 시 종료
            if summary.failed == 0 and summary.error == 0:
                print(f"\n✅ 모든 테스트 통과! ({summary.passed}/{summary.total})")
                return {
                    "success": True,
                    "attempts": attempt + 1,
                    "summary": summary,
                    "fixes": fix_history
                }

            # 실패한 테스트 출력
            print(f"\n❌ 실패한 테스트: {summary.failed + summary.error}개")

            failed_tests = [
                r for r in summary.results
                if r.status in [TestStatus.FAILED, TestStatus.ERROR]
            ]

            for test in failed_tests:
                print(f"   - {test.test_name}: {test.error_message}")

            # 마지막 시도였으면 종료
            if attempt >= max_retries:
                print(f"\n⚠️  최대 재시도 횟수 도달")
                break

            # 각 실패한 테스트에 대해 자동 수정 시도
            print(f"\n🔧 자동 수정 시도...\n")

            for test in failed_tests:
                if not test.file_path:
                    continue

                # 테스트 파일 읽기
                test_file = self.project_path / test.file_path

                if not test_file.exists():
                    print(f"   ⚠️  파일을 찾을 수 없음: {test_file}")
                    continue

                with open(test_file, 'r') as f:
                    code = f.read()

                # 에러 객체 생성 (모의)
                error = Exception(test.error_message or "Test failed")

                # 자동 수정
                try:
                    fix_result = await error_fixer.auto_fix(
                        error=error,
                        code=code,
                        file_path=str(test_file),
                        executor=None
                    )

                    if fix_result["success"]:
                        print(f"   ✅ {test.test_name} 수정 완료")
                        fix_history.append({
                            "test": test.test_name,
                            "attempt": attempt + 1,
                            "success": True
                        })
                    else:
                        print(f"   ❌ {test.test_name} 수정 실패")
                        fix_history.append({
                            "test": test.test_name,
                            "attempt": attempt + 1,
                            "success": False
                        })

                except Exception as e:
                    print(f"   ❌ 수정 중 오류: {e}")

            attempt += 1

        # 최종 실패
        return {
            "success": False,
            "attempts": attempt,
            "summary": summary,
            "fixes": fix_history,
            "message": f"Failed tests after {attempt} attempts"
        }

    def get_coverage(self, test_path: Optional[str] = None) -> Optional[float]:
        """코드 커버리지 측정

        pytest-cov가 설치되어 있어야 합니다.

        Returns:
            커버리지 퍼센트 (0-100)
        """
        cmd = ["pytest", "--cov", "--cov-report=term-missing"]

        if test_path:
            cmd.append(str(test_path))

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300
            )

            # 커버리지 퍼센트 추출
            # TOTAL   100   10   90%
            coverage_pattern = r'TOTAL\s+\d+\s+\d+\s+(\d+)%'
            match = re.search(coverage_pattern, result.stdout)

            if match:
                return float(match.group(1))

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None


# 헬퍼 함수

async def run_tests(test_path: Optional[str] = None, **kwargs) -> TestSummary:
    """편의 함수: 테스트 실행"""
    runner = TestRunner()
    return await runner.run_tests(test_path, **kwargs)


async def run_tests_with_fix(
    test_path: Optional[str] = None,
    error_fixer=None,
    max_retries: int = 2
) -> Dict[str, Any]:
    """편의 함수: 테스트 실행 및 자동 수정"""
    runner = TestRunner()
    return await runner.run_with_auto_fix(test_path, error_fixer, max_retries)
