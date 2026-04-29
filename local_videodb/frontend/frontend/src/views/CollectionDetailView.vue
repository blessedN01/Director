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
        <div class="flex justify-between items-start mb-8">
          <div>
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
                    <span class="ml-4 text-sm font-medium text-gray-500">{{ collection.name }}</span>
                  </div>
                </li>
              </ol>
            </nav>
            <h2 class="mt-2 text-2xl font-bold text-gray-900">{{ collection.name }}</h2>
            <p class="mt-1 text-sm text-gray-600">{{ collection.description || 'No description' }}</p>
          </div>
          <button
            @click="showUploadModal = true"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            Upload Files
          </button>
        </div>

        <!-- Filter Tabs -->
        <div class="mb-6">
          <div class="sm:hidden">
            <select
              v-model="activeFilter"
              class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="all">All Assets</option>
              <option value="video">Videos</option>
              <option value="audio">Audio</option>
              <option value="image">Images</option>
            </select>
          </div>
          <div class="hidden sm:block">
            <div class="border-b border-gray-200">
              <nav class="-mb-px flex space-x-8">
                <button
                  v-for="filter in filters"
                  :key="filter.key"
                  @click="activeFilter = filter.key"
                  :class="[
                    activeFilter === filter.key
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                    'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
                  ]"
                >
                  {{ filter.name }} ({{ filter.count }})
                </button>
              </nav>
            </div>
          </div>
        </div>

        <!-- Assets Grid -->
        <div v-if="filteredAssets.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m0 0V1a1 1 0 011-1h2a1 1 0 011 1v3M9 4V1m6 3V1m-6 8h6m-6 4h6m-6 4h6M3 20V7a2 2 0 012-2h14a2 2 0 012 2v13a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No assets found</h3>
          <p class="mt-1 text-sm text-gray-500">
            {{ activeFilter === 'all' ? 'Upload your first file to get started.' : `No ${activeFilter} files in this collection.` }}
          </p>
          <div class="mt-6">
            <button
              @click="showUploadModal = true"
              class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Upload Files
            </button>
          </div>
        </div>
        <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <div
            v-for="asset in filteredAssets"
            :key="asset.id"
            class="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow duration-200"
          >
            <div class="aspect-w-16 aspect-h-9 bg-gray-200">
              <div v-if="asset.type === 'video'" class="w-full h-full flex items-center justify-center bg-gray-800">
                <svg class="h-12 w-12 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
              <div v-else-if="asset.type === 'audio'" class="w-full h-full flex items-center justify-center bg-blue-500">
                <svg class="h-12 w-12 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
                </svg>
              </div>
              <div v-else-if="asset.type === 'image'" class="w-full h-full flex items-center justify-center bg-green-500">
                <svg class="h-12 w-12 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
              </div>
            </div>
            <div class="p-4">
              <div class="flex items-center justify-between">
                <h3 class="text-sm font-medium text-gray-900 truncate">{{ asset.name || asset.filename }}</h3>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize"
                      :class="{
                        'bg-blue-100 text-blue-800': asset.type === 'video',
                        'bg-green-100 text-green-800': asset.type === 'audio',
                        'bg-purple-100 text-purple-800': asset.type === 'image'
                      }">
                  {{ asset.type }}
                </span>
              </div>
              <p class="mt-1 text-sm text-gray-500 truncate">{{ asset.filename }}</p>
              <div class="mt-3 flex items-center justify-between">
                <div class="flex space-x-2">
                  <router-link
                    v-if="asset.type === 'video'"
                    :to="`/video/${asset.id}`"
                    class="inline-flex items-center px-2 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Edit
                  </router-link>
                  <button
                    @click="downloadAsset(asset)"
                    class="inline-flex items-center px-2 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Download
                  </button>
                </div>
                <button
                  @click="deleteAsset(asset)"
                  class="inline-flex items-center px-2 py-1 border border-red-300 shadow-sm text-xs font-medium rounded text-red-700 bg-white hover:bg-red-50"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Upload Files</h3>
          <form @submit.prevent="uploadFiles">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Select Files</label>
              <div
                @dragover.prevent="dragOver = true"
                @dragleave.prevent="dragOver = false"
                @drop.prevent="handleDrop"
                :class="[
                  'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors',
                  dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
                ]"
                @click="$refs.fileInput.click()"
              >
                <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <div class="mt-4">
                  <p class="text-sm text-gray-600">
                    <span class="font-medium text-blue-600">Click to upload</span> or drag and drop
                  </p>
                  <p class="text-xs text-gray-500">MP4, MP3, JPG, PNG up to 100MB each</p>
                </div>
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept="video/*,audio/*,image/*"
                  class="hidden"
                  @change="handleFileSelect"
                />
              </div>
            </div>
            <div v-if="selectedFiles.length > 0" class="mb-4">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Selected Files:</h4>
              <ul class="space-y-1">
                <li v-for="(file, index) in selectedFiles" :key="index" class="text-sm text-gray-600 flex justify-between">
                  <span>{{ file.name }}</span>
                  <span class="text-gray-400">{{ formatFileSize(file.size) }}</span>
                </li>
              </ul>
            </div>
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="closeUploadModal"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="uploading || selectedFiles.length === 0"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {{ uploading ? 'Uploading...' : 'Upload' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const collection = ref({})
const assets = ref([])
const showUploadModal = ref(false)
const selectedFiles = ref([])
const uploading = ref(false)
const dragOver = ref(false)

const activeFilter = ref('all')

const BACKEND_URL = import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:8000'

const filters = computed(() => [
  { key: 'all', name: 'All Assets', count: assets.value.length },
  { key: 'video', name: 'Videos', count: assets.value.filter(a => a.type === 'video').length },
  { key: 'audio', name: 'Audio', count: assets.value.filter(a => a.type === 'audio').length },
  { key: 'image', name: 'Images', count: assets.value.filter(a => a.type === 'image').length }
])

const filteredAssets = computed(() => {
  if (activeFilter.value === 'all') return assets.value
  return assets.value.filter(asset => asset.type === activeFilter.value)
})

const fetchCollection = async () => {
  try {
    const response = await axios.get(`${BACKEND_URL}/videodb/collection/${route.params.id}`)
    collection.value = response.data
  } catch (error) {
    console.error('Failed to fetch collection:', error)
  }
}

const fetchAssets = async () => {
  try {
    const [videosRes, audioRes, imagesRes] = await Promise.all([
      axios.get(`${BACKEND_URL}/videodb/collection/${route.params.id}/video`),
      axios.get(`${BACKEND_URL}/videodb/collection/${route.params.id}/audio`),
      axios.get(`${BACKEND_URL}/videodb/collection/${route.params.id}/image`)
    ])

    assets.value = [
      ...videosRes.data.map(v => ({ ...v, type: 'video' })),
      ...audioRes.data.map(a => ({ ...a, type: 'audio' })),
      ...imagesRes.data.map(i => ({ ...i, type: 'image' }))
    ]
  } catch (error) {
    console.error('Failed to fetch assets:', error)
  }
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  selectedFiles.value = files
}

const handleDrop = (event) => {
  dragOver.value = false
  const files = Array.from(event.dataTransfer.files)
  selectedFiles.value = files.filter(file => {
    const type = file.type.split('/')[0]
    return ['video', 'audio', 'image'].includes(type)
  })
}

const closeUploadModal = () => {
  showUploadModal.value = false
  selectedFiles.value = []
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const uploadFiles = async () => {
  uploading.value = true
  try {
    for (const file of selectedFiles.value) {
      const formData = new FormData()
      formData.append('file', file)

      const type = file.type.split('/')[0]
      await axios.post(`${BACKEND_URL}/videodb/asset/upload?collection=${route.params.id}&type=${type}&name=${file.name}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }

    closeUploadModal()
    await fetchAssets()
  } catch (error) {
    console.error('Failed to upload files:', error)
    alert('Failed to upload some files. Please try again.')
  } finally {
    uploading.value = false
  }
}

const downloadAsset = async (asset) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/videodb/asset/${asset.id}/download`, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', asset.filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error('Failed to download asset:', error)
    alert('Failed to download file. Please try again.')
  }
}

const deleteAsset = async (asset) => {
  if (!confirm(`Are you sure you want to delete "${asset.name || asset.filename}"? This action cannot be undone.`)) {
    return
  }

  try {
    await axios.delete(`${BACKEND_URL}/videodb/asset/${asset.id}?type=${asset.type}`)
    await fetchAssets()
  } catch (error) {
    console.error('Failed to delete asset:', error)
    alert('Failed to delete asset. Please try again.')
  }
}

onMounted(async () => {
  await fetchCollection()
  await fetchAssets()
})
</script>