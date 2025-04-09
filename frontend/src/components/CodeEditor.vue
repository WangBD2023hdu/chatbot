<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-3/4 h-3/4 flex flex-col">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">Code Editor</h2>
        <button @click="closeEditor" class="text-gray-500 hover:text-gray-700">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="flex-1 grid grid-cols-2 gap-4">
        <!-- CSS Editor -->
        <div class="flex flex-col">
          <div class="flex justify-between items-center mb-2">
            <h3 class="text-lg font-medium">CSS</h3>
            <button @click="saveCSS" class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600">
              Save CSS
            </button>
          </div>
          <textarea
            v-model="cssCode"
            class="flex-1 font-mono p-2 border rounded-lg resize-none"
            spellcheck="false"
          ></textarea>
        </div>

        <!-- JavaScript Editor -->
        <div class="flex flex-col">
          <div class="flex justify-between items-center mb-2">
            <h3 class="text-lg font-medium">JavaScript</h3>
            <button @click="saveJavaScript" class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600">
              Save JavaScript
            </button>
          </div>
          <textarea
            v-model="jsCode"
            class="flex-1 font-mono p-2 border rounded-lg resize-none"
            spellcheck="false"
          ></textarea>
        </div>
      </div>

      <div class="mt-4 flex justify-end space-x-2">
        <button
          @click="applyChanges"
          class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          :disabled="isSaving"
        >
          {{ isSaving ? 'Saving...' : 'Apply Changes' }}
        </button>
        <button
          @click="closeEditor"
          class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  apiEndpoint: String,
  apiKey: String
})

const emit = defineEmits(['close', 'update'])

const cssCode = ref('')
const jsCode = ref('')
const isSaving = ref(false)

const loadCode = async () => {
  try {
    const response = await axios.get(`${props.apiEndpoint}/code`, {
      headers: {
        'Authorization': `Bearer ${props.apiKey}`
      }
    })
    cssCode.value = response.data.css || ''
    jsCode.value = response.data.js || ''
  } catch (error) {
    console.error('Error loading code:', error)
  }
}

const saveCSS = async () => {
  try {
    await axios.post(`${props.apiEndpoint}/code/css`, {
      code: cssCode.value
    }, {
      headers: {
        'Authorization': `Bearer ${props.apiKey}`
      }
    })
  } catch (error) {
    console.error('Error saving CSS:', error)
  }
}

const saveJavaScript = async () => {
  try {
    await axios.post(`${props.apiEndpoint}/code/js`, {
      code: jsCode.value
    }, {
      headers: {
        'Authorization': `Bearer ${props.apiKey}`
      }
    })
  } catch (error) {
    console.error('Error saving JavaScript:', error)
  }
}

const applyChanges = async () => {
  isSaving.value = true
  try {
    await Promise.all([saveCSS(), saveJavaScript()])
    emit('update', { css: cssCode.value, js: jsCode.value })
    closeEditor()
  } catch (error) {
    console.error('Error applying changes:', error)
  } finally {
    isSaving.value = false
  }
}

const closeEditor = () => {
  emit('close')
}

onMounted(() => {
  loadCode()
})
</script> 