<div align="center">

# 🚀 LightRAG: Simple and Fast Retrieval-Augmented Generation
</div>

## Installation
### env
- LLM_MODEL: This would be the model that does your knowledge graph query and response.
  - Orignal [lightRAG repo](https://github.com/HKUDS/LightRAG/) suggests a model with at least 32b params. Though the example directory used a 8b llama model ('@cf/meta/llama-3.2-3b-instruct' that worked moderately well.
  - Context window of at least 32KB
- EMBEDDING_MODEL:
  - LightRAG is very picky when it comes to embedder, so please use a mainstream one like '@cf/baai/bge-m3'
### Install all requirements. '''.py pip install -e lib/backend/requirements.txt'''

## Directories
## Planned development


## Functionalities
