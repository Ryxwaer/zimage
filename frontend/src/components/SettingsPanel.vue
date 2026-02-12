<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  settings: Object,
});

const emit = defineEmits(["update:settings"]);

const IS_OPEN = ref(false);

const RESOLUTIONS = [
  { label: "512", w: 512, h: 512 },
  { label: "768", w: 768, h: 768 },
  { label: "1024", w: 1024, h: 1024 },
  { label: "768:512", w: 768, h: 512 },
  { label: "512:768", w: 512, h: 768 },
];

const STEPS_OPTIONS = [8, 9, 10];

function selectResolution(res) {
  emit("update:settings", { ...props.settings, width: res.w, height: res.h });
}

function selectSteps(val) {
  emit("update:settings", { ...props.settings, steps: val });
}

function updateSeed(val) {
  emit("update:settings", { ...props.settings, seed: parseInt(val) ?? -1 });
}

function randomizeSeed() {
  emit("update:settings", { ...props.settings, seed: -1 });
}

const SUMMARY = computed(() => {
  const R = props.settings.width === props.settings.height
    ? `${props.settings.width}`
    : `${props.settings.width}:${props.settings.height}`;
  return `${R}px / ${props.settings.steps} steps`;
});
</script>

<template>
  <div>
    <button
      @click="IS_OPEN = !IS_OPEN"
      class="flex items-center gap-3 text-[11px] tracking-wide
             hover:text-zinc-300 transition-colors duration-200"
    >
      <span class="uppercase text-zinc-500">settings</span>
      <span class="text-zinc-500">{{ SUMMARY }}</span>
    </button>

    <Transition name="slide">
      <div v-if="IS_OPEN" class="mt-6 space-y-6">

        <!-- Resolution -->
        <div>
          <span class="block text-[10px] uppercase tracking-widest text-zinc-500 mb-3">resolution</span>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="res in RESOLUTIONS"
              :key="res.label"
              @click="selectResolution(res)"
              class="px-3 py-1.5 text-[11px] tracking-wide rounded-full transition-all duration-200 border"
              :class="settings.width === res.w && settings.height === res.h
                ? 'border-zinc-500 text-zinc-300'
                : 'border-zinc-800 text-zinc-500 hover:border-zinc-600 hover:text-zinc-300'"
            >
              {{ res.label }}
            </button>
          </div>
        </div>

        <!-- Steps -->
        <div>
          <span class="block text-[10px] uppercase tracking-widest text-zinc-500 mb-3">steps</span>
          <div class="flex gap-1.5">
            <button
              v-for="s in STEPS_OPTIONS"
              :key="s"
              @click="selectSteps(s)"
              class="px-3 py-1.5 text-[11px] tracking-wide rounded-full transition-all duration-200 border"
              :class="settings.steps === s
                ? 'border-zinc-500 text-zinc-300'
                : 'border-zinc-800 text-zinc-500 hover:border-zinc-600 hover:text-zinc-300'"
            >
              {{ s }}
            </button>
          </div>
        </div>

        <!-- Seed -->
        <div>
          <span class="block text-[10px] uppercase tracking-widest text-zinc-500 mb-3">seed</span>
          <div class="flex items-center gap-3">
            <input
              type="number"
              :value="settings.seed"
              @input="(e) => updateSeed(e.target.value)"
              placeholder="-1"
              class="w-32 bg-transparent border-b border-zinc-800 pb-1
                     text-zinc-400 text-[12px] focus:outline-none focus:border-zinc-600
                     transition-colors"
            />
            <button
              @click="randomizeSeed"
              class="text-[10px] uppercase tracking-widest text-zinc-600
                     hover:text-zinc-400 transition-colors"
            >
              random
            </button>
          </div>
        </div>

      </div>
    </Transition>
  </div>
</template>
