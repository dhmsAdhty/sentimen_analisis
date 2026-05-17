<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useAppStore } from '../store'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Bar } from 'vue-chartjs'
import PipelineNav from '../components/PipelineNav.vue'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const store = useAppStore()

const isLoading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const previewData = ref(null)
const chartData = ref(null)

const handleLabeling = async () => {
  if (!store.sessionId) {
    errorMsg.value = 'Sesi tidak ditemukan. Pastikan Anda sudah melewati proses input data.'
    return
  }

  isLoading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  
  try {
    const response = await axios.post('http://localhost:8000/api/sentiment/label', {
      session_id: store.sessionId
    })
    
    previewData.value = response.data.preview
    
    const dist = response.data.distribution
    
    const labelNames = { 0: 'Negatif', 1: 'Netral', 2: 'Positif' }
    const colors = { 0: '#ef4444', 1: '#94a3b8', 2: '#10b981' }
    
    const labels = Object.keys(dist).map(k => labelNames[k] || k)
    const counts = Object.values(dist)
    const bgColors = Object.keys(dist).map(k => colors[k] || '#3b82f6')
    
    chartData.value = {
      labels,
      datasets: [{
        label: 'Distribusi Sentimen',
        backgroundColor: bgColors,
        data: counts,
        borderRadius: 6
      }]
    }
    
    const total = Object.values(dist).reduce((a, b) => a + b, 0)
    successMsg.value = `Pelabelan selesai! ${total} data berlabel — Positif: ${dist[2]||0}, Netral: ${dist[1]||0}, Negatif: ${dist[0]||0}`
  } catch (error) {
    errorMsg.value = 'Gagal melakukan labeling: ' + (error.response?.data?.detail || error.message)
  } finally {
    isLoading.value = false
  }
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
    y: { ticks: { color: '#e2e8f0' }, grid: { color: '#334155' } }
  }
}
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-white mb-1">Labeling Sentimen (Lexicon)</h1>
    <p class="text-slate-400">Pemberian label positif, negatif, atau netral secara otomatis menggunakan Lexicon.</p>
    
    <div class="mt-8 bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 relative overflow-hidden">
      <div class="absolute top-0 left-1/4 w-1/2 h-px bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50"></div>
      
      <div v-if="errorMsg" class="p-4 bg-red-500/10 border border-red-500/50 rounded-xl text-red-400 mb-6 flex items-center gap-2">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        {{ errorMsg }}
      </div>
      <div v-if="successMsg" class="p-4 bg-emerald-500/10 border border-emerald-500/50 rounded-xl text-emerald-400 mb-6 flex items-center gap-2">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        {{ successMsg }}
      </div>

      <div class="flex flex-col md:flex-row md:items-center justify-between mb-8">
        <div>
          <h3 class="text-lg font-medium text-slate-200">Jalankan Lexicon</h3>
          <p class="text-sm text-slate-400">Proses pencocokan kata dengan kamus (Lexicon).</p>
        </div>
        
        <button 
          @click="handleLabeling"
          :disabled="isLoading || !store.sessionId"
          class="mt-4 md:mt-0 flex items-center justify-center px-6 py-3 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-white font-medium rounded-xl shadow-lg shadow-emerald-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span v-if="!isLoading">Mulai Labeling</span>
          <span v-else>Memproses...</span>
        </button>
      </div>

      <div v-if="chartData && !isLoading" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div class="lg:col-span-1 h-80 bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
          <h4 class="text-slate-300 font-medium mb-4 text-center">Distribusi Sentimen</h4>
          <div class="h-64">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
        </div>
        
        <div class="lg:col-span-2 overflow-x-auto bg-slate-800/50 rounded-xl border border-slate-700/50">
          <table class="w-full text-left text-sm text-slate-400">
            <thead class="text-xs text-slate-300 uppercase bg-slate-700/50">
              <tr>
                <th class="px-4 py-3">Clean Text</th>
                <th class="px-4 py-3">Score</th>
                <th class="px-4 py-3">Label</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in previewData" :key="idx" class="border-b border-slate-700/50">
                <td class="px-4 py-3 max-w-[200px] truncate" :title="row.clean">{{ row.clean }}</td>
                <td class="px-4 py-3 font-mono text-emerald-400">{{ row.sentiment_score }}</td>
                <td class="px-4 py-3">
                  <span v-if="row.sentiment_label === 2" class="text-emerald-400 font-medium">Positif</span>
                  <span v-else-if="row.sentiment_label === 0" class="text-red-400 font-medium">Negatif</span>
                  <span v-else class="text-slate-300 font-medium">Netral</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
      </div>

    </div>
    <PipelineNav :current="5" />
</div>
</template>
