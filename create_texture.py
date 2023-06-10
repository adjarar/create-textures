import discord
import requests
import argparse
import os
import json
import shutil
import time
import glob
import subprocess
from upload_to_fileio import upload_to_fileio
from txt2img_batch_generate import txt2img_batch_generate

webhook = discord.SyncWebhook.partial(1108891310351470662, '5Q-A_WqDX7Iiu6Y30oyifxGHdfL2PeErrW0MWA5kFjRTcGXbMv_Sv6NmtXhIwiOX0hf_')
poll_interval = 5

parser = argparse.ArgumentParser(description="txt2img script")
parser.add_argument("--sd_url", type=str, default="http://localhost:7860", help="Stable Diffusion URL")
parser.add_argument("--steps", type=int, default=5, help="Number of steps")
parser.add_argument("--batch_size", type=int, default=1, help="Batch size")
parser.add_argument("--iterations", type=int, default=1, help="Number of iterations")
parser.add_argument('--destroy_pod', action='store_true', help='Destroy the pod when the script finshed executing')
parser.add_argument("--upload", action="store_true", help="upload the outputs to fileio")
parser.add_argument("--output_dir", type=str, default=os.path.join(os.getcwd(), "output"), help="Output directory path")
parser.add_argument("--prompts_dir", type=str, default=os.path.join(os.getcwd(), "prompts"), help="the prompts directory")
parser.add_argument("--verbose", action="store_true", default=False)
parser.add_argument("--destroy", action="store_true", default=False)

args = parser.parse_args()

prompts_dir = args.prompts_dir
output_dir = args.output_dir

os.makedirs(prompts_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)


# continue working as long as there are prompts in the prompt dir
while True:

    prompt_paths = glob.glob(os.path.join(prompts_dir, "*.json"))

    if len(prompt_paths) > 0:

        # loads the json prompts
        with open(prompt_paths[0], 'r') as prompts_file:
            prompts_file = json.load(prompts_file)
        
        # put the json elements in a variable
        prompts_name = prompts_file["name"]
        prompts = prompts_file["prompts"]

        print(f"Starting work on {prompts_name}.")

        # loads the correct model
        requests.post(url=f'{args.sd_url}/sdapi/v1/options', json={"sd_model_checkpoint": "sxzLuma_097.safetensors [3709e3c3c9]",
                                                                   "sd_vae": "vae-ft-mse-840000-ema-pruned.ckpt",})

        print(f"Generating {prompts_name} images...")
        txt2img_batch_generate(args.sd_url, prompts, output_dir, prompts_name, args.steps, args.batch_size, args.iterations, args.verbose)

        # zip and upload the folder
        if args.upload:
            shutil.make_archive(output_dir, 'zip', output_dir)
           
            print(f"Uploading {prompts_name} with_bg images to file.io.")
            file_url = upload_to_fileio(output_dir + ".zip")
            print(f"Done uploading {prompts_name} with_bg images to file.io.")
            webhook.send(f'Finished generating {prompts_name} images. Download: {file_url}', username='Image Generator')


        # prompt file is no longer needed delete it
        os.remove(prompt_paths[0])
        print(f"Finished work on {prompts_name}.")

        if len(os.listdir(prompts_dir)) == 0:
            webhook.send("Finished all work, waiting for more.", username="Done")

    elif args.destroy_pod:
        break

    if args.verbose:
        
        if  args.destroy:
            print("Destroying pod...")
            subprocess.run("./vast destroy instance ${VAST_CONTAINERLABEL:2}", shell=True)

        print("Waiting for work")
    
    time.sleep(poll_interval)