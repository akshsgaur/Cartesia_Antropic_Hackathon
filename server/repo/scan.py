from __future__ import annotations

import asyncio
import os
import logging
from collections import Counter
from pathlib import Path

from models import RepoScan

logger = logging.getLogger(__name__)

EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox",
                "dist", "build", ".next", ".nuxt", "target", "vendor"}


async def scan_repo(repo_path: str) -> RepoScan:
    """Scan a repo: tree structure, file extensions, language/framework probes."""
    root = Path(repo_path)
    if not root.is_dir():
        raise ValueError(f"Not a directory: {repo_path}")

    extensions: Counter[str] = Counter()
    tree_lines: list[str] = []
    total_files = 0

    for dirpath, dirnames, filenames in os.walk(repo_path):
        # Prune excluded dirs
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        rel = os.path.relpath(dirpath, repo_path)
        depth = rel.count(os.sep)
        if depth > 4:
            dirnames.clear()
            continue

        indent = "  " * depth
        dirname = os.path.basename(dirpath)
        tree_lines.append(f"{indent}{dirname}/")

        for fname in filenames:
            if fname.startswith("."):
                continue
            ext = Path(fname).suffix.lower()
            if ext:
                extensions[ext] += 1
            total_files += 1
            if depth <= 2:
                tree_lines.append(f"{indent}  {fname}")

    # Probe for frameworks/languages
    frameworks: list[str] = []
    languages: list[str] = []

    probes = {
        "package.json": ("Node.js/JavaScript", None),
        "requirements.txt": ("Python", None),
        "Pipfile": ("Python", None),
        "pyproject.toml": ("Python", None),
        "go.mod": ("Go", None),
        "Cargo.toml": ("Rust", None),
        "pom.xml": ("Java", "Maven"),
        "build.gradle": ("Java/Kotlin", "Gradle"),
        "Gemfile": ("Ruby", None),
        "composer.json": ("PHP", None),
        "tsconfig.json": ("TypeScript", None),
        "Dockerfile": (None, "Docker"),
        "docker-compose.yml": (None, "Docker Compose"),
        ".github/workflows": (None, "GitHub Actions"),
    }

    for filename, (lang, fw) in probes.items():
        probe_path = root / filename
        if probe_path.exists():
            if lang and lang not in languages:
                languages.append(lang)
            if fw and fw not in frameworks:
                frameworks.append(fw)

    # Check package.json for framework hints
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            import json
            data = json.loads(pkg_json.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            fw_probes = {
                "react": "React", "next": "Next.js", "vue": "Vue.js",
                "nuxt": "Nuxt.js", "express": "Express", "fastify": "Fastify",
                "nestjs": "NestJS", "angular": "Angular", "svelte": "Svelte",
            }
            for pkg, fw_name in fw_probes.items():
                if any(pkg in k for k in deps) and fw_name not in frameworks:
                    frameworks.append(fw_name)
        except Exception:
            pass

    # Infer languages from extensions
    ext_lang = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".go": "Go", ".rs": "Rust", ".java": "Java", ".rb": "Ruby",
        ".php": "PHP", ".c": "C", ".cpp": "C++", ".cs": "C#",
        ".swift": "Swift", ".kt": "Kotlin",
    }
    for ext, count in extensions.most_common(5):
        lang = ext_lang.get(ext)
        if lang and lang not in languages:
            languages.append(lang)

    tree = "\n".join(tree_lines[:100])  # cap tree output

    return RepoScan(
        tree=tree,
        extensions=dict(extensions),
        frameworks=frameworks,
        languages=languages,
        total_files=total_files,
    )
