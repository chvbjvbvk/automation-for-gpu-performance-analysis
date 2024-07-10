import os
import subprocess
import argparse
import csv
import joblib

MODEL_PATH = 'performance_model.pkl'

def parse_arguments():
    parser = argparse.ArgumentParser(description='Regression Setup for Gist Runs with AI Integration')
    parser.add_argument('--test_dirs', required=True, nargs='+', help='List of test directories')
    parser.add_argument('--model_paths', required=True, nargs='+', help='List of model build paths')
    parser.add_argument('--hash_enabled', type=bool, default=False, help='Enable or disable hash')
    parser.add_argument('--gc_clock_freq', type=int, required=True, help='GC clock frequency')
    parser.add_argument('--sbm_clock_freq', type=int, required=True, help='SBM clock frequency')
    parser.add_argument('--wr_rd_latency', type=int, required=True, help='Write/Read latency')
    parser.add_argument('--gist_script', required=True, help='Path to the existing Gist run Python script')
    args = parser.parse_args()
    return args

def predict_performance(configs, model):
    # Predict performance metrics using the trained model
    prediction = model.predict([configs])
    return prediction[0]

def run_single_gist(test_dir, model_path, hash_enabled, gc_clock_freq, sbm_clock_freq, wr_rd_latency, gist_script):
    env = os.environ.copy()
    env['MODEL_PATH'] = model_path
    env['HASH_ENABLED'] = str(hash_enabled)
    env['GC_CLOCK_FREQ'] = str(gc_clock_freq)
    env['SBM_CLOCK_FREQ'] = str(sbm_clock_freq)
    env['WR_RD_LATENCY'] = str(wr_rd_latency)
    
    result = subprocess.run(['python', gist_script, '--test_dir', test_dir], capture_output=True, text=True, env=env)
    return result

def run_regression(test_dirs, model_paths, hash_enabled, gc_clock_freq, sbm_clock_freq, wr_rd_latency, gist_script, model):
    results = []
    for model_path in model_paths:
        for test_dir in test_dirs:
            print(f"Running Gist for test_dir: {test_dir} with model_path: {model_path}")
            # Predict performance
            configs = [hash_enabled, gc_clock_freq, sbm_clock_freq, wr_rd_latency]
            predicted_performance = predict_performance(configs, model)
            print(f"Predicted Performance for {test_dir} with model {model_path}: {predicted_performance}")
            
            result = run_single_gist(test_dir, model_path, hash_enabled, gc_clock_freq, sbm_clock_freq, wr_rd_latency, gist_script)
            results.append((test_dir, model_path, result.returncode, result.stdout, result.stderr, predicted_performance))
    return results

def collect_results(results, output_file='regression_results.csv'):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['test_dir', 'model_path', 'return_code', 'stdout', 'stderr', 'predicted_performance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for test_dir, model_path, return_code, stdout, stderr, predicted_performance in results:
            writer.writerow({
                'test_dir': test_dir,
                'model_path': model_path,
                'return_code': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'predicted_performance': predicted_performance
            })
    print(f"Results collected in {output_file}")

def main():
    args = parse_arguments()
    model = load_model()
    results = run_regression(args.test_dirs, args.model_paths, args.hash_enabled, args.gc_clock_freq, args.sbm_clock_freq, args.wr_rd_latency, args.gist_script, model)
    collect_results(results)

if __name__ == "__main__":
    main()
