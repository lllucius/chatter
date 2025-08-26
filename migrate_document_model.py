"""Migration script to update DocumentChunk model for dynamic embeddings."""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_document_model():
    """Update the DocumentChunk model to support dynamic embeddings."""
    
    # Read the current document.py file
    document_path = "chatter/models/document.py"
    
    with open(document_path, 'r') as f:
        content = f.read()
    
    # Create a backup
    backup_path = document_path + ".backup"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Update the embedding field and add new fields
    updated_content = content
    
    # Replace the fixed Vector(1536) with Text for compatibility
    old_embedding_field = """    # Vector embedding (conditional on pgvector availability)
    # Use Any type to handle both Vector and Text types
    embedding: Mapped[Any | None] = mapped_column(
        Vector(1536) if PGVECTOR_AVAILABLE else Text, nullable=True
    )"""
    
    new_embedding_field = """    # Legacy embedding field - kept for backwards compatibility during migration
    # No longer used for new embeddings, which go to dynamic tables
    embedding: Mapped[Any | None] = mapped_column(
        Text, nullable=True  # Changed from Vector to Text for compatibility
    )"""
    
    updated_content = updated_content.replace(old_embedding_field, new_embedding_field)
    
    # Add new embedding metadata fields before the existing embedding metadata
    old_embedding_metadata = """    # Embedding metadata
    embedding_model: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    embedding_provider: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    embedding_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )"""
    
    new_embedding_metadata = """    # Embedding metadata - tracks which models have been applied
    embedding_models: Mapped[list[str] | None] = mapped_column(
        "embedding_models", JSON, nullable=True, 
        comment="List of embedding model names that have been applied to this chunk"
    )
    primary_embedding_model: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Primary embedding model for this chunk"
    )
    embedding_provider: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    embedding_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )"""
    
    updated_content = updated_content.replace(old_embedding_metadata, new_embedding_metadata)
    
    # Update the has_embedding property
    old_has_embedding = """    @property
    def has_embedding(self) -> bool:
        \"\"\"Check if chunk has an embedding.\"\"\"
        return self.embedding is not None"""
    
    new_has_embedding = """    @property
    def has_embedding(self) -> bool:
        \"\"\"Check if chunk has any embeddings (legacy or dynamic).\"\"\"
        return (
            self.embedding is not None 
            or (self.embedding_models and len(self.embedding_models) > 0)
        )

    @property
    def has_dynamic_embeddings(self) -> bool:
        \"\"\"Check if chunk has embeddings in dynamic tables.\"\"\"
        return self.embedding_models and len(self.embedding_models) > 0

    def add_embedding_model(self, model_name: str, set_as_primary: bool = False) -> None:
        \"\"\"Add an embedding model to the list of applied models.
        
        Args:
            model_name: Name of the embedding model
            set_as_primary: Whether to set this as the primary model
        \"\"\"
        if not self.embedding_models:
            self.embedding_models = []
        
        if model_name not in self.embedding_models:
            self.embedding_models.append(model_name)
        
        if set_as_primary or not self.primary_embedding_model:
            self.primary_embedding_model = model_name

    def remove_embedding_model(self, model_name: str) -> None:
        \"\"\"Remove an embedding model from the list.
        
        Args:
            model_name: Name of the embedding model to remove
        \"\"\"
        if self.embedding_models and model_name in self.embedding_models:
            self.embedding_models.remove(model_name)
            
            # Update primary if it was the removed model
            if self.primary_embedding_model == model_name:
                self.primary_embedding_model = (
                    self.embedding_models[0] if self.embedding_models else None
                )"""
    
    updated_content = updated_content.replace(old_has_embedding, new_has_embedding)
    
    # Write the updated content
    with open(document_path, 'w') as f:
        f.write(updated_content)
    
    print(f"Updated {document_path} for dynamic embeddings support")
    print("You may need to create an Alembic migration for the database schema changes")


if __name__ == "__main__":
    update_document_model()