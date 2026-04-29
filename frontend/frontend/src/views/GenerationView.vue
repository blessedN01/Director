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
          <h2 class="text-2xl font-bold text-gray-900">Generate Media</h2>
          <p class="mt-1 text-sm text-gray-600">Create new content using AI-powered generation tools</p>
        </div>

        <!-- Generation Tools Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- Image Generation -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-10 h-10 rounded-lg bg-purple-500 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <h3 class="text-lg font-medium text-gray-900">Generate Image</h3>
                  <p class="text-sm text-gray-500">Create images from text descriptions</p>
                </div>
              </div>
              <div class="mt-6">
                <form @submit.prevent="generateImage" class="space-y-4">
                  <div>
                    <label for="image-prompt" class="block text-sm font-medium text-gray-700">Prompt</label>
                    <textarea
                      v-model="imagePrompt"
                      id="image-prompt"
                      rows="3"
                      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Describe the image you want to generate..."
                    ></textarea>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label for="image-aspect-ratio" class="block text-sm font-medium text-gray-700">Aspect Ratio</label>
                      <select
                        v-model="imageAspectRatio"
                        id="image-aspect-ratio"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      >
                        <option value="16:9">16:9 (Landscape)</option>
                        <option value="1:1">1:1 (Square)</option>
                        <option value="9:16">9:16 (Portrait)</option>
                        <option value="4:3">4:3 (Classic)</option>
                      </select>
                    </div>
                    <div>
                      <label for="image-collection" class="block text-sm font-medium text-gray-700">Collection</label>
                      <select
                        v-model="imageCollection"
                        id="image-collection"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      >
                        <option value="default">Default</option>
                        <option v-for="collection in collections" :key="collection.id" :value="collection.id">
                          {{ collection.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <button
                    type="submit"
                    :disabled="generatingImage || !imagePrompt.trim()"
                    class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 disabled:opacity-50"
                  >
                    <svg v-if="generatingImage" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ generatingImage ? 'Generating...' : 'Generate Image' }}
                  </button>
                </form>
              </div>
            </div>
          </div>

          <!-- Video Generation -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <h3 class="text-lg font-medium text-gray-900">Generate Video</h3>
                  <p class="text-sm text-gray-500">Create videos from text descriptions</p>
                </div>
              </div>
              <div class="mt-6">
                <form @submit.prevent="generateVideo" class="space-y-4">
                  <div>
                    <label for="video-prompt" class="block text-sm font-medium text-gray-700">Prompt</label>
                    <textarea
                      v-model="videoPrompt"
                      id="video-prompt"
                      rows="3"
                      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Describe the video you want to generate..."
                    ></textarea>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label for="video-duration" class="block text-sm font-medium text-gray-700">Duration (seconds)</label>
                      <input
                        v-model.number="videoDuration"
                        id="video-duration"
                        type="number"
                        min="1"
                        max="30"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label for="video-collection" class="block text-sm font-medium text-gray-700">Collection</label>
                      <select
                        v-model="videoCollection"
                        id="video-collection"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      >
                        <option value="default">Default</option>
                        <option v-for="collection in collections" :key="collection.id" :value="collection.id">
                          {{ collection.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <button
                    type="submit"
                    :disabled="generatingVideo || !videoPrompt.trim()"
                    class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                  >
                    <svg v-if="generatingVideo" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ generatingVideo ? 'Generating...' : 'Generate Video' }}
                  </button>
                </form>
              </div>
            </div>
          </div>

          <!-- Voice Generation -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-10 h-10 rounded-lg bg-green-500 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <h3 class="text-lg font-medium text-gray-900">Generate Voice</h3>
                  <p class="text-sm text-gray-500">Convert text to speech</p>
                </div>
              </div>
              <div class="mt-6">
                <form @submit.prevent="generateVoice" class="space-y-4">
                  <div>
                    <label for="voice-text" class="block text-sm font-medium text-gray-700">Text</label>
                    <textarea
                      v-model="voiceText"
                      id="voice-text"
                      rows="3"
                      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Enter the text you want to convert to speech..."
                    ></textarea>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label for="voice-type" class="block text-sm font-medium text-gray-700">Voice</label>
                      <select
                        v-model="voiceType"
                        id="voice-type"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      >
                        <option value="alloy">Alloy</option>
                        <option value="echo">Echo</option>
                        <option value="fable">Fable</option>
                        <option value="onyx">Onyx</option>
                        <option value="nova">Nova</option>
                        <option value="shimmer">Shimmer</option>
                      </select>
                    </div>
                    <div>
                      <label for="voice-collection" class="block text-sm font-medium text-gray-700">Collection</label>
                      <select
                        v-model="voiceCollection"
                        id="voice-collection"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      >
                        <option value="default">Default</option>
                        <option v-for="collection in collections" :key="collection.id" :value="collection.id">
                          {{ collection.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <button
                    type="submit"
                    :disabled="generatingVoice || !voiceText.trim()"
                    class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
                  >
                    <svg v-if="generatingVoice" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ generatingVoice ? 'Generating...' : 'Generate Voice' }}
                  </button>
                </form>
              </div>
            </div>
          </div>

          <!-- Music Generation -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-10 h-10 rounded-lg bg-indigo-500 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <h3 class="text-lg font-medium text-gray-900">Generate Music</h3>
                  <p class="text-sm text-gray-500">Create music from descriptions</p>
                </div>
              </div>
              <div class="mt-6">
                <form @submit.prevent="generateMusic" class="space-y-4">
                  <div>
                    <label for="music-prompt" class="block text-sm font-medium text-gray-700">Prompt</label>
                    <textarea
                      v-model="musicPrompt"
                      id="music-prompt"
                      rows="3"
                      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Describe the music you want to generate..."
                    ></textarea>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label for="music-duration" class="block text-sm font-medium text-gray-700">Duration (seconds)</label>
                      <input
                        v-model.number="musicDuration"
                        id="music-duration"
                        type="number"
                        min="10"
                        max="60"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label for="music-collection" class="block text-sm font-medium text-gray-700">Collection</label>
                      <select
                        v-model="musicCollection"
                        id="music-collection"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      >
                        <option value="default">Default</option>
                        <option v-for="collection in collections" :key="collection.id" :value="collection.id">
                          {{ collection.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <button
                    type="submit"
                    :disabled="generatingMusic || !musicPrompt.trim()"
                    class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
                  >
                    <svg v-if="generatingMusic" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ generatingMusic ? 'Generating...' : 'Generate Music' }}
                  </button>
                </form>
              </div>
            </div>
          </div>

          <!-- Sound Effect Generation -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-10 h-10 rounded-lg bg-yellow-500 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <h3 class="text-lg font-medium text-gray-900">Generate Sound Effect</h3>
                  <p class="text-sm text-gray-500">Create sound effects from descriptions</p>
                </div>
              </div>
              <div class="mt-6">
                <form @submit.prevent="generateSoundEffect" class="space-y-4">
                  <div>
                    <label for="sfx-prompt" class="block text-sm font-medium text-gray-700">Prompt</label>
                    <textarea
                      v-model="sfxPrompt"
                      id="sfx-prompt"
                      rows="3"
                      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Describe the sound effect you want to generate..."
                    ></textarea>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label for="sfx-duration" class="block text-sm font-medium text-gray-700">Duration (seconds)</label>
                      <input
                        v-model.number="sfxDuration"
                        id="sfx-duration"
                        type="number"
                        min="1"
                        max="10"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label for="sfx-collection" class="block text-sm font-medium text-gray-700">Collection</label>
                      <select
                        v-model="sfxCollection"
                        id="sfx-collection"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      >
                        <option value="default">Default</option>
                        <option v-for="collection in collections" :key="collection.id" :value="collection.id">
                          {{ collection.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <button
                    type="submit"
                    :disabled="generatingSFX || !sfxPrompt.trim()"
                    class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700 disabled:opacity-50"
                  >
                    <svg v-if="generatingSFX" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ generatingSFX ? 'Generating...' : 'Generate Sound Effect' }}
                  </button>
                </form>
              </div>
            </div>
          </div>

          <!-- YouTube Search -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-10 h-10 rounded-lg bg-red-500 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <h3 class="text-lg font-medium text-gray-900">YouTube Search</h3>
                  <p class="text-sm text-gray-500">Search and download videos from YouTube</p>
                </div>
              </div>
              <div class="mt-6">
                <form @submit.prevent="searchYouTube" class="space-y-4">
                  <div>
                    <label for="youtube-query" class="block text-sm font-medium text-gray-700">Search Query</label>
                    <input
                      v-model="youtubeQuery"
                      id="youtube-query"
                      type="text"
                      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Search for videos on YouTube..."
                    />
                  </div>
                  <div>
                    <label for="youtube-count" class="block text-sm font-medium text-gray-700">Number of Results</label>
                    <select
                      v-model="youtubeCount"
                      id="youtube-count"
                      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    >
                      <option :value="5">5 results</option>
                      <option :value="10">10 results</option>
                      <option :value="20">20 results</option>
                    </select>
                  </div>
                  <button
                    type="submit"
                    :disabled="searchingYouTube || !youtubeQuery.trim()"
                    class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 disabled:opacity-50"
                  >
                    <svg v-if="searchingYouTube" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ searchingYouTube ? 'Searching...' : 'Search YouTube' }}
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>

        <!-- YouTube Results -->
        <div v-if="youtubeResults.length > 0" class="mt-8">
          <h3 class="text-lg font-medium text-gray-900 mb-4">YouTube Search Results</h3>
          <div class="bg-white shadow rounded-lg overflow-hidden">
            <ul class="divide-y divide-gray-200">
              <li v-for="video in youtubeResults" :key="video.id" class="p-6 hover:bg-gray-50">
                <div class="flex items-start space-x-4">
                  <img :src="video.thumbnail" :alt="video.title" class="w-32 h-18 object-cover rounded" />
                  <div class="flex-1">
                    <h4 class="text-lg font-medium text-gray-900">{{ video.title }}</h4>
                    <p class="text-sm text-gray-600 mt-1">{{ video.channel }}</p>
                    <p class="text-sm text-gray-500 mt-1">{{ video.duration }} • {{ video.views }} views</p>
                    <p class="text-sm text-gray-700 mt-2 line-clamp-2">{{ video.description }}</p>
                  </div>
                  <div class="flex-shrink-0">
                    <button
                      @click="downloadYouTubeVideo(video)"
                      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
                    >
                      Download
                    </button>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- Recent Generations -->
        <div class="mt-8 bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Generations</h3>
          <div v-if="recentGenerations.length === 0" class="text-center py-4">
            <p class="text-sm text-gray-500">No recent generations</p>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="generation in recentGenerations"
              :key="generation.id"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
            >
              <div class="flex items-center">
                <div class="flex-shrink-0 h-10 w-10">
                  <div class="h-10 w-10 rounded-lg bg-blue-500 flex items-center justify-center">
                    <span class="text-xs font-medium text-white">{{ generation.type.charAt(0).toUpperCase() }}</span>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-900">{{ generation.type }} generation</p>
                  <p class="text-sm text-gray-500 line-clamp-1">{{ generation.prompt }}</p>
                </div>
              </div>
              <div class="text-sm text-gray-500">
                {{ generation.timestamp }}
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

