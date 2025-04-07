# Vue Chat Interface

A modern chat interface component built with Vue 3 and Tailwind CSS.

## Features

- Clean and modern UI design
- Responsive layout
- Real-time message updates
- User and bot message differentiation
- Enter key support for sending messages

## Installation

1. Make sure you have Vue 3 installed
2. Install Tailwind CSS:
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

3. Add the component to your project:
```vue
import ChatInterface from './ChatInterface.vue'
```

## Usage

```vue
<template>
  <ChatInterface />
</template>

<script setup>
import ChatInterface from './ChatInterface.vue'
</script>
```

## Customization

You can customize the chat interface by:
- Modifying the colors in the template
- Adding more features to the message handling
- Customizing the styling in the style section
- Adding additional UI elements

## License

MIT 