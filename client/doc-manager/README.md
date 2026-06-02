# Frontend

This folder is reserved for the React (TypeScript) frontend implementation.

## Requirements

- **Framework:** Use **React** with **TypeScript**
- **Language:** TypeScript
- **UI Library:** Material UI (MUI)
- **Authentication:** Login must integrate with Django backend  
- **Tooling:** Code must demonstrate use of:
  - React best practices  
  - UI design principles and clean component styling  
  - TypeScript and JavaScript fundamentals  
  - Automated code consistency tooling (e.g. ESLint, Prettier)
  - Unit testing for at least one UI component
- **Bundler:** Vite (preferred)

## ✨ Features to Implement

### 🔐 Login Page
- Authenticates with the Django backend
- All routes after login should be protected

### 📁 My Files Page
- A button to select and upload a document
- Below the button: a paginated data grid showing uploaded files
- Data grid columns:
  - File Name  
  - Version  
  - Actions:
    - **View Versions:** Opens modal listing file versions with copy-to-clipboard shareable links
    - **Download Latest:** Downloads latest version of the file
    - **Upload New Version:** Opens modal showing next version number and allows file upload
    - **Favorite:** Marks file as a favorite (persisted locally); shows in a separate "Favorites" tab

## Notes

- Submissions using frameworks other than React (e.g., Vue, Angular) will not be considered.

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