// Form data
const imagePrompt = ref('')
const imageAspectRatio = ref('16:9')
const imageCollection = ref('default')
const videoPrompt = ref('')
const videoDuration = ref(5)
const videoCollection = ref('default')
const voiceText = ref('')
const voiceType = ref('alloy')
const voiceCollection = ref('default')
const musicPrompt = ref('')
const musicDuration = ref(30)
const musicCollection = ref('default')
const sfxPrompt = ref('')
const sfxDuration = ref(3)
const sfxCollection = ref('default')
const youtubeQuery = ref('')
const youtubeCount = ref(5)

// State
const collections = ref([])
const generatingImage = ref(false)
const generatingVideo = ref(false)
const generatingVoice = ref(false)
const generatingMusic = ref(false)
const generatingSFX = ref(false)
const searchingYouTube = ref(false)
const youtubeResults = ref([])
const recentGenerations = ref([])

const BACKEND_URL = import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:8000'

const fetchCollections = async () => {
  try {
    const response = await axios.get(`${BACKEND_URL}/videodb/collection`)
    collections.value = response.data
  } catch (error) {
    console.error('Failed to fetch collections:', error)
  }
}

const generateImage = async () => {
  generatingImage.value = true
  try {
    await axios.post(`${BACKEND_URL}/videodb/generate/image`, {
      prompt: imagePrompt.value,
      aspect_ratio: imageAspectRatio.value,
      collection: imageCollection.value
    })

    recentGenerations.value.unshift({
      id: Date.now(),
      type: 'image',
      prompt: imagePrompt.value,
      timestamp: new Date().toLocaleString()
    })

    imagePrompt.value = ''
    alert('Image generation started! Check your collection for the result.')
  } catch (error) {
    console.error('Failed to generate image:', error)
    alert('Failed to generate image. Please try again.')
  } finally {
    generatingImage.value = false
  }
}

