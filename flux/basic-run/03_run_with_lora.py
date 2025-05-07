import os
import torch
from diffusers import FluxPipeline
from datetime import datetime

# Choose model
model_id = "/mnt/mydisk/models/hub/models--black-forest-labs--FLUX.1-dev/snapshots/0ef5fff789c832c5c7f4e127f94c8b54bbcced44"

pipe = FluxPipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)

# lora_dir = "output/my_first_flux_lora_v1"
# weight_name = "my_first_flux_lora_v1_000001750.safetensors"

# lora_dir = "output/jr_diandian_flux_lora_v1"
# weight_name = "jr_diandian_flux_lora_v1_000001750.safetensors"

# pipe.load_lora_weights(lora_dir, weight_name=weight_name)
pipe.enable_model_cpu_offload()

# List of prompts, Pikachu, Yorkshire Terrier
prompts = [
    "A women is holding a puppy, a young baby Yorkshire Terrier, by the riverbank. side by her ,a man hold a cat, The image shows the women's upper body, The girl's face is clear. and she is wearing a dress. The graininess of the photo. Clear, high-resolution, with a Japanese-style fresh color palette.",
]

seed = 45
num_inference_steps = 23

# Specify the directory
output_dir = "./imgs/"
os.makedirs(output_dir, exist_ok=True)

for prompt in prompts:
    # Use current timestamp for each image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{timestamp}.jpg")

    print(
        f"Prompt: {prompt}\nRandom seed: {seed}\nNumber of inference steps: {num_inference_steps}\nOutput file name: {output_file}")

    image = pipe(
        prompt,
        output_type="pil",
        num_inference_steps=num_inference_steps,
        generator=torch.Generator("cpu").manual_seed(seed)
    ).images[0]

    image.save(output_file)
    print(f"Image saved to {output_file}")
