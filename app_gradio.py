"""Gradio application for the coding agent - 고정 UI 버전"""
import gradio as gr
from pathlib import Path
from typing import Optional, List, Tuple
import asyncio

from agents import CodingAgent
from config import settings
from utils import get_session_manager
from tools import TestRunner, CodeQuality, ProjectTemplates

# Global instances
agent: Optional[CodingAgent] = None
session_manager = get_session_manager()
current_project_path = str(Path.cwd())


async def initialize_agent(project_path: str, auto_analyze: bool):
    """에이전트 초기화"""
    global agent, current_project_path

    try:
        current_project_path = project_path
        agent = CodingAgent(project_path=project_path)

        msg = f"✅ 에이전트 초기화 완료!\n\n**프로젝트**: `{project_path}`"

        if auto_analyze and Path(project_path).exists():
            msg += "\n\n🔍 프로젝트 분석 중..."
            # 프로젝트 분석은 백그라운드에서
            # 실제로는 asyncio.create_task로 비동기 실행

        return msg
    except Exception as e:
        return f"❌ 초기화 실패: {e}"


async def chat(message: str, history: List[Tuple[str, str]]):
    """채팅 메시지 처리"""
    global agent

    if not agent:
        history.append((message, "❌ 에이전트가 초기화되지 않았습니다. 먼저 프로젝트를 로드하세요."))
        return history, ""

    if not message.strip():
        return history, ""

    # 스트리밍 응답
    response = ""
    try:
        async for chunk in agent.process_message(
            message,
            stream=True,
            use_rag=True,
            use_web=False
        ):
            response += chunk
    except Exception as e:
        response = f"❌ 오류 발생: {e}"

    history.append((message, response))
    return history, ""


async def run_tests():
    """테스트 실행"""
    try:
        runner = TestRunner()
        result = await runner.run_tests(verbose=True)

        msg = f"""# 🧪 테스트 실행 결과

**총 테스트**: {result.get('total', 0)}개
**통과**: {result.get('passed', 0)}개 ✅
**실패**: {result.get('failed', 0)}개 ❌
**에러**: {result.get('errors', 0)}개 ⚠️
**스킵**: {result.get('skipped', 0)}개 ⏭️

**커버리지**: {result.get('coverage', 'N/A')}%
"""

        if result.get('failed', 0) > 0:
            msg += "\n## 실패한 테스트\n"
            for fail in result.get('failures', [])[:5]:
                msg += f"- `{fail}`\n"

        return msg
    except Exception as e:
        return f"❌ 테스트 실행 실패: {e}"


async def check_quality_format():
    """코드 포매팅"""
    try:
        checker = CodeQuality()
        result = await checker.format_code(current_project_path)
        return f"✅ 코드 포매팅 완료!\n\n{result}"
    except Exception as e:
        return f"❌ 포매팅 실패: {e}"


async def check_quality_lint():
    """린팅 검사"""
    try:
        checker = CodeQuality()
        result = await checker.lint_code(current_project_path)
        return f"🔍 린팅 결과:\n\n{result}"
    except Exception as e:
        return f"❌ 린팅 실패: {e}"


async def check_quality_all():
    """종합 검사"""
    try:
        checker = CodeQuality()
        result = await checker.check_all(current_project_path)
        return f"🎯 종합 검사 결과:\n\n{result}"
    except Exception as e:
        return f"❌ 검사 실패: {e}"


async def review_code_file(file_path: str):
    """코드 리뷰"""
    global agent

    if not file_path:
        return "❌ 파일을 선택하세요."

    try:
        from agents import CodeReviewer

        reviewer = CodeReviewer(agent.llm_manager if agent else None)

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        review = await reviewer.review_code(file_path, code)

        result = f"""# 📝 코드 리뷰 결과

**파일**: `{Path(file_path).name}`
**점수**: {review.get('score', 0)}/10

## 강점
{review.get('strengths', 'N/A')}

## 개선점
{review.get('weaknesses', 'N/A')}

## 주요 코멘트
"""
        for comment in review.get('comments', [])[:10]:
            severity = comment.get('severity', 'INFO')
            msg = comment.get('message', '')
            result += f"\n**[{severity}]** {msg}"

        return result
    except Exception as e:
        return f"❌ 리뷰 실패: {e}"


async def create_new_project(template: str, name: str, output_dir: str):
    """프로젝트 생성"""
    try:
        templates = ProjectTemplates()

        template_map = {
            "FastAPI": "fastapi",
            "Flask": "flask",
            "CLI": "cli",
            "Library": "library"
        }

        template_name = template_map.get(template, "fastapi")
        result = await templates.create_project(template_name, name, output_dir)

        msg = f"""✅ 프로젝트 생성 완료!

**템플릿**: {template}
**이름**: {name}
**경로**: `{result['path']}`

## 다음 단계
"""

        if template == "FastAPI":
            msg += """
```bash
cd {path}
pip install -r requirements.txt
uvicorn main:app --reload
# http://localhost:8000/docs 접속
```
""".format(path=result['path'])
        elif template == "Flask":
            msg += """
```bash
cd {path}
pip install -r requirements.txt
python run.py
# http://localhost:5000 접속
```
""".format(path=result['path'])
        elif template == "CLI":
            msg += """
```bash
cd {path}
pip install -e .
{name} --help
```
""".format(path=result['path'], name=name)
        else:  # Library
            msg += """
```bash
cd {path}
pip install -e .[dev]
pytest
```
""".format(path=result['path'])

        return msg
    except Exception as e:
        return f"❌ 프로젝트 생성 실패: {e}"


