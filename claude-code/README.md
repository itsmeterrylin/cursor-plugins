# pstack for Claude Code

This fork of `cursor/plugins` adds a Claude Code build of pstack. The build lives in `pstack-claude/`. Do not edit it by hand, because `adapt_pstack.py` rebuilds it from upstream `pstack/`.

## Install

```bash
claude plugin marketplace add itsmeterrylin/cursor-plugins
claude plugin install pstack@itsmeterrylin-pstack
```

## Update from upstream

```bash
cd ~/cursor-plugins
git checkout main
git fetch upstream && git merge upstream/main
python3 claude-code/adapt_pstack.py
claude plugin validate ./pstack-claude
git add -A && git commit -m "chore: sync pstack from upstream" && git push
claude plugin marketplace update itsmeterrylin-pstack
```

## What the adapter changes

| Cursor | Claude Code |
|---|---|
| `Task` tool, `AskQuestion`, `generalPurpose` | `Agent` tool, `AskUserQuestion`, `general-purpose` |
| Grok, GPT-5.6 Sol, Opus 5.5 slugs | `sonnet`, `fable`, `opus` |
| `~/.cursor/rules/pstack-models.mdc` | `~/.claude/pstack-models.md`, imported from `~/.claude/CLAUDE.md` |
| `~/.cursor/projects/<slug>/agent-transcripts/` | `~/.claude/projects/<slug>/` |
| `readonly: true` subagents | A read-only instruction in the subagent prompt |
| `environment: "cloud"` subagents | `isolation: "remote"` |
| `create-skill` built-in | `anthropic-skills:skill-creator` |
| `disable-model-invocation: true` on 46 skills | Removed, so the router can call each skill |

`overrides/` holds files that replace generated ones. Today that is `skills/setup-pstack/SKILL.md`.

## Known gaps

- Review panels (`arena`, `architect`, `interrogate`) use three Claude models, not three vendors, so they lose cross-vendor diversity.
- `deslop`, `control-cli`, and `control-ui` ship in `cursor-team-kit`, which this fork does not adapt.
