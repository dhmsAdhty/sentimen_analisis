<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useAppStore } from '../store'
import PipelineNav from '../components/PipelineNav.vue'

const store = useAppStore()

const isProcessing = ref(false)
const isResetting = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const rawPreview = ref(null)
const processedData = ref(null)
const totalRows = ref(0)

const clearMessages = () => { errorMsg.value = ''; successMsg.value = '' }

// CSV download helper
const downloadCSV = (data, filename) => {
  if (!data || data.length === 0) return
  const keys = Object.keys(data[0])
  const csv = [keys.join(','), ...data.map(r => keys.map(k => `"${String(r[k] ?? '').replace(/"/g, '""')}"`).join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}

const loadRawPreview = async () => {
  if (!store.sessionId) return
  try {
    // Re-use clean endpoint to get preview
    const res = await axios.post('http://localhost:8000/api/data/info', { session_id: store.sessionId })
    // fetch preview separately
  } catch {}
}

const handlePreprocess = async () => {
  if (!store.sessionId) {
    errorMsg.value = 'Sesi tidak ditemukan. Lakukan Input Data terlebih dahulu.'
    return
  }
  clearMessages()
  isProcessing.value = true
  try {
    const response = await axios.post('http://localhost:8000/api/process/preprocess', { session_id: store.sessionId })
    processedData.value = response.data.preview
    totalRows.value = response.data.total_rows
    successMsg.value = `Preprocessing selesai! Total ${response.data.total_rows} baris berhasil diproses.`
  } catch (error) {
    errorMsg.value = 'Gagal preprocessing: ' + (error.response?.data?.detail || error.message)
  } finally {
    isProcessing.value = false
  }
}

const handleReset = async () => {
  if (!store.sessionId) return
  clearMessages()
  isResetting.value = true
  processedData.value = null
  // Simply clear local state
  setTimeout(() => {
    isResetting.value = false
    successMsg.value = 'Reset berhasil. Anda bisa menjalankan preprocessing ulang.'
  }, 500)
}
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-white mb-1">Preprocessing Data</h1>
    <p class="text-slate-400">Cleaning, Tokenization, Stopword Removal, dan Stemming (Sastrawi).</p>

    <!-- Feedback -->
    <div v-if="successMsg" class="mt-4 p-4 bg-emerald-500/10 border border-emerald-500/50 rounded-xl text-emerald-400 flex items-center">
      <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      {{ successMsg }}
    </div>
    <div v-if="errorMsg" class="mt-4 p-4 bg-red-500/10 border border-red-500/50 rounded-xl text-red-400">
      {{ errorMsg }}
    </div>

    <!-- Action Card -->
    <div class="mt-6 bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 relative overflow-hidden">
      <div class="absolute top-0 left-1/4 w-1/2 h-px bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50"></div>

      <div v-if="!store.sessionId" class="p-4 bg-amber-500/10 border border-amber-500/40 rounded-xl text-amber-400 mb-4 flex items-center">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        Data belum diinput. Silakan ke halaman <strong class="mx-1">Input Data</strong> terlebih dahulu.
      </div>

      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 class="text-lg font-semibold text-slate-200">Jalankan NLP Pipeline</h3>
          <p class="text-sm text-slate-400">Proses: lowercase → hapus noise → stopword → stemming Sastrawi</p>
        </div>
        <div class="flex gap-3">
          <button
            @click="handleReset"
            :disabled="isResetting || !processedData"
            class="flex items-center px-4 py-2 border border-slate-600 text-slate-300 hover:bg-slate-800 rounded-xl transition-all disabled:opacity-40"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            Reset
          </button>
          <button
            @click="handlePreprocess"
            :disabled="isProcessing || !store.sessionId"
            class="flex items-center px-6 py-2 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-white font-medium rounded-xl shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="isProcessing" class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            {{ isProcessing ? 'Memproses...' : 'Jalankan Preprocessing' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Results Preview -->
    <div v-if="processedData && processedData.length > 0" class="mt-6 space-y-4">

      <!-- Stats row -->
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-xl font-bold text-slate-200">Hasil Preprocessing</h3>
          <p class="text-sm text-slate-400">Total {{ totalRows }} baris. Preview 10 baris pertama.</p>
        </div>
        <button
          @click="downloadCSV(processedData, 'data_preprocessing.csv')"
          class="flex items-center px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 text-sm rounded-xl transition-all"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          Download CSV
        </button>
      </div>

      <div class="overflow-x-auto rounded-xl border border-slate-700/50 bg-slate-900/40">
        <table class="w-full text-left text-sm text-slate-400">
          <thead class="text-xs text-slate-300 uppercase bg-slate-800/50">
            <tr>
              <th class="px-6 py-4 border-b border-slate-700 w-16">#</th>
              <th class="px-6 py-4 border-b border-slate-700">Review (Teks Asli)</th>
              <th class="px-6 py-4 border-b border-slate-700">Clean (Hasil Preprocessing)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in processedData" :key="idx" class="border-b border-slate-700/50 hover:bg-slate-800/30 transition-colors">
              <td class="px-6 py-4 text-slate-500">{{ idx + 1 }}</td>
              <td class="px-6 py-4 max-w-xs">
                <p class="truncate" :title="row.Review">{{ row.Review }}</p>
              </td>
              <td class="px-6 py-4 max-w-xs">
                <p class="text-emerald-300 truncate" :title="row.clean">{{ row.clean }}</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <PipelineNav :current="2" />
</div>
</template>
