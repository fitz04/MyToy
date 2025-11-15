"""Chainlit application for the coding agent."""
import chainlit as cl
from pathlib import Path
from typing import Optional
import os

from agents import CodingAgent
from config import settings
from utils import get_session_manager


# Global agent instance
agent: Optional[CodingAgent] = None
session_manager = get_session_manager()


def get_quick_actions():
    """매 응답마다 표시할 핵심 버튼 반환"""
    return [
        cl.Action(name="run_tests", value="run_tests", label="🧪 테스트", payload={}),
        cl.Action(name="check_quality", value="check_quality", label="🔍 품질", payload={}),
        cl.Action(name="review_code", value="review_code", label="📝 리뷰", payload={}),
        cl.Action(name="show_full_menu", value="show_full_menu", label="🔧 전체메뉴", payload={}),
    ]


def get_full_menu_actions():
    """전체 메뉴 버튼 반환"""
    return [
        # 프로젝트 관리
        cl.Action(name="analyze", value="analyze", label="📊 프로젝트 분석", payload={}),
        cl.Action(name="save_session", value="save_session", label="💾 세션 저장", payload={}),

        # Phase 2 도구들
        cl.Action(name="run_tests", value="run_tests", label="🧪 테스트 실행", payload={}),
        cl.Action(name="check_quality", value="check_quality", label="🔍 코드 품질", payload={}),
        cl.Action(name="review_code", value="review_code", label="📝 코드 리뷰", payload={}),
        cl.Action(name="create_project", value="create_project", label="🏗️ 프로젝트 생성", payload={}),

        # 문서 & RAG
        cl.Action(name="upload_docs", value="upload_docs", label="📤 문서 업로드", payload={}),
        cl.Action(name="rag_stats", value="rag_stats", label="📈 RAG 통계", payload={}),

        # 기타
        cl.Action(name="switch_llm", value="switch_llm", label="🔄 LLM 전환", payload={}),
        cl.Action(name="show_sessions", value="show_sessions", label="💾 세션 목록", payload={}),
        cl.Action(name="clear_chat", value="clear_chat", label="🗑️ 대화 초기화", payload={}),
        cl.Action(name="help", value="help", label="❓ 도움말", payload={}),
    ]


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    global agent

    # 프로젝트 경로 설정 UI
    settings_ui = await cl.ChatSettings(
        [
            cl.input_widget.TextInput(
                id="project_path",
                label="📁 프로젝트 경로",
                description="분석할 프로젝트의 절대 경로를 입력하세요",
                initial=str(Path.cwd()),
                placeholder="/path/to/your/project"
            ),
            cl.input_widget.Switch(
                id="auto_analyze",
                label="🔍 자동 분석",
                description="프로젝트를 자동으로 분석하고 RAG에 인덱싱",
                initial=True
            ),
            cl.input_widget.Switch(
                id="restore_session",
                label="🔄 세션 복원",
                description="이전 세션 데이터가 있으면 자동으로 복원",
                initial=True
            ),
        ]
    ).send()

    # 사용자가 설정한 프로젝트 경로 가져오기
    project_path = settings_ui.get("project_path", str(Path.cwd()))
    auto_analyze = settings_ui.get("auto_analyze", True)
    restore_session = settings_ui.get("restore_session", True)

    # 세션 복원 시도
    session_data = None
    if restore_session and await session_manager.session_exists(project_path):
        session_data = await session_manager.load_session(project_path)
        await cl.Message(
            content=f"✅ 이전 세션을 찾았습니다!\n"
                   f"- 마지막 접근: {session_data.get('last_accessed', 'Unknown')}\n"
                   f"- 분석된 파일: {session_data.get('analyzed_files_count', 0)}개"
        ).send()

    # CodingAgent 초기화
    agent = CodingAgent(project_path=project_path)

    # 세션 데이터가 있으면 복원
    if session_data:
        # RAG 인덱스 경로 설정
        rag_index_path = session_data.get("rag_index_path")
        if rag_index_path and os.path.exists(rag_index_path):
            # TODO: RAG 인덱스 로드 로직 추가
            pass

    # Get current LLM info
    llm_info = agent.get_llm_info()
    provider = llm_info["provider"]
    model = llm_info["model"]

    # 프로젝트 정보 표시
    project_info = f"""# 🤖 AI Coding Assistant

Welcome! I'm your AI coding assistant powered by **{provider}** ({model}).

## 📂 로드된 프로젝트
- **경로**: `{project_path}`
- **세션 복원**: {'✅ 활성화' if restore_session else '❌ 비활성화'}
- **자동 분석**: {'✅ 활성화' if auto_analyze else '❌ 비활성화'}

## 🎯 Capabilities
- 📁 **Local File Analysis**: I can read and understand your project files
- 🌐 **Web Search**: I can search for documentation and examples
- 📚 **RAG Knowledge**: Upload docs for me to reference
- ⚡ **Code Execution**: I can run code to verify solutions
- 🔄 **Multi-LLM**: Switch between Claude, OpenAI, Groq, and DeepInfra

## 💡 Tips
- 아래 버튼을 클릭하거나 자연어로 질문하세요
- 명령어 대신 **퀵 액션 버튼**을 사용할 수 있습니다

Ready to help! What would you like to work on?
"""

    # 초기 환영 메시지에는 전체 메뉴 표시
    await cl.Message(content=project_info, actions=get_full_menu_actions()).send()

    # 자동 분석 실행
    if auto_analyze and Path(project_path).exists():
        await cl.Message(content="🔍 프로젝트 자동 분석 중...").send()
        try:
            # 프로젝트 분석
            analysis = await agent.analyze_project()

            # 파일 트리 생성
            file_tree = await generate_file_tree(project_path)

            # 분석 결과 표시
            result_msg = f"""# 📊 프로젝트 분석 완료!

{analysis}

## 📁 파일 구조
```
{file_tree}
```

세션이 자동으로 저장되었습니다.
"""
            await cl.Message(content=result_msg).send()

            # 세션 저장
            await save_current_session(project_path, agent)

        except Exception as e:
            await cl.Message(content=f"⚠️ 자동 분석 중 오류: {e}").send()


