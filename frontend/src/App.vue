<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <RouterLink class="brand" to="/video">种草验真</RouterLink>
      <nav>
        <RouterLink to="/video">视频演示</RouterLink>
        <RouterLink to="/comparison">横评占位</RouterLink>
      </nav>
    </header>
    <main class="page-shell"><RouterView /></main>
  </div>
</template>
