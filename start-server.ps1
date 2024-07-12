# start-server.ps1
param (
    [String]$GITHUB_WORKSPACE,
    [String]$RunFlags,
    [String]$CondaEnv
)

# Initialize Conda environment
# TODO: remove hardcoding
echo "Starting Conda"
conda activate "$CondaEnv"

# Start the web server and redirect output to a log file
echo "Running Server"
echo "python" "$GITHUB_WORKSPACE/main.py" $RunFlags
python "$GITHUB_WORKSPACE/main.py" $RunFlags *> "$GITHUB_WORKSPACE/application.log"

echo "Done"