async def generate_file_tree(project_path: str, max_depth: int = 3, max_files: int = 50) -> str:
    """
    프로젝트 파일 트리를 생성합니다.

    Args:
        project_path: 프로젝트 경로
        max_depth: 최대 깊이
        max_files: 최대 파일 수

    Returns:
        파일 트리 문자열
    """
    def build_tree(path: Path, prefix: str = "", depth: int = 0, file_count: list = [0]) -> list[str]:
        if depth > max_depth or file_count[0] >= max_files:
            return []

        tree_lines = []
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

            # 숨겨진 파일/디렉토리 제외
            items = [item for item in items if not item.name.startswith('.')]

            # node_modules, __pycache__ 등 제외
            exclude = {'node_modules', '__pycache__', '.git', 'venv', 'env', '.venv', 'dist', 'build'}
            items = [item for item in items if item.name not in exclude]

            for i, item in enumerate(items):
                if file_count[0] >= max_files:
                    tree_lines.append(f"{prefix}... (파일 수 제한 도달)")
                    break

                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                next_prefix = "    " if is_last else "│   "

                if item.is_dir():
                    tree_lines.append(f"{prefix}{current_prefix}📁 {item.name}/")
                    tree_lines.extend(build_tree(item, prefix + next_prefix, depth + 1, file_count))
                else:
                    tree_lines.append(f"{prefix}{current_prefix}📄 {item.name}")
                    file_count[0] += 1

        except PermissionError:
            tree_lines.append(f"{prefix}... (권한 없음)")

        return tree_lines

    root = Path(project_path)
    tree = [f"📁 {root.name}/"]
    tree.extend(build_tree(root))

    return "\n".join(tree)


async def save_current_session(project_path: str, agent: CodingAgent):
    """현재 세션을 저장합니다."""
    try:
        # 분석된 파일 목록 수집 (향후 구현)
        analyzed_files = []

        # 세션 데이터 저장
        await session_manager.save_session(
            project_path=project_path,
            analyzed_files=analyzed_files,
            settings={
                "llm_provider": agent.get_llm_info()["provider"],
                "project_loaded": True
            }
        )

        # 마지막 액세스 시간 업데이트
        await session_manager.update_last_accessed(project_path)

    except Exception as e:
        print(f"세션 저장 실패: {e}")


@cl.action_callback("analyze")
async def on_action_analyze(action: cl.Action):
    """프로젝트 분석 버튼 클릭"""
    await handle_command("/analyze")

@cl.action_callback("save_session")
async def on_action_save_session(action: cl.Action):
    """세션 저장 버튼 클릭"""
    await handle_command("/save-session")

