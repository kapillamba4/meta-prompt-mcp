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
_DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
_DEFAULT_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "storage")
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
        """Query the index and return a synthesized answer string."""
        self.ensure_index()

        query_engine = self._index.as_query_engine(similarity_top_k=similarity_top_k)
        response = query_engine.query(question)
        return str(response)

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
        from llama_index.core import Settings, StorageContext, VectorStoreIndex
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
        if not pdf_files:
            raise FileNotFoundError(
                f"No PDF files found in {self.data_dir}. "
                "Please place the Google Prompting Guide 101 PDF in the data/ directory."
            )

        # --- Configure embedding model globally ---
        embed_model = self._get_embed_model()
        Settings.embed_model = embed_model

        # --- Parse PDFs ---
        logger.info("Parsing %d PDF(s) with LlamaParse…", len(pdf_files))
        parser = LlamaParse(
            api_key=api_key,
            result_type="markdown",
        )

        documents = []
        for pdf_path in pdf_files:
            logger.info("  → %s", os.path.basename(pdf_path))
            docs = parser.load_data(pdf_path)
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
        logger.info("Index already exists at %s. Use `make clean-index` to rebuild.", manager.storage_dir)
        return

    logger.info("Building index…")
    manager.ensure_index()
    logger.info("Done! Index saved to %s", manager.storage_dir)
