#!/usr/bin/env python3
"""Script to train dimensional reduction models for embedding vectors."""

import argparse
import os
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.decomposition import TruncatedSVD

# Add the chatter package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatter.services.embeddings import EmbeddingService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


def load_training_corpus(corpus_path: str) -> list[str]:
    """Load training corpus from a text file.

    Args:
        corpus_path: Path to corpus file (one text per line)

    Returns:
        List of text strings
    """
    texts = []
    with open(corpus_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                texts.append(line)

    logger.info(f"Loaded {len(texts)} texts from corpus")
    return texts


def train_truncated_svd(
    texts: list[str],
    provider: str,
    target_dim: int,
    sample_size: int = None,
    output_path: str = None,
) -> str:
    """Train a TruncatedSVD model for dimensional reduction.

    Args:
        texts: List of training texts
        provider: Embedding provider name
        target_dim: Target dimension after reduction
        sample_size: Maximum number of texts to use (None for all)
        output_path: Output path for the trained model

    Returns:
        Path to the saved model
    """
    # Initialize embedding service
    embedding_service = EmbeddingService()
    embeddings_provider = embedding_service.get_provider(provider)

    if not embeddings_provider:
        raise ValueError(f"Provider '{provider}' not available")

    # Sample texts if needed
    if sample_size and len(texts) > sample_size:
        import random

        texts = random.sample(texts, sample_size)
        logger.info(f"Sampled {len(texts)} texts for training")

    # Generate embeddings
    logger.info("Generating embeddings for training...")
    embeddings = []
    batch_size = 50  # Process in batches to avoid memory issues

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        batch_embeddings = embeddings_provider.embed_documents(batch)
        embeddings.extend(batch_embeddings)

        if (i // batch_size + 1) % 10 == 0:
            logger.info(
                f"Processed {i + len(batch)} / {len(texts)} texts"
            )

    # Convert to numpy array
    X = np.array(embeddings)
    logger.info(f"Training data shape: {X.shape}")

    # Train TruncatedSVD
    logger.info(
        f"Training TruncatedSVD with target dimension {target_dim}"
    )
    svd = TruncatedSVD(n_components=target_dim, random_state=42)
    svd.fit(X)

    # Log explained variance
    explained_variance_ratio = svd.explained_variance_ratio_.sum()
    logger.info(
        f"Explained variance ratio: {explained_variance_ratio:.4f}"
    )

    # Save the model
    if not output_path:
        output_path = (
            f"svd_{provider}_{X.shape[1]}_to_{target_dim}.joblib"
        )

    # Ensure output directory exists
    os.makedirs(
        (
            os.path.dirname(output_path)
            if os.path.dirname(output_path)
            else "."
        ),
        exist_ok=True,
    )

    joblib.dump(svd, output_path)
    logger.info(f"Saved TruncatedSVD model to {output_path}")

    return output_path


def main():
    """Main function for training script."""
    parser = argparse.ArgumentParser(
        description="Train dimensional reduction for embeddings"
    )
    parser.add_argument(
        "--corpus",
        type=str,
        required=True,
        help="Path to training corpus file (one text per line)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["openai", "google", "cohere"],
        help="Embedding provider to use",
    )
    parser.add_argument(
        "--target-dim",
        type=int,
        default=1536,
        help="Target dimension after reduction",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        help="Maximum number of texts to use for training",
    )
    parser.add_argument(
        "--output", type=str, help="Output path for the trained model"
    )

    args = parser.parse_args()

    # Validate arguments
    if not os.path.exists(args.corpus):
        logger.error(f"Corpus file not found: {args.corpus}")
        sys.exit(1)

    if args.target_dim <= 0:
        logger.error("Target dimension must be positive")
        sys.exit(1)

    try:
        # Load corpus
        texts = load_training_corpus(args.corpus)

        if len(texts) == 0:
            logger.error("No texts found in corpus")
            sys.exit(1)

        # Train model
        model_path = train_truncated_svd(
            texts=texts,
            provider=args.provider,
            target_dim=args.target_dim,
            sample_size=args.sample_size,
            output_path=args.output,
        )

        print("Training completed successfully!")
        print(f"Model saved to: {model_path}")
        print()
        print(
            "To use this model, set the following environment variables:"
        )
        print("EMBEDDING_REDUCTION_ENABLED=true")
        print("EMBEDDING_REDUCTION_STRATEGY=reducer")
        print(f"EMBEDDING_REDUCTION_TARGET_DIM={args.target_dim}")
        print(f"EMBEDDING_REDUCER_PATH={model_path}")
        print("EMBEDDING_REDUCTION_NORMALIZE=true")

    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
