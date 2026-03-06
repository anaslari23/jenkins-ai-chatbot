# Jenkins Plugin Installation Guide

## Building the Plugin

### Prerequisites
- Java 11+
- Maven 3.x

### Build

```bash
cd plugin/jenkins-ai-assistant-plugin
mvn package
```

This produces: `target/jenkins-ai-assistant.hpi`

## Installing in Jenkins

1. Open Jenkins → **Manage Jenkins** → **Plugins**
2. Click the **Advanced settings** tab
3. Under **Deploy Plugin**, click **Choose File**
4. Select the `.hpi` file
5. Click **Deploy**
6. Restart Jenkins when prompted

## Configuration

### Backend URL

By default the plugin connects to `http://localhost:8000`. To change this, add a Java system property when starting Jenkins:

```bash
java -Dai.assistant.backend.url=http://your-backend:8000 -jar jenkins.war
```

Or in your Jenkins service configuration:

```
JAVA_OPTS="-Dai.assistant.backend.url=http://your-backend:8000"
```

## Using the Plugin

1. After installation, **"AI Assistant"** appears in the Jenkins sidebar
2. Click it to open the chat panel
3. Type your question and press Enter or click Send
4. The assistant queries the backend and returns answers with source links

## Features

- **Pipeline guidance** — Step-by-step pipeline creation instructions
- **Plugin help** — How to install and configure plugins
- **Troubleshooting** — Paste error logs to get diagnostic help
- **Documentation search** — Finds relevant Jenkins docs via RAG

## Architecture

```
Jenkins UI → Plugin (AiAssistantAction.java)
                  ↓ HTTP POST /ask
           FastAPI Backend
                  ↓
            RAG Pipeline → Answer
                  ↓
           Plugin ← JSON response
                  ↓
           Jenkins UI ← rendered answer
```

## Development

To run the plugin in development mode:

```bash
cd plugin/jenkins-ai-assistant-plugin
mvn hpi:run
```

This starts a local Jenkins instance at http://localhost:8080/jenkins with the plugin pre-installed.
