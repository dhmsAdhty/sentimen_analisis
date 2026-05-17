<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAppStore } from '../store'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend
} from 'chart.js'
import { Bar } from 'vue-chartjs'
import PipelineNav from '../components/PipelineNav.vue'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const store = useAppStore()

const isLoading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const insightData = ref(null)

const chartCluster = ref(null)
const chartSentiment = ref(null)

const barOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
  }
}

const sentimentName = (id) => ({ 0: 'Negatif', 1: 'Netral', 2: 'Positif' }[id] || `Label ${id}`)
const sentimentColor = (id) => ({ 0: 'rgba(239,68,68,0.7)', 1: 'rgba(148,163,184,0.7)', 2: 'rgba(16,185,129,0.7)' }[id] || 'rgba(100,116,139,0.7)')

const loadInsight = async () => {
  if (!store.sessionId) {
    errorMsg.value = 'Sesi tidak ditemukan.'
    return
  }
  isLoading.value = true
  try {
    const res = await axios.post('http://localhost:8000/api/insight', { session_id: store.sessionId })
    insightData.value = res.data
    successMsg.value = `Insight berhasil dimuat! Total ${res.data.total_data} data.`

    // Build cluster chart
    if (res.data.cluster_distribution && Object.keys(res.data.cluster_distribution).length > 0) {
      const cd = res.data.cluster_distribution
      chartCluster.value = {
        labels: Object.keys(cd).map(k => `Cluster ${k}`),
        datasets: [{
          label: 'Jumlah Data',
          backgroundColor: ['#10b981','#3b82f6','#f59e0b','#ef4444','#a855f7','#ec4899'],
          data: Object.values(cd),
          borderRadius: 6
        }]
      }
    }

    // Build sentiment chart
    if (res.data.sentiment_distribution && Object.keys(res.data.sentiment_distribution).length > 0) {
      const sd = res.data.sentiment_distribution
      chartSentiment.value = {
        labels: Object.keys(sd).map(k => sentimentName(Number(k))),
        datasets: [{
          label: 'Jumlah Data',
          backgroundColor: Object.keys(sd).map(k => sentimentColor(Number(k))),
          data: Object.values(sd),
          borderRadius: 6
        }]
      }
    }
  } catch (err) {
    errorMsg.value = 'Gagal memuat insight: ' + (err.response?.data?.detail || err.message)
  } finally {
    isLoading.value = false
  }
}

const dominantSentiment = () => {
  if (!insightData.value?.sentiment_distribution) return null
  const sd = insightData.value.sentiment_distribution
  const maxKey = Object.keys(sd).reduce((a, b) => sd[a] > sd[b] ? a : b)
  return sentimentName(Number(maxKey))
}

