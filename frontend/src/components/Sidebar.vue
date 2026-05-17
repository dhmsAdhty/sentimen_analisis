<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

const menuItems = [
  { name: 'DataInput', label: 'Input Data', icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12' },
  { name: 'Preprocessing', label: 'Preprocessing', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
  { name: 'Clustering', label: 'Clustering', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
  { name: 'TopikCluster', label: 'Topik Cluster', icon: 'M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z' },
  { name: 'Labeling', label: 'Labeling', icon: 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z' },
  { name: 'Training', label: 'Training', icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z' },
  { name: 'Evaluasi', label: 'Evaluasi', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { name: 'Insight', label: 'Insight', icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' },
  { name: 'KlasifikasiBaru', label: 'Klasifikasi Baru', icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' }
]
</script>

<template>
  <aside class="w-64 h-screen bg-slate-900/80 backdrop-blur-xl border-r border-slate-700/50 text-slate-300 flex flex-col shadow-2xl relative z-20">
    <div class="h-20 flex items-center px-8 border-b border-slate-700/50">
      <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-500 to-green-500 flex items-center justify-center mr-3 shadow-lg shadow-emerald-500/30">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
      </div>
      <h1 class="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-green-400 tracking-wide">SentimenAI</h1>
    </div>

    <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
      <router-link 
        v-for="item in menuItems" 
        :key="item.name"
        :to="{ name: item.name }"
        class="flex items-center px-4 py-3 rounded-xl transition-all duration-300 group relative"
        :class="route.name === item.name ? 'bg-gradient-to-r from-emerald-500/10 to-green-500/10 text-emerald-400 shadow-sm' : 'hover:bg-slate-800/50 hover:text-slate-100'"
      >
        <div 
          v-if="route.name === item.name"
          class="absolute left-0 w-1 h-6 bg-gradient-to-b from-emerald-500 to-green-500 rounded-r-full"
        ></div>
        
        <svg class="w-5 h-5 mr-3 transition-transform duration-300 group-hover:scale-110" 
             :class="route.name === item.name ? 'text-emerald-500' : 'text-slate-500 group-hover:text-emerald-400'"
             fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"></path>
        </svg>
        <span class="font-medium text-sm">{{ item.label }}</span>
      </router-link>
    </nav>
    
    <div class="p-4 border-t border-slate-700/50">
      <div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
        <p class="text-xs text-slate-400 font-medium mb-1">Status Sistem</p>
        <div class="flex items-center">
          <span class="relative flex h-2.5 w-2.5 mr-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span class="text-sm font-semibold text-slate-200">API Online</span>
        </div>
      </div>
    </div>
  </aside>
</template>
