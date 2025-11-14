# 🤖 AI Coding Assistant

Welcome to your AI Coding Assistant! This tool combines the power of multiple LLMs with advanced capabilities to help you with your coding tasks.

## Features

### 🧠 Multi-LLM Support
Switch between different LLM providers on the fly:
- **Claude** (Anthropic) - Best for complex reasoning and code analysis
- **OpenAI GPT-4** - Great for general coding tasks
- **Groq** - Ultra-fast inference for quick tasks
- **DeepInfra** - Cost-effective for high-volume tasks

### 📁 Local File Analysis
The assistant can:
- Read and analyze your project files
- Understand your codebase structure
- Search through your code
- Parse and explain code structure

### 🌐 Web Search
Search for:
- Official documentation
- API references
- Code examples
- Tutorials and guides

### 📚 RAG (Retrieval Augmented Generation)
- Upload your project documentation
- Upload API references
- Upload any reference materials
- The assistant will use these docs to provide accurate, context-aware help

### ⚡ Code Execution
- Execute Python, JavaScript, and Bash code
- Verify solutions
- Test code snippets
- Debug issues

## Getting Started

1. **Choose your LLM**: Use `/switch <provider>` to select your preferred LLM
2. **Upload docs** (optional): Use `/upload` to add reference documentation
3. **Ask questions**: Just type your questions or requests naturally
4. **Get help**: Type `/help` to see all available commands

## Example Interactions

### Code Review
```
Can you review this Python function and suggest improvements?

def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
```

### Debug Help
```
I'm getting a "TypeError: 'NoneType' object is not iterable" error in my code.
Can you help me debug it?
```

### Documentation Search
```
Search for the latest documentation on Python asyncio
```

### Code Explanation
```
Can you explain how async/await works in JavaScript with examples?
```

## Tips

- Be specific about what you need help with
- Provide context about your project when relevant
- Upload relevant documentation for better accuracy
- Use web search when you need the latest information
- Switch LLMs based on your task (Claude for analysis, Groq for speed, etc.)

Ready to start coding? Ask me anything!
