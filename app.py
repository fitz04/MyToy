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

    # 퀵 액션 버튼 생성
    actions = [
        cl.Action(name="analyze", value="analyze", label="📊 프로젝트 분석"),
        cl.Action(name="save_session", value="save_session", label="💾 세션 저장"),
        cl.Action(name="upload_docs", value="upload_docs", label="📤 문서 업로드"),
        cl.Action(name="rag_stats", value="rag_stats", label="📈 RAG 통계"),
        cl.Action(name="switch_llm", value="switch_llm", label="🔄 LLM 전환"),
        cl.Action(name="show_sessions", value="show_sessions", label="💾 세션 목록"),
        cl.Action(name="clear_chat", value="clear_chat", label="🗑️ 대화 초기화"),
        cl.Action(name="help", value="help", label="❓ 도움말"),
    ]

    await cl.Message(content=project_info, actions=actions).send()

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
            cl.Action(name="claude", value="claude", label="🤖 Claude (Anthropic)"),
            cl.Action(name="openai", value="openai", label="🟢 OpenAI GPT-4"),
            cl.Action(name="groq", value="groq", label="⚡ Groq (빠름)"),
            cl.Action(name="deepinfra", value="deepinfra", label="💰 DeepInfra (저렴)"),
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
