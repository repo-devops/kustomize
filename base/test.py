import os
import subprocess
import zipfile
from datetime import datetime, timedelta

# Define namespaces
namespaces = ['data-fabric']

# Get logs for the last 7 days
start_time = (datetime.now() - timedelta(days=7)).isoformat()

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Iterate over namespaces
for namespace in namespaces:
    try:
        # Check if namespace exists
        check_ns = f"kubectl get ns {namespace}"
        subprocess.check_output(check_ns, shell=True)

        # Get all pod names in the namespace
        command = f"kubectl get pods -n {namespace} -o jsonpath='{{{{.items[*].metadata.name}}}}'"
        pods_output = subprocess.check_output(command, shell=True, text=True).strip()
        pod_names = pods_output.split()

        # Prepare ZIP file for logs
        with zipfile.ZipFile("logs.zip", "a", zipfile.ZIP_DEFLATED) as zip_file:
            for pod_name in pod_names:
                try:
                    # Fetch logs for the last 7 days
                    logs_command = (
                        f"kubectl logs {pod_name} -n {namespace} --since-time={start_time}"
                    )
                    logs_output = subprocess.check_output(logs_command, shell=True, text=True)

                    # Save logs to file
                    log_file_path = f"logs/{pod_name}.yaml"
                    with open(log_file_path, "w") as log_file:
                        log_file.write(logs_output)

                    # Add the log file to the ZIP archive
                    zip_file.write(log_file_path, arcname=f"{pod_name}.yaml")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to fetch logs for pod {pod_name}: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Namespace check failed for {namespace}: {e}")

print("Log collection complete.")