@cl.action_callback("upload_docs")
async def on_action_upload_docs(action: cl.Action):
    """문서 업로드 버튼 클릭"""
    await handle_command("/upload")

@cl.action_callback("rag_stats")
async def on_action_rag_stats(action: cl.Action):
    """RAG 통계 버튼 클릭"""
    await handle_command("/stats")

@cl.action_callback("switch_llm")
async def on_action_switch_llm(action: cl.Action):
    """LLM 전환 버튼 클릭"""
    # LLM 선택 UI 표시
    res = await cl.AskActionMessage(
        content="어떤 LLM으로 전환하시겠습니까?",
        actions=[
            cl.Action(name="claude", value="claude", label="🤖 Claude (Anthropic)", payload={}),
            cl.Action(name="openai", value="openai", label="🟢 OpenAI GPT-4", payload={}),
            cl.Action(name="groq", value="groq", label="⚡ Groq (빠름)", payload={}),
            cl.Action(name="deepinfra", value="deepinfra", label="💰 DeepInfra (저렴)", payload={}),
        ],
    ).send()

    if res:
        await handle_command(f"/switch {res['value']}")

@cl.action_callback("claude")
async def on_llm_claude(action: cl.Action):
    await handle_command("/switch claude")

@cl.action_callback("openai")
async def on_llm_openai(action: cl.Action):
    await handle_command("/switch openai")

@cl.action_callback("groq")
async def on_llm_groq(action: cl.Action):
    await handle_command("/switch groq")

@cl.action_callback("deepinfra")
async def on_llm_deepinfra(action: cl.Action):
    await handle_command("/switch deepinfra")

@cl.action_callback("show_full_menu")
async def on_action_show_full_menu(action: cl.Action):
    """전체 메뉴 버튼 클릭 - 모든 기능 표시"""
    menu_msg = """# 🔧 전체 메뉴

모든 사용 가능한 기능:

**프로젝트 관리**: 분석, 세션 저장
**개발 도구**: 테스트, 코드 품질, 리뷰, 프로젝트 생성
**문서 & RAG**: 문서 업로드, 통계
**기타**: LLM 전환, 세션 관리, 도움말
"""
    await cl.Message(content=menu_msg, actions=get_full_menu_actions()).send()


@cl.action_callback("show_sessions")
async def on_action_show_sessions(action: cl.Action):
    """세션 목록 버튼 클릭"""
    await handle_command("/sessions")

@cl.action_callback("clear_chat")
async def on_action_clear_chat(action: cl.Action):
    """대화 초기화 버튼 클릭"""
    await handle_command("/clear-chat")

@cl.action_callback("help")
async def on_action_help(action: cl.Action):
    """도움말 버튼 클릭"""
    await handle_command("/help")


# Phase 2 도구 핸들러들
@cl.action_callback("run_tests")
async def on_action_run_tests(action: cl.Action):
    """테스트 실행 버튼 클릭"""
    global agent

    await cl.Message(content="🧪 테스트 실행 중...").send()

    try:
        from tools import TestRunner

        runner = TestRunner()

        # 프로젝트 경로의 tests 디렉토리에서 테스트 실행
        project_path = agent.project_path
        test_path = str(Path(project_path) / "tests")

        # tests 디렉토리가 없으면 프로젝트 전체에서 테스트
        if not Path(test_path).exists():
            test_path = project_path

        summary = await runner.run_tests(test_path=test_path, verbose=True)

        # 결과 포맷팅
        result_msg = f"""# 🧪 테스트 결과

## 📊 요약
- **전체**: {summary.total}개
- **✅ 통과**: {summary.passed}개
- **❌ 실패**: {summary.failed}개
- **⚠️ 에러**: {summary.error}개
- **⏭️ 스킵**: {summary.skipped}개
- **⏱️ 시간**: {summary.duration:.2f}초
"""

        if summary.coverage is not None:
            result_msg += f"- **📈 커버리지**: {summary.coverage:.1f}%\n"

        # 실패한 테스트 상세 정보
        if summary.failed > 0 or summary.error > 0:
            result_msg += "\n## ❌ 실패한 테스트\n\n"
            for result in summary.results:
                if result.status.value in ["failed", "error"]:
                    result_msg += f"### {result.test_name}\n"
                    result_msg += f"- **파일**: `{result.file_path}`\n"
                    if result.line_number:
                        result_msg += f"- **라인**: {result.line_number}\n"
                    if result.error_message:
                        result_msg += f"- **에러**: {result.error_message}\n"
                    result_msg += "\n"

        await cl.Message(content=result_msg).send()

    except FileNotFoundError:
        await cl.Message(
            content="⚠️ pytest가 설치되지 않았습니다.\n"
                   "설치: `pip install pytest pytest-cov`"
        ).send()
    except Exception as e:
        await cl.Message(content=f"❌ 테스트 실행 중 오류: {e}").send()


