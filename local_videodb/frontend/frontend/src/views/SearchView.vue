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
          <h2 class="text-2xl font-bold text-gray-900">Search</h2>
          <p class="mt-1 text-sm text-gray-600">Search across your video collections using semantic or keyword search</p>
        </div>

        <!-- Search Form -->
        <div class="bg-white shadow rounded-lg p-6 mb-8">
          <form @submit.prevent="performSearch" class="space-y-4">
            <div>
              <label for="query" class="block text-sm font-medium text-gray-700">Search Query</label>
              <div class="mt-1 flex rounded-md shadow-sm">
                <input
                  v-model="searchQuery"
                  type="text"
                  id="query"
                  class="flex-1 min-w-0 block w-full px-3 py-2 rounded-l-md border-gray-300 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Enter your search query..."
                />
                <button
                  type="submit"
                  :disabled="searching || !searchQuery.trim()"
                  class="inline-flex items-center px-4 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-700 hover:bg-gray-100 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
                >
                  <svg v-if="searching" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span class="ml-2">{{ searching ? 'Searching...' : 'Search' }}</span>
                </button>
              </div>
            </div>

            <div class="flex items-center space-x-6">
              <div class="flex items-center">
                <input
                  v-model="searchType"
                  id="semantic"
                  name="search-type"
                  type="radio"
                  value="semantic"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <label for="semantic" class="ml-2 block text-sm text-gray-900">
                  Semantic Search
                  <span class="text-gray-500">(AI-powered understanding)</span>
                </label>
              </div>
              <div class="flex items-center">
                <input
                  v-model="searchType"
                  id="keyword"
                  name="search-type"
                  type="radio"
                  value="keyword"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <label for="keyword" class="ml-2 block text-sm text-gray-900">
                  Keyword Search
                  <span class="text-gray-500">(exact text matching)</span>
                </label>
              </div>
            </div>

            <div class="flex items-center space-x-6">
              <div class="flex items-center">
                <input
                  v-model="searchInVideo"
                  id="search-in-video"
                  name="search-in-video"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="search-in-video" class="ml-2 block text-sm text-gray-900">
                  Search within specific video
                </label>
              </div>
              <div v-if="searchInVideo" class="flex-1">
                <input
                  v-model="videoId"
                  type="text"
                  placeholder="Enter video ID..."
                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>
          </form>
        </div>

        <!-- Search Results -->
        <div v-if="searchResults.length > 0 || searchPerformed" class="bg-white shadow rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">
              Search Results
              <span class="text-sm font-normal text-gray-500 ml-2">
                ({{ searchResults.length }} results for "{{ lastQuery }}")
              </span>
            </h3>
          </div>

          <div v-if="searchResults.length === 0 && searchPerformed" class="px-6 py-8 text-center">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No results found</h3>
            <p class="mt-1 text-sm text-gray-500">Try adjusting your search query or search type.</p>
          </div>

          <ul v-else class="divide-y divide-gray-200">
            <li v-for="result in searchResults" :key="result.id" class="px-6 py-4 hover:bg-gray-50">
              <div class="flex items-start space-x-4">
                <!-- Media Type Icon -->
                <div class="flex-shrink-0">
                  <div class="w-10 h-10 rounded-lg flex items-center justify-center"
                       :class="{
                         'bg-blue-500': result.type === 'video',
                         'bg-green-500': result.type === 'audio',
                         'bg-purple-500': result.type === 'image'
                       }">
                    <svg v-if="result.type === 'video'" class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                    <svg v-else-if="result.type === 'audio'" class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
                    </svg>
                    <svg v-else-if="result.type === 'image'" class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                  </div>
                </div>

                <!-- Result Content -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <router-link
                      v-if="result.type === 'video'"
                      :to="`/video/${result.id}`"
                      class="text-sm font-medium text-blue-600 hover:text-blue-800 truncate"
                    >
                      {{ result.name || result.filename }}
                    </router-link>
                    <span v-else class="text-sm font-medium text-gray-900 truncate">
                      {{ result.name || result.filename }}
                    </span>
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ml-2"
                          :class="{
                            'bg-blue-100 text-blue-800': result.type === 'video',
                            'bg-green-100 text-green-800': result.type === 'audio',
                            'bg-purple-100 text-purple-800': result.type === 'image'
                          }">
                      {{ result.type }}
                    </span>
                  </div>

                  <p class="mt-1 text-sm text-gray-600">{{ result.collection_name || 'Unknown collection' }}</p>

                  <!-- Transcript snippet or description -->
                  <div v-if="result.snippet || result.description" class="mt-2">
                    <p class="text-sm text-gray-700 line-clamp-2">
                      <span v-if="result.snippet" class="font-medium">"...{{ result.snippet }}..."</span>
                      <span v-else>{{ result.description }}</span>
                    </p>
                  </div>

                  <!-- Metadata -->
                  <div class="mt-2 flex items-center text-xs text-gray-500 space-x-4">
                    <span v-if="result.duration">{{ result.duration }}s</span>
                    <span v-if="result.size">{{ formatFileSize(result.size) }}</span>
                    <span v-if="result.timestamp">at {{ result.timestamp }}</span>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex-shrink-0 flex space-x-2">
                  <button
                    @click="downloadResult(result)"
                    class="inline-flex items-center px-2 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </button>
                  <router-link
                    v-if="result.type === 'video'"
                    :to="`/video/${result.id}`"
                    class="inline-flex items-center px-2 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                  >
                    View
                  </router-link>
                </div>
              </div>
            </li>
          </ul>
        </div>

        <!-- Recent Searches -->
        <div class="mt-8 bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Searches</h3>
          <div v-if="recentSearches.length === 0" class="text-center py-4">
            <p class="text-sm text-gray-500">No recent searches</p>
          </div>
          <div v-else class="space-y-2">
            <button
              v-for="search in recentSearches"
              :key="search.id"
              @click="repeatSearch(search)"
              class="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 hover:bg-gray-100 flex items-center justify-between"
            >
              <span>{{ search.query }}</span>
              <span class="text-xs text-gray-500 capitalize">{{ search.type }}</span>
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const searchQuery = ref('')
const searchType = ref('semantic')
const searchInVideo = ref(false)
const videoId = ref('')
const searching = ref(false)
const searchPerformed = ref(false)
const searchResults = ref([])
const lastQuery = ref('')
const recentSearches = ref([])

