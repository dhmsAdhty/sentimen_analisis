<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useAppStore } from '../store'
import { useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import PipelineNav from '../components/PipelineNav.vue'

const store = useAppStore()
const router = useRouter()

const inputMode = ref('upload')
const urls = ref('')
const maxReviews = ref(50)
const isScraping = ref(false)
const isUploading = ref(false)
const isCleaning = ref(false)

const successMsg = ref('')
const errorMsg = ref('')
const uploadedFile = ref(null)

const rawPreview = ref(null)
const cleanPreview = ref(null)
const totalRaw = ref(0)
const totalClean = ref(0)

const clearMessages = () => { successMsg.value = ''; errorMsg.value = '' }

const handleScrape = async () => {
  if (!urls.value.trim()) { errorMsg.value = 'URL tidak boleh kosong.'; return }
  clearMessages(); rawPreview.value = null; cleanPreview.value = null; isScraping.value = true
  try {
    const response = await axios.post('http://localhost:8000/api/data/scrape', { urls: urls.value, max_reviews: maxReviews.value })
    store.setSessionId(response.data.session_id)
    rawPreview.value = response.data.preview
    totalRaw.value = response.data.total_rows
    successMsg.value = 'Scraping berhasil!'
  } catch (error) {
    errorMsg.value = 'Gagal scraping: ' + (error.response?.data?.detail || error.message)
  } finally { isScraping.value = false }
}

const onFileChange = (event) => { const f = event.target.files[0]; if (f) { uploadedFile.value = f; clearMessages() } }

const handleFileUpload = async () => {
  if (!uploadedFile.value) { errorMsg.value = 'Pilih file terlebih dahulu.'; return }
  const formData = new FormData()
  formData.append('file', uploadedFile.value)
  clearMessages(); rawPreview.value = null; cleanPreview.value = null; isUploading.value = true
  try {
    const response = await axios.post('http://localhost:8000/api/data/upload', formData)
    store.setSessionId(response.data.session_id)
    rawPreview.value = response.data.preview
    totalRaw.value = response.data.total_rows
    successMsg.value = `File berhasil diupload! Total ${response.data.total_rows} baris.`
  } catch (error) {
    errorMsg.value = 'Gagal upload: ' + (error.response?.data?.detail || error.message)
  } finally { isUploading.value = false }
}

const handleClean = async () => {
  if (!store.sessionId) return
  clearMessages(); isCleaning.value = true
  try {
    const response = await axios.post('http://localhost:8000/api/data/clean', { session_id: store.sessionId })
    cleanPreview.value = response.data.preview
    totalClean.value = response.data.clean_rows
    successMsg.value = `Cleaning selesai! Tersisa ${response.data.clean_rows} dari ${response.data.original_rows} baris.`
  } catch (error) {
    errorMsg.value = 'Gagal cleaning: ' + (error.response?.data?.detail || error.message)
  } finally { isCleaning.value = false }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold text-white mb-1">Input Data</h1>
        <p class="text-slate-400">Import dataset ulasan melalui Scraping atau Upload File.</p>
      </div>
      <div class="bg-slate-800/80 p-1 rounded-lg inline-flex backdrop-blur-sm border border-slate-700">
        <button @click="inputMode = 'scraping'; clearMessages()"
          class="px-4 py-2 rounded-md text-sm font-medium transition-all duration-300"
          :class="inputMode === 'scraping' ? 'bg-gradient-to-r from-emerald-500 to-green-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'">
          Scraping Maps
        </button>
        <button @click="inputMode = 'upload'; clearMessages()"
          class="px-4 py-2 rounded-md text-sm font-medium transition-all duration-300"
          :class="inputMode === 'upload' ? 'bg-gradient-to-r from-emerald-500 to-green-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'">
          Upload File
        </button>
      </div>
    </div>

    <!-- Feedback -->
    <div v-if="successMsg" class="p-4 bg-emerald-500/10 border border-emerald-500/50 rounded-xl text-emerald-400 flex items-center">
      <AppIcon name="check" class="w-5 h-5 mr-2 flex-shrink-0" />{{ successMsg }}
    </div>
    <div v-if="errorMsg" class="p-4 bg-red-500/10 border border-red-500/50 rounded-xl text-red-400 flex items-center">
      <AppIcon name="error" class="w-5 h-5 mr-2 flex-shrink-0" />{{ errorMsg }}
    </div>

    <!-- Card -->
    <div class="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
      <div class="absolute top-0 left-1/4 w-1/2 h-px bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50"></div>

      <!-- Scraping -->
      <div v-if="inputMode === 'scraping'" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-slate-300 mb-2">URLs Google Maps</label>
          <textarea v-model="urls" rows="4"
            class="w-full bg-slate-950/50 border border-slate-700 rounded-xl p-4 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
            placeholder="Masukkan URL (1 baris 1 link)"></textarea>
        </div>
        <div class="w-1/2">
          <label class="block text-sm font-medium text-slate-300 mb-2">Jumlah Review per URL</label>
          <input type="number" v-model="maxReviews" min="1" max="1000"
            class="w-full bg-slate-950/50 border border-slate-700 rounded-xl p-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all" />
        </div>
        <button @click="handleScrape" :disabled="isScraping"
          class="flex items-center px-8 py-3 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-white font-medium rounded-xl shadow-lg shadow-emerald-500/25 transition-all disabled:opacity-50">
          <AppIcon v-if="!isScraping" name="play" class="w-5 h-5 mr-2" />
          <AppIcon v-else name="spinner" class="animate-spin w-5 h-5 mr-2" />
          {{ isScraping ? 'Mengeksekusi...' : 'Mulai Scraping' }}
        </button>
      </div>

      <!-- Upload -->
      <div v-else class="space-y-6">
        <label class="block cursor-pointer">
          <div class="border-2 border-dashed border-slate-600 hover:border-emerald-500 rounded-2xl p-10 text-center transition-colors duration-300">
            <div class="mx-auto w-16 h-16 rounded-full bg-slate-800/50 flex items-center justify-center mb-4">
              <AppIcon name="upload" class="w-8 h-8 text-slate-400" />
            </div>
            <h3 class="text-lg font-medium text-slate-200 mb-1">{{ uploadedFile ? uploadedFile.name : 'Klik untuk memilih file' }}</h3>
            <p class="text-sm text-slate-400">Mendukung file <strong>.csv</strong> dan <strong>.xlsx</strong></p>
            <p class="text-xs text-slate-500 mt-2">Pastikan file memiliki kolom bernama <strong>Review</strong></p>
          </div>
          <input type="file" class="hidden" accept=".csv,.xlsx,.xls" @change="onFileChange" />
        </label>

        <div v-if="uploadedFile" class="flex items-center justify-between p-4 bg-slate-800/50 border border-slate-600 rounded-xl">
          <div class="flex items-center">
            <AppIcon name="document" class="w-8 h-8 text-emerald-400 mr-3" />
            <div>
              <p class="text-slate-200 text-sm font-medium">{{ uploadedFile.name }}</p>
              <p class="text-slate-400 text-xs">{{ (uploadedFile.size / 1024).toFixed(1) }} KB</p>
            </div>
          </div>
          <button @click="handleFileUpload" :disabled="isUploading"
            class="flex items-center px-6 py-2 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-white font-medium rounded-lg shadow-lg transition-all disabled:opacity-50">
            <AppIcon v-if="isUploading" name="spinner" class="animate-spin w-4 h-4 mr-2" />
            {{ isUploading ? 'Mengupload...' : 'Upload Sekarang' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Raw Preview -->
    <div v-if="rawPreview" class="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6">
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-slate-800 flex items-center justify-center">
            <AppIcon name="table" class="w-5 h-5 text-slate-400" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-slate-200">Preview Data Mentah</h3>
            <p class="text-sm text-slate-400">Total {{ totalRaw }} baris (Menampilkan max 5)</p>
          </div>
        </div>
        <button @click="handleClean" :disabled="isCleaning"
          class="flex items-center px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white font-medium rounded-lg transition-all disabled:opacity-50">
          <AppIcon v-if="isCleaning" name="spinner" class="animate-spin w-4 h-4 mr-2" />
          <AppIcon v-else name="trash" class="w-4 h-4 mr-2" />
          Cleaning Missing &amp; Duplikat
        </button>
      </div>
      <div class="overflow-x-auto rounded-xl border border-slate-700/50">
        <table class="w-full text-left text-sm text-slate-400">
          <thead class="text-xs text-slate-300 uppercase bg-slate-800/50">
            <tr><th v-for="key in Object.keys(rawPreview[0])" :key="key" class="px-6 py-4 border-b border-slate-700">{{ key }}</th></tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in rawPreview" :key="idx" class="border-b border-slate-700/50 hover:bg-slate-800/30">
              <td v-for="(val, key) in row" :key="key" class="px-6 py-4 truncate max-w-xs">{{ val }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Clean Preview -->
    <div v-if="cleanPreview" class="bg-slate-900/60 backdrop-blur-xl border border-emerald-500/30 rounded-2xl p-6 border-l-4 border-l-emerald-500">
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-emerald-500/10 flex items-center justify-center">
            <AppIcon name="check" class="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-emerald-400">Data Setelah Cleaning</h3>
            <p class="text-sm text-slate-400">Missing values &amp; duplikat telah dihapus. Sisa {{ totalClean }} baris.</p>
          </div>
        </div>
        <button @click="router.push('/preprocessing')"
          class="flex items-center px-6 py-2 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-white font-medium rounded-lg transition-all">
          Lanjut ke Preprocessing
          <AppIcon name="arrow_right" class="w-4 h-4 ml-2" />
        </button>
      </div>
      <div class="overflow-x-auto rounded-xl border border-slate-700/50">
        <table class="w-full text-left text-sm text-slate-400">
          <thead class="text-xs text-slate-300 uppercase bg-slate-800/50">
            <tr><th v-for="key in Object.keys(cleanPreview[0])" :key="key" class="px-6 py-4 border-b border-slate-700">{{ key }}</th></tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in cleanPreview" :key="idx" class="border-b border-slate-700/50 hover:bg-slate-800/30">
              <td v-for="(val, key) in row" :key="key" class="px-6 py-4 truncate max-w-xs text-emerald-200">{{ val }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <PipelineNav :current="1" />
</div>
</template>
