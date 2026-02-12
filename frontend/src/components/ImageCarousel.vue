<script setup>
import { ref } from "vue";

defineProps({
  images: Array,
});

const emit = defineEmits(["select"]);

const SCROLL_CONTAINER = ref(null);

function onWheel(e) {
  if (!SCROLL_CONTAINER.value) return;
  // Convert vertical scroll to horizontal
  if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
    e.preventDefault();
    SCROLL_CONTAINER.value.scrollLeft += e.deltaY;
  }
}

function formatTime(seconds) {
  if (!seconds) return "";
  return `${seconds.toFixed(1)}s`;
}
</script>

<template>
  <div>
    <span class="block text-[10px] uppercase tracking-widest text-zinc-500 mb-4">
      recent &middot; {{ images.length }}
    </span>

    <div
      ref="SCROLL_CONTAINER"
      @wheel="onWheel"
      class="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1"
    >
      <div
        v-for="img in images"
        :key="img.filename"
        @click="emit('select', img)"
        class="flex-shrink-0 cursor-pointer group"
      >
        <div class="w-28 h-28 rounded-lg overflow-hidden
                    border border-zinc-800/60
                    group-hover:border-zinc-600 transition-all duration-300">
          <img
            :src="img.url"
            :alt="img.prompt"
            class="w-full h-full object-cover
                   group-hover:scale-[1.03] transition-transform duration-500 ease-out"
            loading="lazy"
          />
        </div>
        <div class="mt-1.5 w-28">
          <p class="text-[10px] text-zinc-500 truncate">
            {{ img.prompt }}
          </p>
          <p class="text-[10px] text-zinc-600 mt-0.5">
            {{ img.width }}x{{ img.height }}
            <span v-if="img.generation_time_seconds">
              / {{ formatTime(img.generation_time_seconds) }}
            </span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
