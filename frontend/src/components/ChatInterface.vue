<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Left Panel - Chat Interface -->
    <div class="flex flex-col w-2/3">
      <!-- Chat Header -->
      <div class="bg-white shadow-sm p-4">
        <h1 class="text-xl font-semibold text-gray-800">Multimodal Chat Interface</h1>
      </div>

      <!-- Chat Messages -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
        <div v-for="(message, index) in messages" :key="index" 
             :class="['flex', message.isUser ? 'justify-end' : 'justify-start']">
          <div :class="['max-w-[70%] rounded-lg p-4', 
                       message.isUser ? 'bg-blue-500 text-white' : 'bg-white shadow-sm']">
            <!-- Text Message -->
            <div v-if="message.type === 'text'">{{ message.content }}</div>
            
            <!-- Image Message -->
            <div v-else-if="message.type === 'image'" class="mt-2">
              <img :src="message.content" class="max-w-full rounded-lg" />
            </div>
            
            <!-- File Message -->
            <div v-else-if="message.type === 'file'" class="mt-2">
              <a :href="message.content" 
                 class="text-blue-500 hover:text-blue-600 flex items-center"
                 target="_blank">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                </svg>
                Download File
              </a>
            </div>
          </div>
        </div>
        
        <!-- Loading Indicator -->
        <div v-if="isLoading" class="flex justify-start">
          <div class="bg-white shadow-sm rounded-lg p-4">
            <div class="flex space-x-2">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="border-t border-gray-200 p-4 bg-white">
        <div class="flex space-x-2">
          <input
            v-model="newMessage"
            @keyup.enter="sendMessage"
            type="text"
            placeholder="Type your message..."
            class="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            @click="sendMessage"
            :disabled="isLoading"
            class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>

    <!-- Right Panel - Additional Features -->
    <div class="w-1/3 bg-white border-l border-gray-200">
      <div class="p-4">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Tools & Settings</h2>
        
        <!-- Template Selection -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Template</label>
          <select
            v-model="selectedTemplate"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="template1">Professional Business</option>
            <option value="template2">Artistic Painting</option>
            <option value="template3">Modern Minimalist</option>
          </select>
        </div>

        <!-- Image Preview Window -->
        <div class="mb-6">
          <h3 class="text-sm font-medium text-gray-700 mb-2">Image Preview</h3>
          <div class="border-2 border-dashed border-gray-300 rounded-lg p-4 h-64 flex items-center justify-center bg-gray-50">
            <div v-if="previewImage" class="w-full h-full flex items-center justify-center">
              <img :src="previewImage" class="max-h-full max-w-full object-contain" />
            </div>
            <div v-else class="text-gray-400 text-center">
              <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              <p>No image selected</p>
            </div>
          </div>
          <div class="mt-2 flex justify-center">
            <button
              @click="renderImage"
              :disabled="!previewImage || isRendering"
              class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm disabled:opacity-50"
            >
              {{ isRendering ? 'Rendering...' : 'Render Image' }}
            </button>
          </div>
        </div>

        <!-- Settings Panel -->
        <div class="p-4 border-b border-gray-200">
          <h3 class="text-sm font-medium text-gray-700 mb-2">Settings</h3>
          <div class="space-y-4">
            <!-- Model Selection -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Model</label>
              <select
                v-model="selectedModel"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="gpt-4">GPT-4</option>
                <option value="claude">Claude</option>
              </select>
            </div>

            <!-- Multimodal Support Toggle -->
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700">Multimodal Support</span>
              <button
                @click="toggleMultimodal"
                :class="[
                  'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                  multimodalEnabled ? 'bg-blue-500' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                    multimodalEnabled ? 'translate-x-5' : 'translate-x-0'
                  ]"
                />
              </button>
            </div>

            <!-- Data Synthesis Controls -->
            <div class="grid grid-cols-3 gap-2">
              <!-- Data Source Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Data Source</label>
                <select
                  v-model="selectedDataSource"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="source1">Source 1</option>
                  <option value="source2">Source 2</option>
                  <option value="source3">Source 3</option>
                </select>
              </div>

              <!-- Data Count Input -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Data Count</label>
                <input
                  v-model="dataCount"
                  type="number"
                  min="1"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Count"
                />
              </div>

              <!-- Output Filename Input -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Output Filename</label>
                <input
                  v-model="outputFilename"
                  type="text"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Filename"
                />
              </div>
            </div>

            <!-- Start Synthesis Button -->
            <button
              @click="startSynthesis"
              :disabled="isSynthesizing"
              class="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
            >
              {{ isSynthesizing ? 'Synthesizing...' : 'Start Synthesis' }}
            </button>
          </div>
        </div>

        <!-- Quick Actions -->
        <div>
          <h3 class="text-sm font-medium text-gray-700 mb-2">Quick Actions</h3>
          <div class="grid grid-cols-2 gap-2">
            <button
              @click="clearChat"
              class="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 text-sm"
            >
              Clear Chat
            </button>
            <button
              @click="exportChat"
              class="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 text-sm"
            >
              Export Chat
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { useScroll } from '@vueuse/core'

const messages = ref([])
const newMessage = ref('')
const isLoading = ref(false)
const multimodalEnabled = ref(true)
const selectedModel = ref('gpt-4')
const fileInput = ref(null)
const imageInput = ref(null)
const messagesContainer = ref(null)
const previewImage = ref(null)
const isRendering = ref(false)
const selectedTemplate = ref('template1')

