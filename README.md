# Blog-AI-Agent

Designed and implemented a Docker-based self-hosted automation system using ***n8n***, incorporating reverse proxy (Nginx) and HTTPS, and integrating multiple external APIs and AI models to build a fully automated pipeline for keyword generation, content creation, and WordPress deployment.

## Architecture

```
🌐 Client (Browser)
        │
        │ HTTPS :443
        ▼
┌─────────────────────────────────────────────────────┐
│  Contabo VPS  79.143.181.67  (Ubuntu 22.04)         │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Docker                                      │   │
│  │                                              │   │
│  │       ┌─────────────────────────┐            │   │
│  │       │   Nginx Proxy Manager   │            │   │
│  │       │  SSL (Let's Encrypt)    │            │   │
│  │       │  + Reverse Proxy  :81   │            │   │
│  │       └────────────┬────────────┘            │   │
│  │                    │                         │   │
│  │  ┌─────────────────┼──────────────────────┐  │   │
│  │  │  Docker Network                        │  │   │
│  │  │  (containers communicate by name)      │  │   │
│  │  │        ┌────────┴──────┐               │  │   │
│  │  │        │               │               │  │   │
│  │  │   ┌────▼────┐   ┌──────▼──────┐        │  │   │
│  │  │   │   n8n   │   │  WordPress  │        │  │   │
│  │  │   │  :5678  │   │    :80      │        │  │   │
│  │  │   └────┬────┘   └──────┬──────┘        │  │   │
│  │  │        │               │               │  │   │
│  │  │   ┌────▼──────────┐  ┌─▼──────────┐    │  │   │
│  │  │   │  phpMyAdmin   │  │   MySQL    │    │  │   │
│  │  │   │  :80 (IP only)│  │            │    │  │   │
│  │  │   └───────────────┘  └────────────┘    │  │   │
│  │  │                                        │  │   │
│  │  │   ┌─────────────────┐                  │  │   │
│  │  │   │    Portainer    │                  │  │   │
│  │  │   │    :9000        │                  │  │   │
│  │  │   └─────────────────┘                  │  │   │
│  │  └────────────────────────────────────────┘  │   │
│  │                                              │   │
│  │  ┌─────────────────────┐                     │   │
│  │  │   FastAPI  :8833    │ ← n8n AI Tool call  │   │
│  │  │  api.leeeyubin.cloud│   (conditional)     │   │
│  │  └──────────┬──────────┘                     │   │
│  │             │                                │   │
│  └─────────────┼────────────────────────────────┘   │
└────────────────┼────────────────────────────────────┘
                 │
     ┌───────────┼───────────┐
     ▼           ▼           ▼
 Naver API  Google API  Gemini API
```

> **n8n → OpenAI GPT / Perplexity** are called directly from n8n as external LLM providers.


## n8n Workflow

<img width="1503" height="622" alt="n8n workflow" src="https://github.com/user-attachments/assets/b3157801-13e1-4fa7-845a-e0d1fb6106dc" />

### Pipeline Overview

```
Airtable (reserved keywords)
        │
        ▼
  Keyword Agent (GPT-4)
  Keyword analysis & expansion
        │
        ▼
    Split Out  ── 1 → 4 items
        │
        ▼
 Clustering Agent (GPT-4 + Search Tool)
 Semantic keyword clustering
        │
        ▼
   Loop Over Items
        │
        ├── Plan AI        (GPT-4 — content planning)
        ├── Research       (Perplexity — web research)
        ├── WritePost AI   (Gemini / GPT — article writing)
        ├── Image Prompt   (generate image prompt)
        ├── Image Generate (Replicate API)
        └── HTML Maker     (assemble final HTML)
                │
                ▼
     WordPress REST API
     (title / content / category / tags / slug / image)
                │
                ▼
     Airtable update
     proceed → done
```

## Tech Stack

| Category | Technology |
|----------|------------|
| **Infrastructure** | Contabo VPS, Ubuntu 22.04, Docker |
| **Reverse Proxy** | Nginx Proxy Manager, Let's Encrypt SSL |
| **Automation Engine** | n8n (Self-hosted) |
| **CMS** | WordPress + MySQL |
| **Search API Server** | FastAPI (Python) |
| **AI Models** | OpenAI GPT-4, Google Gemini, Perplexity |
| **Image Generation** | Replicate API |
| **Data Management** | Airtable |
| **Container Management** | Portainer |


## Project Structure

```
├── nginx-proxy-manager/
│   └── docker-compose.yml       # Nginx + SSL configuration
│
├── self-hosted-ai-starter-kit/
│   └── docker-compose.yml       # n8n + PostgreSQL + Qdrant
│
├── wordpress/
│   └── docker-compose.yml       # WordPress + MySQL + phpMyAdmin
│
└── python-tools-search-api/
    ├── app.py                   # FastAPI search endpoint
    ├── main.py
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    └── .env                     # API key environment variables
```

## Getting Started

### 1. Start Nginx Proxy Manager

```bash
cd nginx-proxy-manager
docker compose up -d
```

### 2. Start n8n + AI Stack

```bash
cd self-hosted-ai-starter-kit
docker compose up -d
```

### 3. Start WordPress

```bash
cd wordpress
docker compose up -d
```

### 4. Start FastAPI Search Server

```bash
cd python-tools-search-api
docker compose up -d
```

### 5. Connect Docker Networks (first time only)

```bash
docker network connect nginx-proxy-manager_default n8n
```

> For a permanent fix, define a shared network in `docker-compose.yml` instead of using this command.

## Environment Variables

`python-tools-search-api/.env`

```env
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

## Service URLs

| Service | URL |
|---------|-----|
| WordPress | `https://leeeyubin.cloud` |
| FastAPI | `https://api.leeeyubin.cloud` |
