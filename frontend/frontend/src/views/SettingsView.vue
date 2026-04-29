<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">Local VideoDB</h1>
          </div>
          <div class="flex items-center space-x-4">
            <router-link
              to="/dashboard"
              class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              :class="{ 'bg-gray-100': $route.name === 'Dashboard' }"
            >
              Dashboard
            </router-link>
            <router-link
              to="/collections"
              class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              :class="{ 'bg-gray-100': $route.name === 'Collections' }"
            >
              Collections
            </router-link>
            <router-link
              to="/search"
              class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              :class="{ 'bg-gray-100': $route.name === 'Search' }"
            >
              Search
            </router-link>
            <router-link
              to="/generate"
              class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              :class="{ 'bg-gray-100': $route.name === 'Generation' }"
            >
              Generate
            </router-link>
            <router-link
              to="/settings"
              class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              :class="{ 'bg-gray-100': $route.name === 'Settings' }"
            >
              Settings
            </router-link>
            <router-link
              to="/chat"
              class="text-blue-600 hover:text-blue-800 px-3 py-2 rounded-md text-sm font-medium"
            >
              Chat Mode
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Header -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900">Settings</h2>
          <p class="mt-1 text-sm text-gray-600">Configure your local VideoDB preferences and API keys</p>
        </div>

        <div class="space-y-8">
          <!-- API Configuration -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">API Configuration</h3>
              <p class="mt-1 text-sm text-gray-600">Configure API keys for AI-powered features</p>
            </div>
            <div class="px-6 py-6 space-y-6">
              <!-- OpenAI API -->
              <div>
                <label for="openai-key" class="block text-sm font-medium text-gray-700">OpenAI API Key</label>
                <div class="mt-1 flex">
                  <input
                    v-model="settings.openaiApiKey"
                    id="openai-key"
                    type="password"
                    class="flex-1 border-gray-300 rounded-l-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="sk-..."
                  />
                  <button
                    @click="testOpenAI"
                    class="inline-flex items-center px-4 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-700 hover:bg-gray-100"
                  >
                    Test
                  </button>
                </div>
                <p class="mt-1 text-sm text-gray-500">Required for transcription, translation, and image generation</p>
              </div>

              <!-- OpenAI Base URL -->
              <div>
                <label for="openai-url" class="block text-sm font-medium text-gray-700">OpenAI Base URL</label>
                <input
                  v-model="settings.openaiBaseUrl"
                  id="openai-url"
                  type="url"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="https://api.openai.com/v1"
                />
                <p class="mt-1 text-sm text-gray-500">Use custom OpenAI-compatible endpoints</p>
              </div>

              <!-- Fal API Key -->
              <div>
                <label for="fal-key" class="block text-sm font-medium text-gray-700">Fal API Key</label>
                <input
                  v-model="settings.falApiKey"
                  id="fal-key"
                  type="password"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="fal-..."
                />
                <p class="mt-1 text-sm text-gray-500">Optional: For advanced video generation</p>
              </div>

              <!-- Replicate API Token -->
              <div>
                <label for="replicate-token" class="block text-sm font-medium text-gray-700">Replicate API Token</label>
                <input
                  v-model="settings.replicateApiToken"
                  id="replicate-token"
                  type="password"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="r8_..."
                />
                <p class="mt-1 text-sm text-gray-500">Optional: Alternative video generation</p>
              </div>

              <!-- Kling API Key -->
              <div>
                <label for="kling-key" class="block text-sm font-medium text-gray-700">Kling API Key</label>
                <input
                  v-model="settings.klingApiKey"
                  id="kling-key"
                  type="password"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="kling-..."
                />
                <p class="mt-1 text-sm text-gray-500">Optional: Advanced video generation</p>
              </div>

              <!-- ElevenLabs API Key -->
              <div>
                <label for="elevenlabs-key" class="block text-sm font-medium text-gray-700">ElevenLabs API Key</label>
                <input
                  v-model="settings.elevenlabsApiKey"
                  id="elevenlabs-key"
                  type="password"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="..."
                />
                <p class="mt-1 text-sm text-gray-500">Optional: For voice generation and sound effects</p>
              </div>

              <!-- Beatoven API Key -->
              <div>
                <label for="beatoven-key" class="block text-sm font-medium text-gray-700">Beatoven API Key</label>
                <input
                  v-model="settings.beatovenApiKey"
                  id="beatoven-key"
                  type="password"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="..."
                />
                <p class="mt-1 text-sm text-gray-500">Optional: For music generation</p>
              </div>
            </div>
          </div>

          <!-- System Configuration -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">System Configuration</h3>
              <p class="mt-1 text-sm text-gray-600">Configure system-wide settings</p>
            </div>
            <div class="px-6 py-6 space-y-6">
              <!-- Backend URL -->
              <div>
                <label for="backend-url" class="block text-sm font-medium text-gray-700">Backend URL</label>
                <input
                  v-model="settings.backendUrl"
                  id="backend-url"
                  type="url"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="http://localhost:8000"
                />
                <p class="mt-1 text-sm text-gray-500">URL of your local VideoDB backend server</p>
              </div>

              <!-- Default Collection -->
              <div>
                <label for="default-collection" class="block text-sm font-medium text-gray-700">Default Collection</label>
                <select
                  v-model="settings.defaultCollection"
                  id="default-collection"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="default">Default</option>
                  <option v-for="collection in collections" :key="collection.id" :value="collection.id">
                    {{ collection.name }}
                  </option>
                </select>
                <p class="mt-1 text-sm text-gray-500">Default collection for uploads and generations</p>
              </div>

              <!-- Auto-processing -->
              <div class="flex items-center">
                <input
                  v-model="settings.autoProcess"
                  id="auto-process"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="auto-process" class="ml-2 block text-sm text-gray-900">
                  Auto-process videos on upload
                </label>
              </div>

              <!-- Processing Options -->
              <div v-if="settings.autoProcess" class="ml-6 space-y-3">
                <div class="flex items-center">
                  <input
                    v-model="settings.autoTranscript"
                    id="auto-transcript"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label for="auto-transcript" class="ml-2 block text-sm text-gray-900">
                    Generate transcripts
                  </label>
                </div>
                <div class="flex items-center">
                  <input
                    v-model="settings.autoScenes"
                    id="auto-scenes"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label for="auto-scenes" class="ml-2 block text-sm text-gray-900">
                    Extract scene information
                  </label>
                </div>
                <div class="flex items-center">
                  <input
                    v-model="settings.autoSubtitles"
                    id="auto-subtitles"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label for="auto-subtitles" class="ml-2 block text-sm text-gray-900">
                    Generate subtitles
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-3">
            <button
              @click="resetSettings"
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Reset to Defaults
            </button>
            <button
              @click="saveSettings"
              class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              Save Settings
            </button>
          </div>

          <!-- Status Messages -->
          <div v-if="statusMessage" class="rounded-md p-4" :class="statusType === 'success' ? 'bg-green-50' : 'bg-red-50'">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg v-if="statusType === 'success'" class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium" :class="statusType === 'success' ? 'text-green-800' : 'text-red-800'">
                  {{ statusMessage }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const settings = ref({
  openaiApiKey: '',
  openaiBaseUrl: 'https://api.openai.com/v1',
  falApiKey: '',
  replicateApiToken: '',
  klingApiKey: '',
  elevenlabsApiKey: '',
  beatovenApiKey: '',
  backendUrl: 'http://localhost:8000',
  defaultCollection: 'default',
  autoProcess: false,
  autoTranscript: true,
  autoScenes: true,
  autoSubtitles: false
})

const collections = ref([])
const statusMessage = ref('')
const statusType = ref('')

const BACKEND_URL = import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:8000'

const loadSettings = () => {
  const saved = localStorage.getItem('videodb-settings')
  if (saved) {
    Object.assign(settings.value, JSON.parse(saved))
  }
}

const saveSettings = () => {
  localStorage.setItem('videodb-settings', JSON.stringify(settings.value))

  // Update environment variables if supported
  if (settings.value.openaiApiKey) {
    localStorage.setItem('OPENAI_API_KEY', settings.value.openaiApiKey)
  }
  if (settings.value.openaiBaseUrl) {
    localStorage.setItem('OPENAI_BASE_URL', settings.value.openaiBaseUrl)
  }
  if (settings.value.falApiKey) {
    localStorage.setItem('FAL_KEY', settings.value.falApiKey)
  }
  if (settings.value.replicateApiToken) {
    localStorage.setItem('REPLICATE_API_TOKEN', settings.value.replicateApiToken)
  }
  if (settings.value.klingApiKey) {
    localStorage.setItem('KLING_API_KEY', settings.value.klingApiKey)
  }
  if (settings.value.elevenlabsApiKey) {
    localStorage.setItem('ELEVENLABS_API_KEY', settings.value.elevenlabsApiKey)
  }
  if (settings.value.beatovenApiKey) {
    localStorage.setItem('BEATOVEN_API_KEY', settings.value.beatovenApiKey)
  }

  statusMessage.value = 'Settings saved successfully!'
  statusType.value = 'success'
  setTimeout(() => {
    statusMessage.value = ''
  }, 3000)
}

const resetSettings = () => {
  if (confirm('Are you sure you want to reset all settings to defaults?')) {
    localStorage.removeItem('videodb-settings')
    settings.value = {
      openaiApiKey: '',
      openaiBaseUrl: 'https://api.openai.com/v1',
      falApiKey: '',
      replicateApiToken: '',
      klingApiKey: '',
      elevenlabsApiKey: '',
      beatovenApiKey: '',
      backendUrl: 'http://localhost:8000',
      defaultCollection: 'default',
      autoProcess: false,
      autoTranscript: true,
      autoScenes: true,
      autoSubtitles: false
    }
    statusMessage.value = 'Settings reset to defaults.'
    statusType.value = 'success'
  }
}

const testOpenAI = async () => {
  if (!settings.value.openaiApiKey) {
    statusMessage.value = 'Please enter an OpenAI API key first.'
    statusType.value = 'error'
    return
  }

  try {
    // Simple test by making a request to models endpoint
    const response = await axios.get('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${settings.value.openaiApiKey}`
      },
      timeout: 5000
    })

    if (response.status === 200) {
      statusMessage.value = 'OpenAI API key is valid!'
      statusType.value = 'success'
    }
  } catch (error) {
    statusMessage.value = 'OpenAI API key test failed. Please check your key.'
    statusType.value = 'error'
  }

  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

const fetchCollections = async () => {
  try {
    const response = await axios.get(`${BACKEND_URL}/videodb/collection`)
    collections.value = response.data
  } catch (error) {
    console.error('Failed to fetch collections:', error)
  }
}

onMounted(() => {
  loadSettings()
  fetchCollections()
})
</script>