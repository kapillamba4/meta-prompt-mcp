"""
IndexManager — Handles PDF ingestion, embedding, and vector-store persistence.

Uses LlamaParse for high-fidelity PDF parsing and HuggingFace local embeddings
(BAAI/bge-small-en-v1.5) for zero-cost, private vector search.
"""

from __future__ import annotations

import glob
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("meta-prompt-mcp")

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
_PKG_DIR = Path(__file__).resolve().parent  # .../meta_prompt_mcp/
_DEFAULT_DATA_DIR = str(_PKG_DIR / "data")
_DEFAULT_STORAGE_DIR = str(_PKG_DIR / "storage")
_EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"


class IndexManager:
    """Manages the lifecycle of the vector index: build, persist, load, query."""

    def __init__(
        self,
        data_dir: str | None = None,
        storage_dir: str | None = None,
        embed_model_name: str = _EMBED_MODEL_NAME,
    ) -> None:
        self.data_dir = str(Path(data_dir or _DEFAULT_DATA_DIR).resolve())
        self.storage_dir = str(Path(storage_dir or _DEFAULT_STORAGE_DIR).resolve())
        self.embed_model_name = embed_model_name
        self._index = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ensure_index(self) -> None:
        """Load from disk if available, otherwise build from PDFs."""
        if self._index is not None:
            return

        if self._storage_exists():
            logger.info("Loading existing index from %s", self.storage_dir)
            self._load_index()
        else:
            logger.info("No cached index found — building from PDFs in %s", self.data_dir)
            self._build_index()

    def query(self, question: str, similarity_top_k: int = 5) -> str:
        """Query the index and return retrieved context without LLM synthesis."""
        self.ensure_index()

        retriever = self._index.as_retriever(similarity_top_k=similarity_top_k)
        nodes = retriever.retrieve(question)

        if not nodes:
            return "No relevant strategies found."

        result_text = "\n\n---\n\n".join(
            f"**Excerpt (Score: {node.score:.2f}):**\n\n{node.node.get_content()}" for node in nodes
        )
        return (
            f"Found the following relevant strategies from the Prompting Guides:\n\n{result_text}"
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _storage_exists(self) -> bool:
        """Check whether a persisted index exists on disk."""
        return os.path.isdir(self.storage_dir) and os.path.isfile(
            os.path.join(self.storage_dir, "docstore.json")
        )

    def _get_embed_model(self):
        """Lazily create the HuggingFace embedding model."""
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding

        return HuggingFaceEmbedding(model_name=self.embed_model_name)

    def _build_index(self) -> None:
        """Parse PDFs via LlamaParse, embed, and persist the vector store."""
        from llama_index.core import Settings, VectorStoreIndex
        from llama_parse import LlamaParse

        # --- Validate prerequisites ---
        api_key = os.getenv("LLAMA_CLOUD_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "LLAMA_CLOUD_API_KEY is required for the first-time PDF parsing. "
                "Set it in your .env file or environment. "
                "Get a free key at https://cloud.llamaindex.ai/"
            )

        pdf_files = glob.glob(os.path.join(self.data_dir, "*.pdf"))
        md_files = glob.glob(os.path.join(self.data_dir, "*.md"))
        all_files = pdf_files + md_files
        if not all_files:
            raise FileNotFoundError(
                f"No PDF or Markdown files found in {self.data_dir}. "
                "Please place your prompting guides in the data/ directory."
            )

        # --- Configure embedding model globally ---
        embed_model = self._get_embed_model()
        Settings.embed_model = embed_model

        # --- Parse files ---
        logger.info("Parsing %d file(s) with LlamaParse…", len(all_files))
        parser = LlamaParse(
            api_key=api_key,
            result_type="markdown",
        )

        documents = []
        for file_path in all_files:
            logger.info("  → %s", os.path.basename(file_path))
            docs = parser.load_data(file_path)
            documents.extend(docs)

        logger.info("Parsed %d document chunks.", len(documents))

        # --- Build vector index ---
        logger.info("Building vector index…")
        self._index = VectorStoreIndex.from_documents(documents)

        # --- Persist to disk ---
        os.makedirs(self.storage_dir, exist_ok=True)
        self._index.storage_context.persist(persist_dir=self.storage_dir)
        logger.info("Index persisted to %s", self.storage_dir)

    def _load_index(self) -> None:
        """Load a previously persisted index from disk."""
        from llama_index.core import Settings, StorageContext, load_index_from_storage

        Settings.embed_model = self._get_embed_model()

        storage_context = StorageContext.from_defaults(persist_dir=self.storage_dir)
        self._index = load_index_from_storage(storage_context)
        logger.info("Index loaded successfully (%s).", self.storage_dir)


def build_index_cli() -> None:
    """Standalone CLI entry point to pre-build the vector index."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(name)-20s  %(levelname)-8s  %(message)s",
    )
    manager = IndexManager()

    if manager._storage_exists():
        logger.info(
            "Index already exists at %s. Use `make clean-index` to rebuild.", manager.storage_dir
        )
        return

    logger.info("Building index…")
    manager.ensure_index()
    logger.info("Done! Index saved to %s", manager.storage_dir)
