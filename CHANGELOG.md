# MEMOTECH Fork 1.2.0 (09 April 2026)

## Llama 4 Maverick + Planner Fix

- **LLM Upgrade**: `meta/llama-3.1-70b-instruct` replaced with `meta/llama-4-maverick-17b-128e-instruct` (MoE, 400B params, 17B active per token, 1M context)
- **Planner Fix**: Robust agent routing for verbose MoE model responses. Scans for keywords in full LLM output instead of requiring exact single-word responses
- **Shopware Dockware Sync**: 63 products synced from Dockware demo data

## Contributors
- **@MehmetGoekce** ([Mehmet Gökçe](https://github.com/MehmetGoekce))

---

# MEMOTECH Fork 1.1.0 (26 March 2026)

## Shopware 6 Integration + German Language Support

- **Shopware 6 Integration**: Store API sync script (`scripts/sync-shopware.py`), product import, image upload
- **German/English Bilingual**: Routing prompts, chatter prompts, and unsafe messages in both languages
- **MEMOTECH Branding**: Custom Navbar, Footer, Chat UI
- **Embeddable Widget**: `shopware-chat-widget.html` for Shopware storefront injection
- **Dockware**: Shopware 6.6 Docker container in docker-compose for development
- **Nginx Proxy**: Reverse proxy for frontend and API

## Contributors
- **@MehmetGoekce** ([Mehmet Gökçe](https://github.com/MehmetGoekce))

---

# Retail Shopping Assistant 1.0.0 (03 September 2025)

## 🎉 First Release

This is the initial release of the NVIDIA AI Blueprint: Retail Shopping Assistant, a comprehensive AI-powered shopping experience demonstrating multi-agent architecture with LangGraph.

## 🚀 New Features

- 🤖 **Multi-agent Architecture** - LangGraph-orchestrated agents for intelligent shopping assistance
- 🖼️ **Visual Search** - Image-based product search using NVIDIA NV-CLIP model  
- 🛒 **Smart Cart Management** - Conversational shopping cart operations
- 💬 **Conversational AI** - Natural language interactions powered by Llama 3.1 70B Instruct
- 🔒 **Content Safety** - Built-in moderation with Llama 3.1 NemoGuard 8B
- ⚡ **Real-time Streaming** - Live response generation for seamless UX
- 📱 **Modern UI** - Responsive React interface with Material-UI and Tailwind CSS
- 🔍 **Vector Search** - Milvus-powered similarity search for product recommendations
- 🐳 **Containerized Deployment** - Docker compose setup with NVIDIA NIM containers
- ☁️ **Flexible Deployment** - Support for local GPU or cloud API endpoints
- 📊 **Product Catalog** - Comprehensive retail product dataset

## 📋 Pull Requests Included in v1.0.0

### Recent Improvements
- Replace langchain with OpenAI library in ChatterAgent for consistency by @antoniomtz in [#78](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/78)
- Fixed final deployment guide link by @nvidiacbrissette in [#77](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/77)
- Update welcome message and splash image by @antoniomtz in [#76](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/76)
- Made notebook documentation links point to GitHub over local files by @nvidiacbrissette in [#75](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/75)
- One last link update by @nvidiacbrissette in [#74](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/74)
- Changed some bad links by @nvidiacbrissette in [#73](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/73)
- Merge product data by @antoniomtz in [#72](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/72)
- Update license by @antoniomtz in [#71](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/71)
- Update license terms by @antoniomtz in [#70](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/70)
- Update doc requirements by @antoniomtz in [#69](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/69)
- Update notebook with latest instructions by @jahubba in [#68](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/68)
- Update notebook by @antoniomtz in [#67](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/67)
- Update url path by @antoniomtz in [#66](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/66)
- Update notebook paths by @antoniomtz in [#64](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/pull/64)

## 👥 Contributors

- **@nvidiacbrissette** ([Christopher Brissette](https://github.com/nvidiacbrissette))
- **@jahubba** ([Jason Hubbard](https://github.com/jahubba))
- **@antoniomtz** ([Antonio Martinez](https://github.com/antoniomtz))

**Full Changelog**: https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/commits/v1.0.0

**Tag:** [v1.0.0](https://github.com/NVIDIA-AI-Blueprints/retail-shopping-assistant/releases/tag/v1.0.0)
