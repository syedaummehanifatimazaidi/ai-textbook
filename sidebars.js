/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Course Modules',
      items: [
        'introduction',
        'ros2-basics',
        'gazebo-simulation',
        'unity-integration',
        'nvidia-isaac',
        'vla-foundation',
        'whisper-audio',
        'humanoid-robotics',
      ],
    },
    {
      type: 'category',
      label: 'Resources',
      items: [
        'glossary',
        'faq',
        'references',
      ],
    },
  ],
};

module.exports = sidebars;