@cl.action_callback("check_quality")
async def on_action_check_quality(action: cl.Action):
    """코드 품질 검사 버튼 클릭"""
    global agent

    # 파일 선택 UI
    res = await cl.AskActionMessage(
        content="어떤 작업을 수행하시겠습니까?",
        actions=[
            cl.Action(name="format_code", value="format", label="✨ 코드 포매팅 (black)", payload={}),
            cl.Action(name="lint_code", value="lint", label="🔍 린팅 (flake8)", payload={}),
            cl.Action(name="analyze_pylint", value="pylint", label="📊 정적 분석 (pylint)", payload={}),
            cl.Action(name="auto_fix", value="autofix", label="🔧 자동 수정 (isort + black)", payload={}),
            cl.Action(name="check_all", value="all", label="🎯 종합 검사", payload={}),
        ],
    ).send()

    if not res:
        return

    action_type = res["value"]
    project_path = agent.project_path

    try:
        from tools import CodeQuality

        quality = CodeQuality()

        if action_type == "format":
            await cl.Message(content="✨ 코드 포매팅 중...").send()
            result = await quality.format_code(file_path=project_path)

            if result["success"]:
                msg = f"""# ✨ 코드 포매팅 완료

- **포맷팅된 파일**: {result.get('files_formatted', 0)}개
- **변경됨**: {result.get('files_changed', 0)}개
"""
                await cl.Message(content=msg).send()
            else:
                await cl.Message(content=f"⚠️ 포매팅 중 오류: {result.get('error')}").send()

        elif action_type == "lint":
            await cl.Message(content="🔍 린팅 중...").send()
            report = await quality.lint_code(file_path=project_path)

            msg = f"""# 🔍 린팅 결과

- **검사 파일**: `{report.file_path}`
- **발견된 이슈**: {len(report.issues)}개

"""
            if report.issues:
                msg += "## 이슈 목록\n\n"
                for issue in report.issues[:10]:  # 최대 10개만 표시
                    icon = "🔴" if issue.level.value == "error" else "🟡" if issue.level.value == "warning" else "🔵"
                    msg += f"{icon} **{issue.code}** (Line {issue.line_number}): {issue.message}\n"

                if len(report.issues) > 10:
                    msg += f"\n... 그 외 {len(report.issues) - 10}개 이슈\n"
            else:
                msg += "✅ 이슈가 없습니다!\n"

            await cl.Message(content=msg).send()

        elif action_type == "pylint":
            await cl.Message(content="📊 정적 분석 중... (시간이 걸릴 수 있습니다)").send()
            result = await quality.analyze_with_pylint(file_path=project_path)

            msg = f"""# 📊 Pylint 분석 결과

- **점수**: {result.get('score', 0):.2f}/10
- **이슈 수**: {len(result.get('issues', []))}개

"""
            issues = result.get('issues', [])
            if issues:
                msg += "## 주요 이슈\n\n"
                for issue in issues[:10]:
                    msg += f"- **{issue.code}** (Line {issue.line_number}): {issue.message}\n"

            await cl.Message(content=msg).send()

        elif action_type == "autofix":
            await cl.Message(content="🔧 자동 수정 중...").send()
            result = await quality.auto_fix(file_path=project_path)

            msg = f"""# 🔧 자동 수정 완료

- **import 정렬**: {'✅' if result.get('isort_success') else '❌'}
- **코드 포매팅**: {'✅' if result.get('format_success') else '❌'}
"""
            await cl.Message(content=msg).send()

        elif action_type == "all":
            await cl.Message(content="🎯 종합 검사 중... (시간이 걸릴 수 있습니다)").send()
            result = await quality.check_all(file_path=project_path, auto_fix=False)

            flake8_issues = len(result.get('flake8', {}).get('issues', []))
            pylint_score = result.get('pylint', {}).get('score', 0)

            msg = f"""# 🎯 종합 품질 검사 결과

## 📊 Flake8
- **이슈**: {flake8_issues}개

## 📊 Pylint
- **점수**: {pylint_score:.2f}/10

자동 수정을 원하시면 "🔧 자동 수정" 버튼을 클릭하세요.
"""
            await cl.Message(content=msg).send()

    except FileNotFoundError as e:
        await cl.Message(
            content=f"⚠️ 도구가 설치되지 않았습니다.\n"
                   f"설치: `pip install black flake8 pylint isort`"
        ).send()
    except Exception as e:
        await cl.Message(content=f"❌ 코드 품질 검사 중 오류: {e}").send()


