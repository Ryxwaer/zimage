<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  mcpPath: { type: String, default: "/mcp" },
});

const TABS = ["mcp", "rest", "prompt"];

const IS_OPEN = ref(false);
const ACTIVE_TAB = ref("mcp");
const COPIED = ref(false);

const ORIGIN = computed(() => window.location.origin);
const EFFECTIVE_URL = computed(() => `${ORIGIN.value}${props.mcpPath}`);
const API_URL = computed(() => `${ORIGIN.value}/api`);

const MCP_CONFIG = computed(() =>
  JSON.stringify(
    {
      mcpServers: {
        "z-image": {
          url: EFFECTIVE_URL.value,
        },
      },
    },
    null,
    2
  )
);

const REST_CONFIG = computed(() =>
  `# Generate an image
POST ${API_URL.value}/generate
Content-Type: application/json

{
  "prompt": "a serene mountain lake at sunset, photography",
  "width": 512,
  "height": 512,
  "steps": 9,
  "seed": -1
}

# Response → { url, filename, prompt, width, height,
#              steps, seed, generation_time_seconds, ... }

# List recent images
GET ${API_URL.value}/images

# Get model status
GET ${API_URL.value}/status

# Interactive docs
${ORIGIN.value}/docs`
);

const AGENT_PROMPT = computed(() =>
  `You have access to an image generation API at ${API_URL.value}/generate (POST, JSON body with params: prompt, width, height, seed, steps). For MCP-capable agents, connect to "${EFFECTIVE_URL.value}" using Streamable HTTP transport (tool: generate_image). It is good for generating small profile pictures at 512x512 but also capable of highly realistic 1024x1024 images. You should specify a style with each prompt (e.g. photo, illustration, painting). The model runs on CPU so generation may take 30-120 seconds. Interactive API docs: ${ORIGIN.value}/docs`
);

const ACTIVE_CONTENT = computed(() => {
  if (ACTIVE_TAB.value === "mcp") return MCP_CONFIG.value;
  if (ACTIVE_TAB.value === "rest") return REST_CONFIG.value;
  return AGENT_PROMPT.value;
});

function selectTab(tab) {
  ACTIVE_TAB.value = tab;
  IS_OPEN.value = true;
}

async function copyContent() {
  try {
    await navigator.clipboard.writeText(ACTIVE_CONTENT.value);
    COPIED.value = true;
    setTimeout(() => (COPIED.value = false), 2000);
  } catch (e) {
    console.error("Copy failed:", e);
  }
}
</script>

<template>
  <div>
    <div class="flex items-center gap-3">
      <button
        @click="IS_OPEN = !IS_OPEN"
        class="text-[10px] uppercase tracking-widest text-zinc-500
               hover:text-zinc-400 transition-colors duration-200"
      >
        connect
      </button>

      <div class="flex gap-1">
        <button
          v-for="tab in TABS"
          :key="tab"
          @click="selectTab(tab)"
          class="px-2.5 py-1 text-[10px] uppercase tracking-widest rounded-full
                 transition-all duration-200 border"
          :class="IS_OPEN && ACTIVE_TAB === tab
            ? 'border-zinc-600 text-zinc-400'
            : 'border-transparent text-zinc-600 hover:text-zinc-400'"
        >
          {{ tab }}
        </button>
      </div>
    </div>

    <Transition name="slide">
      <div
        v-if="IS_OPEN"
        @click="copyContent"
        class="relative cursor-pointer group mt-4"
      >
        <pre
          class="text-[11px] font-mono leading-relaxed text-zinc-400
                 bg-zinc-900/30 rounded-lg px-4 py-3 overflow-x-auto
                 border border-zinc-800/40 whitespace-pre-wrap break-words
                 transition-colors duration-200
                 hover:border-zinc-700/60"
        >{{ ACTIVE_CONTENT }}</pre>

        <span
          class="absolute top-2 right-2 px-2 py-1 text-[10px] uppercase tracking-widest
                 transition-all duration-200"
          :class="COPIED ? 'text-zinc-300' : 'text-zinc-600 group-hover:text-zinc-400'"
        >
          {{ COPIED ? 'copied' : 'click to copy' }}
        </span>
      </div>
    </Transition>
  </div>
</template>
