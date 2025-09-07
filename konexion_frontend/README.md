# Konexion Frontend

A modern, responsive web interface for AI model interactions built with SvelteKit, providing real-time chat capabilities with multiple AI providers.

## Overview

The Konexion Frontend is a SvelteKit-based web application that provides an intuitive interface for interacting with AI models through the Konexion Backend. It features real-time WebSocket communication, responsive design with Tailwind CSS, and support for multiple AI providers.

## Features

- 🚀 **Modern SvelteKit Framework**: Built with Svelte 5 and SvelteKit 2
- 💬 **Real-time Chat Interface**: WebSocket-based streaming responses
- 🎨 **Responsive Design**: Built with Tailwind CSS 4
- 🌓 **Dark/Light Mode**: Automatic theme switching
- ⌨️ **Keyboard Shortcuts**: Enhanced productivity features
- 🔄 **Hot Module Replacement**: Fast development with Vite
- 📱 **Mobile-Friendly**: Responsive design for all devices
- 🎯 **Type-Safe**: ESLint and Prettier for code quality

## Tech Stack

- **Framework**: SvelteKit 2.22+
- **Build Tool**: Vite 7
- **Styling**: Tailwind CSS 4
- **Language**: JavaScript ES2022+
- **Code Quality**: ESLint + Prettier
- **Syntax Highlighting**: Highlight.js
- **Markdown Rendering**: Marked

## Prerequisites

- **Node.js**: 18.0 or higher
- **Package Manager**: npm, pnpm, or yarn
- **Backend**: Konexion Backend running on port 8000

## Installation

### 1. Install Dependencies

```bash
# Using npm
npm install

# Using pnpm (recommended)
pnpm install

# Using yarn
yarn install
```

### 2. Environment Setup

The frontend automatically connects to the backend via proxy configuration. Ensure the backend is running on `http://localhost:8000`.

If you need to change the backend URL, modify the proxy configuration in `vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://your-backend-url:port',
      changeOrigin: true,
      secure: false,
    },
  },
}
```

## Development

### Start Development Server

```bash
# Using npm
npm run dev

# Using pnpm
pnpm dev

# Using yarn
yarn dev

# Open in browser automatically
npm run dev -- --open
```

The development server will start on `http://localhost:5173` by default.

### Development Features

- **Hot Module Replacement**: Changes are reflected instantly
- **Error Overlay**: Detailed error information in the browser
- **Source Maps**: Debug with original source code
- **TypeScript Support**: Full TypeScript integration

## Building

### Production Build

```bash
# Using npm
npm run build

# Using pnpm
pnpm build

# Using yarn
yarn build
```

### Preview Production Build

```bash
# Using npm
npm run preview

# Using pnpm
pnpm preview

# Using yarn
yarn preview
```

The preview server will start on `http://localhost:4173`.

## Code Quality

### Linting

```bash
# Check code style
npm run lint

# Fix linting issues automatically
npm run format
```

### Code Formatting

The project uses Prettier for code formatting with the following plugins:
- `prettier-plugin-svelte`: Svelte component formatting
- `prettier-plugin-tailwindcss`: Tailwind class sorting

## Project Structure

```
src/
├── routes/                # SvelteKit routes
│   ├── +layout.svelte     # Global layout
│   ├── +page.svelte       # Home page
│   └── +page.js           # Page load functions
├── lib/                   # Shared utilities and components
│   ├── components/        # Svelte components
│   │   ├── ChatInput.svelte
│   │   ├── ChatWindow.svelte
│   │   ├── CodeBlock.svelte
│   │   ├── ConnectionStatus.svelte
│   │   ├── ErrorMessage.svelte
│   │   ├── Header.svelte
│   │   ├── KeyboardShortcuts.svelte
│   │   ├── LoadingSpinner.svelte
│   │   └── ModelSelector.svelte
│   ├── assets/          # Static assets
│   ├── api.js           # API client functions
│   ├── stores.js        # Svelte stores
│   ├── websocket.js     # WebSocket management
│   ├── validation.js    # Input validation
│   └── performance.js   # Performance utilities
├── app.html             # HTML template
└── app.css              # Global styles
```

## Configuration Files

- **`vite.config.js`**: Vite and development server configuration
- **`svelte.config.js`**: SvelteKit configuration
- **`tailwind.config.js`**: Tailwind CSS configuration
- **`eslint.config.js`**: ESLint rules and settings
- **`package.json`**: Dependencies and scripts

## API Integration

The frontend communicates with the backend through:

### REST API
- **GET /models**: Fetch available AI models
- **WebSocket /chat**: Real-time chat communication

### WebSocket Events
- `message`: Send chat messages
- `model_change`: Switch AI models
- `error`: Handle error responses
- `stream`: Receive streaming responses

## Components

### Core Components

- **ChatWindow**: Main chat interface with message history
- **ChatInput**: Message input with validation and shortcuts
- **ModelSelector**: AI model selection dropdown
- **ConnectionStatus**: Backend connection indicator
- **CodeBlock**: Syntax-highlighted code rendering

### Utility Components

- **LoadingSpinner**: Loading state indicator
- **ErrorMessage**: Error display component
- **KeyboardShortcuts**: Help modal for shortcuts

## Keyboard Shortcuts

- **Ctrl/Cmd + Enter**: Send message
- **Ctrl/Cmd + L**: Clear chat
- **Ctrl/Cmd + D**: Toggle dark mode
- **Ctrl/Cmd + K**: Focus model selector
- **Ctrl/Cmd + ?**: Show shortcuts help

## Styling

### Tailwind CSS 4

The project uses Tailwind CSS 4 with the following features:
- **CSS-first configuration**: Modern @config directive
- **Container queries**: Responsive design utilities
- **Form styling**: Enhanced form components
- **Typography**: Rich text formatting

### Custom Styles

Global styles are defined in `src/app.css` and include:
- CSS custom properties for theming
- Base component styles
- Responsive typography scales

## Deployment

### Static Site Generation

```bash
# Build for static hosting
npm run build

# The build output will be in the 'build' directory
```

### Deployment Platforms

The application can be deployed to:
- **Vercel**: Automatic SvelteKit support
- **Netlify**: Static site hosting
- **GitHub Pages**: Static hosting
- **Docker**: Container deployment

### Environment Variables

For production deployment, you may need to set:
- `VITE_API_URL`: Backend API URL (if different from proxy)
- `VITE_WS_URL`: WebSocket URL (if different from proxy)

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure the backend is running on port 8000
   - Check proxy configuration in `vite.config.js`

2. **WebSocket Connection Issues**
   - Verify backend WebSocket endpoint is accessible
   - Check browser developer tools for connection errors

3. **Build Errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Update dependencies: `npm update`

4. **Styling Issues**
   - Ensure Tailwind is properly configured
   - Check for CSS conflicts in browser developer tools

### Development Tools

- **Browser DevTools**: Network, Console, and Elements tabs
- **Svelte DevTools**: Browser extension for Svelte debugging
- **Vite DevTools**: Development server information

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`npm run lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow the existing code style (Prettier + ESLint)
- Write meaningful component names and comments
- Test components in different browsers
- Ensure responsive design works on mobile devices
- Update documentation for new features

## Performance

### Optimization Features

- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Dead code elimination
- **Asset Optimization**: Image and font optimization
- **Lazy Loading**: Dynamic imports for large components

### Performance Monitoring

The application includes performance utilities in `lib/performance.js` for monitoring:
- WebSocket connection latency
- Message rendering times
- Component load times

## License

This project is licensed under the MIT License - see the main project README for details.
