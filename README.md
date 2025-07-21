<div align="center">

# 🚀 LightRAG: Simple and Fast Retrieval-Augmented Generation
</div>

## Deployment
### env
- LLM_MODEL: This would be the model that does your knowledge graph query and response.
  - Orignal [lightRAG repo](https://github.com/HKUDS/LightRAG/) suggests a model with at least 32b params. Though the example directory used a 8b llama model (`@cf/meta/llama-3.2-3b-instruct` that worked moderately well.
  - Context window of at least 32KB
- EMBEDDING_MODEL:
  - LightRAG is very picky when it comes to embedder, so please use a mainstream one like `@cf/baai/bge-m3`
- CLOUDFLARE_API_KEY: Generate an API key at [https://dash.cloudflare.com](https://dash.cloudflare.com)
- API_BASE_URL: Generate an API base url at [https://dash.cloudflare.com](https://dash.cloudflare.com)
- WORKING_DIR="", for now put `QCVN-06-2022-BXD.docx`. If file upload functionality is fully added, this env variable would become deprecated since the working directory (knoweledge graph and base text storage) is determined by the source document.
- USER_DATA_DIR="" &  JWT_SECRET="" are optional

### backend deployment
`app.py` runs a FastAPI server, 
### frontend deployment

### quickstart
If you want to visualize how LightRAG works, and specifically how you can use Cloudflare worker API to interact with it, refer to [this link](
### Install all requirements.
`py pip install -e lib/backend/requirements.txt`

## Directories
## Planned development
### True lightRAG functionality
#### Retrieval
#### Reranker model
### Multiple working directory shared through server backend
### LLM cache

## Functionalities
