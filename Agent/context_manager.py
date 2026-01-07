"""
Context Manager for the Autonomous Game Development Agent.

This module handles context window management, including:
- Token counting and budget tracking
- Conversation summarization
- Retrieval-Augmented Generation (RAG) with local vector store
- Prompt caching optimization
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from config import get_config, ContextConfig


logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A single message in the conversation."""
    role: str  # "user", "assistant", or "system"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    token_estimate: int = 0
    cached: bool = False

    def __post_init__(self):
        if self.token_estimate == 0:
            # Rough estimation: ~4 characters per token
            self.token_estimate = len(self.content) // 4


@dataclass
class ContextWindow:
    """Represents the current context window state."""
    messages: List[Message]
    system_prompt: str
    summary: Optional[str] = None
    total_tokens: int = 0
    cached_tokens: int = 0


class TokenCounter:
    """Utility class for counting tokens."""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count for text."""
        # Claude uses roughly 4 characters per token on average
        return len(text) // 4

    @staticmethod
    def estimate_message_tokens(message: Dict[str, str]) -> int:
        """Estimate tokens for a message dict."""
        content = message.get("content", "")
        # Add overhead for role and formatting
        return TokenCounter.estimate_tokens(content) + 4


class ConversationSummarizer:
    """
    Handles summarization of conversation history.

    When context grows too large, this class compresses older
    messages into a concise summary.
    """

    def __init__(self):
        self.summary_prompt = """Summarize the following conversation history into concise bullet points.
Focus on:
- Key architectural decisions made
- Important code patterns established
- Errors encountered and how they were resolved
- Current state of the task

