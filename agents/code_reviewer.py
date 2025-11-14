"""코드 리뷰 에이전트

LLM을 활용하여 코드를 분석하고 개선 제안을 제공합니다.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ReviewLevel(Enum):
    """리뷰 심각도"""
    CRITICAL = "critical"  # 치명적 (보안, 버그)
    MAJOR = "major"        # 중요 (성능, 구조)
    MINOR = "minor"        # 경미 (스타일, 가독성)
    SUGGESTION = "suggestion"  # 제안 (개선 아이디어)


@dataclass
class ReviewComment:
    """리뷰 코멘트"""
    level: ReviewLevel
    line_number: Optional[int]
    code_snippet: Optional[str]
    issue: str
    suggestion: str
    reason: str


@dataclass
class CodeReview:
    """코드 리뷰 결과"""
    file_path: str
    overall_score: float  # 0-10
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    comments: List[ReviewComment]
    refactoring_suggestions: List[str]


class CodeReviewer:
    """코드 리뷰어

    LLM을 사용하여 코드 품질, 보안, 성능 등을 종합적으로 리뷰합니다.
    """

    def __init__(self, llm_manager):
        """
        Args:
            llm_manager: LLM 관리자
        """
        self.llm = llm_manager

    async def review_code(
        self,
        file_path: str,
        code: Optional[str] = None,
        focus: Optional[List[str]] = None
    ) -> CodeReview:
        """코드 리뷰

        Args:
            file_path: 파일 경로
            code: 코드 내용 (None이면 파일에서 읽음)
            focus: 집중 검토 항목 (예: ["security", "performance"])

        Returns:
            CodeReview: 리뷰 결과
        """
        # 코드 읽기
        if code is None:
            with open(file_path, 'r') as f:
                code = f.read()

        # 리뷰 프롬프트 생성
        prompt = self._build_review_prompt(code, focus)

        # LLM 호출
        from llm.models import Message

        messages = [
            Message(role="system", content=self._get_system_prompt()),
            Message(role="user", content=prompt)
        ]

        response = await self.llm.generate(messages)

        # 응답 파싱
        review = self._parse_review_response(response.content, file_path)

        return review

    def _get_system_prompt(self) -> str:
        """시스템 프롬프트"""
        return """당신은 전문 코드 리뷰어입니다.

코드를 다음 관점에서 검토합니다:
1. **보안**: SQL injection, XSS, 인증/인가 문제
2. **성능**: 비효율적인 알고리즘, 메모리 누수, N+1 쿼리
3. **가독성**: 명확한 변수명, 적절한 주석, 구조화
4. **유지보수성**: 중복 코드, 결합도, 테스트 가능성
5. **모범 사례**: 디자인 패턴, SOLID 원칙, 파이썬 관례

리뷰 시 다음 형식을 따릅니다:
- 구체적인 라인 번호와 코드 스니펫 제공
- 문제점과 개선 방법을 명확히 설명
- 심각도를 구분 (Critical, Major, Minor, Suggestion)
- 건설적이고 친절한 톤 유지
"""

    def _build_review_prompt(
        self,
        code: str,
        focus: Optional[List[str]] = None
    ) -> str:
        """리뷰 프롬프트 생성"""

        prompt = f"""다음 Python 코드를 종합적으로 리뷰해주세요.

## 코드

```python
{code}
```

## 요청사항

다음 형식으로 응답해주세요:

### 1. 전체 평가 (0-10점)
[점수와 간단한 총평]

### 2. 요약
[코드의 목적과 전반적인 품질 요약]

### 3. 강점
- [강점 1]
- [강점 2]

### 4. 개선 필요 사항
- [약점 1]
- [약점 2]

### 5. 상세 리뷰

#### Critical (치명적)
[보안 취약점, 심각한 버그 등]

**Line X:**
```python
[문제가 있는 코드]
```
- **이슈**: [문제점]
- **제안**: [개선 방법]
- **이유**: [왜 중요한지]

