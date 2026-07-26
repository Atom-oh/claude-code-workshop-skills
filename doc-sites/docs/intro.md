---
sidebar_position: 1
slug: /intro
title: 시작하기
---

# claude-code-workshop-skills 시작하기

**claude-code-workshop-skills**는 [Claude Code](https://claude.ai/code) 워크숍 실습용 플러그인 마켓플레이스입니다. 4개의 플러그인을 제공합니다.

## 플러그인 목록

| 플러그인 | 설명 | Agents | Skills |
|----------|------|--------|--------|
| [co-agent](/docs/co-agent/overview) | 멀티-AI 협업 (Kiro/Codex/Antigravity) — 리뷰·의사결정·ADR·컨텍스트 동기화·consensus·harness 파이프라인, 5개 명령 | 3 | 1 |
| [kiro](/docs/kiro/overview) | 비용 절감 구현 위임 — Claude가 계획·검증, Kiro CLI가 구독 크레딧으로 구현·리뷰, 4개 명령 | 1 | 1 |
| [project-init](/docs/project-init/overview) | 프로젝트 스캐폴딩, 문서 동기화, ADR 모순 검토, 10개 명령 | 3 | 3 |
| [kiro-power-converter](/docs/kiro-power-converter/overview) | Claude Code 플러그인 → Kiro Power 변환 | 1 | 1 |

## 설치 방법

### Marketplace에서 설치 (권장)

```bash
# 마켓플레이스 추가
/plugin marketplace add https://github.com/Atom-oh/claude-code-workshop-skills

# 플러그인 설치
/plugin install co-agent@claude-code-workshop-skills
/plugin install kiro@claude-code-workshop-skills
/plugin install project-init@claude-code-workshop-skills
/plugin install kiro-power-converter@claude-code-workshop-skills
```

### 로컬에서 직접 로드

```bash
# 저장소 클론
git clone https://github.com/Atom-oh/claude-code-workshop-skills.git

# 플러그인 디렉토리를 직접 지정하여 로드
claude --plugin-dir ./claude-code-workshop-skills/plugins/co-agent
claude --plugin-dir ./claude-code-workshop-skills/plugins/kiro
claude --plugin-dir ./claude-code-workshop-skills/plugins/project-init
claude --plugin-dir ./claude-code-workshop-skills/plugins/kiro-power-converter
```

## 플러그인 구조

각 플러그인은 동일한 구조를 따릅니다:

```
plugins/<plugin-name>/
├── .claude-plugin/plugin.json    # 매니페스트: agents[], skills[]
├── CLAUDE.md                     # 자동 호출 키워드 → 에이전트 라우팅 규칙
├── agents/<name>.md              # 에이전트 정의 (YAML frontmatter + markdown)
└── skills/<name>/                # 스킬 디렉토리
    ├── SKILL.md                  # 진입점 (YAML frontmatter + triggers)
    └── references/               # 참조 문서
```

## 다음 단계

- [co-agent 개요](/docs/co-agent/overview) — 멀티-AI 협업 플러그인 (리뷰·의사결정·ADR·컨텍스트 동기화 + `/co-agent:configure`)
- [kiro 개요](/docs/kiro/overview) — 비용 절감 구현 위임 플러그인 (Claude 계획·검증 + Kiro CLI 구현·리뷰)
- [project-init 개요](/docs/project-init/overview) — 프로젝트 스캐폴딩 플러그인
- [kiro-power-converter 개요](/docs/kiro-power-converter/overview) — Kiro Power 변환 플러그인
