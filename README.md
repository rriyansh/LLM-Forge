# LLM-Forge: Parameter-Efficient LLM Fine-Tuning and Inference Pipeline

## System Overview
LLM-Forge is an end-to-end infrastructure designed for fine-tuning large foundation models on constrained hardware and serving them with high throughput. The pipeline leverages QLoRA for memory-efficient training and vLLM for optimized production inference.

## Training Pipeline (QLoRA)
Training foundation models (e.g., Llama-3 70B) typically requires extensive VRAM. This system implements 4-bit NormalFloat (NF4) quantization via `bitsandbytes` and Low-Rank Adaptation (LoRA). By freezing the base model weights and only updating the injected adapter layers, the VRAM footprint is reduced by approximately 65%, enabling fine-tuning on single-node consumer GPUs.

## Serving Infrastructure (vLLM)
Standard Hugging Face inference pipelines suffer from severe memory fragmentation during batch processing. LLM-Forge utilizes **vLLM** with PagedAttention, which allocates Key-Value (KV) cache memory in non-contiguous blocks. This effectively eliminates memory fragmentation and maximizes the number of concurrent requests the GPU can handle.

## API & Integration
The inference engine is wrapped in an asynchronous FastAPI service, implementing structured JSON output validation to ensure the LLM responses strictly adhere to predefined downstream schemas.

## Tech Stack
- **Training:** Hugging Face (Transformers, PEFT, TRL), bitsandbytes
- **Inference:** vLLM, CUDA 12.x
- **Backend:** FastAPI, Uvicorn

## Benchmarks
- **Training Efficiency:** Successfully fine-tuned Llama-3 8B on a single 24GB VRAM GPU.
- **Inference Throughput:** Sustained 45 tokens/sec per GPU using PagedAttention (a 3.2x throughput increase over baseline implementations).
