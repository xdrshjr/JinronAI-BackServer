from diffusers import AutoPipelineForText2Image
import torch

pipeline = AutoPipelineForText2Image.from_pretrained('black-forest-labs/FLUX.1-dev', torch_dtype=torch.bfloat16).to('cuda')
pipeline.load_lora_weights('openfree/flux-chatgpt-ghibli-lora', weight_name='flux-chatgpt-ghibli-lora.safetensors')
image = pipeline('a boy and a girl looking out of a window with a cat perched on the window sill. There is a bicycle parked in front of them and a plant with flowers to the right side of the image. The wall behind them is visible in the background. ').images[0]
image.save("./img/my_image.png")
