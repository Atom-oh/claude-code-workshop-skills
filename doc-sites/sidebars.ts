import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  intro: [
    'intro',
  ],

  coAgent: [
    'co-agent/overview',
    'co-agent/installation',
    'co-agent/usage-guide',
    'co-agent/agents/co-agent',
    'co-agent/skills/co-agent',
    'co-agent/commands/commands',
  ],

  kiro: [
    'kiro/overview',
    'kiro/installation',
    'kiro/usage-guide',
    'kiro/agents/kiro-delegate-agent',
    'kiro/skills/kiro-delegate',
    'kiro/commands/commands',
  ],

  projectInit: [
    'project-init/overview',
    'project-init/installation',
    'project-init/agents/doc-sync-checker',
    'project-init/skills/project-scaffolder',
    'project-init/skills/pr-autofix',
    'project-init/skills/decision-reconcile',
    'project-init/commands/commands',
  ],

  kiroConverter: [
    'kiro-power-converter/overview',
    'kiro-power-converter/installation',
    'kiro-power-converter/agents/kiro-converter-agent',
    'kiro-power-converter/skills/kiro-convert',
    'kiro-power-converter/demos/conversion-example',
  ],
};

export default sidebars;
