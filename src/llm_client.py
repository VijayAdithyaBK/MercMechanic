import shutil
import subprocess

class LLMClient:
    def __init__(self, mode="auto"):
        self.mode = mode
        if self.mode == "auto":
            if shutil.which("ollama"):
                self.mode = "ollama"
                print("[LLM] Ollama detected. Using local LLM.")
            else:
                self.mode = "mock"
                print("\n[LLM Warning] Ollama not found in PATH.")
                print("To enable Real LLM: Install from https://ollama.com/ and restart terminal.")
                print("Falling back to Mock LLM.\n")
    
    def generate(self, prompt):
        if self.mode == "mock":
            return self._mock_generate(prompt)
        elif self.mode == "ollama":
            return self._ollama_generate(prompt)
    
    def _mock_generate(self, prompt):
        # determininstic simple mock response
        return (
            "\n[MOCK LLM RESPONSE]\n"
            "Based on the context provided, here is the diagnosis:\n"
            "1. Check the specific fuse mentioned in the retrieved context.\n"
            "2. Inspect the related components in the graph path.\n"
            "This is a simulated response because no real LLM is connected."
        )

    def _ollama_generate(self, prompt):
        import requests
        import json
        
        # 1. Discover available models
        model = "llama3" # Default fallback
        try:
            tags_res = requests.get("http://localhost:11434/api/tags")
            if tags_res.status_code == 200:
                models = [m['name'] for m in tags_res.json().get('models', [])]
                # Prefer tinyllama (fastest), then phi3, then llama3
                if "tinyllama:latest" in models or "tinyllama" in models:
                    model = "tinyllama"
                elif "phi3:latest" in models or "phi3" in models:
                   model = "phi3"
                elif "llama3:latest" in models or "llama3" in models:
                   model = "llama3"
                # Else keep default or take first
        except Exception as e:
            print(f"[LLM Warning] Could not list models: {e}")

        print(f"[LLM] Generating with model: {model}...")

        # 2. Call Generate API
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"[Error calling Ollama API]: {response.status_code} - {response.text}"
        except Exception as e:
            return f"[Exception calling Ollama API]: {str(e)}"
