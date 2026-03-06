"""
Jenkins AI Chatbot — Troubleshooting Service

Analyzes Jenkins error logs and build failures to extract error
keywords, search the knowledge base, and suggest solutions.

Usage:
    from services.troubleshooter import analyze_error
    result = analyze_error("java.lang.OutOfMemoryError: Java heap space")
"""

from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Known error patterns and solutions
# ---------------------------------------------------------------------------

ERROR_PATTERNS: list[dict] = [
    {
        "pattern": r"java\.lang\.OutOfMemoryError",
        "keywords": ["OutOfMemoryError", "heap space", "memory"],
        "title": "Java OutOfMemoryError",
        "solutions": [
            "Increase Jenkins JVM heap size: edit JENKINS_JAVA_OPTIONS or JAVA_OPTS.",
            "  Example: JAVA_OPTS='-Xmx2g -Xms512m'",
            "Check for memory leaks in plugins — update or remove problematic plugins.",
            "Reduce the number of concurrent builds.",
            "If in a pipeline: use lightweight executors or agent-based builds.",
        ],
        "docs": [
            "https://www.jenkins.io/doc/book/scaling/hardware-recommendations/",
        ],
    },
    {
        "pattern": r"Permission\s*denied|permission denied|EACCES",
        "keywords": ["permission denied", "access denied", "EACCES"],
        "title": "Permission Denied Error",
        "solutions": [
            "Check file/directory ownership: ensure the Jenkins user has access.",
            "  Run: chown -R jenkins:jenkins /var/lib/jenkins",
            "For Docker builds: ensure the container user has correct permissions.",
            "For SSH: check SSH key permissions (should be 600) and known_hosts.",
            "For workspace issues: delete the workspace and rebuild.",
        ],
        "docs": [
            "https://www.jenkins.io/doc/book/security/",
        ],
    },
    {
        "pattern": r"No\s*such\s*DSL\s*method|WorkflowScript.*MissingMethodException",
        "keywords": ["no such DSL method", "MissingMethodException", "pipeline syntax"],
        "title": "Pipeline DSL Method Not Found",
        "solutions": [
            "Check Jenkinsfile syntax — ensure you're using valid pipeline DSL.",
            "Verify the required plugin is installed (e.g., Pipeline: Basic Steps).",
            "Update all pipeline-related plugins to latest versions.",
            "Check if the method is available in Declarative vs Scripted pipeline.",
            "Use the 'Pipeline Syntax' snippet generator in Jenkins for reference.",
        ],
        "docs": [
            "https://www.jenkins.io/doc/book/pipeline/syntax/",
            "https://www.jenkins.io/doc/pipeline/steps/",
        ],
    },
    {
        "pattern": r"Could not resolve dependencies|Failed to collect dependencies",
        "keywords": ["dependency resolution", "maven", "could not resolve"],
        "title": "Dependency Resolution Failure",
        "solutions": [
            "Check your dependency declarations in pom.xml / build.gradle / package.json.",
            "Verify network connectivity from the Jenkins agent.",
            "Check if repository URLs are correct and accessible.",
            "Clear local caches: ~/.m2/repository or node_modules/.",
            "If behind a proxy: configure Maven/npm proxy settings.",
        ],
        "docs": [
            "https://www.jenkins.io/doc/book/pipeline/docker/",
        ],
    },
    {
        "pattern": r"FATAL.*agent|Connection was broken|Agent.*offline|slave.*offline",
        "keywords": ["agent offline", "connection broken", "slave disconnected"],
        "title": "Agent Connection Failure",
        "solutions": [
            "Check agent machine is running and reachable from Jenkins controller.",
            "Verify SSH credentials and connectivity for SSH-based agents.",
            "Check Java version on the agent (must match controller requirements).",
            "Review agent logs in Manage Jenkins → Nodes → [agent] → Log.",
            "Increase connection timeout in agent configuration.",
            "For JNLP agents: ensure the agent process is running.",
        ],
        "docs": [
            "https://www.jenkins.io/doc/book/managing/nodes/",
        ],
    },
    {
        "pattern": r"docker.*not found|Cannot connect to the Docker daemon",
        "keywords": ["docker not found", "docker daemon", "docker"],
        "title": "Docker Not Available",
        "solutions": [
            "Ensure Docker is installed on the Jenkins agent.",
            "Verify Docker daemon is running: 'systemctl status docker'.",
            "Add the Jenkins user to the docker group: 'usermod -aG docker jenkins'.",
            "Restart Jenkins after adding user to docker group.",
            "If using Docker-in-Docker: mount the Docker socket correctly.",
        ],
        "docs": [
            "https://www.jenkins.io/doc/book/pipeline/docker/",
        ],
    },
    {
        "pattern": r"Build timed out|Timeout.*exceeded|hudson\.AbortException.*timeout",
        "keywords": ["timeout", "build timed out", "exceeded"],
        "title": "Build Timeout",
        "solutions": [
            "Increase timeout in pipeline: options { timeout(time: 30, unit: 'MINUTES') }",
            "Check if the build is stuck on user input or approval step.",
            "Review build logs for hanging processes or infinite loops.",
            "Check network connectivity if downloading dependencies.",
            "Consider splitting long builds into parallel stages.",
        ],
        "docs": [
            "https://www.jenkins.io/doc/book/pipeline/syntax/#options",
        ],
    },
    {
        "pattern": r"git.*fatal|Could not read from remote|Repository not found",
        "keywords": ["git fatal", "repository not found", "remote"],
        "title": "Git/SCM Connection Error",
        "solutions": [
            "Verify the Git repository URL is correct and accessible.",
            "Check credentials configuration in Jenkins Credentials Manager.",
            "For SSH: ensure SSH key is added and has access to the repository.",
            "For HTTPS: verify username/token credentials.",
            "Test connectivity manually: 'git ls-remote <repo-url>'.",
        ],
        "docs": [
            "https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-a-jenkinsfile",
            "https://plugins.jenkins.io/git/",
        ],
    },
]


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------


