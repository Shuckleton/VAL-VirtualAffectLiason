from llama_cpp import Llama
import time

# Setup Llama model
model_path = "models/DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored.Q4_K_M.gguf"

def create_llm():
    return Llama(
        model_path=model_path,
        n_ctx=2060,
        n_threads=8,
        n_gpu_layers=-1,
        chat_format="llama-3",
        use_mlock=False,
        use_mmap=False
    )

llm = create_llm()
