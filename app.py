import os
import gradio as gr
import pandas as pd
import json
from functools import cache
import subprocess
from io import StringIO

SINFO_PATH = "sinfo.txt"
SINFO2_PATH = "sinfo2.txt"
SQUEUE_PATH = "squeue.txt"
SACCT_PATH = "sacct.txt"
SETTINGS_PATH = "config/settings.json"

SLURM_BASE_CMD = "bash"
# Load settings from JSON file
if os.path.exists(SETTINGS_PATH):
    with open(SETTINGS_PATH, 'r') as f:
        settings = json.load(f)
        SLURM_BASE_CMD = settings["slurm_base_cmd"]


def run_cmd(cmd):
    """Run a command and return the output."""
    full_cmd = SLURM_BASE_CMD + " -c " + cmd
    print(f"Running command: {full_cmd}")
    result = subprocess.check_output(full_cmd, shell=True, text=True)
    print("Command done")
    return result

def read_slurm_csv(path, **kwargs):
    df = pd.read_csv(path, **kwargs)
    for col in df.columns:
        if df[col].dtype == 'object':  # Check if the column is of type 'object' (string)
            df[col] = df[col].str.strip()
    df.columns = df.columns.str.strip()  # Strip whitespace from column names
    return df

def read_cluster_data():
    result = run_cmd("sinfo")
    return read_slurm_csv(StringIO(result), sep='\s+')

def read_running_jobs():
    result = run_cmd("'squeue -u $LOGNAME --format=%all'")
    print(result)
    df = read_slurm_csv(StringIO(result), sep="|")
    df = df[['JOBID', 'USER', 'PARTITION', 'NAME', 'STATE', 'TIME', 'NODES', 'NODELIST']]
    return df

def read_historical_jobs():
    result = run_cmd("'sacct --format=%all -P'")
    df = read_slurm_csv(StringIO(result), sep="|")
    # JobID           JobName  Partition    Account  AllocCPUS      State ExitCode 
    df = df[['JobID', 'JobName', 'Partition', 'Account', 'AllocCPUS', 'State', 'ExitCode']]
    return df

with gr.Blocks(title="Cluster Helper", fill_width=True) as demo:
        with gr.Tab("Running Jobs"):
            with gr.Row():
                gr.Markdown("# Running Jobs")
                gr.Markdown("Command: `queue -u $LOGNAME`")
                refresh_running_jobs = gr.Button("Refresh", size="sm", scale=0)
            running_jobs_output = gr.DataFrame(read_running_jobs())
            refresh_running_jobs.click(fn=read_running_jobs, outputs=running_jobs_output)

        with gr.Tab("Historical Jobs"):
            with gr.Row():
                gr.Markdown("# Historical Jobs")
                gr.Markdown("Command: `sacct`")
                refresh_historical_jobs = gr.Button("Refresh", size="sm", scale=0)
            historical_jobs_output = gr.DataFrame(read_historical_jobs())
            refresh_historical_jobs.click(fn=read_historical_jobs, outputs=historical_jobs_output)

        with gr.Tab("Cluster"):
            with gr.Row():
                gr.Markdown("# Cluster Information")
                gr.Markdown("Command: `sinfo`")
                refresh_cluster = gr.Button("Refresh", size="sm", scale=0)
            cluster_output = gr.DataFrame(read_cluster_data(), interactive=False)
            refresh_cluster.click(fn=read_cluster_data, outputs=cluster_output)




if __name__ == "__main__":
    port = int(os.environ.get("GRADIO_SERVER_PORT"))
    host = os.environ.get("GRADIO_HOST")
    root_path = f"/node/{host}/{port}"
    demo.launch(server_port=port, server_name="0.0.0.0", root_path=root_path)
