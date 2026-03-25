# LMS Telegram Bot — Development Plan

## Overview

This document outlines the development plan for building a Telegram bot that integrates with the Learning Management System (LMS) backend. The bot allows users to check system health, browse labs, view scores, and ask questions in plain language using an LLM for intent routing.

## Task 1: Plan and Scaffold

**Goal:** Establish project structure and testable architecture.

- Create `bot/` directory with `bot.py` entry point
- Implement `--test` mode for offline command testing
- Separate handlers from Telegram transport layer (`handlers/`)
- Add configuration loading from `.env.bot.secret`
- Document the development approach in `PLAN.md`

**Key architectural decision:** Handlers are plain functions that take input and return text. They don't depend on Telegram. This allows testing via `--test` mode and reuse in the actual bot.

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

- Create `services/api_client.py` for HTTP requests
- Implement Bearer token authentication using `LMS_API_KEY`
- Update handlers to fetch real data:
  - `/health` → `GET /health` endpoint
  - `/labs` → `GET /items/` with lab filtering
  - `/scores <lab>` → `GET /analytics/` for pass rates
- Add error handling for backend unavailability

## Task 3: Intent-Based Natural Language Routing

**Goal:** Enable plain language queries via LLM tool use.

- Create `services/llm_client.py` for LLM API calls
- Wrap all 9 backend endpoints as LLM tools with descriptions
- Implement intent router that sends user messages to LLM
- LLM decides which tool to call based on tool descriptions
- Add inline keyboard buttons for common actions

**Key insight:** Tool description quality matters more than prompt engineering. Clear, precise descriptions help the LLM choose correctly.

## Task 4: Containerize and Document

**Goal:** Deploy the bot alongside the backend.

- Create `bot/Dockerfile` for the bot container
- Add bot service to `docker-compose.yml`
- Configure bot to use backend service name (not localhost)
- Document deployment steps and troubleshooting
- Verify bot works in Telegram after deployment

## Testing Strategy

- Unit tests for handlers (test mode)
- Integration tests for API client
- Manual testing in Telegram after each task
- Autochecker verification on VM deployment

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| LLM picks wrong tool | Improve tool descriptions, not regex routing |
| Backend unavailable | Graceful error messages, not crashes |
| Secrets in git | Use `.env*.secret` files, gitignored |
| Docker networking | Use service names, not localhost |
