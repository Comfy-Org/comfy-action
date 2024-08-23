import argparse, datetime, json, os, sys, pprint, re, subprocess, requests, platform, psutil, traceback, threading, time
from enum import Enum
from google.cloud import storage


# Reference: https://github.com/Comfy-Org/registry-backend/blob/main/openapi.yml#L2031
class WfRunStatus(Enum):
    Started = "WorkflowRunStatusStarted"
    Failed = "WorkflowRunStatusFailed"
    Completed = "WorkflowRunStatusCompleted"

def get_gpu():
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        return gpus[0] if gpus else None
    except:
        return None

def get_gpu_info():
    try:
        gpu = get_gpu()
        return gpu.name if gpu else "No GPU detected"
    except:
        return "Unable to detect GPU"

def get_pip_freeze():
    try:
        return subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode('utf-8')
    except:
        traceback.print_exc()
        return "Unable to get pip freeze output"

def measure_vram(vram_time_series, stop_event):
    stopped_for = 0
    while True:
        gpu = get_gpu()
        vram_time_series.append(gpu.memoryUsed if gpu else -1)
        time.sleep(0.5)
        if stop_event.is_set():
            stopped_for += 1
            if stopped_for > 2:
                break

# https://github.com/Comfy-Org/registry-backend/blob/main/openapi.yml#L2037
machine_stats = {
    "machine_name": platform.node(),
    "os_version": f"{platform.system()} {platform.release()}",
    "gpu_type": get_gpu_info(),
    "cpu_capacity": f"{psutil.cpu_count()} cores",
    "initial_cpu": f"{psutil.cpu_count() - psutil.cpu_count(logical=False)} cores available",
    "memory_capacity": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
    "initial_ram": f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB available",
    "vram_time_series": {},
    "disk_capacity": f"{psutil.disk_usage('/').total / (1024 ** 3):.2f} GB",
    "initial_disk": f"{psutil.disk_usage('/').free / (1024 ** 3):.2f} GB available",
    "pip_freeze": get_pip_freeze()
}

def read_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def post_json_to_server(json_data, url):
    return requests.post(url, json=json_data)


def get_status(prompt_id, url):
    response = requests.get(f"{url}/{prompt_id}")
    if response.status_code == 200:
        return response.json()
    return None


def make_unix_safe(filename):
    # Replace spaces with underscores
    safe_filename = filename.replace(" ", "_")

    # Remove any characters that are not alphanumeric, underscores, or hyphens
    safe_filename = re.sub(r'[^\w\-\.]', '', safe_filename)

    return safe_filename

def is_completed(status_response, prompt_id):
    # Check if the expected fields exist in the response
    return (
        status_response
        and prompt_id in status_response
        and "status" in status_response[prompt_id]
        and status_response[prompt_id]["status"].get("completed", False)
    )


def upload_to_gcs(bucket_name: str, destination_blob_name: str, source_file_name: str):
    print(f"Uploading file {source_file_name} to GCS bucket {bucket_name} as {destination_blob_name}")
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}")


def send_payload_to_api(args, output_files_gcs_paths, workflow_name, start_time, end_time, vram_time_series, status=WfRunStatus.Completed):

    is_pr = args.branch_name.endswith("/merge")
    pr_number = None
    if is_pr:
        pr_number = args.branch_name.split("/")[0]

    # Create the payload as a dictionary
    # Should be mapping to https://github.com/Comfy-Org/registry-backend/blob/main/openapi.yml#L26

    local_machine_stats = machine_stats.copy()

    local_machine_stats["vram_time_series"] = {f"{i / 2} seconds": f"{int(vram_time_series[i])} MiB" for i in range(len(vram_time_series))}
    avg_vram = 0
    peak_vram = 0
    if -1 in vram_time_series:
        avg_vram = -1
        peak_vram = -1
    else:
        avg_vram = sum(vram_time_series) / len(vram_time_series)
        peak_vram = max(vram_time_series)

    payload = {
        "repo": args.repo,
        "job_id": args.job_id,
        "run_id": args.run_id,
        "os": args.os,
        "cuda_version": args.cuda_version,
        "bucket_name": args.gsc_bucket_name,
        "output_files_gcs_paths": output_files_gcs_paths,
        # TODO: support comfy logs
        # "comfy_logs_gcs_path":
        "commit_hash": args.commit_hash,
        "commit_time": args.commit_time,
        "commit_message": args.commit_message,
        "workflow_name": workflow_name,
        "branch_name": args.branch_name,
        "start_time": start_time,
        "end_time": end_time,
        "avg_vram": int(avg_vram),
        "peak_vram": int(peak_vram),
        "pr_number": pr_number,
        # TODO: support PR author
        # "author": args.,
        "job_trigger_user": args.job_trigger_user,
        "comfy_run_flags": args.comfy_run_flags,
        "python_version": args.python_version,
        "pytorch_version": args.torch_version,
        "status": status.value,
        "machine_stats": local_machine_stats
    }

    # Convert payload dictionary to a JSON string
    payload_json = json.dumps(payload)

    # Send POST request
    headers = {"Content-Type": "application/json"}
    response = requests.post(args.api_endpoint, headers=headers, data=payload_json)
    print("#### Payload ####")
    pprint.pprint(payload)
    print("#### Response ####")
    try:
        pprint.pprint(response.json())
    except json.JSONDecodeError:
        print(f"Invalid JSON: {response.text}")

    # Write response to application.log
    log_file_path = "./application.log"
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        log_file.write("\n##### Comfy CI Post Response #####\n")
        log_file.write(response.text)

    # Check the response code
    if response.status_code != 200:
        print(f"API request failed with status code {response.status_code} and response body")
        print(response.text)
        exit(1)
    else:
        print("API request successful")

    return response.status_code


