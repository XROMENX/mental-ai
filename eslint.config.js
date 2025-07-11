import js from '@eslint/js';
import reactPlugin from 'eslint-plugin-react';
import jsxA11yPlugin from 'eslint-plugin-jsx-a11y';
import importPlugin from 'eslint-plugin-import';

export default [
  js.configs.recommended,
  {
    files: ['**/*.js', '**/*.jsx'],
    plugins: {
      react: reactPlugin,
      'jsx-a11y': jsxA11yPlugin,
      import: importPlugin
    },
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module'
    },
    settings: {
      react: { version: 'detect' }
    },
    rules: {
      'react/react-in-jsx-scope': 'off'
    }
  }
];