@cl.action_callback("format_code")
@cl.action_callback("lint_code")
@cl.action_callback("analyze_pylint")
@cl.action_callback("auto_fix")
@cl.action_callback("check_all")
async def on_quality_sub_action(action: cl.Action):
    """코드 품질 하위 액션 핸들러"""
    # 이미 on_action_check_quality에서 처리됨
    pass


@cl.action_callback("review_code")
async def on_action_review_code(action: cl.Action):
    """코드 리뷰 버튼 클릭"""
    global agent

    # 파일 선택 안내
    files = await cl.AskFileMessage(
        content="📝 리뷰할 Python 파일을 선택하거나 업로드하세요",
        accept=[".py"],
        max_size_mb=5,
        max_files=1
    ).send()

    if not files:
        await cl.Message(content="파일이 선택되지 않았습니다.").send()
        return

    file = files[0]
    await cl.Message(content=f"📝 `{file.name}` 파일을 리뷰 중...").send()

    try:
        from agents import CodeReviewer
        from llm import LLMManager

        # 파일 읽기
        with open(file.path, 'r', encoding='utf-8') as f:
            code = f.read()

        # 코드 리뷰 실행
        llm_manager = LLMManager()
        reviewer = CodeReviewer(llm_manager)

        review = await reviewer.review_code(
            file_path=file.name,
            code=code,
            focus=["security", "performance", "readability"]
        )

        # 결과 포맷팅
        result_msg = f"""# 📝 코드 리뷰 결과

## 📊 전체 점수: {review.overall_score:.1f}/10

### ✅ 강점
"""
        for strength in review.strengths:
            result_msg += f"- {strength}\n"

        result_msg += "\n### ⚠️ 개선점\n"
        for weakness in review.weaknesses:
            result_msg += f"- {weakness}\n"

        result_msg += "\n### 📌 상세 코멘트\n\n"
        for comment in review.comments[:5]:  # 최대 5개만 표시
            icon = "🔴" if comment.level.value == "critical" else "🟠" if comment.level.value == "major" else "🟡" if comment.level.value == "minor" else "💡"
            result_msg += f"{icon} **{comment.level.value.upper()}**"
            if comment.line_number:
                result_msg += f" (Line {comment.line_number})"
            result_msg += f"\n- **이슈**: {comment.issue}\n"
            result_msg += f"- **제안**: {comment.suggestion}\n\n"

        if len(review.comments) > 5:
            result_msg += f"... 그 외 {len(review.comments) - 5}개 코멘트\n"

        await cl.Message(content=result_msg).send()

    except Exception as e:
        await cl.Message(content=f"❌ 코드 리뷰 중 오류: {e}").send()


