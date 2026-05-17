<script setup>
import { computed } from 'vue'
import { useAppStore } from '../store'
import PipelineNav from '../components/PipelineNav.vue'

const store = useAppStore()

const report = computed(() => store.evaluationReport)
const cm = computed(() => store.confusionMatrix)
const cmLabels = computed(() => store.confusionMatrixLabels)
const testAcc = computed(() => store.testAccuracy)
const trainAcc = computed(() => store.trainAccuracy)

const fmt = (num) => num !== undefined && num !== null ? Number(num).toFixed(4) : '-'
const pct = (num) => num !== undefined && num !== null ? (Number(num) * 100).toFixed(2) + '%' : '-'

const labelName = (k) => ({ 0: 'Negatif', 1: 'Netral', 2: 'Positif' }[k] || `Kelas ${k}`)

const classesList = computed(() => {
  if (!report.value) return []
  return Object.keys(report.value).filter(k => !['accuracy', 'macro avg', 'weighted avg'].includes(k))
})

// Confusion matrix cell coloring
const cmMax = computed(() => {
  if (!cm.value) return 1
  return Math.max(...cm.value.flat())
})
const cmCellStyle = (val, row, col) => {
  const intensity = val / cmMax.value
  const isCorrect = row === col
  if (isCorrect) return `background: rgba(16, 185, 129, ${Math.max(0.1, intensity * 0.8)}); color: ${intensity > 0.4 ? 'white' : '#10b981'};`
  return `background: rgba(239, 68, 68, ${Math.max(0.03, intensity * 0.5)}); color: ${intensity > 0.4 ? 'white' : '#ef4444'};`
}

