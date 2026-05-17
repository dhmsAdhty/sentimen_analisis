<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../store'
import axios from 'axios'

const router = useRouter()
const store = useAppStore()
const apiOnline = ref(null) // null = checking

const checkApi = async () => {
  try {
    await axios.get('http://localhost:8000/', { timeout: 3000 })
    apiOnline.value = true
  } catch {
    apiOnline.value = false
  }
}

const pipeline = [
  { step: '01', label: 'Input Data',    path: '/input-data',       desc: 'Upload CSV/Excel atau scraping Google Maps',    color: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400',   icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12' },
  { step: '02', label: 'Preprocessing', path: '/preprocessing',    desc: 'Lowercase, stopword removal, stemming Sastrawi', color: 'bg-cyan-500/15 border-cyan-500/30 text-cyan-400',            icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
  { step: '03', label: 'Clustering',    path: '/clustering',       desc: 'K-Means + evaluasi Elbow & Silhouette',          color: 'bg-violet-500/15 border-violet-500/30 text-violet-400',      icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
  { step: '04', label: 'Topik Cluster', path: '/topik-cluster',    desc: 'Kata kunci tiap cluster via TF-IDF',             color: 'bg-amber-500/15 border-amber-500/30 text-amber-400',         icon: 'M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z' },
  { step: '05', label: 'Labeling',      path: '/labeling',         desc: 'Pelabelan sentimen berbasis lexicon',            color: 'bg-rose-500/15 border-rose-500/30 text-rose-400',            icon: 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z' },
  { step: '06', label: 'Training',      path: '/training',         desc: 'Random Forest dengan TF-IDF vectorizer',        color: 'bg-green-500/15 border-green-500/30 text-green-400',         icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z' },
  { step: '07', label: 'Evaluasi',      path: '/evaluasi',         desc: 'Confusion matrix & classification report',      color: 'bg-blue-500/15 border-blue-500/30 text-blue-400',            icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { step: '08', label: 'Insight',       path: '/insight',          desc: 'Ringkasan distribusi sentimen & cluster',        color: 'bg-yellow-500/15 border-yellow-500/30 text-yellow-400',      icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' },
  { step: '09', label: 'Klasifikasi',   path: '/klasifikasi-baru', desc: 'Prediksi sentimen teks baru atau batch file',    color: 'bg-fuchsia-500/15 border-fuchsia-500/30 text-fuchsia-400',  icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' },
]

const animatedWords = ['AI & NLP', 'K-Means Clustering', 'Random Forest', 'TF-IDF Vectorizer']
const currentWordIndex = ref(0)
let wordInterval

onMounted(() => {
  checkApi()
  wordInterval = setInterval(() => {
    currentWordIndex.value = (currentWordIndex.value + 1) % animatedWords.length
  }, 2500)
})

import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (wordInterval) clearInterval(wordInterval)
})
</script>

<template>
  <div class="space-y-14">

    <!-- ══════════ HERO ══════════ -->
    <section class="py-10 md:py-16 relative flex flex-col-reverse lg:flex-row items-center justify-between gap-10 lg:gap-12">
      <!-- Glow blob behind text -->
      <div class="absolute inset-0 flex justify-center lg:justify-start items-start pt-8 pointer-events-none">
        <div class="w-[480px] h-52 bg-emerald-500/10 rounded-full blur-[80px] animate-blob"></div>
      </div>

      <!-- Left Text -->
      <div class="lg:w-1/2 text-center lg:text-left relative z-10 flex flex-col items-center lg:items-start">
        
        <!-- Badge -->
        <div class="animate-fade-up relative inline-flex items-center gap-2 px-4 py-1.5 mb-6 rounded-full
          border border-emerald-500/30 bg-emerald-500/10 backdrop-blur-md shadow-[0_0_15px_rgba(16,185,129,0.15)] text-emerald-400 text-xs font-semibold uppercase tracking-widest">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          Sistem Analisis Sentimen &amp; Clustering
        </div>

        <!-- Title -->
        <h1 class="animate-fade-up delay-100 relative text-4xl md:text-5xl lg:text-6xl font-black text-white leading-tight mb-4 flex flex-col items-center lg:items-start tracking-tight">
          <span class="bg-clip-text text-transparent bg-gradient-to-br from-white via-slate-100 to-slate-400 drop-shadow-sm">Analisis Sentimen</span>
          <div class="flex flex-col md:flex-row items-center justify-center lg:justify-start md:gap-3 mt-1 md:mt-2 w-full">
            <span>Berbasis</span>
            <span class="relative h-[1.3em] w-[280px] md:w-[340px] lg:w-[420px] text-center lg:text-left overflow-hidden">
              <transition name="text-slide">
                <span :key="currentWordIndex" class="absolute left-0 top-0 w-full text-center lg:text-left bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-400">
                  {{ animatedWords[currentWordIndex] }}
                </span>
              </transition>
            </span>
          </div>
        </h1>

        <!-- Sub -->
        <p class="animate-fade-up delay-200 relative text-slate-400 text-base lg:text-lg max-w-lg leading-relaxed mb-8">
          Kelompokkan ulasan secara otomatis menggunakan K-Means,
          lalu klasifikasikan sentimen dengan model Random Forest.
        </p>

        <!-- CTA -->
        <div class="animate-fade-up delay-300 relative flex flex-wrap items-center justify-center lg:justify-start gap-3 w-full">
          <button @click="router.push('/input-data')"
            class="flex items-center gap-2 px-7 py-3.5 bg-gradient-to-r from-emerald-500 to-green-500
              hover:from-emerald-400 hover:to-green-400 text-white font-semibold rounded-xl
              shadow-lg shadow-emerald-500/25 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-emerald-500/40">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            Mulai Analisis
          </button>
          <button @click="router.push('/klasifikasi-baru')"
            class="flex items-center gap-2 px-7 py-3.5 bg-slate-800 hover:bg-slate-700
              border border-slate-700 hover:border-slate-600 text-slate-200 font-semibold rounded-xl
              transition-all duration-200 hover:-translate-y-0.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            Prediksi Langsung
          </button>
        </div>

        <!-- API status -->
        <div class="animate-fade-in delay-500 relative mt-6 text-xs text-center lg:text-left w-full">
          <span v-if="apiOnline === null" class="text-slate-500">Memeriksa koneksi API…</span>
          <span v-else-if="apiOnline" class="inline-flex items-center gap-1.5 text-emerald-400">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Backend API terhubung
          </span>
          <span v-else class="inline-flex items-center gap-1.5 text-red-400">
            <span class="w-1.5 h-1.5 rounded-full bg-red-400"></span>
            Backend tidak terdeteksi — jalankan <code class="font-mono mx-1">uvicorn main:app</code>
          </span>
        </div>
      </div>

      <!-- 3D AI Character (Right) -->
      <div class="lg:w-1/2 relative flex justify-center z-10 animate-fade-in delay-400 mt-8 lg:mt-0">
        <!-- Inner glow aura for the robot -->
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div class="w-64 h-64 bg-emerald-500/20 rounded-full blur-[80px] animate-pulse"></div>
        </div>
        <!-- 3D Image floating -->
        <img src="/3d-ai-transparent.png" alt="3D AI Robot" 
          class="relative w-[280px] md:w-[380px] lg:w-[480px] object-contain animate-float drop-shadow-[0_10px_40px_rgba(16,185,129,0.3)]" />
      </div>
    </section>

    <!-- ══════════ SESSION BANNER ══════════ -->
    <section v-if="store.sessionId"
      class="animate-fade-up delay-400 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4
        p-5 rounded-2xl bg-emerald-900/30 backdrop-blur-xl border border-emerald-500/30 shadow-[0_8px_30px_rgb(0,0,0,0.12)]">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
          <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div>
          <p class="text-sm font-semibold text-emerald-400">Sesi aktif tersedia</p>
          <p class="text-xs text-slate-500 font-mono mt-0.5 truncate max-w-xs">{{ store.sessionId }}</p>
        </div>
      </div>
      <div class="flex gap-2 flex-shrink-0">
        <button @click="router.push('/preprocessing')"
          class="px-4 py-2 text-xs font-semibold text-emerald-400 border border-emerald-500/30
            bg-emerald-500/10 hover:bg-emerald-500/20 rounded-lg transition-all">
          Lanjutkan →
        </button>
        <button @click="store.clearSession()"
          class="px-4 py-2 text-xs font-semibold text-slate-400 border border-slate-700
            hover:bg-slate-800 rounded-lg transition-all">
          Reset
        </button>
      </div>
    </section>

    <!-- ══════════ PIPELINE ══════════ -->
    <section>
      <div class="mb-6 animate-fade-up delay-200">
        <h2 class="text-2xl font-bold text-white mb-1">Pipeline Analisis</h2>
        <p class="text-slate-400 text-sm">Ikuti 9 tahapan berikut secara berurutan.</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <button
          v-for="(item, index) in pipeline"
          :key="item.step"
          :style="{ animationDelay: `${300 + index * 50}ms` }"
          @click="router.push(item.path)"
          class="animate-fade-up group relative flex items-center gap-4 p-5 rounded-2xl border bg-slate-900/40 backdrop-blur-md shadow-lg shadow-black/20
            hover:bg-slate-800/60 hover:backdrop-blur-xl transition-all duration-300 hover:-translate-y-1 text-left overflow-hidden"
          :class="item.color.split(' ').slice(1).join(' ').replace(/text-\S+/, '').trim() + ' border-white/5 hover:border-white/10'"
        >
          <!-- Accent Line on Hover -->
          <div class="absolute inset-y-0 left-0 w-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300" 
            :class="item.color.split(' ')[0]"></div>
          <!-- Step icon box -->
          <div class="flex-shrink-0 w-10 h-10 rounded-xl border flex items-center justify-center"
            :class="item.color">
            <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"/>
            </svg>
          </div>
          <!-- Text -->
          <div class="flex-1 min-w-0">
            <div class="flex items-baseline gap-2">
              <span class="text-[10px] font-mono font-bold text-slate-600">{{ item.step }}</span>
              <span class="text-sm font-semibold text-slate-200 group-hover:text-white transition-colors">{{ item.label }}</span>
            </div>
            <p class="text-xs text-slate-500 mt-0.5 leading-tight truncate">{{ item.desc }}</p>
          </div>
          <!-- Arrow -->
          <svg class="w-4 h-4 text-slate-600 group-hover:text-slate-400 group-hover:translate-x-0.5 transition-all duration-200 flex-shrink-0"
            fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    </section>

    <!-- ══════════ FITUR ══════════ -->
    <section>
      <div class="mb-6 animate-fade-up delay-400">
        <h2 class="text-2xl font-bold text-white mb-1">Teknologi yang Digunakan</h2>
        <p class="text-slate-400 text-sm">Stack NLP & Machine Learning untuk Bahasa Indonesia.</p>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="(feat, index) in [
          { title: 'K-Means Clustering', color: 'from-emerald-500 to-teal-500', shadow: 'shadow-emerald-500/15',
            icon: 'M13 10V3L4 14h7v7l9-11h-7z',
            desc: 'Evaluasi K terbaik via Elbow, Silhouette Score & Calinski-Harabasz Index secara otomatis.' },
          { title: 'Random Forest', color: 'from-blue-500 to-indigo-500', shadow: 'shadow-blue-500/15',
            icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z',
            desc: 'Klasifikasi sentimen 3 kelas (Positif/Netral/Negatif) dengan class_weight balanced.' },
          { title: 'NLP Preprocessing', color: 'from-violet-500 to-purple-600', shadow: 'shadow-violet-500/15',
            icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
            desc: 'Pipeline lengkap dengan PySastrawi stemmer & stopword Bahasa Indonesia.' },
        ]" :key="feat.title"
          :style="{ animationDelay: `${500 + index * 100}ms` }"
          class="relative p-[1px] rounded-2xl overflow-hidden animate-fade-up group shadow-xl shadow-black/20 hover:-translate-y-1 transition-all duration-300 cursor-default"
        >
          <!-- Glowing Animated Border (Reveals on Hover) -->
          <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/0 via-teal-500/0 to-emerald-500/0 
            group-hover:from-emerald-500/40 group-hover:via-teal-500/10 group-hover:to-transparent 
            transition-all duration-500 opacity-0 group-hover:opacity-100"></div>
            
          <!-- Inner Card -->
          <div class="relative h-full p-6 rounded-[15px] bg-slate-900/70 backdrop-blur-xl border border-white/5 group-hover:bg-slate-800/60 transition-all duration-300">
            <!-- Ikon dengan animasi mengambang (float) terus-menerus -->
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center mb-5 shadow-lg animate-float"
              :style="{ animationDelay: `${index * 0.5}s` }"
              :class="[feat.color, feat.shadow]">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="feat.icon"/>
              </svg>
            </div>
            <h3 class="text-white font-bold mb-2 tracking-wide">{{ feat.title }}</h3>
            <p class="text-slate-400 text-sm leading-relaxed">{{ feat.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ CTA ══════════ -->
    <section class="animate-fade-up delay-500 relative overflow-hidden rounded-3xl border border-white/10
      bg-slate-900/40 backdrop-blur-2xl p-8 md:p-12 shadow-[0_8px_30px_rgb(0,0,0,0.2)]">
      <div class="absolute -top-12 -right-12 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none animate-blob-slow"></div>
      <div class="absolute -bottom-12 -left-12 w-48 h-48 bg-teal-500/10 rounded-full blur-3xl pointer-events-none animate-blob" style="animation-delay: 2s;"></div>
      
      <div class="relative flex flex-col md:flex-row items-center justify-between gap-8">
        <!-- Text -->
        <div class="md:w-3/5 text-center md:text-left">
          <h2 class="text-3xl font-bold text-white mb-3">Siap Memulai Analisis?</h2>
          <p class="text-slate-400 text-sm md:text-base mb-8 max-w-md mx-auto md:mx-0 leading-relaxed">
            Upload dataset dan sistem akan memproses dari langkah pembersihan data hingga pelabelan sentimen secara otomatis.
          </p>
          <button @click="router.push('/input-data')"
            class="inline-flex items-center gap-2 px-8 py-3.5 bg-gradient-to-r from-emerald-500 to-green-500
              hover:from-emerald-400 hover:to-green-400 text-white font-bold rounded-xl
              shadow-lg shadow-emerald-500/25 transition-all duration-200 hover:-translate-y-0.5">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
            </svg>
            Upload Data Sekarang
          </button>
        </div>

        <!-- 3D Element -->
        <div class="md:w-2/5 flex justify-center md:justify-end">
          <img src="/3d-crystal-transparent.png" alt="3D Data Crystal" 
            class="w-[200px] md:w-[280px] lg:w-[320px] object-contain animate-float drop-shadow-[0_10px_40px_rgba(16,185,129,0.3)]" 
            style="animation-duration: 4.5s;" />
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
@keyframes fadeUp {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

.animate-fade-up {
  animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
  opacity: 0;
}

/* Animasi Bergerak Terus-Menerus */
@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
}

@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

.animate-blob {
  animation: blob 7s infinite;
}

.animate-blob-slow {
  animation: blob 10s infinite reverse;
}

/* Stagger delays */
.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }
.delay-400 { animation-delay: 400ms; }
.delay-500 { animation-delay: 500ms; }

/* Text Slide Animation */
.text-slide-enter-active,
.text-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.text-slide-enter-from {
  opacity: 0;
  transform: translateY(100%);
}
.text-slide-leave-to {
  opacity: 0;
  transform: translateY(-100%);
}
</style>
