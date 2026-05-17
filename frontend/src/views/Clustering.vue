<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAppStore } from '../store'
import { useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, BarElement, Title, Tooltip, Legend, Filler
} from 'chart.js'
import { Line, Bar } from 'vue-chartjs'
import PipelineNav from '../components/PipelineNav.vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler)

const store = useAppStore()
const router = useRouter()

const isLoading = ref(false)
const isApplying = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const clusteringApplied = ref(false)
const clusterResult = ref(null) // distribution after apply

const evaluationData = ref(null)
const bestK = ref(3)

const chartElbow = ref(null)
const chartSilhouette = ref(null)
const chartCalinski = ref(null)
const chartDistribution = ref(null)

const lineOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { labels: { color: '#cbd5e1' } } },
  scales: {
    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
  }
}
const barOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
  }
}

const loadEvaluation = async () => {
  if (!store.sessionId) {
    errorMsg.value = 'Sesi tidak ditemukan. Lakukan input data dan preprocessing terlebih dahulu.'
    return
  }
  isLoading.value = true
  errorMsg.value = ''
  try {
    const res = await axios.post('http://localhost:8000/api/cluster/evaluate', {
      session_id: store.sessionId, max_k: 10
    })
    evaluationData.value = res.data.evaluation
    const labels = evaluationData.value.map(d => `K=${d.k}`)
    const inertias = evaluationData.value.map(d => d.inertia)
    const silhouettes = evaluationData.value.map(d => d.silhouette)
    const calinskis = evaluationData.value.map(d => d.calinski)

    const bestIdx = silhouettes.indexOf(Math.max(...silhouettes))
    bestK.value = evaluationData.value[bestIdx].k

    chartElbow.value = {
      labels,
      datasets: [{ label: 'Inertia', backgroundColor: 'rgba(16,185,129,0.1)', borderColor: '#10b981', pointBackgroundColor: '#10b981', data: inertias, tension: 0.3, fill: true }]
    }
    chartSilhouette.value = {
      labels,
      datasets: [{ label: 'Silhouette Score', backgroundColor: 'rgba(59,130,246,0.1)', borderColor: '#3b82f6', pointBackgroundColor: '#3b82f6', data: silhouettes, tension: 0.3, fill: true }]
    }
    chartCalinski.value = {
      labels,
      datasets: [{ label: 'Calinski-Harabasz', backgroundColor: 'rgba(245,158,11,0.1)', borderColor: '#f59e0b', pointBackgroundColor: '#f59e0b', data: calinskis, tension: 0.3, fill: true }]
    }
  } catch (err) {
    errorMsg.value = 'Gagal evaluasi: ' + (err.response?.data?.detail || err.message)
  } finally {
    isLoading.value = false
  }
}

const applyClustering = async () => {
  isApplying.value = true
  try {
    const res = await axios.post('http://localhost:8000/api/cluster/apply', {
      session_id: store.sessionId, k: bestK.value
    })
    clusterResult.value = res.data
    clusteringApplied.value = true
    successMsg.value = `Clustering K=${bestK.value} berhasil! Data terbagi ke ${Object.keys(res.data.distribution).length} cluster.`
    // Build distribution chart
    const dist = res.data.distribution
    chartDistribution.value = {
      labels: Object.keys(dist).map(k => `Cluster ${k}`),
      datasets: [{ label: 'Jumlah Data', backgroundColor: ['#10b981','#3b82f6','#f59e0b','#ef4444','#a855f7','#ec4899'], data: Object.values(dist), borderRadius: 6 }]
    }
  } catch (err) {
    errorMsg.value = 'Gagal clustering: ' + (err.response?.data?.detail || err.message)
  } finally {
    isApplying.value = false
  }
}

