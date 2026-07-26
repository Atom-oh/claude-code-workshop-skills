import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

const plugins = [
  {
    title: 'co-agent',
    description: 'Kiro/Codex/Agy와 협업해 코드/아키텍처 리뷰, 의사결정 보조, ADR 작성을 진행합니다. 자율 doc→plan→구현 consensus 파이프라인과 harness 오케스트레이터도 지원합니다.',
    agents: 3,
    skills: 1,
    link: '/docs/co-agent/overview',
  },
  {
    title: 'kiro',
    description: 'Claude가 계획을 세우고 검증하며, Kiro CLI가 자체 구독 크레딧으로 격리된 git worktree 안에서 구현을 수행합니다. 비용 절감형 구현 위임 플러그인입니다.',
    agents: 1,
    skills: 1,
    link: '/docs/kiro/overview',
  },
  {
    title: 'kiro-power-converter',
    description: 'Claude Code 플러그인을 Kiro Power 포맷으로 변환합니다. GitHub URL, 로컬 경로, 마켓플레이스 이름을 지원합니다.',
    agents: 1,
    skills: 1,
    link: '/docs/kiro-power-converter/overview',
  },
];

function PluginCard({title, description, agents, skills, link}: typeof plugins[0]) {
  return (
    <div className={clsx('col col--4')}>
      <Link to={link} style={{textDecoration: 'none', color: 'inherit'}}>
        <div className="plugin-card">
          <div className="plugin-card__title">{title}</div>
          <div className="plugin-card__description">{description}</div>
          <div className="plugin-card__stats">
            <span>{agents} Agents</span>
            <span>{skills} Skills</span>
          </div>
        </div>
      </Link>
    </div>
  );
}

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            시작하기
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="Home"
      description={siteConfig.tagline}>
      <HomepageHeader />
      <main>
        <section style={{padding: '3rem 0'}}>
          <div className="container">
            <div className="row">
              {plugins.map((plugin) => (
                <PluginCard key={plugin.title} {...plugin} />
              ))}
            </div>
          </div>
        </section>
        <section style={{padding: '2rem 0 4rem'}}>
          <div className="container">
            <div className="row">
              <div className="col col--8 col--offset-2" style={{textAlign: 'center'}}>
                <Heading as="h2">Claude Code Plugin Marketplace</Heading>
                <p style={{fontSize: '1.1rem', color: 'var(--ifm-font-color-secondary)'}}>
                  <code>/plugin marketplace add claude-code-workshop-skills</code> 명령어 하나로 설치하고,
                  자연어로 멀티 AI 협업, 구현 위임, 프로젝트 초기화를 진행하세요.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
