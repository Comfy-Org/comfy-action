# start-server.ps1
param (
    [String]$GITHUB_WORKSPACE
)

# Initialize Conda environment
# TODO: remove hardcoding
& conda activate comfyui

# Start the web server and redirect output to a log file
& python "$GITHUB_WORKSPACE/main.py" --force-fp16 *> "$GITHUB_WORKSPACE/application.log"