onMounted(() => { if (store.sessionId) loadEvaluation() })
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-white mb-1">Clustering K-Means</h1>
    <p class="text-slate-400">Evaluasi metrik Elbow, Silhouette, & Calinski-Harabasz → terapkan K terbaik.</p>

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
      <span class="ml-3 text-lg">Mengevaluasi K=2 sampai K=10...</span>
    </div>

    <div v-if="chartElbow && !isLoading" class="mt-6 space-y-6">

      <!-- Success Banner -->
      <div v-if="clusteringApplied" class="p-4 bg-emerald-500/10 border border-emerald-500/50 rounded-xl flex items-center justify-between">
        <div class="flex items-center text-emerald-400">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          Berhasil membuat <strong class="mx-1">{{ bestK }} cluster</strong>! Lanjut ke Topik Cluster.
        </div>
        <button @click="router.push('/topik-cluster')" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white text-sm font-medium rounded-lg transition-colors flex items-center">
          Topik Cluster <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
        </button>
      </div>

      <!-- Metrics Table -->
      <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
        <h3 class="text-slate-200 font-semibold mb-4">Tabel Metrik Evaluasi</h3>
        <div class="overflow-x-auto rounded-xl border border-slate-700/50">
          <table class="w-full text-left text-sm text-slate-400">
            <thead class="text-xs text-slate-300 uppercase bg-slate-800/50">
              <tr>
                <th class="px-4 py-3 border-b border-slate-700">K</th>
                <th class="px-4 py-3 border-b border-slate-700">Inertia (Elbow)</th>
                <th class="px-4 py-3 border-b border-slate-700">Silhouette Score</th>
                <th class="px-4 py-3 border-b border-slate-700">Calinski-Harabasz</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in evaluationData" :key="row.k"
                class="border-b border-slate-700/50 transition-colors"
                :class="row.k === bestK ? 'bg-emerald-500/10' : 'hover:bg-slate-800/30'">
                <td class="px-4 py-3 font-bold" :class="row.k === bestK ? 'text-emerald-400' : 'text-slate-200'">
                  {{ row.k }} <span v-if="row.k === bestK" class="ml-1 text-xs bg-emerald-500/20 px-1.5 py-0.5 rounded-full">rekomendasi</span>
                </td>
                <td class="px-4 py-3">{{ row.inertia.toFixed(2) }}</td>
                <td class="px-4 py-3">{{ row.silhouette.toFixed(4) }}</td>
                <td class="px-4 py-3">{{ row.calinski.toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 3 Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 relative" style="height: 280px;">
          <div class="absolute top-0 left-1/4 w-1/2 h-px bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50"></div>
          <h3 class="text-slate-200 text-sm font-medium mb-3 text-center">Elbow Method (Inertia)</h3>
          <div style="height: 210px;"><Line :data="chartElbow" :options="lineOptions" /></div>
        </div>
        <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 relative" style="height: 280px;">
          <div class="absolute top-0 left-1/4 w-1/2 h-px bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-50"></div>
          <h3 class="text-slate-200 text-sm font-medium mb-3 text-center">Silhouette Score</h3>
          <div style="height: 210px;"><Line :data="chartSilhouette" :options="lineOptions" /></div>
        </div>
        <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 relative" style="height: 280px;">
          <div class="absolute top-0 left-1/4 w-1/2 h-px bg-gradient-to-r from-transparent via-amber-500 to-transparent opacity-50"></div>
          <h3 class="text-slate-200 text-sm font-medium mb-3 text-center">Calinski-Harabasz Index</h3>
          <div style="height: 210px;"><Line :data="chartCalinski" :options="lineOptions" /></div>
        </div>
      </div>

      <!-- Apply Action -->
      <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
        <div class="flex flex-col md:flex-row md:items-end gap-6">
          <div class="flex-1">
            <div class="flex justify-between items-center mb-2">
              <label class="text-sm font-medium text-slate-300">Pilih K</label>
              <span class="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-full">Rekomendasi: K={{ bestK }}</span>
            </div>
            <input type="range" min="2" max="10" v-model="bestK" class="w-full accent-emerald-500 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer" />
            <div class="flex justify-between text-xs text-slate-500 mt-2">
              <span>K=2</span>
              <span class="text-emerald-400 font-bold text-sm">K = {{ bestK }}</span>
              <span>K=10</span>
            </div>
          </div>
          <div class="text-center">
            <button @click="applyClustering" :disabled="isApplying"
              class="px-8 py-3 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-white font-medium rounded-xl shadow-lg transition-all disabled:opacity-50">
              <span v-if="!isApplying" class="flex items-center">
                <AppIcon name="play" class="w-4 h-4 mr-2" />
                Lakukan Clustering
              </span>
              <span v-else class="flex items-center"><svg class="animate-spin mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>Memproses...</span>
            </button>
            <p class="text-xs text-slate-500 mt-2">Wajib klik sebelum ke Topik Cluster</p>
          </div>
        </div>
      </div>

      <!-- Cluster Result & Distribution -->
      <div v-if="clusterResult && chartDistribution" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
          <h3 class="text-slate-200 font-semibold mb-4">Distribusi Cluster</h3>
          <div style="height: 220px;"><Bar :data="chartDistribution" :options="barOptions" /></div>
        </div>
        <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
          <h3 class="text-slate-200 font-semibold mb-4">ℹ️ Ringkasan</h3>
          <ul class="space-y-3">
            <li class="flex justify-between items-center border-b border-slate-700/50 pb-2">
              <span class="text-slate-400">Total Data</span>
              <span class="text-slate-200 font-bold">{{ clusterResult.preview?.length ? `${clusterResult.preview.length}+` : '-' }}</span>
            </li>
            <li class="flex justify-between items-center border-b border-slate-700/50 pb-2">
              <span class="text-slate-400">Jumlah Cluster</span>
              <span class="text-emerald-400 font-bold">{{ bestK }}</span>
            </li>
            <li v-for="(count, cid) in clusterResult.distribution" :key="cid" class="flex justify-between items-center">
              <span class="text-slate-400">Cluster {{ cid }}</span>
              <span class="bg-slate-800 px-3 py-1 rounded-full text-slate-200 text-sm">{{ count }} data</span>
            </li>
          </ul>
        </div>
      </div>

    </div>
    <PipelineNav :current="3" />
</div>
</template>
