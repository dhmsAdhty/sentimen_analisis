<script setup>
import Navbar from './Navbar.vue'
import ShapeGrid from './ShapeGrid.vue'
</script>

<template>
  <div class="min-h-screen bg-[#080e1a] font-sans text-slate-300 flex flex-col relative overflow-x-hidden">

    <!-- ShapeGrid fullscreen background -->
    <div class="fixed inset-0 z-0 pointer-events-none">
      <ShapeGrid
        :squareSize="42"
        borderColor="#1a2744"
        hoverFillColor="#10b981"
        :hoverTrailAmount="5"
        :speed="0.28"
        direction="diagonal"
        shape="square"
        :opacity="0.55"
      />
    </div>

    <!-- Subtle center vignette — keeps content legible without hiding the grid -->
    <div class="fixed inset-0 z-[1] pointer-events-none"
      style="background: radial-gradient(ellipse 80% 60% at 50% 0%, transparent 0%, #080e1aaa 60%, #080e1a 100%);">
    </div>

    <!-- Navbar -->
    <Navbar class="relative z-30" />

    <!-- Page content -->
    <main class="relative z-10 flex-1">
      <div class="max-w-6xl mx-auto px-6 md:px-10 py-10">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

  </div>
</template>

<style>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
</style>