const generateVideo = async () => {
  generatingVideo.value = true
  try {
    await axios.post(`${BACKEND_URL}/videodb/generate/video`, {
      prompt: videoPrompt.value,
      duration: videoDuration.value,
      collection: videoCollection.value
    })

    recentGenerations.value.unshift({
      id: Date.now(),
      type: 'video',
      prompt: videoPrompt.value,
      timestamp: new Date().toLocaleString()
    })

    videoPrompt.value = ''
    alert('Video generation started! Check your collection for the result.')
  } catch (error) {
    console.error('Failed to generate video:', error)
    alert('Failed to generate video. Please try again.')
  } finally {
    generatingVideo.value = false
  }
}

const generateVoice = async () => {
  generatingVoice.value = true
  try {
    await axios.post(`${BACKEND_URL}/videodb/generate/voice`, {
      text: voiceText.value,
      voice: voiceType.value,
      collection: voiceCollection.value
    })

    recentGenerations.value.unshift({
      id: Date.now(),
      type: 'voice',
      prompt: voiceText.value,
      timestamp: new Date().toLocaleString()
    })

    voiceText.value = ''
    alert('Voice generation started! Check your collection for the result.')
  } catch (error) {
    console.error('Failed to generate voice:', error)
    alert('Failed to generate voice. Please try again.')
  } finally {
    generatingVoice.value = false
  }
}

