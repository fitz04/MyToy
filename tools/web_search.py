"""Web search tool for finding documentation and resources."""
import asyncio
from typing import List, Dict, Optional
from duckduckgo_search import AsyncDDGS
import aiohttp
from bs4 import BeautifulSoup
from config import settings


class WebSearchTool:
    """Tool for searching the web and fetching documentation."""

    def __init__(self):
        self.max_results = settings.max_search_results
        self.enabled = settings.enable_web_search

    async def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """Search the web using DuckDuckGo."""
        if not self.enabled:
            return []

        max_results = max_results or self.max_results
        results = []

        try:
            async with AsyncDDGS() as ddgs:
                search_results = await ddgs.text(query, max_results=max_results)

                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                    })
        except Exception as e:
            print(f"Search error: {e}")

        return results

    async def fetch_page_content(self, url: str, max_length: int = 10000) -> Dict[str, str]:
        """Fetch and extract main content from a web page."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        return {
                            "url": url,
                            "error": f"HTTP {response.status}",
                        }

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Remove script and style elements
                    for script in soup(["script", "style", "nav", "header", "footer"]):
                        script.decompose()

                    # Get text
                    text = soup.get_text()

                    # Clean up text
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)

                    # Truncate if too long
                    if len(text) > max_length:
                        text = text[:max_length] + "... [truncated]"

                    return {
                        "url": url,
                        "title": soup.title.string if soup.title else "",
                        "content": text,
                    }
        except asyncio.TimeoutError:
            return {"url": url, "error": "Timeout"}
        except Exception as e:
            return {"url": url, "error": str(e)}

    async def search_documentation(self, query: str, doc_site: Optional[str] = None) -> List[Dict]:
        """Search for documentation on specific sites or in general."""
        # Add documentation keywords to query
        doc_query = f"{query} documentation"

        if doc_site:
            doc_query = f"site:{doc_site} {query}"

        results = await self.search(doc_query)

        # Optionally fetch content from top results
        enhanced_results = []
        for result in results[:3]:  # Fetch content for top 3 results
            content = await self.fetch_page_content(result["url"])
            enhanced_results.append({
                **result,
                "content": content.get("content", ""),
                "fetch_error": content.get("error"),
            })

        return enhanced_results

    async def search_code_examples(self, query: str, language: Optional[str] = None) -> List[Dict]:
        """Search for code examples."""
        code_query = f"{query} code example"
        if language:
            code_query += f" {language}"

        # Search on GitHub, Stack Overflow, etc.
        code_query += " site:github.com OR site:stackoverflow.com"

        return await self.search(code_query)

    async def search_api_docs(self, library: str, method: Optional[str] = None) -> List[Dict]:
        """Search for API documentation for a specific library."""
        if method:
            query = f"{library} {method} API documentation"
        else:
            query = f"{library} API documentation"

        return await self.search_documentation(query)
