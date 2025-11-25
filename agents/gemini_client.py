import os, time, json, traceback
from typing import Any

# Try import
try:
    from google import genai
    SDK_AVAILABLE = True
except Exception:
    genai = None
    SDK_AVAILABLE = False

MAX_RETRIES = 3
BACKOFF_BASE = 1.0

class GeminiClient:
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        self.model = model
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "False").lower() in ("1","true","yes")
        self.client = None

        if not SDK_AVAILABLE:
            print("[gemini_client] WARNING: google-genai SDK not installed. Falling back to mock.")
            return

        try:
            if self.api_key and not self.use_vertex:
                try:
                    self.client = genai.Client(api_key=self.api_key)
                except TypeError:
                    self.client = genai.Client()
            else:
                try:
                    self.client = genai.Client(vertexai=self.use_vertex, api_key=self.api_key)
                except TypeError:
                    self.client = genai.Client()
        except Exception as e:
            print("[gemini_client] Failed to init genai client:", e)
            traceback.print_exc()
            self.client = None

    def _extract_text_from_response(self, response: Any) -> str:
        """
        Try common response shapes to extract text content.
        """
        # 1) response.text (common)
        text = getattr(response, "text", None)
        if text:
            return text

        # 2) response.output or response.outputs (Vertex-style)
        out = getattr(response, "output", None) or getattr(response, "outputs", None)
        if out:
            # try to find text field in outputs
            try:
                # sometimes output is list of dicts with 'content' fields
                if isinstance(out, (list, tuple)) and len(out) > 0:
                    first = out[0]
                    if isinstance(first, dict):
                        for k in ("content", "text", "output"):
                            if k in first:
                                return first[k]
                    # fallback stringify
                    return json.dumps(first)
                else:
                    return str(out)
            except Exception:
                pass

        # 3) response.candidates[0].content (older/newer variants)
        try:
            cand = getattr(response, "candidates", None)
            if cand and len(cand) > 0:
                c0 = cand[0]
                if isinstance(c0, dict) and "content" in c0:
                    return c0["content"]
                # sometimes candidate is object with .content
                return getattr(c0, "content", str(c0))
        except Exception:
            pass

        # 4) top-level str(response)
        try:
            return str(response)
        except Exception:
            return ""

    def _try_generate(self, prompt: str, max_output_tokens: int = 512) -> str:
        """
        Try different SDK call signatures until one works.
        Returns raw text from the model.
        Raises the last exception if all attempts fail.
        """
        if not self.client:
            raise RuntimeError("GenAI client not configured.")

        last_exc = None
        # Try multiple call patterns (order matters)
        call_variants = [
            # modern: models.generate_content(model=..., contents=..., max_output_tokens=...)
            lambda: self.client.models.generate_content(model=self.model, contents=prompt, max_output_tokens=max_output_tokens),
            # variant without max_output_tokens
            lambda: self.client.models.generate_content(model=self.model, contents=prompt),
            # some SDKs provide generate_text on client
            lambda: self.client.generate_text(model=self.model, prompt=prompt, max_output_tokens=max_output_tokens),
            lambda: self.client.generate_text(model=self.model, prompt=prompt),
            # top-level genai convenience
            lambda: genai.generate_text(model=self.model, prompt=prompt, max_output_tokens=max_output_tokens) if hasattr(genai, "generate_text") else (_ for _ in ()).throw(TypeError("no genai.generate_text")),
            lambda: genai.generate_text(model=self.model, prompt=prompt) if hasattr(genai, "generate_text") else (_ for _ in ()).throw(TypeError("no genai.generate_text2")),
        ]

        for attempt in range(1, MAX_RETRIES + 1):
            for variant in call_variants:
                try:
                    response = variant()
                    text = self._extract_text_from_response(response)
                    if text is None:
                        text = ""
                    return text
                except TypeError as te:
                    # signature mismatch — try next variant
                    last_exc = te
                    continue
                except Exception as e:
                    last_exc = e
                    # For transient errors, break out to retry with backoff
                    break
            # if we get here, do a backoff then retry
            wait = BACKOFF_BASE * (2 ** (attempt - 1))
            print(f"[gemini_client] model call failed (attempt {attempt}/{MAX_RETRIES}): {last_exc}. Retrying in {wait:.1f}s")
            time.sleep(wait)

        # exhausted
        raise last_exc

    def generate_structured(self, prompt: str, max_output_tokens: int = 512) -> Any:
        """
        Returns parsed JSON when model responds with JSON, else returns {"text": raw}.
        On failure returns deterministic mock structure for offline demo.
        """
        if not SDK_AVAILABLE or not self.client:
            return {
                "mock": True,
                "ddx": [
                    {"condition": "Viral illness", "confidence": 0.6, "evidence": "fever + cough common"},
                    {"condition": "Bacterial infection", "confidence": 0.3, "evidence": "differential fallback"}
                ],
                "note": "mock fallback - no gemini client configured"
            }

        try:
            text = self._try_generate(prompt, max_output_tokens=max_output_tokens)
            # attempt to parse JSON
            try:
                parsed = json.loads(text)
                return parsed
            except Exception:
                # return raw text for downstream parsing attempt
                return {"text": text}
        except Exception as e:
            print("[gemini_client] Final model call failed:", e)
            traceback.print_exc()
            return {
                "mock": True,
                "ddx": [
                    {"condition": "Viral illness", "confidence": 0.6, "evidence": "fever + cough common"},
                    {"condition": "Bacterial infection", "confidence": 0.3, "evidence": "differential fallback"}
                ],
                "error": str(e)
            }