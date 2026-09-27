#!/usr/bin/env python3
"""Generate pstack-claude/ (a Claude Code plugin) from upstream pstack/.

Rerun after every `git merge upstream/main`. The output is rebuilt from
scratch, so the run is idempotent. Hand-written files in overrides/ replace
generated ones where a mechanical rewrite is not enough.
"""

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "pstack"
OUT = ROOT / "pstack-claude"
OVERRIDES = Path(__file__).resolve().parent / "overrides"

COPY = ["skills", "agents", "docs", "LICENSE", "README.md", "assets"]

TRANSCRIPTS = (
    "the current project's transcript directory, `~/.claude/projects/<slug>/`, "
    "where `<slug>` is the working directory with every \"/\" turned into \"-\""
)

REPLACEMENTS: list[tuple[str, str]] = [
    # Models. The Agent tool accepts only Claude aliases.
    (r"grok-4\.7-(xhigh|medium)-fast", "sonnet"),
    (r"claude-opus-5-5-(max|medium)", "opus"),
    (r"gpt-5\.6-sol-max", "fable"),
    # Model config file.
    (r"~/\.cursor/rules/pstack-models\.mdc", "~/.claude/pstack-models.md"),
    (r"`pstack-models\.mdc` rule", "`~/.claude/pstack-models.md` file"),
    # Tools and subagent types.
    (r"\bAskQuestion\b", "AskUserQuestion"),
    (r"`generalPurpose`", "`general-purpose`"),
    (r"\bgeneralPurpose\b", "general-purpose"),
    (r"`Task`", "`Agent`"),
    (r"\bTask (tool|call|calls|subagent)\b", r"Agent \1"),
    (r'subagent_type: "poteto-agent"', 'subagent_type: "pstack:poteto-agent"'),
    (r'subagent_type: "Comment Sicko"', 'subagent_type: "pstack:comment-sicko"'),
    (r"`poteto-agent`", "`pstack:poteto-agent`"),
    (r"^- `readonly`: `true`\n", "- Tell the subagent it is read-only: no file edits.\n"),
    (r"^- `readonly`: `false`.*\n", ""),
    (r", agent mode \(`readonly: false`\)", ""),
    (r", agent mode \(readonly strips MCP\)", ""),
    # Transcripts.
    (r"the active workspace's `agent-transcripts/` directory \(the system prompt names (the|this) path\)", TRANSCRIPTS),
    (r"the active workspace's `agent-transcripts/` directory", TRANSCRIPTS),
    (r"The system prompt names the workspace's `agent-transcripts/` directory\. Use (that|only that) path\.", "Use only that directory."),
    (r"The system prompt names the active workspace's `agent-transcripts/` directory\. Use that path\.", "Use only that directory."),
    (r"~/\.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>\.jsonl", "~/.claude/projects/<slug>/<session-uuid>.jsonl"),
    (r"with the leading slash dropped and each \"/\" turned into \"-\" \(so `/Users/you/proj` becomes `Users-you-proj`\)",
     "with each \"/\" turned into \"-\" (so `/Users/you/proj` becomes `-Users-you-proj`)"),
    (r"~/\.cursor/projects/", "~/.claude/projects/"),
    # Skill locations.
    (r"~/\.cursor/plugins/", "~/.claude/plugins/"),
    (r"~/\.cursor/skills/", "~/.claude/skills/"),
    (r"\.cursor/skills/", ".claude/skills/"),
    (r"\.cursor/worktrees/", ".claude/worktrees/"),
    # Cursor built-ins.
    (r"the \*\*create-skill\*\* skill \(Cursor's built-in for authoring SKILL\.md files\)", "the **anthropic-skills:skill-creator** skill"),
    (r"Cursor's built-in `create-skill` skill", "the `anthropic-skills:skill-creator` skill"),
    (r"Cursor's built-in `create-skill`", "`anthropic-skills:skill-creator`"),
    (r", and not Cursor's built-in babysit skill, whose description matches the same words", ""),
    (r" This playbook replaces Cursor's built-in babysit skill for these requests, so do not route there even though i[^.]*\.", ""),
    (r"Cursor's `/loop` command \(a built-in, not a pstack skill\)", "the `/loop` skill (a Claude Code built-in, not a pstack skill)"),
    (r"list the available MCPs from the Cursor environment\. Use the available-tools map when present\. Otherwise inspect the `mcps/` directory Cursor exposes for enabled MCP servers\.",
     "list the MCP servers available in this session: the loaded `mcp__*` tools and the deferred tool names."),
    (r"Families go by prefix: `claude-\*`, `gpt-\*`, and `grok-\*`\. With no family match, use", "Otherwise use"),
    (r"The system prompt names (the current project's transcript directory)", r"Use \1"),
    (r"<agent-transcripts>", "~/.claude/projects/<slug>"),
    (r"`agent-transcripts/`", "`~/.claude/projects/<slug>/`"),
    (r'`environment: "cloud"`', '`isolation: "remote"`'),
    (r"^name: Poteto Mode$", "name: poteto-mode"),
    (r"^name: Make Bot UI$", "name: make-bot-ui"),
    (r"Cursor restart", "Claude Code restart"),
    (r"the Cursor dashboard", "the claude.ai/code session list"),
]

FRONTMATTER_DROP = re.compile(r"^(disable-model-invocation|mode|icon|color|reminder|is_background):.*\n", re.M)


def rewrite(text: str) -> str:
    for pattern, repl in REPLACEMENTS:
        text = re.sub(pattern, repl, text, flags=re.M)
    return text


def strip_frontmatter_keys(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.index("\n---\n", 4)
    return FRONTMATTER_DROP.sub("", text[: end + 1]) + text[end + 1 :]


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for name in COPY:
        src = SRC / name
        if src.is_dir():
            shutil.copytree(src, OUT / name)
        else:
            shutil.copy2(src, OUT / name)

    sicko = OUT / "agents" / "comment-sicko.md"
    sicko.write_text(sicko.read_text().replace("name: Comment Sicko", "name: comment-sicko", 1))

    for path in OUT.rglob("*.md"):
        text = rewrite(path.read_text())
        if path.name == "SKILL.md" or path.parent.name == "agents":
            text = strip_frontmatter_keys(text)
        path.write_text(text)

    if OVERRIDES.exists():
        shutil.copytree(OVERRIDES, OUT, dirs_exist_ok=True)

    upstream = json.loads((SRC / ".cursor-plugin" / "plugin.json").read_text())
    manifest = {
        "name": "pstack",
        "version": upstream["version"],
        "description": upstream["description"],
        "author": upstream.get("author", {}),
        "license": upstream.get("license", "MIT"),
    }
    (OUT / ".claude-plugin").mkdir()
    (OUT / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    build()
    print(f"built {OUT.relative_to(ROOT)}")
