---
name: setup-pstack
description: Configure which Claude model pstack uses per role. Writes ~/.claude/pstack-models.md, which overrides the skill defaults. Use for /setup-pstack, "configure pstack models", or changing pstack's model choices.
---

# Setup pstack

Write `~/.claude/pstack-models.md`, the file that sets pstack's model per role. `~/.claude/CLAUDE.md` imports it with `@~/.claude/pstack-models.md`, so every session reads it.

## Steps

### 1. Available models

The Agent tool's `model` parameter accepts `opus`, `sonnet`, `haiku`, and `fable`. The alias `inherit-parent` means: omit `model`, so the role runs on the parent chat model. There is no per-subagent reasoning budget in Claude Code. A subagent's effort comes from its agent definition.

### 2. Load current state

If `~/.claude/pstack-models.md` exists, read it and treat its role values as the current choices. Otherwise start from the defaults in step 4. Drop any role line that step 4 does not list.

### 3. Map and confirm

Show every role with its model. Ask with AskUserQuestion whether to accept as-is or change specific roles. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one subagent runs per entry, so the list length sets the count. Claude Code has one model family, so a panel gets its diversity from different Claude models, not different vendors.

### 4. Write the file

Overwrite the whole file so reruns stay idempotent. Shape:

```
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit-parent` as a value: the role runs on the parent chat model (omit Agent `model`).
feature, refactoring: sonnet
bug-fix: sonnet
perf-issue: sonnet
hillclimb: sonnet
judgment and prose: opus
hardest tasks: opus
how explorer: sonnet
how explainer: opus
why investigators: sonnet
why synthesizer: opus
reflect tooling: fable
reflect judgment, divergent, synthesizer: opus
arena runners: opus, fable, sonnet
arena cross-judge pool: opus, fable, sonnet
swarm workers: sonnet
architect runners: opus, fable, sonnet
interrogate reviewers: opus, fable, sonnet
```

Then confirm `~/.claude/CLAUDE.md` contains the line `@~/.claude/pstack-models.md`. Add it if it is missing.

### 5. Confirm

Tell the user the file was written and that it applies to new sessions.

### 6. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill." On yes, invoke `/create-verification-skill`. On no, move on without pushing.
