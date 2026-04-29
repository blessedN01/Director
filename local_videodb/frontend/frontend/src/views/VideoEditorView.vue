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
          <nav class="flex" aria-label="Breadcrumb">
            <ol class="flex items-center space-x-4">
              <li>
                <div>
                  <router-link to="/collections" class="text-gray-400 hover:text-gray-500">
                    Collections
                  </router-link>
                </div>
              </li>
              <li>
                <div class="flex items-center">
                  <svg class="flex-shrink-0 h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                  <router-link :to="`/collections/${video.collection_id}`" class="ml-4 text-sm font-medium text-gray-400 hover:text-gray-500">
                    {{ video.collection_name || 'Collection' }}
                  </router-link>
                </div>
              </li>
              <li>
                <div class="flex items-center">
                  <svg class="flex-shrink-0 h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span class="ml-4 text-sm font-medium text-gray-500">{{ video.name || video.filename }}</span>
                </div>
              </li>
            </ol>
          </nav>
          <h2 class="mt-2 text-2xl font-bold text-gray-900">Video Editor</h2>
          <p class="mt-1 text-sm text-gray-600">Process and edit your video with manual controls</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Video Player -->
          <div class="lg:col-span-2">
            <div class="bg-white shadow rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Video Preview</h3>
              <div class="aspect-w-16 aspect-h-9 bg-gray-900 rounded-lg overflow-hidden">
                <video
                  v-if="video.stream_url"
                  :src="video.stream_url"
                  controls
                  class="w-full h-full"
                  ref="videoPlayer"
                ></video>
                <div v-else class="w-full h-full flex items-center justify-center">
                  <div class="text-center text-white">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <p class="mt-2 text-sm">Video not available</p>
                  </div>
                </div>
              </div>

              <!-- Basic Controls -->
              <div class="mt-4 flex space-x-2">
                <button
                  @click="playVideo"
                  class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l.707.707A1 1 0 0012.414 11H13m-3 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Play
                </button>
                <button
                  @click="extractFrame"
                  class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Extract Frame
                </button>
              </div>
            </div>
          </div>

          <!-- Processing Panel -->
          <div class="space-y-6">
            <!-- Video Info -->
            <div class="bg-white shadow rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Video Information</h3>
              <dl class="space-y-3">
                <div>
                  <dt class="text-sm font-medium text-gray-500">Filename</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ video.filename }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Duration</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ video.duration ? `${video.duration}s` : 'Unknown' }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Size</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ video.size ? formatFileSize(video.size) : 'Unknown' }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Status</dt>
                  <dd class="mt-1">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="{
                            'bg-green-100 text-green-800': video.status === 'processed',
                            'bg-yellow-100 text-yellow-800': video.status === 'processing',
                            'bg-gray-100 text-gray-800': !video.status
                          }">
                      {{ video.status || 'raw' }}
                    </span>
                  </dd>
                </div>
              </dl>
            </div>

            <!-- Processing Actions -->
            <div class="bg-white shadow rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Processing Actions</h3>
              <div class="space-y-3">
                <button
                  @click="processVideo"
                  :disabled="processing"
                  class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  <svg v-if="processing" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ processing ? 'Processing...' : 'Process Video' }}
                </button>

                <button
                  @click="getTranscript"
                  :disabled="loadingTranscript"
                  class="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  {{ loadingTranscript ? 'Loading...' : 'Get Transcript' }}
                </button>

                <button
                  @click="generateSubtitles"
                  :disabled="generatingSubtitles"
                  class="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  {{ generatingSubtitles ? 'Generating...' : 'Generate Subtitles' }}
                </button>

                <button
                  @click="translateVideo"
                  class="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Translate
                </button>

                <button
                  @click="dubVideo"
                  class="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Dub Audio
                </button>
              </div>
            </div>

            <!-- Transcript Display -->
            <div v-if="transcript" class="bg-white shadow rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Transcript</h3>
              <div class="max-h-60 overflow-y-auto">
                <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ transcript }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Processing Results -->
        <div v-if="processingResults.length > 0" class="mt-8">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Processing Results</h3>
          <div class="bg-white shadow rounded-lg overflow-hidden">
            <ul class="divide-y divide-gray-200">
              <li v-for="result in processingResults" :key="result.id" class="px-6 py-4">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ result.action }}</p>
                    <p class="text-sm text-gray-500">{{ result.timestamp }}</p>
                  </div>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="{
                          'bg-green-100 text-green-800': result.status === 'success',
                          'bg-red-100 text-red-800': result.status === 'error',
                          'bg-yellow-100 text-yellow-800': result.status === 'processing'
                        }">
                    {{ result.status }}
                  </span>
                </div>
                <p v-if="result.message" class="mt-2 text-sm text-gray-600">{{ result.message }}</p>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const video = ref({})
