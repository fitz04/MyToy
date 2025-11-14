"""Chainlit application for the coding agent."""
import chainlit as cl
from pathlib import Path
from typing import Optional

from agents import CodingAgent
from config import settings


# Global agent instance
agent: Optional[CodingAgent] = None


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    global agent

    # Get project path from settings or use current directory
    project_path = cl.user_session.get("project_path", str(Path.cwd()))
    agent = CodingAgent(project_path=project_path)

    # Get current LLM info
    llm_info = agent.get_llm_info()
    provider = llm_info["provider"]
    model = llm_info["model"]

    # Welcome message
    welcome_msg = f"""# 🤖 AI Coding Assistant

Welcome! I'm your AI coding assistant powered by **{provider}** ({model}).

## 🎯 Capabilities
- 📁 **Local File Analysis**: I can read and understand your project files
- 🌐 **Web Search**: I can search for documentation and examples
- 📚 **RAG Knowledge**: Upload docs for me to reference
- ⚡ **Code Execution**: I can run code to verify solutions
- 🔄 **Multi-LLM**: Switch between Claude, OpenAI, Groq, and DeepInfra

## 📝 Available Commands
- `/switch <provider>` - Switch LLM provider (claude, openai, groq, deepinfra)
- `/analyze` - Analyze current project structure
- `/search <query>` - Search the web for documentation
- `/upload` - Upload documentation for RAG
- `/stats` - Show RAG statistics
- `/clear-docs` - Clear uploaded documentation
- `/clear-chat` - Clear conversation history
- `/help` - Show this help message

## 💡 Tips
- Ask me to analyze your code, explain concepts, or help debug issues
- I can search the web for official documentation when needed
- Upload your project docs for better context-aware assistance

Ready to help! What would you like to work on?
"""

    await cl.Message(content=welcome_msg).send()


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

- `/switch <provider>` - Switch LLM provider
  - Available: claude, openai, groq, deepinfra
  - Example: `/switch openai`

- `/analyze` - Analyze current project structure
  - Shows file statistics and structure

- `/search <query>` - Search web for documentation
  - Example: `/search python asyncio tutorial`

- `/upload` - Upload documentation for RAG
  - Click to upload files (PDF, DOCX, TXT, MD, code files)

- `/stats` - Show RAG statistics
  - Display info about uploaded documents

- `/clear-docs` - Clear all uploaded documentation
  - Removes all documents from RAG

- `/clear-chat` - Clear conversation history
  - Start fresh conversation

- `/current-llm` - Show current LLM provider

- `/help` - Show this help message
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
