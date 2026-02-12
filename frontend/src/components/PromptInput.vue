<script setup>
import { ref, computed, watch } from "vue";

const props = defineProps({
  isGenerating: Boolean,
  isModelReady: Boolean,
  error: String,
});

const emit = defineEmits(["generate"]);

const PROMPT = ref("");
const ELAPSED = ref(0);
let TIMER = null;

const CAN_GENERATE = computed(
  () => PROMPT.value.trim().length > 0 && props.isModelReady && !props.isGenerating
);

function startGeneration() {
  if (!CAN_GENERATE.value) return;
  ELAPSED.value = 0;
  TIMER = setInterval(() => ELAPSED.value++, 1000);
  emit("generate", PROMPT.value);
}

watch(
  () => props.isGenerating,
  (generating) => {
    if (!generating && TIMER) {
      clearInterval(TIMER);
      TIMER = null;
    }
  }
);

function onKeydown(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    startGeneration();
  }
}
</script>

<template>
  <div>
    <textarea
      v-model="PROMPT"
      @keydown="onKeydown"
      placeholder="describe what you see..."
      rows="3"
      class="w-full bg-transparent border-b border-zinc-800 pb-3
             text-zinc-200 placeholder-zinc-600 text-[15px] leading-relaxed
             focus:outline-none focus:border-zinc-600
             resize-none transition-colors duration-300"
    ></textarea>

    <div class="flex items-center justify-between mt-4">
      <span class="text-[11px] tracking-wide text-zinc-500">
        <template v-if="isGenerating">
          {{ ELAPSED }}s
        </template>
        <template v-else-if="!isModelReady">
          waiting for model
        </template>
        <template v-else>
          enter to generate
        </template>
      </span>

      <button
        @click="startGeneration"
        :disabled="!CAN_GENERATE"
        class="inline-flex items-center gap-2 px-5 py-2 text-[12px] tracking-wide uppercase
               rounded-full transition-all duration-300
               text-zinc-300 border border-zinc-700/60
               hover:border-zinc-500 hover:text-zinc-100
               disabled:opacity-25 disabled:cursor-not-allowed disabled:hover:border-zinc-700/60"
      >
        <span v-if="isGenerating" class="spinner"></span>
        <template v-else>generate</template>
      </button>
    </div>

    <p v-if="error" class="mt-3 text-[11px] text-red-400/70 leading-relaxed">
      {{ error }}
    </p>
  </div>
</template>