const generateMusic = async () => {
  generatingMusic.value = true
  try {
    await axios.post(`${BACKEND_URL}/videodb/generate/music`, {
      prompt: musicPrompt.value,
      duration: musicDuration.value,
      collection: musicCollection.value
    })

    recentGenerations.value.unshift({
      id: Date.now(),
      type: 'music',
      prompt: musicPrompt.value,
      timestamp: new Date().toLocaleString()
    })

    musicPrompt.value = ''
    alert('Music generation started! Check your collection for the result.')
  } catch (error) {
    console.error('Failed to generate music:', error)
    alert('Failed to generate music. Please try again.')
  } finally {
    generatingMusic.value = false
  }
}

const generateSoundEffect = async () => {
  generatingSFX.value = true
  try {
    await axios.post(`${BACKEND_URL}/videodb/generate/sound-effect`, {
      prompt: sfxPrompt.value,
      duration: sfxDuration.value,
      collection: sfxCollection.value
    })

    recentGenerations.value.unshift({
      id: Date.now(),
      type: 'sound effect',
      prompt: sfxPrompt.value,
      timestamp: new Date().toLocaleString()
    })

    sfxPrompt.value = ''
    alert('Sound effect generation started! Check your collection for the result.')
  } catch (error) {
    console.error('Failed to generate sound effect:', error)
    alert('Failed to generate sound effect. Please try again.')
  } finally {
    generatingSFX.value = false
  }
}

const searchYouTube = async () => {
  searchingYouTube.value = true
  try {
    const response = await axios.get(`${BACKEND_URL}/videodb/youtube`, {
      params: {
        query: youtubeQuery.value,
        count: youtubeCount.value
      }
    })
    youtubeResults.value = response.data
  } catch (error) {
    console.error('Failed to search YouTube:', error)
    alert('Failed to search YouTube. Please try again.')
  } finally {
    searchingYouTube.value = false
  }
}

const downloadYouTubeVideo = async (video) => {
  try {
    const name = prompt('Enter a name for the downloaded video:', video.title)
    if (!name) return

    await axios.post(`${BACKEND_URL}/videodb/download`, {
      url: video.url,
      name: name
    })

    alert('Download started! Check your default collection for the video.')
  } catch (error) {
    console.error('Failed to download video:', error)
    alert('Failed to download video. Please try again.')
  }
}

onMounted(() => {
  fetchCollections()
})
</script>