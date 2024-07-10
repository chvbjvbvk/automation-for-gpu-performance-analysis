import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_traces(trace_files):
    # Assuming trace_files is a list of paths to AQL/PM4 trace files
    for file in trace_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Trace file {file} does not exist.")
    return trace_files

def replay_trace(trace_file, work_area):
    # Assuming there is a script `replay.py` that handles the replay
    subprocess.run(['python', 'replay.py', trace_file, work_area], check=True)
    return trace_file  # Return the trace file to identify which trace was processed

def capture_intents(work_area):
    # Assuming there is a script `intent_capture.py` that handles intent capturing
    subprocess.run(['python', 'intent_capture.py', work_area], check=True)

def generate_test_directory(source_dir, test_dir):
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    for filename in ['sp3', 'command.txt', 'intent_capture', 'intent.cpp', 'tcore.log']:
        src_file = os.path.join(source_dir, filename)
        if os.path.exists(src_file):
            shutil.copy(src_file, test_dir)
        else:
            print(f"Warning: {filename} not found in {source_dir}.")

def main(trace_files, work_area, test_dir):
    try:
        traces = load_traces(trace_files)
        
        # Replay traces in parallel
        with ThreadPoolExecutor() as executor:
            future_to_trace = {executor.submit(replay_trace, trace, work_area): trace for trace in traces}
            for future in as_completed(future_to_trace):
                trace = future_to_trace[future]
                try:
                    future.result()  # Ensure no exceptions were raised
                    print(f"Replay completed for trace: {trace}")
                except Exception as e:
                    print(f"An error occurred during replay of {trace}: {e}")
        
        capture_intents(work_area)
        generate_test_directory(work_area, test_dir)
        print(f"Test directory generated successfully at {test_dir}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    trace_files = ['path/to/trace1.aql', 'path/to/trace2.pm4']  # Update with actual trace file paths
    work_area = 'path/to/work_area'  # Update with the actual work area path
    test_dir = 'path/to/test_dir'  # Update with the actual test directory path
    main(trace_files, work_area, test_dir)
