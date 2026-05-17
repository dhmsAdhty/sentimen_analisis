<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAppStore } from '../store'
import { useRouter } from 'vue-router'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend
} from 'chart.js'
import { Bar } from 'vue-chartjs'
import PipelineNav from '../components/PipelineNav.vue'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const store = useAppStore()
const router = useRouter()

const isTraining = ref(false)
const isLoadingInfo = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const dataInfo = ref(null)
const maxFeatures = ref(1000)
const testSize = ref(20)

const labelDistChart = ref(null)
const barOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
  }
}

const labelName = (k) => ({ 0: 'Negatif', 1: 'Netral', 2: 'Positif' }[k] || k)
const labelBgColor = (k) => ({ 0: 'rgba(239,68,68,0.7)', 1: 'rgba(148,163,184,0.7)', 2: 'rgba(16,185,129,0.7)' }[k] || 'rgba(100,116,139,0.7)')

const loadDataInfo = async () => {
  if (!store.sessionId) return
  isLoadingInfo.value = true
  try {
    const res = await axios.post('http://localhost:8000/api/data/info', { session_id: store.sessionId })
    dataInfo.value = res.data
    if (res.data.label_distribution && Object.keys(res.data.label_distribution).length > 0) {
      const dist = res.data.label_distribution
      labelDistChart.value = {
        labels: Object.keys(dist).map(k => labelName(Number(k))),
        datasets: [{
          label: 'Jumlah Data',
          backgroundColor: Object.keys(dist).map(k => labelBgColor(Number(k))),
          data: Object.values(dist),
          borderRadius: 6
        }]
      }
    }
  } catch {}
  finally { isLoadingInfo.value = false }
}

const handleTrain = async () => {
  if (!store.sessionId) {
    errorMsg.value = 'Sesi tidak ditemukan.'
    return
  }
  isTraining.value = true
  errorMsg.value = ''
  try {
    const response = await axios.post('http://localhost:8000/api/model/train', {
      session_id: store.sessionId,
      max_features: maxFeatures.value,
      test_size: testSize.value / 100
    })
    store.setTrainingResults({
      report: response.data.classification_report,
      cm: response.data.confusion_matrix,
      cmLabels: response.data.confusion_matrix_labels,
      testAcc: response.data.test_accuracy,
      trainAcc: response.data.train_accuracy
    })
    successMsg.value = `Model berhasil dilatih! Akurasi: ${(response.data.test_accuracy * 100).toFixed(1)}%`
    router.push('/evaluasi')
  } catch (error) {
    errorMsg.value = 'Gagal melatih model: ' + (error.response?.data?.detail || error.message)
  } finally {
    isTraining.value = false
  }
}

onMounted(() => { loadDataInfo() })
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-white mb-1">Training Model (Random Forest)</h1>
    <p class="text-slate-400">Latih model Machine Learning berbasis TF-IDF + Random Forest dengan data yang telah dilabeli.</p>

    <div v-if="errorMsg" class="mt-4 p-4 bg-red-500/10 border border-red-500/50 rounded-xl text-red-400 flex items-center gap-2">
      <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      {{ errorMsg }}
    </div>
    <div v-if="successMsg" class="mt-4 p-4 bg-emerald-500/10 border border-emerald-500/50 rounded-xl text-emerald-400 flex items-center gap-2">
      <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      {{ successMsg }}
    </div>

    <!-- Info Cards -->
    <div v-if="dataInfo" class="mt-6 grid grid-cols-3 gap-4">
      <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 text-center">
        <p class="text-slate-400 text-sm mb-1">Jumlah Data</p>
        <p class="text-3xl font-bold text-white">{{ dataInfo.total_rows }}</p>
      </div>
      <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 text-center">
        <p class="text-slate-400 text-sm mb-1">Jumlah Kolom</p>
        <p class="text-3xl font-bold text-white">{{ dataInfo.total_columns }}</p>
      </div>
      <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 text-center">
        <p class="text-slate-400 text-sm mb-1">Missing Label</p>
        <p class="text-3xl font-bold" :class="dataInfo.missing_label > 0 ? 'text-red-400' : 'text-emerald-400'">{{ dataInfo.missing_label }}</p>
      </div>
    </div>

    <!-- Label Distribution Chart -->
    <div v-if="labelDistChart" class="mt-4 bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
      <h3 class="text-slate-200 font-semibold mb-4">Distribusi Label Sentimen</h3>
      <div style="height: 180px;">
        <Bar :data="labelDistChart" :options="barOptions" />
      </div>
    </div>

    <!-- Training Config -->
    <div class="mt-4 bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
      <h3 class="text-slate-200 font-semibold mb-6">Parameter TF-IDF & Training</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
        <div>
          <label class="block text-sm text-slate-400 mb-2">Max Features (TF-IDF): <span class="text-emerald-400 font-bold">{{ maxFeatures }}</span></label>
          <input type="range" min="500" max="5000" step="100" v-model="maxFeatures" class="w-full accent-emerald-500 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer" />
          <div class="flex justify-between text-xs text-slate-500 mt-1"><span>500</span><span>5000</span></div>
        </div>
        <div>
          <label class="block text-sm text-slate-400 mb-2">Test Size: <span class="text-emerald-400 font-bold">{{ testSize }}%</span></label>
          <input type="range" min="10" max="40" step="5" v-model="testSize" class="w-full accent-emerald-500 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer" />
          <div class="flex justify-between text-xs text-slate-500 mt-1"><span>10%</span><span>40%</span></div>
        </div>
      </div>
      <div class="flex flex-col items-center pt-4 border-t border-slate-700/50">
        <p class="text-slate-400 text-sm text-center mb-4">Random Forest (100 estimators) dengan class_weight="balanced" untuk menangani data imbalance.</p>
        <button
          @click="handleTrain"
          :disabled="isTraining || !store.sessionId"
          class="flex items-center justify-center w-full max-w-sm px-6 py-4 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-lg"
        >
          <svg v-if="isTraining" class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
          <span v-if="!isTraining">Latih Model Random Forest</span>
          <span v-else>Melatih model...</span>
        </button>
        <p v-if="store.evaluationReport" class="mt-3 text-sm text-emerald-400">Model sudah dilatih. Lihat hasil di halaman Evaluasi.</p>
      </div>
    </div>
    <PipelineNav :current="6" />
</div>
</template>