def parse_raw_output(full_output):
    """
        This is a hack, because we're not calling the Comfy JSON API directly, we need to reparse the output list from the Comfy-CLI text dump.
        TODO: Comfy-CLI should be able to yield usable JSONs directly instead of this cursed manual parse
    """
    outputs_start = full_output.find('Outputs:')
    if outputs_start == -1:
        return None

    output = full_output[outputs_start + len('Outputs:'):].replace('\r', '\n').strip()

    outputnl = output.find('\n')
    if outputnl != -1:
        output = output[:outputnl]

    lines = output.split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    filenames = []
    for line in lines:
        fnind = line.find('filename=')
        if fnind == -1:
            continue
        fnstart = fnind + len('filename=')
        fnend = line.find('&', fnstart)
        if fnend == -1:
            fnend = len(line)
        filenames.append(line[fnstart:fnend])

    return filenames


def main(args):
    # Split the workflow file names using ","
    workflow_files = args.comfy_workflow_names.split(",")
    print("Running workflows")
    counter = 1

    for workflow_file_name in workflow_files:
        gs_path = make_unix_safe(f"output-files/{args.github_action_workflow_name}-{args.os}-{args.python_version}-{args.cuda_version}-{args.torch_version}-{workflow_file_name}-run-{args.run_id}")
        #send_payload_to_api(args, gs_path, workflow_file_name, 0, 0, WfRunStatus.Started)
        file_path = f"workflows/{workflow_file_name}"

        print(f"Running workflow {file_path}")
        start_time = int(datetime.datetime.now().timestamp())
        output_filenames = []

        stop_event = threading.Event()
        vram_time_series = []
        vram_thread = threading.Thread(target=measure_vram, args=(vram_time_series, stop_event))
        vram_thread.start()

        try:
            result = subprocess.run(
                [
                    "comfy", "--skip-prompt", "--no-enable-telemetry",
                    "run",
                    "--workflow", file_path,
                    "--timeout", "600" # 10min timeout for workflow
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ,
            )

            stop_event.set()
            vram_thread.join()

            full_output = f"{result.stdout}"
            print(f"stdout: {full_output}")
            print(f"stderr: {result.stderr}")
            output_filenames = parse_raw_output(full_output)
            if output_filenames is None:
                if not os.path.exists(f"{args.workspace_path}/output/{args.output_file_prefix}_{counter:05}_.png"):
                    raise RuntimeError("Invalid output from Comfy-CLI, no outputs found")
                output_filenames = [f"{args.output_file_prefix}_{counter:05}_.png"]

        except subprocess.CalledProcessError as e:
            send_payload_to_api(args, gs_path, workflow_file_name, start_time, int(datetime.datetime.now().timestamp()), vram_time_series, WfRunStatus.Failed)
            print("Error STD Out:", e.stdout)
            print("Error:", e.stderr)
            raise e

        print(f"Workflow {file_path} completed")
        end_time = int(datetime.datetime.now().timestamp())

        for filename in output_filenames:
            upload_to_gcs(args.gsc_bucket_name, gs_path, f"{args.workspace_path}/output/{filename}")

        send_payload_to_api(args, gs_path, workflow_file_name, start_time, end_time, vram_time_series, WfRunStatus.Completed)
        counter += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a JSON file contents to a server as a prompt.")
    parser.add_argument("--api-endpoint", type=str, help="API endpoint.")
    parser.add_argument("--comfy-workflow-names", type=str, help="List of comfy workflow names.")
    parser.add_argument("--github-action-workflow-name", type=str, help="Github action workflow name.")
    parser.add_argument("--os", type=str, help="Operating system.")
    parser.add_argument("--run-id", type=str, help="Github Run ID.")
    parser.add_argument("--job-id", type=str, help="Github Run Job ID.")
    parser.add_argument("--job-trigger-user", type=str, help="User who triggered the job")
    parser.add_argument("--comfy-run-flags", default="", nargs='?', type=str, help="Comfy run flags.")
    parser.add_argument("--repo", type=str, help="Github repo.")
    parser.add_argument("--cuda-version", type=str, help="CUDA version.")
    parser.add_argument("--python-version", type=str, help="Python version.")
    parser.add_argument("--torch-version", type=str, help="Torch version.")
    parser.add_argument("--commit-hash", type=str, help="Commit hash.")
    parser.add_argument("--commit-time", type=str, help="Commit time.")
    parser.add_argument("--commit-message", type=str, help="Commit message.")
    parser.add_argument("--branch-name", type=str, help="Branch name.")
    parser.add_argument("--gsc-bucket-name", type=str, help="Name of the GCS bucket to store the output files in.")
    parser.add_argument("--workspace-path", type=str, help="Workspace (ComfyUI repo) path, likely ${HOME}/action_runners/_work/ComfyUI/ComfyUI/.")
    parser.add_argument("--action-path", type=str, help="Action path., likely ${HOME}/action_runners/_work/comfy-action/.")
    parser.add_argument("--output-file-prefix", type=str, help="Output file prefix.")

    args = parser.parse_args()
    main(args)
