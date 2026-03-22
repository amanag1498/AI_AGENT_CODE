from pathlib import Path


SKIP_EXTENSIONS = {
    ".lock", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".mp4", ".mp3", ".pdf", ".zip", ".tar", ".gz", ".woff", ".woff2",
    ".class", ".jar", ".min.js", ".map"
}

SKIP_FILENAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Cargo.lock"
}


def should_skip_file(filename: str) -> bool:
    lower = filename.lower()
    name = Path(lower).name

    if name in SKIP_FILENAMES:
        return True

    for ext in SKIP_EXTENSIONS:
        if lower.endswith(ext):
            return True

    bad_dirs = ("dist/", "build/", "node_modules/", "vendor/", ".git/", ".venv/", "__pycache__/")
    return any(part in lower for part in bad_dirs)


def trim_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [TRUNCATED]"


def build_prompt(
    patches: list[dict],
    max_files: int,
    max_patch_chars_per_file: int,
) -> str:
    usable = []
    for item in patches:
        filename = item["filename"]
        if should_skip_file(filename):
            continue
        patch = item.get("patch", "")
        if not patch.strip():
            continue
        usable.append({
            "filename": filename,
            "patch": trim_text(patch, max_patch_chars_per_file),
        })

    usable = usable[:max_files]

    lines = [
        "Review this code diff.",
        "",
        "Focus only on:",
        "- correctness bugs",
        "- security issues",
        "- performance problems",
        "- maintainability risks likely to matter in production",
        "- missing tests for risky logic changes",
        "",
        "Ignore:",
        "- formatting",
        "- style-only suggestions",
        "- trivial naming opinions",
        "",
        "Return valid JSON only using this exact schema:",
        "{",
        '  "summary": "string",',
        '  "findings": [',
        "    {",
        '      "severity": "high|medium|low",',
        '      "file": "string",',
        '      "title": "string",',
        '      "impact": "string",',
        '      "suggested_fix": "string",',
        '      "confidence": 0.0',
        "    }",
        "  ]",
        "}",
        "",
        "Files and patches:"
    ]

    if not usable:
        lines.append("No reviewable text patches found.")
    else:
        for item in usable:
            lines.extend([
                "",
                f"File: {item['filename']}",
                "Patch:",
                item["patch"],
            ])

    return "\n".join(lines)
