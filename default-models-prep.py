import os, requests, argparse, hashlib, shutil
from tqdm import tqdm


MODELS = {
    "checkpoints/v1-5-pruned-emaonly.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/resolve/c36740b77a55ec396ace7c8c26589cdf2b4bc3da/v1-5-pruned-emaonly.safetensors",
        "hash": "6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa"
    },
    "loras/epiNoiseoffset_v2.safetensors": {
        "url": "https://huggingface.co/adhikjoshi/epi_noiseoffset/resolve/e018bf906acfcd139ca23553ea2c6ea9f5fd65fd/epiNoiseoffset_v2.safetensors",
        "hash": "81680c064e9f50dfcc11ec5e25da1832f523ec84afd544f372c7786f3ddcbbac"
    },
    "clip/clip_l.safetensors": {
        "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/8e77bf03ec19bd890923edca2982516a1bdd92bc/text_encoder/model.fp16.safetensors",
        "hash": "660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd"
    },
    "clip/clip_g.safetensors": {
        "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/8e77bf03ec19bd890923edca2982516a1bdd92bc/text_encoder_2/model.fp16.safetensors",
        "hash": "ec310df2af79c318e24d20511b601a591ca8cd4f1fce1d8dff822a356bcdb1f4"
    },
    "clip/t5xxl_fp8_e4m3fn.safetensors": {
        "url": "https://huggingface.co/mcmonkey/google_t5-v1_1-xxl_encoderonly/resolve/50d42fdb91a03fb7b6d2b9f395bbaa11482086c9/t5xxl_fp8_e4m3fn.safetensors",
        "hash": "7d330da4816157540d6bb7838bf63a0f02f573fc48ca4d8de34bb0cbfd514f09"
    },
    "checkpoints/sd_xl_base_1.0.safetensors": {
        "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/462165984030d82259a11f4367a4eed129e94a7b/sd_xl_base_1.0.safetensors",
        "hash": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b"
    },
    "controlnet/control-lora-sketch-rank128-metadata.safetensors": {
        "url": "https://huggingface.co/stabilityai/control-lora/resolve/75590eb0e7868d3d0f1581b5126d487b33c7fdb4/control-LoRAs-rank128/control-lora-sketch-rank128-metadata.safetensors",
        "hash": "679c616807aec73c47bb7281a24a76ddfe52fa5b5d68532f542ab813347b2eae"
    },
    # SD3 gate blocks autodownload, but HF allows this other to stay up - the hash check will verify nothing weird happened
    "checkpoints/sd3_medium.safetensors": {
        "url": "https://huggingface.co/adamo1139/stable-diffusion-3-medium-ungated/resolve/74b6131496fceb9f896c2e3d6465c2241ea22ae6/sd3_medium.safetensors",
        "hash": "cc236278d28c8c3eccb8e21ee0a67ebed7dd6e9ce40aa9de914fa34e8282f191"
    },
    "checkpoints/flux1-schnell-fp8.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/flux1-schnell/resolve/f2808ab17fe9ff81dcf89ed0301cf644c281be0a/flux1-schnell-fp8.safetensors",
        "hash": "ead426278b49030e9da5df862994f25ce94ab2ee4df38b556ddddb3db093bf72"
    }
}


def download_model(url, path, model_name, expected_hash):
    print(f"Downloading {model_name} from {url}...")

    temp_file_path = os.path.join(path, f"{model_name}.tmp")
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

    hash_tracker = hashlib.sha256()

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))

        with tqdm(total=total_size, unit="B", unit_scale=True, mininterval=2) as progress_bar:
            with open(temp_file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    hash_tracker.update(chunk)
                    progress_bar.update(len(chunk))

        if total_size != 0 and progress_bar.n != total_size:
            raise RuntimeError("Could not download file")

    file_hash = hash_tracker.hexdigest()
    if expected_hash != file_hash:
        raise RuntimeError(f"Hash mismatch for {model_name} - expected {expected_hash} but got {file_hash}")

    os.rename(temp_file_path, os.path.join(path, model_name))
    print(f"Downloaded {model_name}.")


def main(args):
    cache_dir = args.cache_directory
    live_dir = args.live_directory
    for model_name, model_info in MODELS.items():
        cache_target = os.path.join(cache_dir, model_name)
        os.makedirs(os.path.dirname(cache_target), exist_ok=True)
        if not os.path.exists(cache_target):
            download_model(model_info['url'], cache_dir, model_name, model_info['hash'])
        live_target = os.path.join(live_dir, model_name)
        os.makedirs(os.path.dirname(live_target), exist_ok=True)
        if not os.path.exists(live_target):
            try:
                if args.copy_models:
                    raise OSError("Copying requested")  # Skip symlink attempt
                os.symlink(cache_target, live_target)
                print(f"Linked {model_name} to {live_target}.")
            except:
                shutil.copyfile(cache_target, live_target)
                print(f"Copied {model_name} to {live_target}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download and prepare the standard models the Comfy Action Runner tests against."
    )
    parser.add_argument(
        "--cache-directory", help="Cache directory where models will be downloaded."
    )
    parser.add_argument(
        "--live-directory", help="Directory where models will be placed for live usage."
    )
    parser.add_argument(
        "--copy-models", help="Copy models to the live directory instead of symlinking them."
    )

    args = parser.parse_args()
    main(args)
