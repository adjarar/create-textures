import argparse
import json
import os
import requests
import discord
from sd_api_tools import *


def txt2img_batch_generate(sd_url: str, prompts: json, output_dir: str,
                            prefix: str, steps: int, batch_size: int, iterations: int, verbose=False,
                            sampler="DPM++ 2M Karras"):
    """
        Takes a json file of prompts and runs them through txt2img.
    """
    for prompt_number, prompt in enumerate(prompts, start=1):
        payload = {
            "enable_hr": True,
            "denoising_strength": 0.7,
            "hr_scale": 2,
            "hr_upscaler": "Latent",
            "steps": steps,
            "hr_second_pass_steps": steps,
            "batch_size": batch_size,
            "n_iter": iterations,
            "prompt": prompt,
            "negative_prompt": "text signature",
            "sampler_name": sampler,
        }

        response_json = response2json(sd_url, 'txt2img', payload)

        for i, encoded_img in enumerate(response_json['images']):
            # this prevents saving the controlnet masks
            if i == batch_size * iterations:
                break

            decoded_img = decode_img(encoded_img)
            output_file = os.path.join(output_dir, "_".join([prefix, str(prompt_number), str(i)])) + '.png'
            decoded_img.save(output_file)

        if verbose:
            print(f"Done processing prompt: {prompt} ({prompt_number} / {len(prompts)})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="txt2img script")
    parser.add_argument("--sd_url", type=str, default="http://localhost:7860", help="URL for the service")
    parser.add_argument("--prompts", type=str, required=True, help="Path to the JSON file containing prompts")
    parser.add_argument("--output_dir_with_bg", type=str, default=os.path.join(os.getcwd(), "with_bg"), help="Output directory")
    parser.add_argument("--output_dir_without_bg", type=str, default=os.path.join(os.getcwd(), "without_bg"), help="Output directory")
    parser.add_argument("--prefix", type=str, default="", help="optional string for identification")
    parser.add_argument("--steps", type=int, default=5, help="Number of steps")
    parser.add_argument("--batch_size", type=int, default=1, help="Batch size")
    parser.add_argument("--iterations", type=int, default=1, help="Number of iterations")
    parser.add_argument("--verbose", action="store_true", default=False)

    args = parser.parse_args()

    with open(args.prompts, 'r') as prompts_file:
        prompts = json.load(prompts_file)

    requests.post(url=f'{args.sd_url}/sdapi/v1/options', json={"sd_model_checkpoint": "fantassifiedIcons_fantassifiedIconsV20.safetensors [8340e74c3e]"})

    txt2img_batch_generate(args.sd_url, prompts, args.output_dir_with_bg, args.prefix,
                     args.steps, args.batch_size, args.iterations, args.verbose)
    
    webhook = discord.SyncWebhook.partial(1108891310351470662, '5Q-A_WqDX7Iiu6Y30oyifxGHdfL2PeErrW0MWA5kFjRTcGXbMv_Sv6NmtXhIwiOX0hf_')
    webhook.send('Finnished generating images', username='Image Generator')