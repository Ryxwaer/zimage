<script setup>
import { ref, onMounted } from "vue";
import PromptInput from "./components/PromptInput.vue";
import SettingsPanel from "./components/SettingsPanel.vue";
import ImageCarousel from "./components/ImageCarousel.vue";
import ImageModal from "./components/ImageModal.vue";
import McpConnect from "./components/McpConnect.vue";

// ── State ───────────────────────────────────────────────────────

const CONFIG = ref(null);
const STATUS = ref({ is_loaded: false, is_loading: true });
const IMAGES = ref([]);
const SELECTED_IMAGE = ref(null);
const IS_GENERATING = ref(false);
const GENERATION_ERROR = ref("");

const SETTINGS = ref({
  width: 512,
  height: 512,
  steps: 9,
  seed: -1,
});

// ── API Calls ───────────────────────────────────────────────────

async function fetchConfig() {
  try {
    const RES = await fetch("/api/config");
    CONFIG.value = await RES.json();
    SETTINGS.value.width = CONFIG.value.default_width;
    SETTINGS.value.height = CONFIG.value.default_height;
    SETTINGS.value.steps = CONFIG.value.default_steps;
  } catch (e) {
    console.error("Failed to fetch config:", e);
  }
}

async function fetchStatus() {
  try {
    const RES = await fetch("/api/status");
    STATUS.value = await RES.json();
  } catch (e) {
    console.error("Failed to fetch status:", e);
  }
}

async function fetchImages() {
  try {
    const RES = await fetch("/api/images");
    IMAGES.value = await RES.json();
  } catch (e) {
    console.error("Failed to fetch images:", e);
  }
}

async function handleGenerate(prompt) {
  if (!prompt.trim() || IS_GENERATING.value) return;

  IS_GENERATING.value = true;
  GENERATION_ERROR.value = "";

  try {
    const RES = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: prompt.trim(),
        width: SETTINGS.value.width,
        height: SETTINGS.value.height,
        steps: SETTINGS.value.steps,
        seed: SETTINGS.value.seed,
      }),
    });

    if (!RES.ok) {
      const ERR = await RES.json();
      throw new Error(ERR.detail || "Generation failed");
    }

    await fetchImages();
  } catch (e) {
    GENERATION_ERROR.value = e.message;
  } finally {
    IS_GENERATING.value = false;
  }
}

// ── Status Polling ──────────────────────────────────────────────

let STATUS_INTERVAL = null;

onMounted(async () => {
  await fetchConfig();
  await fetchStatus();
  await fetchImages();

  if (!STATUS.value.is_loaded) {
    STATUS_INTERVAL = setInterval(async () => {
      await fetchStatus();
      if (STATUS.value.is_loaded || STATUS.value.error) {
        clearInterval(STATUS_INTERVAL);
      }
    }, 3000);
  }
});
</script>

<template>
  <!-- Background -->
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
  <div class="blob blob-3"></div>

  <div class="relative z-10 min-h-screen flex flex-col items-center px-5 py-10 sm:py-16">

    <!-- Header -->
    <header class="mb-12 text-center">
      <div class="flex items-baseline justify-center gap-1">
        <span class="text-3xl font-light tracking-[-0.02em] text-zinc-200">z-image</span>
        <span class="text-[11px] uppercase tracking-[0.15em] text-zinc-500 ml-1.5">turbo</span>
      </div>

      <!-- Status -->
      <div class="mt-4 flex items-center justify-center gap-2 text-[11px] tracking-wide">
        <span class="w-1.5 h-1.5 rounded-full"
              :class="STATUS.is_loaded
                ? 'bg-zinc-400'
                : STATUS.error
                  ? 'bg-red-400/60'
                  : 'bg-zinc-500 animate-pulse'">
        </span>
        <span class="text-zinc-500">
          {{ STATUS.is_loaded ? 'ready' : STATUS.error ? 'error' : 'loading model' }}
        </span>
      </div>
    </header>

    <!-- Content -->
    <main class="w-full max-w-xl space-y-10">

      <PromptInput
        :is-generating="IS_GENERATING"
        :is-model-ready="STATUS.is_loaded"
        :error="GENERATION_ERROR"
        @generate="handleGenerate"
      />

      <SettingsPanel v-model:settings="SETTINGS" />

      <p v-if="STATUS.error" class="text-[11px] text-red-400/70 leading-relaxed">
        {{ STATUS.error }}
      </p>

      <ImageCarousel
        v-if="IMAGES.length > 0"
        :images="IMAGES"
        @select="(img) => SELECTED_IMAGE = img"
      />

      <McpConnect :mcp-path="CONFIG?.mcp_path || '/mcp'" />

    </main>

    <footer class="mt-16 text-[10px] tracking-wider uppercase text-zinc-600">
      cpu-optimized inference
    </footer>
  </div>

  <Transition name="fade">
    <ImageModal
      v-if="SELECTED_IMAGE"
      :image="SELECTED_IMAGE"
      @close="SELECTED_IMAGE = null"
    />
  </Transition>
</template>
