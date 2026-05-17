<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const pipelineOpen = ref(false)
const mobileOpen = ref(false)

// Main nav — only key pages shown directly
const mainNav = [
  { name: 'Beranda',       path: '/',                 icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { name: 'Input Data',    path: '/input-data',       icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12' },
  { name: 'Klasifikasi',   path: '/klasifikasi-baru', icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' },
  { name: 'Insight',       path: '/insight',          icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' },
]

// Pipeline steps inside dropdown
const pipelineSteps = [
  { step: '01', name: 'Input Data',     path: '/input-data',       icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12' },
  { step: '02', name: 'Preprocessing',  path: '/preprocessing',    icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
  { step: '03', name: 'Clustering',     path: '/clustering',       icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
  { step: '04', name: 'Topik Cluster',  path: '/topik-cluster',    icon: 'M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z' },
  { step: '05', name: 'Labeling',       path: '/labeling',         icon: 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z' },
  { step: '06', name: 'Training',       path: '/training',         icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z' },
  { step: '07', name: 'Evaluasi',       path: '/evaluasi',         icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { step: '08', name: 'Insight',        path: '/insight',          icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' },
  { step: '09', name: 'Klasifikasi',    path: '/klasifikasi-baru', icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' },
]

const isPipelineActive = () => pipelineSteps.some(s => s.path === route.path)
const isActive = (path) => route.path === path

const goTo = (path) => {
  router.push(path)
  pipelineOpen.value = false
  mobileOpen.value = false
}

// Close dropdown on outside click
const handleOutside = (e) => {
  if (!e.target.closest('#pipeline-dropdown')) pipelineOpen.value = false
}
onMounted(() => document.addEventListener('click', handleOutside))
onUnmounted(() => document.removeEventListener('click', handleOutside))
</script>

<template>
  <header class="sticky top-0 z-50 w-full bg-slate-900/90 backdrop-blur-xl border-b border-slate-700/60 shadow-xl shadow-black/20">
    <div class="px-4 md:px-8 max-w-[1400px] mx-auto">
      <div class="flex items-center h-[60px] gap-8">

        <!-- ── Logo ── -->
        <router-link to="/" class="flex items-center gap-2.5 flex-shrink-0">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-green-400 flex items-center justify-center shadow-md shadow-emerald-500/30">
            <svg class="w-[18px] h-[18px] text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
          </div>
          <span class="font-bold text-[15px] bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-green-300 tracking-wide">
            SentimenAI
          </span>
        </router-link>

        <!-- ── Divider ── -->
        <div class="hidden md:block h-6 w-px bg-slate-700"></div>

        <!-- ── Desktop nav ── -->
        <nav class="hidden md:flex items-center gap-1">

          <!-- Main items -->
          <router-link
            v-for="item in mainNav"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-[13px] font-medium transition-all duration-200 group"
            :class="isActive(item.path)
              ? 'text-emerald-400 bg-emerald-500/10'
              : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/70'"
          >
            <svg class="w-3.5 h-3.5 flex-shrink-0"
              :class="isActive(item.path) ? 'text-emerald-400' : 'text-slate-500 group-hover:text-emerald-400'"
              fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"/>
            </svg>
            {{ item.name }}
          </router-link>

          <!-- Pipeline dropdown -->
          <div class="relative" id="pipeline-dropdown">
            <button
              @click.stop="pipelineOpen = !pipelineOpen"
              class="flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-[13px] font-medium transition-all duration-200 group"
              :class="isPipelineActive()
                ? 'text-emerald-400 bg-emerald-500/10'
                : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/70'"
            >
              <svg class="w-3.5 h-3.5"
                :class="isPipelineActive() ? 'text-emerald-400' : 'text-slate-500 group-hover:text-emerald-400'"
                fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
              </svg>
              Pipeline
              <svg class="w-3 h-3 transition-transform duration-200" :class="pipelineOpen ? 'rotate-180' : ''"
                fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>

            <!-- Dropdown panel -->
            <transition name="dropdown">
              <div v-if="pipelineOpen"
                class="absolute top-[calc(100%+8px)] left-0 w-64 bg-slate-900 border border-slate-700/60 rounded-2xl shadow-2xl shadow-black/40 overflow-hidden p-2">
                <p class="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-3 pt-1 pb-2">Alur Analisis</p>
                <button
                  v-for="step in pipelineSteps"
                  :key="step.path"
                  @click="goTo(step.path)"
                  class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left text-[13px] transition-all duration-150 group"
                  :class="isActive(step.path)
                    ? 'bg-emerald-500/10 text-emerald-400'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'"
                >
                  <span class="text-[10px] font-mono font-bold text-slate-600 w-5 flex-shrink-0">{{ step.step }}</span>
                  <svg class="w-4 h-4 flex-shrink-0"
                    :class="isActive(step.path) ? 'text-emerald-400' : 'text-slate-600 group-hover:text-emerald-400'"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="step.icon"/>
                  </svg>
                  <span>{{ step.name }}</span>
                  <svg v-if="isActive(step.path)" class="w-3.5 h-3.5 ml-auto text-emerald-400"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                  </svg>
                </button>
              </div>
            </transition>
          </div>
        </nav>

        <!-- ── Spacer ── -->
        <div class="flex-1"></div>

        <!-- ── API Status ── -->
        <div class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
          <span class="relative flex h-1.5 w-1.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
          </span>
          <span class="text-[11px] font-semibold text-emerald-400">API Online</span>
        </div>

        <!-- ── Mobile burger ── -->
        <button @click="mobileOpen = !mobileOpen"
          class="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!mobileOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- ── Mobile menu ── -->
    <transition name="slide-down">
      <div v-if="mobileOpen" class="md:hidden border-t border-slate-700/60 bg-slate-900/98">
        <div class="p-3 space-y-1">
          <button v-for="step in pipelineSteps" :key="step.path"
            @click="goTo(step.path)"
            class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all"
            :class="isActive(step.path)
              ? 'bg-emerald-500/10 text-emerald-400'
              : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'"
          >
            <span class="text-[10px] font-mono font-bold text-slate-600 w-5">{{ step.step }}</span>
            <svg class="w-4 h-4 flex-shrink-0" :class="isActive(step.path) ? 'text-emerald-400' : 'text-slate-500'"
              fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="step.icon"/>
            </svg>
            {{ step.name }}
          </button>
        </div>
      </div>
    </transition>
  </header>
</template>

<style scoped>
.dropdown-enter-active { transition: all 0.2s cubic-bezier(0.16,1,0.3,1); }
.dropdown-leave-active { transition: all 0.15s ease; }
.dropdown-enter-from  { opacity: 0; transform: translateY(-6px) scale(0.97); }
.dropdown-leave-to    { opacity: 0; transform: translateY(-4px) scale(0.98); }

.slide-down-enter-active { transition: all 0.25s ease; }
.slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
