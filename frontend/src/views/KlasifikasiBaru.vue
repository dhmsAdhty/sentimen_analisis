<script setup>
import { ref } from 'vue'
import axios from 'axios'
import PipelineNav from '../components/PipelineNav.vue'

const textInput = ref('')
const isPredicting = ref(false)
const isProcessingFile = ref(false)
const result = ref(null)
const errorMsg = ref('')
const mode = ref('manual') // 'manual' or 'file'
const uploadedFile = ref(null)
const batchResults = ref(null)

const sentimentName = (id) => ({ 0: 'Negatif', 1: 'Netral', 2: 'Positif' }[id] || 'Unknown')
const sentimentColorClass = (id) => ({
  0: 'text-red-400 bg-red-400/10 border-red-400/30',
  1: 'text-slate-300 bg-slate-300/10 border-slate-300/30',
  2: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30'
}[id] || 'text-slate-400 bg-slate-800 border-slate-700')

const handlePredict = async () => {
  if (!textInput.value.trim()) { errorMsg.value = 'Teks tidak boleh kosong.'; return }
  isPredicting.value = true
  errorMsg.value = ''
  result.value = null
  try {
    const res = await axios.post('http://localhost:8000/api/model/predict', { text: textInput.value })
    result.value = res.data
  } catch (err) {
    errorMsg.value = 'Gagal memprediksi: ' + (err.response?.data?.detail || err.message)
  } finally {
    isPredicting.value = false
  }
}

const onFileChange = (e) => { uploadedFile.value = e.target.files[0] }

const handleBatchPredict = async () => {
  if (!uploadedFile.value) { errorMsg.value = 'Pilih file terlebih dahulu.'; return }
  const formData = new FormData()
  formData.append('file', uploadedFile.value)
  isProcessingFile.value = true
  errorMsg.value = ''
  batchResults.value = null
  try {
    const res = await axios.post('http://localhost:8000/api/model/predict_batch', formData)
    batchResults.value = res.data
  } catch (err) {
    errorMsg.value = 'Gagal memproses file: ' + (err.response?.data?.detail || err.message)
  } finally {
    isProcessingFile.value = false
  }
}

