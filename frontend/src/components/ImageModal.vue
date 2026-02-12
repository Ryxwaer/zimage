<script setup>
import { onMounted, onUnmounted } from "vue";

defineProps({
  image: Object,
});

const emit = defineEmits(["close"]);

function onKeydown(e) {
  if (e.key === "Escape") emit("close");
}

onMounted(() => document.addEventListener("keydown", onKeydown));
onUnmounted(() => document.removeEventListener("keydown", onKeydown));
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-6 cursor-pointer"
    @click="emit('close')"
  >
    <div class="absolute inset-0 bg-zinc-950/90 backdrop-blur-sm"></div>

    <div class="relative z-10 max-w-4xl max-h-[90vh] flex flex-col items-center">
      <img
        :src="image.url"
        :alt="image.prompt"
        class="max-h-[75vh] max-w-full rounded-lg object-contain"
      />

      <div class="mt-4 max-w-md text-center">
        <p class="text-[13px] text-zinc-400 leading-relaxed">{{ image.prompt }}</p>
        <div class="flex items-center justify-center gap-4 mt-2 text-[10px] tracking-wide text-zinc-500">
          <span>{{ image.width }}x{{ image.height }}</span>
          <span>{{ image.steps }} steps</span>
          <span>seed {{ image.seed }}</span>
          <span v-if="image.generation_time_seconds">
            {{ image.generation_time_seconds.toFixed(1) }}s
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
