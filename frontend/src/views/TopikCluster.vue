<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAppStore } from '../store'
import { useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend
} from 'chart.js'
import { Bar } from 'vue-chartjs'
import PipelineNav from '../components/PipelineNav.vue'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const store = useAppStore()
const router = useRouter()

const isLoading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const notClustered = ref(false)
const topicsData = ref(null) // { clusterId: { words: [{word, score}], chartData } }
const clusterSummary = ref(null)

const clusterColors = [
  'rgba(16, 185, 129, 0.8)', 'rgba(59, 130, 246, 0.8)',
  'rgba(245, 158, 11, 0.8)', 'rgba(239, 68, 68, 0.8)',
  'rgba(168, 85, 247, 0.8)', 'rgba(236, 72, 153, 0.8)'
]
const getColor = (id) => clusterColors[parseInt(id) % clusterColors.length]

const barOptions = {
  indexAxis: 'y', responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { callbacks: { label: (ctx) => ` TF-IDF: ${ctx.raw.toFixed(4)}` } } },
  scales: {
    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
    y: { ticks: { color: '#e2e8f0', font: { size: 11 } }, grid: { display: false } }
  }
}

const loadTopics = async () => {
  if (!store.sessionId) {
    errorMsg.value = 'Sesi tidak ditemukan.'
    return
  }
  isLoading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  notClustered.value = false

  try {
    const res = await axios.post('http://localhost:8000/api/cluster/topic', { session_id: store.sessionId })
    const formatted = {}

    for (const [clusterId, words] of Object.entries(res.data.topics)) {
      formatted[clusterId] = {
        words,
        chartData: {
          labels: words.map(w => w.word),
          datasets: [{
            label: 'TF-IDF',
            backgroundColor: getColor(clusterId),
            data: words.map(w => parseFloat(w.score.toFixed(4))),
            borderRadius: 4
          }]
        }
      }
    }
    topicsData.value = formatted
    const numClusters = Object.keys(formatted).length
    successMsg.value = `Topik berhasil dimuat untuk ${numClusters} cluster.`

    // Build summary
    const ids = Object.keys(formatted).map(Number)
    clusterSummary.value = {
      total: ids.length,
      largest: ids.reduce((a, b) => formatted[a].words.length >= formatted[b].words.length ? a : b),
      smallest: ids.reduce((a, b) => formatted[a].words.length <= formatted[b].words.length ? a : b)
    }
  } catch (err) {
    if (err.response?.status === 404) {
      notClustered.value = true
    } else {
      errorMsg.value = 'Gagal memuat topik: ' + (err.response?.data?.detail || err.message)
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => { loadTopics() })
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-2">
      <div>
        <h1 class="text-3xl font-bold text-white mb-1">Topik Tiap Cluster</h1>
        <p class="text-slate-400">Kata-kata dominan pada setiap cluster (berdasarkan TF-IDF).</p>
      </div>
      <button @click="loadTopics" class="flex items-center gap-2 px-4 py-2 text-sm border border-slate-600 text-slate-300 hover:bg-slate-800 rounded-xl transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
        Refresh
      </button>
    </div>

    <!-- Not clustered warning -->
    <div v-if="notClustered" class="mt-6 bg-amber-500/10 border border-amber-500/40 rounded-2xl p-8 text-center">
      <svg class="w-14 h-14 mx-auto mb-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
      <h3 class="text-xl font-bold text-amber-300 mb-2">Clustering Belum Dieksekusi</h3>
      <p class="text-slate-400 mb-6">Kembali ke halaman <strong class="text-white">Clustering K-Means</strong>, pilih K, lalu tekan <strong class="text-white">"Lakukan Clustering"</strong> terlebih dahulu.</p>
      <button @click="router.push('/clustering')" class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white font-medium rounded-xl transition-all">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
        Kembali ke Clustering
      </button>
    </div>

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
      <span class="ml-3 text-lg">Mengekstrak topik...</span>
    </div>

    <!-- Global Insight Summary -->
    <div v-if="clusterSummary && !isLoading && !notClustered" class="mt-4 bg-emerald-900/20 border border-emerald-500/30 rounded-2xl p-4 flex flex-wrap gap-6">
      <div class="text-center">
        <p class="text-xs text-slate-400 mb-1">Total Cluster</p>
        <p class="text-2xl font-bold text-emerald-400">{{ clusterSummary.total }}</p>
      </div>
    </div>

    <!-- Clusters -->
    <div v-if="topicsData && !isLoading && !notClustered" class="mt-4 space-y-8">
      <div v-for="(data, clusterId) in topicsData" :key="clusterId"
        class="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6">
        <h3 class="text-lg font-bold text-white mb-4 flex items-center">
          <span class="inline-block w-3 h-3 rounded-full mr-2" :style="{ backgroundColor: getColor(clusterId) }"></span>
          Cluster {{ clusterId }}
        </h3>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Word Table -->
          <div class="overflow-x-auto rounded-xl border border-slate-700/50">
            <table class="w-full text-left text-sm text-slate-400">
              <thead class="text-xs text-slate-300 uppercase bg-slate-800/50">
                <tr>
                  <th class="px-4 py-3 border-b border-slate-700">#</th>
                  <th class="px-4 py-3 border-b border-slate-700">Kata</th>
                  <th class="px-4 py-3 border-b border-slate-700">Skor TF-IDF</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(w, idx) in data.words" :key="idx" class="border-b border-slate-700/50 hover:bg-slate-800/30">
                  <td class="px-4 py-2 text-slate-500">{{ idx + 1 }}</td>
                  <td class="px-4 py-2 text-slate-200 font-medium">{{ w.word }}</td>
                  <td class="px-4 py-2 text-emerald-400 font-mono">{{ w.score.toFixed(4) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Bar Chart -->
          <div style="height: 280px;">
            <Bar :data="data.chartData" :options="barOptions" />
          </div>
        </div>

        <!-- CSS Word Cloud -->
        <div class="mt-4 p-4 bg-slate-800/40 rounded-xl border border-slate-700/40">
          <p class="text-xs text-slate-500 mb-3">Word Cloud (ukuran proporsional dengan skor)</p>
          <div class="flex flex-wrap gap-2 items-center">
            <span
              v-for="w in data.words" :key="w.word"
              class="px-3 py-1 rounded-full font-medium transition-all hover:scale-110 cursor-default"
              :style="{
                fontSize: `${Math.max(11, Math.min(26, 11 + (w.score / Math.max(...data.words.map(x => x.score))) * 15))}px`,
                opacity: 0.5 + (w.score / Math.max(...data.words.map(x => x.score))) * 0.5,
                backgroundColor: getColor(clusterId).replace('0.8', '0.15'),
                color: getColor(clusterId).replace('0.8', '1')
              }"
            >
              {{ w.word }}
            </span>
          </div>
        </div>
      </div>
    </div>
    <PipelineNav :current="4" />
  </div>
</template>
