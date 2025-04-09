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
          <button
            @click="triggerFileUpload"
            class="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 transition-colors"
            title="Upload File"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
            </svg>
          </button>
          <button
            @click="triggerImageUpload"
            class="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 transition-colors"
            title="Upload Image"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
          </button>
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
        <!-- Hidden file inputs -->
        <input
          type="file"
          ref="fileInput"
          @change="handleFileUpload"
          class="hidden"
        />
        <input
          type="file"
          ref="imageInput"
          @change="handleImageUpload"
          accept="image/*"
          class="hidden"
        />
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
          <div class="mt-2 flex justify-center space-x-2">
            <button
              @click="renderImage"
              :disabled="isRenderButtonDisabled"
              class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm disabled:opacity-50"
            >
              {{ isRendering ? 'Rendering...' : 'Render Image' }}
            </button>
            <button
              @click="showCodeEditor = true"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
            >
              Edit Code
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
            <div class="grid grid-cols-2 gap-2">
              <!-- Language Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Language</label>
                <select
                  v-model="selectedLanguage"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="en">English</option>
                  <option value="zh">Chinese</option>
                  <option value="ja">Japanese</option>
                  <option value="ko">Korean</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="es">Spanish</option>
                </select>
              </div>

              <!-- Scene Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Scene</label>
                <select
                  v-model="selectedScene"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="business">Business</option>
                  <option value="education">Education</option>
                  <option value="entertainment">Entertainment</option>
                  <option value="technology">Technology</option>
                  <option value="health">Health</option>
                  <option value="travel">Travel</option>
                  <option value="food">Food</option>
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
            <div class="flex space-x-2">
              <button
                @click="startSynthesis"
                :disabled="isSynthesizing || !selectedLanguage || !selectedScene || !dataCount || !outputFilename"
                class="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
              >
                {{ isSynthesizing ? 'Synthesizing...' : 'Start Synthesis' }}
              </button>
              <button
                v-if="isSynthesizing"
                @click="stopSynthesis"
                class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                Stop
              </button>
            </div>
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
  <CodeEditor
    v-if="showCodeEditor"
    :api-endpoint="apiEndpoint"
    :api-key="apiKey"
    @close="showCodeEditor = false"
    @update="handleCodeUpdate"
  />
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import axios from 'axios'
import { useScroll } from '@vueuse/core'
import CodeEditor from './CodeEditor.vue'

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
const showCodeEditor = ref(false)

// 数据合成相关状态
const selectedLanguage = ref('en')
const selectedScene = ref('business')
const dataCount = ref(100)
const outputFilename = ref('synthesized_data')
const isSynthesizing = ref(false)

// API configuration
const apiEndpoint = ref('http://localhost:8000')
const apiKey = ref('your-api-key-here') // 这里应该替换为实际的 API key

const { y: scrollY } = useScroll(messagesContainer)

// Scroll to bottom when new messages arrive
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() && !previewImage.value) return

  try {
    isLoading.value = true
    
    // Prepare the message content
    const messageContent = {
      text: newMessage.value,
      image: previewImage.value,
      model: selectedModel.value,
      multimodal: multimodalEnabled.value,
      template: selectedTemplate.value
    }

    // Add user message to chat
    messages.value.push({
      type: 'text',
      content: newMessage.value,
      isUser: true
    })

    if (previewImage.value) {
      messages.value.push({
        type: 'image',
        content: previewImage.value,
        isUser: true
      })
    }

    // Send to API
    const response = await axios.post(`${apiEndpoint.value}/chat`, messageContent, {
      headers: {
        'Authorization': `Bearer ${apiKey.value}`,
        'Content-Type': 'application/json'
      }
    })

    // Handle response
    if (response.data.response) {
      messages.value.push({
        type: 'text',
        content: response.data.response,
        isUser: false
      })
    }

    if (response.data.image) {
      messages.value.push({
        type: 'image',
        content: response.data.image,
        isUser: false
      })
      previewImage.value = response.data.image
    }

  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.push({
      type: 'text',
      content: 'Error: ' + error.message,
      isUser: false
    })
  } finally {
    isLoading.value = false
    newMessage.value = ''
    scrollToBottom()
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

    const fileUrl = `${apiEndpoint.value}${response.data.fileUrl}`
    messages.value.push({
      type: 'file',
      content: fileUrl,
      isUser: true
    })

    // Add file content to the next message
    newMessage.value = `File uploaded: ${file.name}\n${newMessage.value}`
    scrollToBottom()
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
    const formData = new FormData()
    formData.append('image', file)

    const response = await axios.post(`${apiEndpoint.value}/upload-image`, formData, {
      headers: {
        'Authorization': `Bearer ${apiKey.value}`,
        'Content-Type': 'multipart/form-data'
      }
    })

    previewImage.value = `${apiEndpoint.value}${response.data.imageUrl}`
    messages.value.push({
      type: 'image',
      content: previewImage.value,
      isUser: true
    })

    // Add image description to the next message
    newMessage.value = `Image uploaded: ${file.name}\n${newMessage.value}`
    scrollToBottom()
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
  if (!previewImage.value) {
    messages.value.push({
      type: 'text',
      content: 'Please upload an image first',
      isUser: false
    })
    return
  }

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
  if (!selectedLanguage.value || !selectedScene.value || !dataCount.value || !outputFilename.value) {
    messages.value.push({
      type: 'text',
      content: 'Please select language, scene, data count and output filename',
      isUser: false
    })
    return
  }

  try {
    isSynthesizing.value = true
    const response = await axios.post(`${apiEndpoint.value}/synthesize`, {
      language: selectedLanguage.value,
      scene: selectedScene.value,
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
      content: response.data.message,
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

const stopSynthesis = () => {
  isSynthesizing.value = false
  // 这里可以添加取消请求的逻辑
  messages.value.push({
    type: 'text',
    content: 'Synthesis stopped by user',
    isUser: false
  })
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

const handleCodeUpdate = (code) => {
  // 处理代码更新
  console.log('Code updated:', code)
  // 这里可以添加代码更新后的处理逻辑
}

// 修改渲染按钮的禁用条件
const isRenderButtonDisabled = computed(() => {
  return !previewImage.value || isRendering.value
})

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