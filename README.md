# comfy-action

[![Verify GitHub Action YML](https://github.com/Comfy-Org/comfy-action/actions/workflows/verify-action.yml/badge.svg)](https://github.com/Comfy-Org/comfy-action/actions/workflows/verify-action.yml)

Sets up ComfyUI on Github Action Runner and execute a workflow json.

This is meant to be run in the ComfyUI repository.

### Set up your local self-hosted runner

- Follow the steps here: https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners

### Modify the script to run your workflow

- Remember to ALWAYS ALWAYS add `[Win]` or `[Unix]` to the step name
- Use `[Win-Only]` for Windows only steps
- Use `[Unix-Only]` for Unix only steps

### Test running the workflow

- Manually run the action.py script
```bash
python action.py \
  --comfy-workflow-names="default.json,lora.json" \
  --github-action-workflow-name="test" \
  --os=mac \
  --run-id=10 \
  --repo=fake-repo \
  --cuda-version=12.1 \
  --commit-hash=12345 \
  --commit-time="2024-06-12T01:07:58-04:00" \
  --commit-message="test message" \
  --branch-name="main" \
  --gsc-bucket-name="comfy-ci-results" \
  --workspace-path=/Users/yoland/Code/ComfyUI \
  --output-file-prefix="ComfyUI" \
  --api-endpoint="http://localhost:8080/upload-artifact" # Need you to spin up a local CI backend server to receive the artifact 
```
- Create a temporary workflow json in Comfy repo to use your action branch e.g.
  `uses comfy-org/comfy-action@<branch-name>`

### Make sure to verify using action_yaml_checker.py

Run the following command to verify the action.yml file:

```bash
python action_yaml_checker.py action.yml
```

And you can get something like this to manually verify the steps are consistent

```
╒═══════════════════════════════════════╤══════════════════════════════════════╕
│ Unix                                  │ Windows                              │
╞═══════════════════════════════════════╪══════════════════════════════════════╡
│ [Unix] Auth to GCS                    │ [Win] Auth to GCS                    │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ [Unix] Setup Conda                    │ [Win] Setup Conda                    │
├───────────────────────────────────────┼──────────────────────────────────────┤
│                                       │ [Win-Only] Install Pytorch           │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ [Unix] Install dependencies           │ [Win] Install dependencies           │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ [Unix] Check conda environment        │ [Win] Check conda environment        │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ [Unix] Download models                │ [Win] Download models                │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ [Unix] Run ComfyUI                    │ [Win] Run ComfyUI                    │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ [Unix] Check if the server is running │ [Win] Check if the server is running │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ [Unix] Get Commit Details             │ [Win] Get Commit Details             │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ [Unix] Run Python Action              │ [Win] Run Python Action              │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ [Unix] Upload Output Files            │ [Win] Upload Output Files            │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ [Unix] Upload log file                │ [Win] Upload log file                │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ [Unix] Cleanup output files only      │ [Win] Cleanup output files only      │
╘═══════════════════════════════════════╧══════════════════════════════════════╛
```

You can also do `-c` for complete step list and `-k` for key it looks up (e.g.
`uses`, `if`, `run`, `shell`), and fallback key for if the key is not available

```bash
python action_yaml_checker.py -c -k shell --fallback-key uses action.yml
```

You will get the name of the step and also the shell it uses (or if shell is not
available for the step, then "uses" info)

```
╒═══════════════════════════════════════╤════════════════════════════════════════╕
│ Unix                                  │ Windows                                │
╞═══════════════════════════════════════╪════════════════════════════════════════╡
│ [Unix] Auth to GCS                    │ [Win] Auth to GCS                      │
│ google-github-actions/auth@v2         │ google-github-actions/auth@v2          │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ [Unix] Setup Conda                    │ [Win] Setup Conda                      │
│ conda-incubator/setup-miniconda@v3    │ conda-incubator/setup-miniconda@v3.0.3 │
├───────────────────────────────────────┼────────────────────────────────────────┤
│                                       │ [Win-Only] Install Pytorch             │
│                                       │ powershell                             │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ [Unix] Install dependencies           │ [Win] Install dependencies             │
│ bash -el {0}                          │ powershell                             │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ [Unix] Check conda environment        │ [Win] Check conda environment          │
│ bash -el {0}                          │ powershell                             │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ [Unix] Download models                │ [Win] Download models                  │
│ bash -el {0}                          │ powershell                             │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ [Unix] Run ComfyUI                    │ [Win] Run ComfyUI                      │
│ bash -el {0}                          │ powershell                             │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ [Unix] Check if the server is running │ [Win] Check if the server is running   │
│ bash -el {0}                          │ powershell                             │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ [Unix] Get Commit Details             │ [Win] Get Commit Details               │
│ bash -el {0}                          │ powershell                             │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ [Unix] Run Python Action              │ [Win] Run Python Action                │
│ bash -el {0}                          │ powershell                             │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ [Unix] Upload Output Files            │ [Win] Upload Output Files              │
│ actions/upload-artifact@v4            │ actions/upload-artifact@v4             │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ [Unix] Upload log file                │ [Win] Upload log file                  │
│ actions/upload-artifact@v4            │ actions/upload-artifact@v4             │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ [Unix] Cleanup output files only      │ [Win] Cleanup output files only        │
│ bash -el {0}                          │ powershell                             │
╘═══════════════════════════════════════╧════════════════════════════════════════╛
```