def extract_error_keywords(log_text: str) -> list[str]:
    """Extract relevant error keywords from a log/error text."""
    keywords: list[str] = []

    for pattern_info in ERROR_PATTERNS:
        if re.search(pattern_info["pattern"], log_text, re.IGNORECASE):
            keywords.extend(pattern_info["keywords"])

    # Also extract generic error indicators
    generic_patterns = [
        r"(ERROR|FATAL|FAILURE|Exception|Error)\b",
        r"exit\s+code\s+(\d+)",
        r"(FAILED|ABORTED)",
    ]
    for gp in generic_patterns:
        found = re.findall(gp, log_text, re.IGNORECASE)
        for item in found:
            if isinstance(item, str) and item:
                keywords.append(item)

    return list(set(keywords))


def match_error_patterns(log_text: str) -> list[dict]:
    """Match log text against known error patterns."""
    matches: list[dict] = []

    for pattern_info in ERROR_PATTERNS:
        if re.search(pattern_info["pattern"], log_text, re.IGNORECASE):
            matches.append(pattern_info)

    return matches


def format_troubleshooting(matches: list[dict]) -> str:
    """Format matched error patterns into a readable troubleshooting response."""
    if not matches:
        return (
            "I couldn't identify a specific known error pattern in the log. "
            "Here are some general troubleshooting steps:\n\n"
            "1. Check the full console output for the first ERROR line.\n"
            "2. Look for stack traces — the root cause is usually at the bottom.\n"
            "3. Check Manage Jenkins → System Log for controller-level errors.\n"
            "4. Verify plugin versions are up to date.\n"
            "5. Try 'Clean Workspace' and rebuild.\n"
            "6. Search community.jenkins.io or Stack Overflow for the error message."
        )

    parts: list[str] = []
    for m in matches:
        parts.append(f"## {m['title']}\n")
        parts.append("### Suggested Solutions\n")
        for s in m["solutions"]:
            parts.append(f"- {s}")
        if m.get("docs"):
            parts.append("\n### References")
            for url in m["docs"]:
                parts.append(f"- {url}")
        parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_error(log_text: str) -> dict:
    """
    Analyze an error log and return troubleshooting guidance.

    Args:
        log_text: Raw error log or error message from Jenkins.

    Returns:
        {
            "keywords": list of extracted error keywords,
            "matches": list of matched error patterns,
            "formatted": formatted troubleshooting response,
            "has_known_pattern": bool,
        }
    """
    keywords = extract_error_keywords(log_text)
    matches = match_error_patterns(log_text)

    return {
        "keywords": keywords,
        "matches": [
            {
                "title": m["title"],
                "solutions": m["solutions"],
                "docs": m.get("docs", []),
            }
            for m in matches
        ],
        "formatted": format_troubleshooting(matches),
        "has_known_pattern": len(matches) > 0,
    }