// 数据合成相关状态
const selectedDataSource = ref('source1')
const dataCount = ref(100)
const outputFilename = ref('synthesized_data')
const isSynthesizing = ref(false)

const { y: scrollY } = useScroll(messagesContainer)

// Scroll to bottom when new messages arrive
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim()) return
  
  const message = {
    type: 'text',
    content: newMessage.value,
    isUser: true
  }
  
  messages.value.push(message)
  newMessage.value = ''
  
  await scrollToBottom()
  
  try {
    isLoading.value = true
    const response = await axios.post(`${apiEndpoint.value}/chat`, {
      message: message.content,
      model: selectedModel.value,
      multimodal: multimodalEnabled.value
    }, {
      headers: {
        'Authorization': `Bearer ${apiKey.value}`,
        'Content-Type': 'application/json'
      }
    })
    
    messages.value.push({
      type: 'text',
      content: response.data.response,
      isUser: false
    })
  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.push({
      type: 'text',
      content: 'Sorry, there was an error processing your message.',
      isUser: false
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

const triggerFileUpload = () => {
  fileInput.value.click()
}

const triggerImageUpload = () => {
  imageInput.value.click()
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axios.post(`${apiEndpoint.value}/upload`, formData, {
      headers: {
        'Authorization': `Bearer ${apiKey.value}`,
        'Content-Type': 'multipart/form-data'
      }
    })
    
    messages.value.push({
      type: 'file',
      content: response.data.fileUrl,
      isUser: true
    })
    
    await scrollToBottom()
  } catch (error) {
    console.error('Error uploading file:', error)
    messages.value.push({
      type: 'text',
      content: 'Error uploading file: ' + error.message,
      isUser: false
    })
  }
}

const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImage.value = e.target.result
    }
    reader.readAsDataURL(file)
    
    // Upload image
    const formData = new FormData()
    formData.append('image', file)
    
    const response = await axios.post(`${apiEndpoint.value}/upload-image`, formData, {
      headers: {
        'Authorization': `Bearer ${apiKey.value}`,
        'Content-Type': 'multipart/form-data'
      }
    })
    
    messages.value.push({
      type: 'image',
      content: response.data.imageUrl,
      isUser: true
    })
    
    await scrollToBottom()
  } catch (error) {
    console.error('Error uploading image:', error)
    messages.value.push({
      type: 'text',
      content: 'Error uploading image: ' + error.message,
      isUser: false
    })
  }
}

const renderImage = async () => {
  if (!previewImage.value) return
  
  try {
    isRendering.value = true
    const response = await axios.post(`${apiEndpoint.value}/render`, {
      image: previewImage.value,
      model: selectedModel.value,
      prompt: newMessage.value,
      template: selectedTemplate.value
    }, {
      headers: {
        'Authorization': `Bearer ${apiKey.value}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.data.renderedImage) {
      previewImage.value = response.data.renderedImage
      messages.value.push({
        type: 'image',
        content: response.data.renderedImage,
        isUser: false
      })
    }
    
    if (response.data.textResponse) {
      messages.value.push({
        type: 'text',
        content: response.data.textResponse,
        isUser: false
      })
    }
    
    await scrollToBottom()
  } catch (error) {
    console.error('Error rendering image:', error)
    messages.value.push({
      type: 'text',
      content: 'Error rendering image: ' + error.message,
      isUser: false
    })
  } finally {
    isRendering.value = false
  }
}

const startSynthesis = async () => {
  if (!selectedDataSource.value || !dataCount.value || !outputFilename.value) {
    messages.value.push({
      type: 'text',
      content: 'Please fill in all synthesis parameters',
      isUser: false
    })
    return
  }

  try {
    isSynthesizing.value = true
    const response = await axios.post(`${apiEndpoint.value}/synthesize`, {
      dataSource: selectedDataSource.value,
      count: dataCount.value,
      filename: outputFilename.value
    }, {
      headers: {
        'Authorization': `Bearer ${apiKey.value}`,
        'Content-Type': 'application/json'
      }
    })

    messages.value.push({
      type: 'text',
      content: `Data synthesis completed. ${response.data.message}`,
      isUser: false
    })
  } catch (error) {
    console.error('Error during synthesis:', error)
    messages.value.push({
      type: 'text',
      content: 'Error during synthesis: ' + error.message,
      isUser: false
    })
  } finally {
    isSynthesizing.value = false
  }
}

const toggleMultimodal = () => {
  multimodalEnabled.value = !multimodalEnabled.value
}

const clearChat = () => {
  messages.value = []
}

const exportChat = () => {
  const chatData = {
    messages: messages.value,
    settings: {
      model: selectedModel.value,
      multimodal: multimodalEnabled.value
    }
  }
  
  const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'chat-export.json'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

onMounted(() => {
  // Load saved settings from localStorage
  const savedSettings = localStorage.getItem('chatSettings')
  if (savedSettings) {
    const settings = JSON.parse(savedSettings)
    apiEndpoint.value = settings.apiEndpoint || 'http://localhost:8000'
    apiKey.value = settings.apiKey || ''
    selectedModel.value = settings.model || 'gpt-4'
    multimodalEnabled.value = settings.multimodal ?? true
  }
})
</script>

<style scoped>
/* Add any additional styles here */
</style> 