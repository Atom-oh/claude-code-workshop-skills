# claude-code-workshop-skills

Claude Code plugin marketplace for workshop practice — AWS-internal plugins excluded.

## Plugins

| Plugin | What it does |
|--------|--------------|
| **co-agent** | Multi-AI collaboration (Kiro CLI, Codex, Antigravity): review, decision support, ADR co-authoring — Claude chairs |
| **kiro** | Cost-savings delegation: Claude plans and verifies, Kiro CLI implements and reviews on its own subscription credits inside an isolated git worktree |
| **project-init** | Project scaffolding and documentation management |
| **kiro-power-converter** | Convert Claude Code plugins to Kiro IDE Power format |

## Usage

```
/plugin marketplace add git@github.com:Atom-oh/claude-code-workshop-skills.git
/plugin install co-agent
/plugin install kiro
/plugin install project-init
/plugin install kiro-power-converter
```

Or load a plugin locally for testing:

```
claude --plugin-dir ./plugins/co-agent
```