onMounted(() => { if (store.sessionId) loadInsight() })
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-white mb-1">Insight Global</h1>
    <p class="text-slate-400">Ringkasan otomatis dari hasil clustering & sentimen analisis.</p>

    <div v-if="errorMsg" class="mt-4 p-4 bg-red-500/10 border border-red-500/50 rounded-xl text-red-400 flex items-center gap-2">
      <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      {{ errorMsg }}
    </div>
    <div v-if="successMsg" class="mt-4 p-4 bg-emerald-500/10 border border-emerald-500/50 rounded-xl text-emerald-400 flex items-center gap-2">
      <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      {{ successMsg }}
    </div>

    <div v-if="isLoading" class="mt-12 flex justify-center items-center text-emerald-500">
      <svg class="animate-spin h-10 w-10" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
      <span class="ml-3 text-lg">Memuat Insight...</span>
    </div>

    <div v-if="insightData && !isLoading" class="mt-6 space-y-6">

      <!-- Summary Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 text-center">
          <p class="text-slate-400 text-sm mb-1">Total Data</p>
          <p class="text-3xl font-bold text-white">{{ insightData.total_data }}</p>
        </div>
        <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 text-center">
          <p class="text-slate-400 text-sm mb-1">Total Cluster</p>
          <p class="text-3xl font-bold text-white">{{ insightData.total_clusters ?? '-' }}</p>
        </div>
        <div class="bg-slate-900/60 border border-emerald-500/30 rounded-2xl p-5 text-center">
          <p class="text-slate-400 text-sm mb-1">Cluster Terbaik</p>
          <p class="text-3xl font-bold text-emerald-400">{{ insightData.best_cluster !== undefined ? `#${insightData.best_cluster}` : '-' }}</p>
        </div>
        <div class="bg-slate-900/60 border border-red-500/30 rounded-2xl p-5 text-center">
          <p class="text-slate-400 text-sm mb-1">Cluster Terburuk</p>
          <p class="text-3xl font-bold text-red-400">{{ insightData.worst_cluster !== undefined ? `#${insightData.worst_cluster}` : '-' }}</p>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-if="chartCluster" class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
          <h3 class="text-slate-200 font-semibold mb-4">Distribusi Cluster</h3>
          <div style="height: 200px;"><Bar :data="chartCluster" :options="barOptions" /></div>
          <div class="mt-4 space-y-2">
            <div v-for="(count, cid) in insightData.cluster_distribution" :key="cid" class="flex justify-between items-center text-sm">
              <span class="text-slate-400">Cluster {{ cid }}</span>
              <span class="text-slate-200 font-medium">{{ count }} data</span>
            </div>
          </div>
        </div>

        <div v-if="chartSentiment" class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
          <h3 class="text-slate-200 font-semibold mb-1">Distribusi Sentimen</h3>
          <div v-if="dominantSentiment()" class="text-xs text-emerald-400 mb-3">Sentimen dominan: <strong>{{ dominantSentiment() }}</strong></div>
          <div style="height: 200px;"><Bar :data="chartSentiment" :options="barOptions" /></div>
          <div class="mt-4 space-y-2">
            <div v-for="(count, sid) in insightData.sentiment_distribution" :key="sid" class="flex justify-between items-center text-sm">
              <span class="text-slate-400">{{ sentimentName(Number(sid)) }}</span>
              <span class="font-medium"
                :class="{ 'text-emerald-400': Number(sid) === 2, 'text-red-400': Number(sid) === 0, 'text-slate-300': Number(sid) === 1 }">
                {{ count }} data
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Cluster Best/Worst -->
      <div v-if="insightData.best_cluster !== undefined" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-emerald-900/20 border border-emerald-500/30 p-4 rounded-xl text-emerald-400">
          Cluster paling positif: <strong>Cluster {{ insightData.best_cluster }}</strong>
        </div>
        <div class="bg-red-900/20 border border-red-500/30 p-4 rounded-xl text-red-400">
          Cluster paling negatif: <strong>Cluster {{ insightData.worst_cluster }}</strong>
        </div>
      </div>

      <!-- Kesimpulan -->
      <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
        <h3 class="text-slate-200 font-semibold mb-3">Kesimpulan Otomatis</h3>
        <p class="text-slate-300 leading-relaxed">
          Dari total <strong class="text-white">{{ insightData.total_data }} review</strong>, data berhasil dikelompokkan menjadi
          <strong class="text-emerald-400">{{ insightData.total_clusters }} cluster</strong>.
          Setiap cluster memiliki pola topik yang berbeda berdasarkan hasil TF-IDF dan K-Means.
          <span v-if="insightData.best_cluster !== undefined">
            Cluster <strong class="text-emerald-400">{{ insightData.best_cluster }}</strong> memiliki sentimen paling positif,
            sementara Cluster <strong class="text-red-400">{{ insightData.worst_cluster }}</strong> perlu mendapat perhatian lebih.
          </span>
          Model ini dapat digunakan untuk analisis persepsi pengguna secara otomatis dan terstruktur.
        </p>
      </div>

    </div>
    <PipelineNav :current="8" />
</div>
</template>