@cl.action_callback("create_project")
async def on_action_create_project(action: cl.Action):
    """프로젝트 생성 버튼 클릭"""
    global agent

    # 템플릿 선택 UI
    res = await cl.AskActionMessage(
        content="어떤 프로젝트 템플릿을 생성하시겠습니까?",
        actions=[
            cl.Action(name="fastapi", value="fastapi", label="⚡ FastAPI - REST API", payload={}),
            cl.Action(name="flask", value="flask", label="🌶️ Flask - Web App", payload={}),
            cl.Action(name="cli", value="cli", label="💻 CLI - Command Line Tool", payload={}),
            cl.Action(name="library", value="library", label="📦 Library - Python Package", payload={}),
        ],
    ).send()

    if not res:
        return

    template_name = res["value"]

    # 프로젝트 이름 입력 받기
    project_name = await cl.AskUserMessage(
        content=f"🏗️ {template_name} 프로젝트 이름을 입력하세요:",
        timeout=60
    ).send()

    if not project_name:
        await cl.Message(content="프로젝트 이름이 입력되지 않았습니다.").send()
        return

    project_name = project_name["output"].strip()

    # 출력 디렉토리 (현재 프로젝트 경로)
    output_dir = agent.project_path

    await cl.Message(content=f"🏗️ `{project_name}` 프로젝트를 생성 중...").send()

    try:
        from tools import ProjectTemplates

        templates = ProjectTemplates()

        result = await templates.create_project(
            template_name=template_name,
            project_name=project_name,
            output_dir=output_dir
        )

        msg = f"""# 🎉 프로젝트 생성 완료!

## 📂 프로젝트 정보
- **이름**: {project_name}
- **템플릿**: {template_name}
- **경로**: `{result['project_path']}`
- **생성된 파일**: {result['files_created']}개
- **생성된 디렉토리**: {result['directories_created']}개

## 🚀 다음 단계

```bash
cd {project_name}
```
"""

        if template_name == "fastapi":
            msg += """
```bash
# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn app.main:app --reload

# http://localhost:8000/docs 접속
```
"""
        elif template_name == "flask":
            msg += """
```bash
# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
python run.py

# http://localhost:5000 접속
```
"""
        elif template_name == "cli":
            msg += """
```bash
# 패키지 설치 (editable mode)
pip install -e .

# CLI 실행
{project_name} --help
```
"""
        elif template_name == "library":
            msg += """
```bash
# 개발 의존성 설치
pip install -e .[dev]

# 테스트 실행
pytest

# 코드 포매팅
black src/
```
"""

        await cl.Message(content=msg).send()

    except Exception as e:
        await cl.Message(content=f"❌ 프로젝트 생성 중 오류: {e}").send()


@cl.action_callback("fastapi")
@cl.action_callback("flask")
@cl.action_callback("cli")
@cl.action_callback("library")
async def on_template_selected(action: cl.Action):
    """템플릿 선택 핸들러"""
    # 이미 on_action_create_project에서 처리됨
    pass


@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages."""
    global agent

    if agent is None:
        await cl.Message(content="Error: Agent not initialized. Please refresh the page.").send()
        return

    user_message = message.content.strip()

    # Handle commands
    if user_message.startswith("/"):
        await handle_command(user_message)
        return

    # Check for special flags in message
    use_web = "search" in user_message.lower() or "documentation" in user_message.lower()
    analyze_project = "analyze" in user_message.lower() or "project structure" in user_message.lower()

    # Process message with streaming
    msg = cl.Message(content="")
    await msg.send()

    async for chunk in agent.process_message(
        user_message,
        stream=True,
        use_rag=True,
        use_web=use_web,
        analyze_project=analyze_project
    ):
        await msg.stream_token(chunk)

    await msg.update()

    # 매 응답마다 핵심 버튼 표시
    await cl.Message(content="", actions=get_quick_actions()).send()


async def handle_command(command: str):
    """Handle special commands."""
    global agent

    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "/help":
        help_msg = """# 📖 Available Commands

## 프로젝트 관리
- `/load-project` - 프로젝트 다시 로드 (페이지 새로고침)
- `/save-session` - 현재 세션 저장
- `/sessions` - 저장된 세션 목록 보기
- `/analyze` - Analyze current project structure

## LLM 관리
- `/switch <provider>` - Switch LLM provider
  - Available: claude, openai, groq, deepinfra
  - Example: `/switch openai`
- `/current-llm` - Show current LLM provider

## 문서 및 검색
- `/search <query>` - Search web for documentation
  - Example: `/search python asyncio tutorial`
- `/upload` - Upload documentation for RAG
- `/stats` - Show RAG statistics
- `/clear-docs` - Clear all uploaded documentation

## 기타
- `/clear-chat` - Clear conversation history
- `/help` - Show this help message

## 💡 팁
- 프로젝트 경로는 초기 화면에서 설정할 수 있습니다
- 자동 분석을 활성화하면 프로젝트 파일이 자동으로 인덱싱됩니다
- 세션은 자동으로 저장되며 다음 접속 시 복원됩니다
"""
        await cl.Message(content=help_msg).send()

    elif cmd == "/switch":
        if not args:
            await cl.Message(content="Please specify a provider: claude, openai, groq, or deepinfra").send()
            return

        try:
            result = agent.switch_llm(args.lower())
            llm_info = agent.get_llm_info()
            await cl.Message(content=f"✅ {result}\nModel: {llm_info['model']}").send()
        except Exception as e:
            await cl.Message(content=f"❌ Error: {e}").send()

    elif cmd == "/current-llm":
        llm_info = agent.get_llm_info()
        msg = f"""**Current LLM Provider**
