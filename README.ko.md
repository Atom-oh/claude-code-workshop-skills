# claude-code-workshop-skills

워크숍 실습용 Claude Code 플러그인 마켓플레이스 — AWS 내부 전용 플러그인은 제외했습니다.

## 플러그인

| 플러그인 | 설명 |
|--------|--------------|
| **co-agent** | 다중 AI 협업 (Kiro CLI, Codex, Antigravity): 리뷰, 의사결정 지원, ADR 공동 작성 — Claude가 의장 역할 |
| **kiro** | 비용 절감형 위임: Claude가 계획을 세우고 검증하며, Kiro CLI가 자체 구독 크레딧으로 격리된 git worktree 안에서 구현 수행 |
| **project-init** | 프로젝트 스캐폴딩 및 문서 관리 |
| **kiro-power-converter** | Claude Code 플러그인을 Kiro IDE Power 포맷으로 변환 |

## 사용법

```
/plugin marketplace add git@github.com:Atom-oh/claude-code-workshop-skills.git
/plugin install co-agent
/plugin install kiro
/plugin install project-init
/plugin install kiro-power-converter
```

또는 로컬에서 테스트용으로 플러그인을 불러올 수 있습니다:

```
claude --plugin-dir ./plugins/co-agent
```