def create_ui():
    """Gradio UI 생성"""

    with gr.Blocks(
        theme=gr.themes.Soft(),
        title="🤖 AI Coding Agent (Gradio)",
        css="""
        .quick-button { min-height: 50px !important; }
        """
    ) as app:

        gr.Markdown("# 🤖 AI Coding Agent - Gradio Edition")

        # 상단: 프로젝트 설정
        with gr.Row():
            with gr.Column(scale=3):
                project_path = gr.Textbox(
                    label="📁 프로젝트 경로",
                    value=str(Path.cwd()),
                    placeholder="/path/to/your/project"
                )
            with gr.Column(scale=1):
                auto_analyze = gr.Checkbox(label="🔍 자동 분석", value=True)
            with gr.Column(scale=1):
                load_btn = gr.Button("🚀 프로젝트 로드", variant="primary", size="lg")

        init_status = gr.Markdown("⏳ 프로젝트를 로드하세요.")

        gr.Markdown("---")

        # 메인 영역: 채팅 + 사이드바
        with gr.Row():
            # 왼쪽: 채팅 영역 (65%)
            with gr.Column(scale=65):
                chatbot = gr.Chatbot(
                    label="💬 대화",
                    height=500,
                    show_label=False,
                    bubble_full_width=False,
                    avatar_images=(None, "🤖")
                )

                with gr.Row():
                    msg_input = gr.Textbox(
                        label="메시지",
                        placeholder="무엇을 도와드릴까요?",
                        scale=9,
                        show_label=False,
                        container=False
                    )
                    send_btn = gr.Button("전송", scale=1, variant="primary")

            # 오른쪽: 고정 버튼 패널 (35%)
            with gr.Column(scale=35):
                gr.Markdown("## 🔧 빠른 도구")

                # 핵심 도구들
                with gr.Accordion("🧪 테스트 & 품질", open=True):
                    test_btn = gr.Button("🧪 테스트 실행", size="lg", elem_classes=["quick-button"])

                    with gr.Row():
                        format_btn = gr.Button("✨ 포매팅", size="sm")
                        lint_btn = gr.Button("🔍 린팅", size="sm")

                    quality_all_btn = gr.Button("🎯 종합 검사", size="sm")

                # 코드 리뷰
                with gr.Accordion("📝 코드 리뷰", open=False):
                    review_file = gr.File(
                        label="Python 파일 선택",
                        file_types=[".py"],
                        type="filepath"
                    )
                    review_btn = gr.Button("📝 리뷰 시작", variant="secondary")

                # 프로젝트 생성
                with gr.Accordion("🏗️ 프로젝트 생성", open=False):
                    template_radio = gr.Radio(
                        choices=["FastAPI", "Flask", "CLI", "Library"],
                        label="템플릿",
                        value="FastAPI"
                    )
                    project_name = gr.Textbox(
                        label="프로젝트 이름",
                        placeholder="my-awesome-project"
                    )
                    output_dir = gr.Textbox(
                        label="출력 디렉토리",
                        value="./projects"
                    )
                    create_btn = gr.Button("🏗️ 생성", variant="secondary")

                # 설정
                with gr.Accordion("⚙️ 설정", open=False):
                    llm_dropdown = gr.Dropdown(
                        choices=["claude", "openai", "groq", "deepinfra"],
                        value="claude",
                        label="🤖 LLM 선택",
                        interactive=True
                    )
                    clear_btn = gr.Button("🗑️ 대화 초기화", size="sm")

        # 하단: 결과 표시 영역
        with gr.Row():
            output_display = gr.Markdown(label="결과", visible=False)

        # 이벤트 핸들러 연결

        # 프로젝트 로드
        load_btn.click(
            fn=lambda p, a: asyncio.run(initialize_agent(p, a)),
            inputs=[project_path, auto_analyze],
            outputs=[init_status]
        )

        # 채팅
        def chat_wrapper(msg, history):
            return asyncio.run(chat(msg, history))

        send_btn.click(
            fn=chat_wrapper,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )

        msg_input.submit(
            fn=chat_wrapper,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )

        # 테스트 실행
        def test_wrapper():
            result = asyncio.run(run_tests())
            return gr.Markdown(value=result, visible=True)

        test_btn.click(
            fn=test_wrapper,
            outputs=[output_display]
        )

        # 코드 품질
        format_btn.click(
            fn=lambda: gr.Markdown(value=asyncio.run(check_quality_format()), visible=True),
            outputs=[output_display]
        )

        lint_btn.click(
            fn=lambda: gr.Markdown(value=asyncio.run(check_quality_lint()), visible=True),
            outputs=[output_display]
        )

        quality_all_btn.click(
            fn=lambda: gr.Markdown(value=asyncio.run(check_quality_all()), visible=True),
            outputs=[output_display]
        )

        # 코드 리뷰
        review_btn.click(
            fn=lambda f: gr.Markdown(value=asyncio.run(review_code_file(f)), visible=True),
            inputs=[review_file],
            outputs=[output_display]
        )

        # 프로젝트 생성
        create_btn.click(
            fn=lambda t, n, o: gr.Markdown(value=asyncio.run(create_new_project(t, n, o)), visible=True),
            inputs=[template_radio, project_name, output_dir],
            outputs=[output_display]
        )

        # 대화 초기화
        clear_btn.click(
            fn=lambda: [],
            outputs=[chatbot]
        )

    return app


if __name__ == "__main__":
    print("🚀 Gradio 앱 시작...")
    print("📍 URL: http://localhost:7860")
    print("\n두 가지 UI 비교:")
    print("  - Chainlit: chainlit run app.py -w")
    print("  - Gradio:   python app_gradio.py")

    app = create_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
