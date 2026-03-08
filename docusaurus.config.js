// @ts-check
const { themes: prismThemes } = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Learn ROS 2, Gazebo, Isaac Sim, VLA, and Humanoid Control with AI',
  favicon: 'img/favicon.ico',
  url: 'https://yourusername.github.io',
  baseUrl: '/robotics-ai-textbook/',
  organizationName: 'yourusername',
  projectName: 'robotics-ai-textbook',
  deploymentBranch: 'gh-pages',
  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur'],
    localeConfigs: {
      en: {
        label: 'English',
        htmlLang: 'en-US',
      },
      ur: {
        label: 'اردو',
        htmlLang: 'ur-PK',
        direction: 'rtl',
      },
    },
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl:
            'https://github.com/yourusername/robotics-ai-textbook/tree/main/frontend',
          showLastUpdateAuthor: false,
          showLastUpdateTime: false,
        },
        blog: {
          showReadingTime: true,
          editUrl:
            'https://github.com/yourusername/robotics-ai-textbook/tree/main/frontend',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/robotics-social-card.jpg',
      navbar: {
        title: 'Robotics AI Textbook',
        logo: {
          alt: 'Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Chapters',
          },
          {
            type: 'localeDropdown',
            position: 'right',
          },
          {
            href: 'https://github.com/yourusername/robotics-ai-textbook',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Introduction',
                to: '/docs/introduction',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub Issues',
                href: 'https://github.com/yourusername/robotics-ai-textbook/issues',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/yourusername/robotics-ai-textbook',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Robotics AI Textbook. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.palenight,
        additionalLanguages: ['python', 'cpp', 'bash', 'yaml', 'json'],
      },
      // Algolia search — uncomment and fill in real credentials when ready
      // algolia: {
      //   appId: 'YOUR_ALGOLIA_APP_ID',
      //   apiKey: 'YOUR_ALGOLIA_SEARCH_API_KEY',
      //   indexName: 'robotics-ai-textbook',
      // },
    }),

  stylesheets: [
    {
      href: 'https://fonts.googleapis.com/css2?family=Noto+Sans+Urdu:wght@400;700&display=swap',
      type: 'text/css',
    },
  ],

  scripts: [
    {
      src: 'https://fonts.googleapis.com/css2?family=Noto+Sans+Urdu:wght@400;700&display=swap',
      async: true,
    },
  ],
};

module.exports = config;