const processing = ref(false)
const loadingTranscript = ref(false)
const generatingSubtitles = ref(false)
const transcript = ref('')
const processingResults = ref([])

const BACKEND_URL = import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:8000'

const fetchVideo = async () => {
  try {
    const response = await axios.get(`${BACKEND_URL}/videodb/video/${route.params.id}`)
    video.value = response.data
  } catch (error) {
    console.error('Failed to fetch video:', error)
  }
}

const processVideo = async () => {
  processing.value = true
  try {
    await axios.post(`${BACKEND_URL}/videodb/video/${route.params.id}/process`)
    processingResults.value.unshift({
      id: Date.now(),
      action: 'Video Processing',
      status: 'processing',
      timestamp: new Date().toLocaleString(),
      message: 'Processing video with AI features...'
    })
    await fetchVideo()
  } catch (error) {
    console.error('Failed to process video:', error)
    processingResults.value.unshift({
      id: Date.now(),
      action: 'Video Processing',
      status: 'error',
      timestamp: new Date().toLocaleString(),
      message: 'Failed to process video'
    })
  } finally {
    processing.value = false
  }
}

const getTranscript = async () => {
  loadingTranscript.value = true
  try {
    const response = await axios.get(`${BACKEND_URL}/videodb/video/${route.params.id}/transcript`)
    transcript.value = response.data.transcript || 'No transcript available'
  } catch (error) {
    console.error('Failed to get transcript:', error)
    transcript.value = 'Failed to load transcript'
  } finally {
    loadingTranscript.value = false
  }
}

const generateSubtitles = async () => {
  generatingSubtitles.value = true
  try {
    await axios.post(`${BACKEND_URL}/videodb/video/${route.params.id}/subtitle`)
    processingResults.value.unshift({
      id: Date.now(),
      action: 'Subtitle Generation',
      status: 'success',
      timestamp: new Date().toLocaleString(),
      message: 'Subtitles generated successfully'
    })
  } catch (error) {
    console.error('Failed to generate subtitles:', error)
    processingResults.value.unshift({
      id: Date.now(),
      action: 'Subtitle Generation',
      status: 'error',
      timestamp: new Date().toLocaleString(),
      message: 'Failed to generate subtitles'
    })
  } finally {
    generatingSubtitles.value = false
  }
}

const translateVideo = () => {
  const language = prompt('Enter target language code (e.g., es, fr, de):')
  if (!language) return

  const notes = prompt('Optional translation notes:')
  axios.post(`${BACKEND_URL}/videodb/video/${route.params.id}/translate/${language}`, { notes })
    .then(() => {
      processingResults.value.unshift({
        id: Date.now(),
        action: 'Translation',
        status: 'success',
        timestamp: new Date().toLocaleString(),
        message: `Translated to ${language}`
      })
    })
    .catch(error => {
      console.error('Failed to translate video:', error)
      processingResults.value.unshift({
        id: Date.now(),
        action: 'Translation',
        status: 'error',
        timestamp: new Date().toLocaleString(),
        message: 'Failed to translate video'
      })
    })
}

const dubVideo = () => {
  const language = prompt('Enter target language code (e.g., es, fr, de):')
  if (!language) return

  axios.post(`${BACKEND_URL}/videodb/video/${route.params.id}/dub/${language}`)
    .then(() => {
      processingResults.value.unshift({
        id: Date.now(),
        action: 'Audio Dubbing',
        status: 'success',
        timestamp: new Date().toLocaleString(),
        message: `Dubbed to ${language}`
      })
    })
    .catch(error => {
      console.error('Failed to dub video:', error)
      processingResults.value.unshift({
        id: Date.now(),
        action: 'Audio Dubbing',
        status: 'error',
        timestamp: new Date().toLocaleString(),
        message: 'Failed to dub video'
      })
    })
}

const playVideo = () => {
  const player = document.querySelector('video')
  if (player) {
    player.play()
  }
}

const extractFrame = () => {
  const timestamp = prompt('Enter timestamp in seconds (e.g., 10.5):')
  if (!timestamp) return

  axios.post(`${BACKEND_URL}/videodb/video/${route.params.id}/extract-frame`, {
    timestamp: parseFloat(timestamp)
  })
    .then(() => {
      processingResults.value.unshift({
        id: Date.now(),
        action: 'Frame Extraction',
        status: 'success',
        timestamp: new Date().toLocaleString(),
        message: `Frame extracted at ${timestamp}s`
      })
    })
    .catch(error => {
      console.error('Failed to extract frame:', error)
      processingResults.value.unshift({
        id: Date.now(),
        action: 'Frame Extraction',
        status: 'error',
        timestamp: new Date().toLocaleString(),
        message: 'Failed to extract frame'
      })
    })
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  fetchVideo()
})
</script>