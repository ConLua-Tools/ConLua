import json
from pathlib import Path

# Simple knowledge store that loads your RAG data
class SimpleKnowledgeStore:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.chunks = []
        self.entities = []
        self.load_data()

    def load_data(self):
        try:
            # Load text chunks
            chunks_file = Path(self.data_dir) / "kv_store_text_chunks.json"
            if chunks_file.exists():
                with open(chunks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chunks = list(data.values()) if data else []

            # Load custom knowledge if exists
            knowledge_file = Path(self.data_dir) / "knowledge.json"
            if knowledge_file.exists():
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'chunks' in data:
                        self.chunks = data['chunks']

            # Load entities
            entities_file = Path(self.data_dir) / "vdb_entities.json"
            if entities_file.exists():
                with open(entities_file, 'r', encoding='utf-8') as f:
                    entities_data = json.load(f)
                    if isinstance(entities_data, dict) and 'data' in entities_data:
                        self.entities = entities_data['data']
                    elif isinstance(entities_data, list):
                        self.entities = entities_data
                    else:
                        self.entities = []

            print(f"✅ Loaded {len(self.chunks)} chunks and {len(self.entities)} entities")

        except Exception as e:
            print(f"⚠️ Error loading data: {e}")
            self.chunks = []
            self.entities = []

    def search(self, query: str, limit: int = 5) -> List[str]:
        query_lower = query.lower()
        results = []

        # Search through chunks
        for chunk in self.chunks:
            if isinstance(chunk, str):
                if any(word in chunk.lower() for word in query_lower.split()):
                    results.append(chunk)
            elif isinstance(chunk, dict) and 'content' in chunk:
                content = chunk['content']
                if any(word in content.lower() for word in query_lower.split()):
                    results.append(content)

        # Search through entities
        for entity in self.entities:
            if isinstance(entity, dict):
                entity_text = json.dumps(entity, ensure_ascii=False)
                if any(word in entity_text.lower() for word in query_lower.split()):
                    results.append(entity_text)

        return results[:limit]
