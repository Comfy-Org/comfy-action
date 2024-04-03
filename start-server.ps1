# start-server.ps1

# Initialize Conda environment
# TODO: remove hardcoding
$Env:Path = "C:\Users\yoland68\miniconda3\shell\condabin;" + $Env:Path
& conda activate comfyui

# Start the web server and redirect output to a log file
python "$Env:GITHUB_WORKSPACE/main.py" --force-fp16 *> "application.log"