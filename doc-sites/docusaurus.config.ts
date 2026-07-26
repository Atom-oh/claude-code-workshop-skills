import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'claude-code-workshop-skills',
  tagline: 'Claude Code 워크숍 실습용 플러그인 마켓플레이스',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://www.atomai.click',
  baseUrl: '/claude-code-workshop-skills/',

  organizationName: 'Atom-oh',
  projectName: 'claude-code-workshop-skills',

  onBrokenLinks: 'throw',

  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],

  i18n: {
    defaultLocale: 'ko',
    locales: ['ko'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/Atom-oh/claude-code-workshop-skills/tree/main/doc-sites/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/og-image.png',
    colorMode: {
      defaultMode: 'dark',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'claude-code-workshop-skills',
      logo: {
        alt: 'claude-code-workshop-skills Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'intro',
          position: 'left',
          label: 'Home',
        },
        {
          type: 'docSidebar',
          sidebarId: 'coAgent',
          position: 'left',
          label: 'co-agent',
        },
        {
          type: 'docSidebar',
          sidebarId: 'kiro',
          position: 'left',
          label: 'kiro',
        },
        {
          type: 'docSidebar',
          sidebarId: 'kiroConverter',
          position: 'left',
          label: 'kiro-power-converter',
        },
        {
          href: 'https://github.com/Atom-oh/claude-code-workshop-skills',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Plugins',
          items: [
            {label: 'co-agent', to: '/docs/co-agent/overview'},
            {label: 'kiro', to: '/docs/kiro/overview'},
            {label: 'kiro-power-converter', to: '/docs/kiro-power-converter/overview'},
          ],
        },
        {
          title: 'Guides',
          items: [
            {label: '시작하기', to: '/docs/intro'},
          ],
        },
        {
          title: 'Links',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/Atom-oh/claude-code-workshop-skills',
            },
            {
              label: 'Claude Code',
              href: 'https://claude.ai/code',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Atom-oh. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'yaml', 'json', 'python', 'typescript', 'markdown'],
    },
    mermaid: {
      theme: {light: 'neutral', dark: 'dark'},
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
