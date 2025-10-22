class EmbeddingService:
    async def generate_embeddings(self, text: str):
        # Return dummy vector
        return [0.0] * min(10, max(1, len(text) // 100))
