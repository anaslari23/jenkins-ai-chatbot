"""
Jenkins AI Chatbot — Workflow Guidance Service

Provides step-by-step workflow instructions, example Jenkinsfiles,
and links to official Jenkins documentation for common tasks.

Usage:
    from services.workflow_guide import get_workflow_guidance
    guidance = get_workflow_guidance("How to create a Jenkins pipeline")
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Workflow knowledge base
# ---------------------------------------------------------------------------

WORKFLOWS: dict[str, dict] = {
    "create_pipeline": {
        "keywords": [
            "create pipeline",
            "new pipeline",
            "pipeline setup",
            "jenkinsfile",
            "write pipeline",
        ],
        "title": "How to Create a Jenkins Pipeline",
        "steps": [
            "1. Open Jenkins Dashboard and click 'New Item'.",
            "2. Enter a name for your pipeline and select 'Pipeline' as the project type.",
            "3. Click 'OK' to create the project.",
            "4. Scroll to the 'Pipeline' section in the configuration page.",
            "5. Choose 'Pipeline script' to write inline, or 'Pipeline script from SCM' to load from Git.",
            "6. Write your Jenkinsfile (see example below).",
            "7. Click 'Save' and then 'Build Now' to run your pipeline.",
        ],
        "jenkinsfile": """pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/your-repo.git'
            }
        }

        stage('Build') {
            steps {
                sh 'echo "Building..."'
                // For Maven: sh 'mvn clean package'
                // For Node:  sh 'npm install && npm run build'
            }
        }

        stage('Test') {
            steps {
                sh 'echo "Running tests..."'
                // sh 'mvn test'
                // sh 'npm test'
            }
        }

        stage('Deploy') {
            steps {
                sh 'echo "Deploying..."'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs for details.'
        }
    }
}""",
        "docs": [
            "https://www.jenkins.io/doc/book/pipeline/",
            "https://www.jenkins.io/doc/book/pipeline/jenkinsfile/",
            "https://www.jenkins.io/doc/book/pipeline/syntax/",
        ],
    },
    "configure_nodejs": {
        "keywords": ["nodejs", "node.js", "node js", "npm", "node project"],
        "title": "How to Configure Jenkins for Node.js",
        "steps": [
            "1. Install the 'NodeJS' plugin from Manage Jenkins → Plugin Manager.",
            "2. Navigate to Manage Jenkins → Tools (or Global Tool Configuration).",
            "3. Under 'NodeJS installations', click 'Add NodeJS'.",
            "4. Give it a name (e.g., 'Node-18') and select the version.",
            "5. Optionally add global npm packages (e.g., 'yarn', 'pm2').",
            "6. Click 'Save'.",
            "7. In your pipeline, use the 'nodejs' tool wrapper (see example).",
        ],
        "jenkinsfile": """pipeline {
    agent any

    tools {
        nodejs 'Node-18'
    }

    stages {
        stage('Install') {
            steps {
                sh 'node --version'
                sh 'npm install'
            }
        }

        stage('Test') {
            steps {
                sh 'npm test'
            }
        }

        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
    }
}""",
        "docs": [
            "https://plugins.jenkins.io/nodejs/",
            "https://www.jenkins.io/doc/book/pipeline/",
        ],
    },
    "install_plugins": {
        "keywords": [
            "install plugin",
            "add plugin",
            "plugin manager",
            "manage plugins",
        ],
        "title": "How to Install Jenkins Plugins",
        "steps": [
            "1. Navigate to Manage Jenkins → Plugin Manager.",
            "2. Click the 'Available plugins' tab.",
            "3. Use the search/filter box to find the plugin you need.",
            "4. Check the box next to the desired plugin(s).",
            "5. Click 'Install without restart' or 'Download now and install after restart'.",
            "6. Wait for the installation to complete.",
            "7. Restart Jenkins if required (Manage Jenkins → Restart).",
        ],
        "jenkinsfile": None,
        "docs": [
            "https://www.jenkins.io/doc/book/managing/plugins/",
            "https://plugins.jenkins.io/",
        ],
    },
    "configure_agents": {
        "keywords": ["agent", "node", "slave", "distributed build", "add agent"],
        "title": "How to Configure Jenkins Agents",
        "steps": [
            "1. Navigate to Manage Jenkins → Nodes.",
            "2. Click 'New Node'.",
            "3. Enter a node name and select 'Permanent Agent'.",
            "4. Configure: Remote root directory, Labels, Usage, Launch method.",
            "5. For SSH agents: provide host, credentials, and Java path.",
            "6. Click 'Save'.",
            "7. The agent will appear in the node list. Click it to verify connection.",
        ],
        "jenkinsfile": """pipeline {
    agent { label 'my-agent-label' }

    stages {
        stage('Build on Agent') {
            steps {
                sh 'echo "Running on agent: ${NODE_NAME}"'
            }
        }
    }
}""",
        "docs": [
            "https://www.jenkins.io/doc/book/managing/nodes/",
            "https://www.jenkins.io/doc/book/using/using-agents/",
        ],
    },
    "setup_credentials": {
        "keywords": [
            "credentials",
            "secret",
            "password",
            "token",
            "api key",
            "ssh key",
        ],
        "title": "How to Manage Jenkins Credentials",
        "steps": [
            "1. Navigate to Manage Jenkins → Credentials.",
            "2. Select the appropriate scope (Global or a specific domain).",
            "3. Click 'Add Credentials'.",
            "4. Select the credential type (Username/Password, SSH Key, Secret text, etc.).",
            "5. Fill in the ID, description, and credential data.",
            "6. Click 'Create'.",
            "7. Reference credentials in your pipeline using the 'credentials()' helper.",
        ],
        "jenkinsfile": """pipeline {
    agent any

    environment {
        MY_CREDS = credentials('my-credential-id')
    }

    stages {
        stage('Use Credentials') {
            steps {
                sh 'echo "Using credentials securely"'
                // MY_CREDS_USR and MY_CREDS_PSW are available
            }
        }
    }
}""",
        "docs": [
            "https://www.jenkins.io/doc/book/using/using-credentials/",
            "https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#handling-credentials",
        ],
    },
    "setup_webhooks": {
        "keywords": [
            "webhook",
            "github webhook",
            "trigger",
            "auto build",
            "push trigger",
        ],
        "title": "How to Set Up Webhooks for Automatic Builds",
        "steps": [
            "1. Install the 'GitHub' or 'Generic Webhook Trigger' plugin.",
            "2. In your pipeline config, check 'GitHub hook trigger for GITScm polling'.",
            "3. Go to your GitHub repository → Settings → Webhooks → Add webhook.",
            "4. Set Payload URL to: http://<jenkins-url>/github-webhook/",
            "5. Set Content type to 'application/json'.",
            "6. Select 'Just the push event' or customize events.",
            "7. Save. Pushes to the repo will now trigger builds.",
        ],
        "jenkinsfile": """pipeline {
    agent any

    triggers {
        githubPush()
    }

    stages {
        stage('Build') {
            steps {
                sh 'echo "Triggered by webhook push!"'
            }
        }
    }
}""",
        "docs": [
            "https://www.jenkins.io/doc/book/pipeline/multibranch/",
            "https://plugins.jenkins.io/github/",
        ],
    },
}


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------


def _match_workflow(query: str) -> dict | None:
    """Find the best matching workflow for a user query."""
    query_lower = query.lower()
    best_match = None
    best_score = 0

    for _key, workflow in WORKFLOWS.items():
        score = sum(1 for kw in workflow["keywords"] if kw in query_lower)
        if score > best_score:
            best_score = score
            best_match = workflow

    return best_match if best_score > 0 else None


def format_workflow(workflow: dict) -> str:
    """Format a workflow into a readable text response."""
    parts = [f"## {workflow['title']}\n"]

    parts.append("### Steps\n")
    parts.extend(workflow["steps"])
    parts.append("")

    if workflow.get("jenkinsfile"):
        parts.append("### Example Jenkinsfile\n```groovy")
        parts.append(workflow["jenkinsfile"])
        parts.append("```\n")

    if workflow.get("docs"):
        parts.append("### Official Documentation")
        for doc_url in workflow["docs"]:
            parts.append(f"- {doc_url}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_workflow_guidance(query: str) -> dict | None:
    """
    Check if the query matches a known workflow and return guidance.

    Returns:
        {
            "title": str,
            "steps": list[str],
            "jenkinsfile": str | None,
            "docs": list[str],
            "formatted": str,  # full formatted text
        }
        or None if no workflow matches.
    """
    workflow = _match_workflow(query)
    if workflow is None:
        return None

    return {
        "title": workflow["title"],
        "steps": workflow["steps"],
        "jenkinsfile": workflow.get("jenkinsfile"),
        "docs": workflow.get("docs", []),
        "formatted": format_workflow(workflow),
    }


def get_all_workflow_topics() -> list[str]:
    """Return a list of all available workflow topics."""
    return [w["title"] for w in WORKFLOWS.values()]
