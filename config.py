# config.py
# বাংলা: OpenRouter এর May 2026 সালের সেরা সম্পূর্ণ ফ্রি মডেলগুলো
import os
from dotenv import load_dotenv

load_dotenv()

class FreeLLMConfig:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    HF_API_KEY = os.getenv("HF_API_KEY")
    #GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
    BASE_URL = "https://openrouter.ai/api/v1"

    # ══════════════════════════════════════════════════════
    # PLANNER — সবচেয়ে ভালো reasoning দরকার
    # inclusionAI Ling-2.6-1T: SWE-bench Verified এ state-of-the-art
    # AIME26 benchmark এ top performance, agentic workflow এর জন্য বানানো
    # ══════════════════════════════════════════════════════
    # PLANNER_MODEL = "liquid/lfm-2.5-1.2b-thinking:free"
    PLANNER_MODEL ="gemini-2.5-flash"

    # ══════════════════════════════════════════════════════
    # CODER — code generation এ specialized
    # Poolside Laguna M.1: dedicated coding agent model
    # SWE-bench এ optimize, tool calling support আছে
    # ══════════════════════════════════════════════════════
    CODER_MODEL = "poolside/laguna-m.1:free"

    # ══════════════════════════════════════════════════════
    # REVIEWER — deep analysis দরকার
    # OpenAI gpt-oss-120b: 117B parameter, chain-of-thought
    # native tool use, structured output supportu   
    # ══════════════════════════════════════════════════════
    REVIEWER_MODEL = "Qwen/Qwen2.5-7B-Instruct"

    # ══════════════════════════════════════════════════════
    # TESTER — test generation + reasoning
    # Google Gemma 4 31B: 256K context, function calling
    # multimodal, Apache 2.0 license
    # ══════════════════════════════════════════════════════
    TESTER_MODEL = "Qwen/Qwen2.5-7B-Instruct"

    # ══════════════════════════════════════════════════════
    # DEBUGGER — complex reasoning/thinking model
    # NVIDIA Nemotron 3 Super: 1M context window!
    # multi-agent এর জন্য বিশেষভাবে তৈরি, MoE architecture
    # ══════════════════════════════════════════════════════
    DEBUGGER_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

    # ══════════════════════════════════════════════════════
    # FALLBACK — যখন specific model rate limit হয়
    # openrouter/free: automatically best available free model select করে
    # ══════════════════════════════════════════════════════
    FALLBACK_MODEL = "openrouter/free"

    # Rate limits (free tier)
    MAX_REQUESTS_PER_MIN = 20
    MAX_REQUESTS_PER_DAY = 200