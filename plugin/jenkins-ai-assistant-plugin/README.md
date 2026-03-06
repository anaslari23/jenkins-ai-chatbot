# Jenkins AI Assistant Plugin

A Jenkins plugin that embeds an AI chatbot assistant directly into the Jenkins dashboard.

## Features

- **Sidebar Link** — Adds "AI Assistant" to the Jenkins sidebar navigation
- **Chat Panel** — Full chat interface within Jenkins (dark theme, premium design)
- **Backend Proxy** — Routes questions through Jenkins to the FastAPI backend
- **CSRF Protection** — Handles Jenkins crumb tokens automatically

## Architecture

```
Jenkins UI → Plugin (Java) → FastAPI Backend → RAG Pipeline → LLM → Response
```

## Building

Requires Maven 3.x and Java 11+.

```bash
cd plugin/jenkins-ai-assistant-plugin
mvn package
```

This produces `target/jenkins-ai-assistant.hpi` which can be installed in Jenkins.

## Configuration

Set the backend URL via Java system property:

```
-Dai.assistant.backend.url=http://localhost:8000
```

## Files

| File | Purpose |
|---|---|
| `pom.xml` | Maven build config (hpi packaging) |
| `AiAssistantAction.java` | RootAction — sidebar link + /ask proxy |
| `index.jelly` | Jelly view — chat panel HTML |
| `chat.css` | Chat UI styles |
| `chat.js` | Chat frontend logic |