const downloadBatchCSV = () => {
  if (!batchResults.value?.predictions) return
  const data = batchResults.value.predictions
  const keys = Object.keys(data[0])
  const csv = [keys.join(','), ...data.map(r => keys.map(k => `"${String(r[k] ?? '').replace(/"/g, '""')}"`).join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = 'prediksi.csv'; a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-white mb-1">Klasifikasi Baru</h1>
    <p class="text-slate-400">Prediksi sentimen & cluster untuk teks baru menggunakan model yang telah dilatih.</p>

    <!-- Mode Toggle -->
    <div class="mt-6 bg-slate-800/80 p-1 rounded-lg inline-flex border border-slate-700">
      <button @click="mode = 'manual'; errorMsg = ''; result = null; batchResults = null"
        class="px-4 py-2 rounded-md text-sm font-medium transition-all duration-300"
        :class="mode === 'manual' ? 'bg-gradient-to-r from-emerald-500 to-green-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'">
        Teks Manual
      </button>
      <button @click="mode = 'file'; errorMsg = ''; result = null; batchResults = null"
        class="px-4 py-2 rounded-md text-sm font-medium transition-all duration-300"
        :class="mode === 'file' ? 'bg-gradient-to-r from-emerald-500 to-green-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'">
        Upload File (Batch)
      </button>
    </div>

    <div v-if="errorMsg" class="mt-4 p-4 bg-red-500/10 border border-red-500/50 rounded-xl text-red-400">{{ errorMsg }}</div>

    <!-- === MANUAL MODE === -->
    <div v-if="mode === 'manual'" class="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div class="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 relative">
        <div class="absolute top-0 left-1/4 w-1/2 h-px bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50"></div>
        <h3 class="text-slate-200 font-semibold mb-4">Masukkan Teks Baru</h3>
        <textarea v-model="textInput" rows="6"
          class="w-full bg-slate-950/50 border border-slate-700 rounded-xl p-4 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all mb-4"
          placeholder="Ketik ulasan atau opini baru di sini...">
        </textarea>
        <button @click="handlePredict" :disabled="isPredicting"
          class="w-full flex items-center justify-center px-6 py-3 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-white font-medium rounded-xl shadow-lg transition-all disabled:opacity-50">
          <svg v-if="isPredicting" class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
          <span>{{ isPredicting ? 'Menganalisis...' : 'Prediksi' }}</span>
        </button>
      </div>

      <div class="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 flex flex-col items-center justify-center min-h-[280px]">
        <div v-if="!result && !isPredicting" class="text-slate-500 text-center">
          <svg class="w-16 h-16 mx-auto mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <p>Hasil prediksi akan muncul di sini.</p>
        </div>
        <div v-if="isPredicting" class="text-emerald-500 text-center">
          <svg class="animate-spin h-12 w-12 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
          <p>Model sedang menganalisis...</p>
        </div>
        <div v-if="result && !isPredicting" class="w-full space-y-4">
          <div class="text-center mb-4">
            <p class="text-slate-400 text-xs mb-1">Teks Input</p>
            <p class="text-slate-200 italic text-sm">"{{ result.text }}"</p>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="border rounded-xl p-6 text-center" :class="sentimentColorClass(result.sentiment)">
              <p class="text-xs uppercase tracking-wider mb-1 opacity-70">Sentimen</p>
              <h2 class="text-2xl font-black">{{ sentimentName(result.sentiment) }}</h2>
            </div>
            <div class="border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 rounded-xl p-6 text-center">
              <p class="text-xs uppercase tracking-wider mb-1 opacity-70">Topik Cluster</p>
              <h2 class="text-2xl font-black">Cluster {{ result.cluster }}</h2>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- === FILE MODE === -->
    <div v-if="mode === 'file'" class="mt-4 space-y-4">
      <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
        <h3 class="text-slate-200 font-semibold mb-4">Upload File CSV / Excel</h3>
        <p class="text-sm text-slate-400 mb-4">File harus memiliki kolom <strong class="text-white">Review</strong>. Sistem akan memprediksi sentimen & cluster untuk setiap baris.</p>
        <label class="block cursor-pointer">
          <div class="border-2 border-dashed border-slate-600 hover:border-emerald-500 rounded-xl p-8 text-center transition-colors">
            <svg class="w-10 h-10 mx-auto mb-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>
            <p class="text-slate-200">{{ uploadedFile ? uploadedFile.name : 'Klik untuk pilih file' }}</p>
            <p class="text-xs text-slate-500 mt-1">Mendukung .csv dan .xlsx</p>
          </div>
          <input type="file" class="hidden" accept=".csv,.xlsx" @change="onFileChange" />
        </label>
        <div v-if="uploadedFile" class="mt-4 flex items-center justify-between p-4 bg-slate-800/50 border border-slate-600 rounded-xl">
          <span class="text-slate-300 text-sm">{{ uploadedFile.name }}</span>
          <button @click="handleBatchPredict" :disabled="isProcessingFile"
            class="flex items-center px-6 py-2 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-white font-medium rounded-lg transition-all disabled:opacity-50">
            <svg v-if="isProcessingFile" class="animate-spin mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            {{ isProcessingFile ? 'Memproses...' : '🚀 Proses Data' }}
          </button>
        </div>
      </div>

      <!-- Batch Results -->
      <div v-if="batchResults" class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
        <div class="flex justify-between items-center mb-4">
          <div>
            <h3 class="text-slate-200 font-semibold">Hasil Prediksi</h3>
            <p class="text-sm text-slate-400">Total {{ batchResults.total }} data. Cluster unik: {{ batchResults.unique_clusters }}.</p>
          </div>
          <button @click="downloadBatchCSV" class="flex items-center px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 text-sm rounded-xl transition-all">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            Download CSV
          </button>
        </div>
        <div class="overflow-x-auto rounded-xl border border-slate-700/50">
          <table class="w-full text-left text-sm text-slate-400">
            <thead class="text-xs text-slate-300 uppercase bg-slate-800/50">
              <tr>
                <th class="px-4 py-3 border-b border-slate-700">Review</th>
                <th class="px-4 py-3 border-b border-slate-700">Clean</th>
                <th class="px-4 py-3 border-b border-slate-700">Sentimen</th>
                <th class="px-4 py-3 border-b border-slate-700">Cluster</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in batchResults.predictions" :key="idx" class="border-b border-slate-700/50 hover:bg-slate-800/30">
                <td class="px-4 py-3 max-w-xs truncate" :title="row.Review">{{ row.Review }}</td>
                <td class="px-4 py-3 max-w-xs truncate text-emerald-300" :title="row.clean">{{ row.clean }}</td>
                <td class="px-4 py-3">
                  <span class="px-2 py-1 rounded-full text-xs font-medium" :class="sentimentColorClass(row.sentiment_label)">{{ sentimentName(row.sentiment_label) }}</span>
                </td>
                <td class="px-4 py-3 text-emerald-400 font-medium">Cluster {{ row.cluster }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <PipelineNav :current="9" />
</div>
</template>