Keep the summary under 500 words. Use bullet points for clarity."""

    def create_summary(self, messages: List[Message]) -> str:
        """
        Create a summary of messages.

        Note: In production, this would call the LLM API.
        Here we provide a template for the summary structure.
        """
        # Group messages by topic/task for better summarization
        summary_parts = []

        # Extract key decisions
        decisions = []
        errors = []
        completions = []

        for msg in messages:
            content_lower = msg.content.lower()
            if "decided" in content_lower or "will use" in content_lower:
                decisions.append(msg.content[:200])
            if "error" in content_lower or "failed" in content_lower:
                errors.append(msg.content[:200])
            if "completed" in content_lower or "finished" in content_lower:
                completions.append(msg.content[:200])

        if decisions:
            summary_parts.append("**Key Decisions:**")
            for d in decisions[:5]:
                summary_parts.append(f"- {d}")

        if errors:
            summary_parts.append("\n**Resolved Issues:**")
            for e in errors[:3]:
                summary_parts.append(f"- {e}")

        if completions:
            summary_parts.append("\n**Completed Tasks:**")
            for c in completions[:5]:
                summary_parts.append(f"- {c}")

        return "\n".join(summary_parts) if summary_parts else "No significant history to summarize."

    def should_summarize(self, total_tokens: int, max_tokens: int, threshold: float = 0.8) -> bool:
        """Check if summarization should be triggered."""
        return total_tokens > (max_tokens * threshold)


class VectorStore:
    """
    Simple vector store for Retrieval-Augmented Generation.

    In production, this would use ChromaDB or FAISS.
    This implementation provides a basic keyword-based fallback.
    """

    def __init__(self, store_path: Optional[Path] = None):
        config = get_config()
        self.store_path = store_path or (config.workspace.root_path / config.context.vector_db_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.store_path / "index.json"
        self._index: Dict[str, Dict[str, Any]] = {}
        self._load_index()

    def _load_index(self) -> None:
        """Load the index from disk."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    self._index = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load vector index: {e}")
                self._index = {}

    def _save_index(self) -> None:
        """Save the index to disk."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self._index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save vector index: {e}")

    def _generate_id(self, content: str, source: str) -> str:
        """Generate a unique ID for a document."""
        hash_input = f"{source}:{content[:100]}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for basic search."""
        # Remove common words and split
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be",
                      "been", "being", "have", "has", "had", "do", "does",
                      "did", "will", "would", "could", "should", "may",
                      "might", "must", "to", "of", "in", "for", "on", "with",
                      "at", "by", "from", "as", "into", "through", "during",
                      "before", "after", "above", "below", "between", "under",
                      "again", "further", "then", "once", "here", "there",
                      "when", "where", "why", "how", "all", "each", "few",
                      "more", "most", "other", "some", "such", "no", "nor",
                      "not", "only", "own", "same", "so", "than", "too",
                      "very", "just", "and", "but", "if", "or", "because",
                      "until", "while", "this", "that", "these", "those"}

        words = text.lower().split()
        keywords = [w.strip('.,;:!?"\'()[]{}') for w in words
                    if len(w) > 2 and w.lower() not in stop_words]
        return list(set(keywords))

    def add_document(self, content: str, source: str, metadata: Optional[Dict] = None) -> str:
        """
        Add a document to the vector store.

        Args:
            content: The document content
            source: Source file or identifier
            metadata: Optional metadata

        Returns:
            Document ID
        """
        doc_id = self._generate_id(content, source)
        keywords = self._extract_keywords(content)

        self._index[doc_id] = {
            "content": content,
            "source": source,
            "keywords": keywords,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat()
        }

        self._save_index()
        logger.debug(f"Added document {doc_id} from {source}")
        return doc_id

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of matching documents with scores
        """
        query_keywords = set(self._extract_keywords(query))

        results = []
        for doc_id, doc in self._index.items():
            doc_keywords = set(doc["keywords"])
            # Simple keyword overlap scoring
            overlap = len(query_keywords & doc_keywords)
            if overlap > 0:
                score = overlap / max(len(query_keywords), len(doc_keywords))
                results.append({
                    "id": doc_id,
                    "content": doc["content"],
                    "source": doc["source"],
                    "score": score,
                    "metadata": doc["metadata"]
                })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def index_swift_file(self, file_path: Path) -> None:
        """Index a Swift source file for RAG."""
        if not file_path.exists():
            return

        try:
            content = file_path.read_text()
            # Split into chunks for better retrieval
            chunks = self._chunk_code(content)

            for i, chunk in enumerate(chunks):
                self.add_document(
                    content=chunk,
                    source=str(file_path),
                    metadata={"chunk_index": i, "language": "swift"}
                )
        except Exception as e:
            logger.warning(f"Failed to index {file_path}: {e}")

    def _chunk_code(self, code: str, chunk_size: int = 500) -> List[str]:
        """Split code into chunks, respecting function boundaries."""
        chunks = []
        lines = code.split('\n')
        current_chunk = []
        current_size = 0

        for line in lines:
            line_size = len(line)

            # Check for natural break points (function/class definitions)
            is_definition = any(line.strip().startswith(kw) for kw in
                                ['func ', 'class ', 'struct ', 'enum ', 'protocol ', 'extension '])

            if is_definition and current_chunk and current_size > chunk_size // 2:
                # Start new chunk at definition
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            elif current_size + line_size > chunk_size:
                # Chunk full, start new one
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks

    def clear(self) -> None:
        """Clear all documents from the store."""
        self._index = {}
        self._save_index()


class ContextManager:
    """
    Main context manager for the agent.

    Coordinates token counting, summarization, and RAG
    to optimize context window usage.
    """

    def __init__(self, config: Optional[ContextConfig] = None):
        agent_config = get_config()
        self.config = config or agent_config.context
        self.messages: List[Message] = []
        self.system_prompt: str = ""
        self.summary: Optional[str] = None
        self.summarizer = ConversationSummarizer()
        self.vector_store = VectorStore()
        self._cached_prompt_hash: Optional[str] = None

    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt (cached for cost optimization)."""
        self.system_prompt = prompt
        self._cached_prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()

    def add_message(self, role: str, content: str) -> Message:
        """Add a message to the conversation."""
        message = Message(role=role, content=content)
        self.messages.append(message)

        # Check if summarization needed
        if self._should_summarize():
            self._perform_summarization()

        return message

    def get_total_tokens(self) -> int:
        """Get total token count for current context."""
        total = TokenCounter.estimate_tokens(self.system_prompt)
        if self.summary:
            total += TokenCounter.estimate_tokens(self.summary)
        total += sum(m.token_estimate for m in self.messages)
        return total

    def _should_summarize(self) -> bool:
        """Check if summarization should be triggered."""
        return self.summarizer.should_summarize(
            self.get_total_tokens(),
            self.config.max_context_tokens,
            self.config.safety_threshold
        )

    def _perform_summarization(self) -> None:
        """Perform summarization of older messages."""
        if len(self.messages) < 10:
            return  # Not enough messages to summarize

        # Calculate how many messages to summarize
        num_to_summarize = int(len(self.messages) * self.config.summarization_ratio)
        to_summarize = self.messages[:num_to_summarize]
        to_keep = self.messages[num_to_summarize:]

        # Create summary
        new_summary = self.summarizer.create_summary(to_summarize)

        # Combine with existing summary if present
        if self.summary:
            self.summary = f"{self.summary}\n\n---\n\n{new_summary}"
        else:
            self.summary = new_summary

        # Keep only recent messages
        self.messages = to_keep
        logger.info(f"Summarized {num_to_summarize} messages, {len(to_keep)} remaining")

    def get_context_for_api(self) -> List[Dict[str, str]]:
        """
        Get the conversation context formatted for the API.

        Returns:
            List of message dictionaries for the API call
        """
        api_messages = []

        # Add summary as a system message if present
        if self.summary:
            api_messages.append({
                "role": "user",
                "content": f"[Previous conversation summary]\n{self.summary}"
            })
            api_messages.append({
                "role": "assistant",
                "content": "I understand the previous context. Let me continue from where we left off."
            })

        # Add recent messages
        for msg in self.messages:
            api_messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return api_messages

    def get_relevant_context(self, query: str, max_tokens: int = 2000) -> str:
        """
        Get relevant context from vector store for a query.

        Args:
            query: The query to find context for
            max_tokens: Maximum tokens to return

        Returns:
            Relevant context as a string
        """
        results = self.vector_store.search(query, top_k=10)

        context_parts = []
        current_tokens = 0

        for result in results:
            content = result["content"]
            tokens = TokenCounter.estimate_tokens(content)

            if current_tokens + tokens > max_tokens:
                break

            source = result["source"]
            context_parts.append(f"// From: {source}\n{content}")
            current_tokens += tokens

        return "\n\n".join(context_parts)

    def clear(self) -> None:
        """Clear the conversation history."""
        self.messages = []
        self.summary = None
        logger.info("Cleared conversation context")

    def get_state(self) -> Dict[str, Any]:
        """Get serializable state for checkpointing."""
        return {
            "messages": [{"role": m.role, "content": m.content, "timestamp": m.timestamp}
                         for m in self.messages],
            "summary": self.summary,
            "system_prompt_hash": self._cached_prompt_hash
        }

    def restore_state(self, state: Dict[str, Any]) -> None:
        """Restore state from checkpoint."""
        self.messages = [
            Message(role=m["role"], content=m["content"], timestamp=m.get("timestamp", ""))
            for m in state.get("messages", [])
        ]
        self.summary = state.get("summary")


class PromptCache:
    """
    Manages prompt caching for cost optimization.

    Tracks which prompts have been cached to minimize
    redundant token processing.
    """

    def __init__(self):
        self._cache: Dict[str, str] = {}

    def get_cache_key(self, content: str) -> str:
        """Generate a cache key for content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def is_cached(self, content: str) -> bool:
        """Check if content is in cache."""
        return self.get_cache_key(content) in self._cache

    def add_to_cache(self, content: str) -> str:
        """Add content to cache and return cache key."""
        key = self.get_cache_key(content)
        self._cache[key] = content
        return key

    def get_cached_tokens_estimate(self) -> int:
        """Estimate total cached tokens."""
        return sum(TokenCounter.estimate_tokens(c) for c in self._cache.values())
