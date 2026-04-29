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
        <div class="flex justify-between items-center mb-8">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">Collections</h2>
            <p class="mt-1 text-sm text-gray-600">Manage your video collections</p>
          </div>
          <button
            @click="showCreateModal = true"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Create Collection
          </button>
        </div>

        <!-- Collections Grid -->
        <div v-if="collections.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No collections</h3>
          <p class="mt-1 text-sm text-gray-500">Get started by creating your first collection.</p>
          <div class="mt-6">
            <button
              @click="showCreateModal = true"
              class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Create Collection
            </button>
          </div>
        </div>
        <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="collection in collections"
            :key="collection.id"
            class="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow duration-200"
          >
            <div class="p-6">
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-lg bg-blue-500 flex items-center justify-center">
                      <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                    </div>
                  </div>
                  <div class="ml-4">
                    <router-link
                      :to="`/collections/${collection.id}`"
                      class="text-lg font-medium text-gray-900 hover:text-blue-600"
                    >
                      {{ collection.name }}
                    </router-link>
                    <p class="text-sm text-gray-500">{{ collection.description || 'No description' }}</p>
                  </div>
                </div>
              </div>
              <div class="mt-4 flex items-center justify-between">
                <div class="text-sm text-gray-500">
                  {{ collection.asset_count || 0 }} assets
                </div>
                <div class="flex space-x-2">
                  <router-link
                    :to="`/collections/${collection.id}`"
                    class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                  >
                    View
                  </router-link>
                  <button
                    @click="deleteCollection(collection.id)"
                    class="inline-flex items-center px-3 py-1 border border-red-300 shadow-sm text-xs font-medium rounded text-red-700 bg-white hover:bg-red-50"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Create Collection Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Create New Collection</h3>
          <form @submit.prevent="createCollection">
            <div class="mb-4">
              <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
              <input
                v-model="newCollection.name"
                type="text"
                id="name"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                required
              />
            </div>
            <div class="mb-4">
              <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                v-model="newCollection.description"
                id="description"
                rows="3"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              ></textarea>
            </div>
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="showCreateModal = false"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="loading"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {{ loading ? 'Creating...' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const collections = ref([])
const showCreateModal = ref(false)
const loading = ref(false)
const newCollection = ref({
  name: '',
  description: ''
})

const BACKEND_URL = import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:8000'

const fetchCollections = async () => {
  try {
    const response = await axios.get(`${BACKEND_URL}/videodb/collection`)
    collections.value = response.data
  } catch (error) {
    console.error('Failed to fetch collections:', error)
  }
}

const createCollection = async () => {
  loading.value = true
  try {
    await axios.post(`${BACKEND_URL}/videodb/collection`, {
      name: newCollection.value.name,
      description: newCollection.value.description
    })
    showCreateModal.value = false
    newCollection.value = { name: '', description: '' }
    await fetchCollections()
  } catch (error) {
    console.error('Failed to create collection:', error)
    alert('Failed to create collection. Please try again.')
  } finally {
    loading.value = false
  }
}

const deleteCollection = async (collectionId) => {
  if (!confirm('Are you sure you want to delete this collection? This action cannot be undone.')) {
    return
  }

  try {
    await axios.delete(`${BACKEND_URL}/videodb/collection/${collectionId}`)
    await fetchCollections()
  } catch (error) {
    console.error('Failed to delete collection:', error)
    alert('Failed to delete collection. Please try again.')
  }
}

onMounted(() => {
  fetchCollections()
})
</script>