- Provider: {llm_info['provider']}
- Model: {llm_info['model']}
- API Key: {'✅ Configured' if llm_info['has_api_key'] else '❌ Not configured'}
"""
        await cl.Message(content=msg).send()

    elif cmd == "/analyze":
        await cl.Message(content="🔍 Analyzing project...").send()
        try:
            analysis = await agent.analyze_project()
            await cl.Message(content=f"# Project Analysis\n\n{analysis}").send()
        except Exception as e:
            await cl.Message(content=f"❌ Error analyzing project: {e}").send()

    elif cmd == "/search":
        if not args:
            await cl.Message(content="Please provide a search query").send()
            return

        await cl.Message(content=f"🔍 Searching for: {args}...").send()
        try:
            results = await agent.web_search.search_documentation(args)
            if results:
                msg = "# Search Results\n\n"
                for i, result in enumerate(results[:5], 1):
                    msg += f"{i}. **{result['title']}**\n"
                    msg += f"   {result['url']}\n"
                    msg += f"   {result['snippet']}\n\n"
                await cl.Message(content=msg).send()
            else:
                await cl.Message(content="No results found.").send()
        except Exception as e:
            await cl.Message(content=f"❌ Error searching: {e}").send()

    elif cmd == "/upload":
        files = await cl.AskFileMessage(
            content="Please upload documentation files (PDF, DOCX, TXT, MD, code files)",
            accept=["text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".md", ".py", ".js", ".ts"],
            max_size_mb=10,
            max_files=10
        ).send()

        if files:
            await cl.Message(content=f"📤 Uploading {len(files)} file(s)...").send()
            total_added = 0

            for file in files:
                try:
                    count = await agent.add_document_to_rag(file.path)
                    total_added += count
                except Exception as e:
                    await cl.Message(content=f"❌ Error processing {file.name}: {e}").send()

            await cl.Message(content=f"✅ Added {total_added} document chunks to knowledge base").send()

    elif cmd == "/stats":
        stats = agent.get_rag_stats()
        msg = f"""# 📊 RAG Statistics

- Total documents: {stats['total_documents']}
- Unique sources: {stats['unique_sources']}
- File types: {', '.join(stats['file_types']) if stats['file_types'] else 'None'}

**Sources:**
"""
        for source in stats['sources'][:10]:
            msg += f"- {source}\n"

        await cl.Message(content=msg).send()

    elif cmd == "/clear-docs":
        agent.clear_rag()
        await cl.Message(content="✅ Cleared all uploaded documentation").send()

    elif cmd == "/clear-chat":
        agent.clear_conversation()
        await cl.Message(content="✅ Cleared conversation history").send()

    elif cmd == "/save-session":
        project_path = agent.project_path
        await cl.Message(content="💾 세션 저장 중...").send()
        try:
            await save_current_session(project_path, agent)
            await cl.Message(content=f"✅ 세션이 저장되었습니다.\n경로: {project_path}").send()
        except Exception as e:
            await cl.Message(content=f"❌ 세션 저장 실패: {e}").send()

    elif cmd == "/load-project":
        await cl.Message(content="📂 프로젝트 다시 로드하려면 새로고침(F5)하세요.").send()

    elif cmd == "/sessions":
        await cl.Message(content="📊 저장된 세션 목록 조회 중...").send()
        try:
            sessions = await session_manager.list_sessions()
            if sessions:
                msg = "# 💾 저장된 세션 목록\n\n"
                for i, session in enumerate(sessions, 1):
                    msg += f"{i}. **{session.get('project_path', 'Unknown')}**\n"
                    msg += f"   - 마지막 접근: {session.get('last_accessed', 'Unknown')}\n"
                    msg += f"   - 분석된 파일: {session.get('analyzed_files_count', 0)}개\n"
                    msg += f"   - 대화 기록: {session.get('history_count', 0)}개\n\n"
                await cl.Message(content=msg).send()
            else:
                await cl.Message(content="저장된 세션이 없습니다.").send()
        except Exception as e:
            await cl.Message(content=f"❌ 세션 목록 조회 실패: {e}").send()

    else:
        await cl.Message(content=f"Unknown command: {cmd}\nType /help for available commands").send()


@cl.on_settings_update
async def setup_agent(settings):
    """Handle settings updates."""
    global agent
    # Could update agent settings here if needed
    pass


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