#### Major (중요)
[성능 문제, 구조적 문제 등]

#### Minor (경미)
[스타일, 가독성 등]

#### Suggestion (제안)
[추가 개선 아이디어]

### 6. 리팩토링 제안
- [제안 1]
- [제안 2]
"""

        if focus:
            focus_text = ", ".join(focus)
            prompt += f"\n\n**특히 다음 항목에 집중해주세요**: {focus_text}\n"

        return prompt

    def _parse_review_response(
        self,
        response: str,
        file_path: str
    ) -> CodeReview:
        """리뷰 응답 파싱"""

        # 점수 추출
        score = 7.0  # 기본값
        score_match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*10', response)
        if score_match:
            score = float(score_match.group(1))

        # 요약 추출
        summary = ""
        summary_match = re.search(
            r'### 2\. 요약\s*\n(.+?)(?=###|$)',
            response,
            re.DOTALL
        )
        if summary_match:
            summary = summary_match.group(1).strip()

        # 강점 추출
        strengths = []
        strengths_match = re.search(
            r'### 3\. 강점\s*\n(.+?)(?=###|$)',
            response,
            re.DOTALL
        )
        if strengths_match:
            strengths_text = strengths_match.group(1)
            strengths = [
                s.strip('- ').strip()
                for s in strengths_text.split('\n')
                if s.strip().startswith('-')
            ]

        # 약점 추출
        weaknesses = []
        weaknesses_match = re.search(
            r'### 4\. 개선 필요 사항\s*\n(.+?)(?=###|$)',
            response,
            re.DOTALL
        )
        if weaknesses_match:
            weaknesses_text = weaknesses_match.group(1)
            weaknesses = [
                w.strip('- ').strip()
                for w in weaknesses_text.split('\n')
                if w.strip().startswith('-')
            ]

        # 코멘트 추출
        comments = self._extract_comments(response)

        # 리팩토링 제안 추출
        refactoring = []
        refactoring_match = re.search(
            r'### 6\. 리팩토링 제안\s*\n(.+?)(?=###|$)',
            response,
            re.DOTALL
        )
        if refactoring_match:
            refactoring_text = refactoring_match.group(1)
            refactoring = [
                r.strip('- ').strip()
                for r in refactoring_text.split('\n')
                if r.strip().startswith('-')
            ]

        return CodeReview(
            file_path=file_path,
            overall_score=score,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            comments=comments,
            refactoring_suggestions=refactoring
        )

    def _extract_comments(self, response: str) -> List[ReviewComment]:
        """상세 코멘트 추출"""
        comments = []

        # 각 레벨별로 추출
        levels = {
            "Critical": ReviewLevel.CRITICAL,
            "Major": ReviewLevel.MAJOR,
            "Minor": ReviewLevel.MINOR,
            "Suggestion": ReviewLevel.SUGGESTION
        }

        for level_name, level_enum in levels.items():
            # 해당 레벨 섹션 찾기
            section_pattern = f'#### {level_name}.*?\n(.+?)(?=####|###|$)'
            section_match = re.search(section_pattern, response, re.DOTALL)

            if not section_match:
                continue

            section_text = section_match.group(1)

            # 개별 코멘트 파싱
            # 패턴: **Line X:** ... **이슈**: ... **제안**: ... **이유**: ...
            comment_pattern = r'\*\*Line\s+(\d+):\*\*.*?```python\s*\n(.+?)\n```.*?\*\*이슈\*\*:\s*(.+?)\n.*?\*\*제안\*\*:\s*(.+?)\n.*?\*\*이유\*\*:\s*(.+?)(?=\*\*Line|####|###|$)'

            for match in re.finditer(comment_pattern, section_text, re.DOTALL):
                line_number = int(match.group(1))
                code_snippet = match.group(2).strip()
                issue = match.group(3).strip()
                suggestion = match.group(4).strip()
                reason = match.group(5).strip()

                comments.append(ReviewComment(
                    level=level_enum,
                    line_number=line_number,
                    code_snippet=code_snippet,
                    issue=issue,
                    suggestion=suggestion,
                    reason=reason
                ))

        return comments

    async def review_diff(
        self,
        old_code: str,
        new_code: str,
        file_path: str
    ) -> Dict[str, Any]:
        """변경사항 리뷰

        Args:
            old_code: 이전 코드
            new_code: 새로운 코드
            file_path: 파일 경로

        Returns:
            변경사항 리뷰
        """
        import difflib

        # Diff 생성
        diff = list(difflib.unified_diff(
            old_code.splitlines(keepends=True),
            new_code.splitlines(keepends=True),
            fromfile=f"{file_path} (old)",
            tofile=f"{file_path} (new)"
        ))

        diff_text = ''.join(diff)

        # Diff 리뷰 프롬프트
        prompt = f"""다음 코드 변경사항을 리뷰해주세요.