const BACKEND_URL = import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:8000'

const performSearch = async () => {
  if (!searchQuery.value.trim()) return

  searching.value = true
  searchPerformed.value = true
  lastQuery.value = searchQuery.value

  try {
    const params = {
      query: searchQuery.value,
      type: searchType.value
    }

    if (searchInVideo.value && videoId.value) {
      params.video_id = videoId.value
    }

    const response = await axios.get(`${BACKEND_URL}/videodb/search`, { params })
    searchResults.value = response.data.results || []

    // Add to recent searches
    const searchEntry = {
      id: Date.now(),
      query: searchQuery.value,
      type: searchType.value,
      timestamp: new Date().toISOString()
    }
    recentSearches.value.unshift(searchEntry)
    if (recentSearches.value.length > 10) {
      recentSearches.value = recentSearches.value.slice(0, 10)
    }
    localStorage.setItem('recentSearches', JSON.stringify(recentSearches.value))

  } catch (error) {
    console.error('Search failed:', error)
    searchResults.value = []
  } finally {
    searching.value = false
  }
}

const repeatSearch = (search) => {
  searchQuery.value = search.query
  searchType.value = search.type
  performSearch()
}

const downloadResult = async (result) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/videodb/asset/${result.id}/download`, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', result.filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error('Failed to download result:', error)
    alert('Failed to download file. Please try again.')
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  const saved = localStorage.getItem('recentSearches')
  if (saved) {
    recentSearches.value = JSON.parse(saved)
  }
})
</script>