const overfitWarning = computed(() => {
  if (!trainAcc.value || !testAcc.value) return null
  const diff = trainAcc.value - testAcc.value
  if (diff > 0.15) return 'Selisih Train vs Test besar → kemungkinan overfitting.'
  return null
})
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-white mb-1">Evaluasi Model Random Forest</h1>
    <p class="text-slate-400">Performa model klasifikasi sentimen berdasarkan data testing.</p>

    <div v-if="!report" class="mt-8 p-6 bg-amber-500/10 border border-amber-500/40 rounded-2xl text-amber-400 text-center">
      <svg class="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      Belum ada hasil evaluasi. Silakan latih model di halaman <strong>Training Model</strong> terlebih dahulu.
    </div>

    <div v-else class="mt-6 space-y-6">

      <!-- Accuracy Cards (Train vs Test) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6 text-center">
          <p class="text-slate-400 text-sm mb-1">Train Accuracy</p>
          <p class="text-4xl font-black text-blue-400">{{ pct(trainAcc) }}</p>
          <p class="text-xs text-slate-500 mt-1">(Data latih)</p>
        </div>
        <div class="bg-slate-900/60 border border-emerald-500/40 rounded-2xl p-6 text-center">
          <p class="text-slate-400 text-sm mb-1">Test Accuracy</p>
          <p class="text-4xl font-black text-emerald-400">{{ pct(testAcc) }}</p>
          <p class="text-xs text-slate-500 mt-1">(Data testing)</p>
        </div>
        <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6 text-center">
          <p class="text-slate-400 text-sm mb-1">Weighted F1-Score</p>
          <p class="text-4xl font-black text-purple-400">{{ fmt(report['weighted avg']?.['f1-score']) }}</p>
          <p class="text-xs text-slate-500 mt-1">(Bobot per kelas)</p>
        </div>
      </div>

      <!-- Overfit Warning -->
      <div v-if="overfitWarning" class="p-4 bg-red-500/10 border border-red-500/40 rounded-xl text-red-400 flex items-center">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        {{ overfitWarning }}
      </div>

      <!-- Classification Report Table -->
      <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
        <h3 class="text-slate-200 font-semibold mb-4">Classification Report</h3>
        <div class="overflow-x-auto rounded-xl border border-slate-700/50">
          <table class="w-full text-left text-sm text-slate-400">
            <thead class="text-xs text-slate-300 uppercase bg-slate-800/50">
              <tr>
                <th class="px-6 py-4 border-b border-slate-700">Kelas</th>
                <th class="px-6 py-4 border-b border-slate-700">Precision</th>
                <th class="px-6 py-4 border-b border-slate-700">Recall</th>
                <th class="px-6 py-4 border-b border-slate-700">F1-Score</th>
                <th class="px-6 py-4 border-b border-slate-700">Support</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="key in classesList" :key="key" class="border-b border-slate-700/50 hover:bg-slate-800/30">
                <td class="px-6 py-4 font-bold text-slate-200">{{ labelName(Number(key)) }}</td>
                <td class="px-6 py-4">{{ fmt(report[key].precision) }}</td>
                <td class="px-6 py-4">{{ fmt(report[key].recall) }}</td>
                <td class="px-6 py-4">{{ fmt(report[key]['f1-score']) }}</td>
                <td class="px-6 py-4">{{ report[key].support }}</td>
              </tr>
            </tbody>
            <tfoot class="bg-slate-800/30">
              <tr class="border-t border-slate-600">
                <td class="px-6 py-4 font-bold text-slate-200">Macro Avg</td>
                <td class="px-6 py-4">{{ fmt(report['macro avg'].precision) }}</td>
                <td class="px-6 py-4">{{ fmt(report['macro avg'].recall) }}</td>
                <td class="px-6 py-4">{{ fmt(report['macro avg']['f1-score']) }}</td>
                <td class="px-6 py-4">{{ report['macro avg'].support }}</td>
              </tr>
              <tr>
                <td class="px-6 py-4 font-bold text-slate-200">Weighted Avg</td>
                <td class="px-6 py-4">{{ fmt(report['weighted avg'].precision) }}</td>
                <td class="px-6 py-4">{{ fmt(report['weighted avg'].recall) }}</td>
                <td class="px-6 py-4">{{ fmt(report['weighted avg']['f1-score']) }}</td>
                <td class="px-6 py-4">{{ report['weighted avg'].support }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <!-- Confusion Matrix Heatmap -->
      <div v-if="cm && cmLabels" class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
        <h3 class="text-slate-200 font-semibold mb-2">Confusion Matrix</h3>
        <p class="text-sm text-slate-400 mb-6">Hijau = prediksi benar. Merah = prediksi salah.</p>

        <div class="overflow-x-auto">
          <table class="mx-auto text-sm">
            <thead>
              <tr>
                <th class="px-4 py-2 text-slate-400 text-xs"></th>
                <th class="px-1 py-2 text-slate-400 text-xs text-center" colspan="1">← Predicted →</th>
              </tr>
              <tr>
                <th class="px-4 py-2 text-slate-400 text-xs">Actual ↓</th>
                <th v-for="lbl in cmLabels" :key="lbl" class="px-6 py-3 text-slate-300 font-semibold text-center">{{ labelName(lbl) }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rIdx) in cm" :key="rIdx">
                <td class="px-4 py-3 text-slate-300 font-semibold text-right pr-4">{{ labelName(cmLabels[rIdx]) }}</td>
                <td
                  v-for="(val, cIdx) in row" :key="cIdx"
                  class="px-6 py-4 text-center font-bold text-lg rounded-lg m-1"
                  :style="cmCellStyle(val, rIdx, cIdx)"
                >
                  {{ val }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Auto Insight -->
      <div class="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
        <h3 class="text-slate-200 font-semibold mb-3">Insight Evaluasi</h3>
        <ul class="space-y-2 text-slate-300 text-sm">
          <li class="flex items-start"><span class="text-emerald-400 mr-2">•</span>Test Accuracy: <strong class="text-emerald-400 mx-1">{{ pct(testAcc) }}</strong></li>
          <li class="flex items-start"><span class="text-blue-400 mr-2">•</span>Train Accuracy: <strong class="text-blue-400 mx-1">{{ pct(trainAcc) }}</strong> (evaluasi pada data training)</li>
          <li class="flex items-start"><span class="text-slate-400 mr-2">•</span>Evaluasi dilakukan pada data testing (bukan data training)</li>
          <li class="flex items-start"><span class="text-slate-400 mr-2">•</span>Jika selisih Train vs Test besar → kemungkinan <strong class="text-red-400">overfitting</strong></li>
          <li class="flex items-start"><span class="text-slate-400 mr-2">•</span>Perhatikan confusion matrix untuk melihat kesalahan antar kelas</li>
          <li class="flex items-start"><span class="text-slate-400 mr-2">•</span>Jika kelas "Netral" sering salah → indikasi <strong class="text-amber-400">data imbalance</strong></li>
        </ul>
      </div>

    </div>
    <PipelineNav :current="7" />
</div>
</template>
