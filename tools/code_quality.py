"""코드 품질 도구 통합

black, flake8, pylint 등 코드 품질 도구를 자동으로 실행합니다.
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class IssueLevel(Enum):
    """이슈 심각도"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class CodeIssue:
    """코드 이슈"""
    file_path: str
    line_number: int
    column: Optional[int]
    level: IssueLevel
    code: str  # 예: E501, W503
    message: str
    tool: str  # black, flake8, pylint


@dataclass
class QualityReport:
    """코드 품질 리포트"""
    total_issues: int
    errors: int
    warnings: int
    infos: int
    issues: List[CodeIssue]
    files_checked: int
    score: Optional[float] = None  # pylint 점수 (0-10)


class CodeQuality:
    """코드 품질 검사 및 자동 수정

    black, flake8, pylint 등의 도구를 통합하여 실행합니다.
    """

    def __init__(self, project_path: str = "."):
        """
        Args:
            project_path: 프로젝트 루트 경로
        """
        self.project_path = Path(project_path)

    async def format_code(
        self,
        file_path: Optional[str] = None,
        line_length: int = 88,
        check_only: bool = False
    ) -> Dict[str, Any]:
        """black으로 코드 포매팅

        Args:
            file_path: 파일 경로 (None이면 전체)
            line_length: 최대 라인 길이
            check_only: 수정하지 않고 확인만

        Returns:
            포매팅 결과
        """
        cmd = ["black"]

        if check_only:
            cmd.append("--check")

        cmd.extend(["--line-length", str(line_length)])

        if file_path:
            cmd.append(str(file_path))
        else:
            cmd.append(".")

        print(f"🎨 코드 포매팅: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=60
            )

            stdout = result.stdout
            returncode = result.returncode

            # 파일 변경 여부 파싱
            changed_files = []
            if "reformatted" in stdout:
                changed_pattern = r'reformatted\s+(.+)'
                for match in re.finditer(changed_pattern, stdout):
                    changed_files.append(match.group(1).strip())

            return {
                "success": returncode == 0,
                "changed_files": changed_files,
                "total_changed": len(changed_files),
                "output": stdout
            }

        except FileNotFoundError:
            return {
                "success": False,
                "error": "black이 설치되지 않았습니다. pip install black"
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout"
            }

    async def lint_code(
        self,
        file_path: Optional[str] = None,
        max_line_length: int = 88
    ) -> QualityReport:
        """flake8으로 코드 린팅

        Args:
            file_path: 파일 경로 (None이면 전체)
            max_line_length: 최대 라인 길이

        Returns:
            QualityReport: 품질 리포트
        """
        cmd = ["flake8"]
        cmd.extend(["--max-line-length", str(max_line_length)])

        if file_path:
            cmd.append(str(file_path))
        else:
            cmd.append(".")

        print(f"🔍 린팅: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=60
            )

            stdout = result.stdout

            # 이슈 파싱
            # 패턴: file.py:10:5: E501 line too long
            issues = []
            issue_pattern = r'([^:]+):(\d+):(\d+):\s+([EW]\d+)\s+(.+)'

            for match in re.finditer(issue_pattern, stdout):
                file_path = match.group(1)
                line_number = int(match.group(2))
                column = int(match.group(3))
                code = match.group(4)
                message = match.group(5)

                level = IssueLevel.ERROR if code.startswith('E') else IssueLevel.WARNING

                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_number,
                    column=column,
                    level=level,
                    code=code,
                    message=message,
                    tool="flake8"
                ))

            errors = len([i for i in issues if i.level == IssueLevel.ERROR])
            warnings = len([i for i in issues if i.level == IssueLevel.WARNING])

            files_checked = len(set(i.file_path for i in issues))

            return QualityReport(
                total_issues=len(issues),
                errors=errors,
                warnings=warnings,
                infos=0,
                issues=issues,
                files_checked=files_checked if files_checked > 0 else 1
            )

        except FileNotFoundError:
            print("⚠️  flake8이 설치되지 않았습니다")
            return QualityReport(
                total_issues=0, errors=0, warnings=0, infos=0,
                issues=[], files_checked=0
            )
        except subprocess.TimeoutExpired:
            print("⏱️  린팅 타임아웃")
            return QualityReport(
                total_issues=0, errors=0, warnings=0, infos=0,
                issues=[], files_checked=0
            )

    async def analyze_with_pylint(
        self,
        file_path: str
    ) -> QualityReport:
        """pylint으로 상세 분석

        Args:
            file_path: 파일 경로

        Returns:
            QualityReport: 품질 리포트 (score 포함)
        """
        cmd = ["pylint", str(file_path)]

        print(f"🔬 상세 분석: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=120
            )

            stdout = result.stdout

            # 점수 추출
            # Your code has been rated at 8.50/10
            score = None
            score_pattern = r'rated at ([\d.]+)/10'
            score_match = re.search(score_pattern, stdout)
            if score_match:
                score = float(score_match.group(1))

            # 이슈 파싱
            issues = []
            issue_pattern = r'([^:]+):(\d+):(\d+):\s+([CWERF]\d+):\s+(.+)'

            for match in re.finditer(issue_pattern, stdout):
                file_path = match.group(1)
                line_number = int(match.group(2))
                column = int(match.group(3))
                code = match.group(4)
                message = match.group(5)

                # pylint 코드에 따른 레벨 매핑
                if code.startswith('E') or code.startswith('F'):
                    level = IssueLevel.ERROR
                elif code.startswith('W'):
                    level = IssueLevel.WARNING
                else:
                    level = IssueLevel.INFO

                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_number,
                    column=column,
                    level=level,
                    code=code,
                    message=message,
                    tool="pylint"
                ))

            errors = len([i for i in issues if i.level == IssueLevel.ERROR])
            warnings = len([i for i in issues if i.level == IssueLevel.WARNING])
            infos = len([i for i in issues if i.level == IssueLevel.INFO])

            return QualityReport(
                total_issues=len(issues),
                errors=errors,
                warnings=warnings,
                infos=infos,
                issues=issues,
                files_checked=1,
                score=score
            )

        except FileNotFoundError:
            print("⚠️  pylint이 설치되지 않았습니다")
            return QualityReport(
                total_issues=0, errors=0, warnings=0, infos=0,
                issues=[], files_checked=0
            )
        except subprocess.TimeoutExpired:
            print("⏱️  분석 타임아웃")
            return QualityReport(
                total_issues=0, errors=0, warnings=0, infos=0,
                issues=[], files_checked=0
            )

    async def auto_fix(
        self,
        file_path: Optional[str] = None,
        format_code: bool = True,
        fix_imports: bool = True
    ) -> Dict[str, Any]:
        """자동 수정

        Args:
            file_path: 파일 경로
            format_code: 코드 포매팅 수행
            fix_imports: import 정리 (isort)

        Returns:
            수정 결과
        """
        results = {}

        # 1. import 정리 (isort)
        if fix_imports:
            try:
                cmd = ["isort", str(file_path) if file_path else "."]

                result = subprocess.run(
                    cmd,
                    cwd=str(self.project_path),
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                results["imports_fixed"] = result.returncode == 0

            except (FileNotFoundError, subprocess.TimeoutExpired):
                results["imports_fixed"] = False

        # 2. 코드 포매팅 (black)
        if format_code:
            format_result = await self.format_code(file_path)
            results["formatted"] = format_result["success"]
            results["changed_files"] = format_result.get("changed_files", [])

        return results

    async def check_all(
        self,
        file_path: Optional[str] = None,
        auto_fix: bool = False
    ) -> Dict[str, Any]:
        """전체 품질 검사

        Args:
            file_path: 파일 경로
            auto_fix: 자동 수정 수행

        Returns:
            전체 결과
        """
        print(f"\n{'='*60}")
        print(f"🔍 코드 품질 검사")
        print(f"{'='*60}\n")

        results = {}

        # 1. 자동 수정 (옵션)
        if auto_fix:
            print("🔧 자동 수정 수행 중...\n")
            fix_result = await self.auto_fix(file_path)
            results["auto_fix"] = fix_result

        # 2. 린팅
        lint_report = await self.lint_code(file_path)
        results["lint"] = {
            "total_issues": lint_report.total_issues,
            "errors": lint_report.errors,
            "warnings": lint_report.warnings,
            "files_checked": lint_report.files_checked
        }

        # 3. 포매팅 확인
        format_result = await self.format_code(file_path, check_only=True)
        results["format_check"] = format_result

        # 결과 요약
        print(f"\n{'='*60}")
        print(f"📊 검사 결과")
        print(f"{'='*60}")
        print(f"  린팅 이슈: {lint_report.total_issues}개")
        print(f"    - 에러: {lint_report.errors}개")
        print(f"    - 경고: {lint_report.warnings}개")

        if format_result.get("changed_files"):
            print(f"  포매팅 필요: {len(format_result['changed_files'])}개 파일")
        else:
            print(f"  포매팅: ✅ 양호")

        print(f"{'='*60}\n")

        # 전체 통과 여부
        all_pass = (
            lint_report.errors == 0 and
            not format_result.get("changed_files")
        )

        results["all_pass"] = all_pass

        return results


# 헬퍼 함수

async def format_file(file_path: str, **kwargs) -> Dict[str, Any]:
    """편의 함수: 파일 포매팅"""
    quality = CodeQuality()
    return await quality.format_code(file_path, **kwargs)


async def lint_file(file_path: str, **kwargs) -> QualityReport:
    """편의 함수: 파일 린팅"""
    quality = CodeQuality()
    return await quality.lint_code(file_path, **kwargs)


async def check_quality(file_path: Optional[str] = None, auto_fix: bool = False) -> Dict[str, Any]:
    """편의 함수: 전체 품질 검사"""
    quality = CodeQuality()
    return await quality.check_all(file_path, auto_fix)
