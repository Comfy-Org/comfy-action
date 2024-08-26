# Workflows for Comfy GitHub Action

- SDv1.5:
    - `sd15_default`: just a basic gen
    - `sd15_lora`: basic gen with a single LoRA
- SDXL:
    - `xl_default`: just a basic gen
    - `xl_sketch_control`: uses a sketch controlnet
- SD3:
    - `sd3_default`: just a basic gen
    - `sd3-single-t5`: uses just T5, and excludes CLIP
    - `sd3_multi_prompt`: sends a different prompt to T5 vs CLIP
- Flux:
    - `flux_schnell_fp8_default`: just a basic gen, with Flux Schnell (fp8 checkpoint format)
