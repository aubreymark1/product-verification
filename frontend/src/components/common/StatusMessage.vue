<script setup lang="ts">
defineProps<{ type: 'loading' | 'empty' | 'error'; message: string }>()
</script>

<template><div class="status-message" :class="type">{{ message }}</div></template>