## Diff

```diff
{diff_text}
```

## 요청사항

1. 변경사항이 적절한가요?
2. 새로운 버그나 문제가 없나요?
3. 성능이나 보안에 영향은 없나요?
4. 추가 개선 사항이 있나요?

간결하게 답변해주세요.
"""

        from llm.models import Message

        messages = [
            Message(role="system", content="당신은 코드 리뷰어입니다. 변경사항을 빠르게 검토합니다."),
            Message(role="user", content=prompt)
        ]

        response = await self.llm.generate(messages)

        return {
            "diff": diff_text,
            "review": response.content,
            "file_path": file_path
        }

    async def suggest_improvements(
        self,
        code: str,
        aspect: str = "all"
    ) -> List[Dict[str, str]]:
        """개선 제안

        Args:
            code: 코드
            aspect: 개선 측면 (performance, readability, security, all)

        Returns:
            개선 제안 목록
        """
        aspect_prompts = {
            "performance": "성능 최적화 관점에서",
            "readability": "가독성 향상 관점에서",
            "security": "보안 강화 관점에서",
            "all": "전반적인 품질 향상 관점에서"
        }

        aspect_text = aspect_prompts.get(aspect, aspect_prompts["all"])

        prompt = f"""{aspect_text} 다음 코드의 개선 방법을 제안해주세요.

```python
{code}
```

각 제안은 다음 형식으로:
1. **개선 항목**: [무엇을 개선할지]
   **현재**: [현재 코드]
   **개선**: [개선된 코드]
   **효과**: [개선 효과]
"""

        from llm.models import Message

        messages = [
            Message(role="system", content="당신은 코드 개선 전문가입니다."),
            Message(role="user", content=prompt)
        ]

        response = await self.llm.generate(messages)

        # 개선 제안 파싱
        suggestions = []
        suggestion_pattern = r'\*\*개선 항목\*\*:\s*(.+?)\n.*?\*\*현재\*\*:\s*(.+?)\n.*?\*\*개선\*\*:\s*(.+?)\n.*?\*\*효과\*\*:\s*(.+?)(?=\*\*개선 항목|$)'

        for match in re.finditer(suggestion_pattern, response.content, re.DOTALL):
            suggestions.append({
                "title": match.group(1).strip(),
                "current": match.group(2).strip(),
                "improved": match.group(3).strip(),
                "benefit": match.group(4).strip()
            })

        return suggestions


# 헬퍼 함수

async def review_file(file_path: str, llm_manager, **kwargs) -> CodeReview:
    """편의 함수: 파일 리뷰"""
    reviewer = CodeReviewer(llm_manager)
    return await reviewer.review_code(file_path, **kwargs)


async def quick_review(code: str, llm_manager) -> str:
    """편의 함수: 빠른 리뷰"""
    reviewer = CodeReviewer(llm_manager)
    review = await reviewer.review_code("temp.py", code)
    return review.summary
