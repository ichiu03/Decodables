import sys
from main import main as process_main
from statistics import mean
from datetime import datetime
import json
import io
import re
import time
from contextlib import redirect_stdout

def extract_decodability_and_story(output: str) -> tuple[float, float, str]:
    """
    Extract decodability percentages and final story from the program output
    Returns: (initial_decodability, final_decodability, final_story)
    """
    # Look for the pattern "This text is X% decodable" for initial decodability
    initial_match = re.search(r"This text is (\d+\.\d+)% decodable", output)
    initial = float(initial_match.group(1))/100 if initial_match else 0.0
    
    # Look for the final decodability value
    final_match = re.search(r"Decodability: (\d+\.\d+)", output)
    final = float(final_match.group(1)) if final_match else 0.0
    
    # Extract final story
    story_match = re.search(r"Final Story: (.*?)\nDecodability:", output, re.DOTALL)
    final_story = story_match.group(1).strip() if story_match else ""
    
    return initial, final, final_story

def run_main_with_inputs(inputs):
    """
    Run main() function with simulated user inputs and measure execution time
    """
    input_string = '\n'.join(inputs)
    output = io.StringIO()
    
    start_time = time.time()
    with redirect_stdout(output):
        sys.stdin = io.StringIO(input_string)
        try:
            final_decodability = process_main()
        except Exception as e:
            print(f"Error during execution: {str(e)}")
            final_decodability = 0.0
        finally:
            sys.stdin = sys.__stdin__
    end_time = time.time()
    
    execution_time = end_time - start_time
    output_str = output.getvalue()
    initial_decodability, _, final_story = extract_decodability_and_story(output_str)
    
    return initial_decodability, final_decodability, execution_time, final_story

def save_test_results(test_config, run_results, filename="main_test_results.txt"):
    """
    Save test results to a file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'a') as f:
        f.write(f"\n=== Test Results {timestamp} ===\n")
        f.write(f"Test Configuration:\n")
        for key, value in test_config.items():
            f.write(f"  {key}: {value}\n")
        
        f.write("\nAggregate Results:\n")
        f.write(f"  Average Initial Decodability: {mean(run_results['initial_decodabilities']):.2f}%\n")
        f.write(f"  Average Final Decodability: {mean(run_results['final_decodabilities']):.2f}%\n")
        f.write(f"  Average Runtime: {mean(run_results['runtimes']):.2f} seconds\n")
        f.write(f"  Number of Runs: {len(run_results['initial_decodabilities'])}\n")
        
        f.write("\nDetailed Results:\n")
        for i, (initial_decodability, final_decodability, runtime, story) in enumerate(zip(
            run_results['initial_decodabilities'],
            run_results['final_decodabilities'],
            run_results['runtimes'],
            run_results['final_stories']
        ), 1):
            f.write(f"\nRun {i}:\n")
            f.write(f"  Initial Decodability: {initial_decodability:.2f}%\n")
            f.write(f"  Final Decodability: {final_decodability:.2f}%\n")
            f.write(f"  Runtime: {runtime:.2f} seconds\n")
            f.write("  Final Story:\n")
            f.write(f"  {story}\n")
            f.write("\n" + "-"*30 + "\n")
        
        f.write("\n" + "="*50 + "\n")

def main():
    NUM_RUNS = 3  # Number of times to run each configuration
    
    test_configs = [
        {
            'description': "Generate story with these problems w/ openai and limited processing",
            'inputs': [
                "",  # default sight words
                "g",  # generate story
                "200",  # story length
                "A day at the park",  # topic
                "b/l/p/j/ck/wh/aw/tch/igh/ir/oi",  # problem sounds
                "Tom",  # name
                "7",  # reading level
                "openai"   # API choice
            ]
        }
        # {
        #     'description': "Generate story with s problems w/ anthropic",
        #     'inputs': [
        #         "",  # default sight words
        #         "g",  # generate story
        #         "200",  # story length
        #         "A day at the park",  # topic
        #         "s",  # problem sounds
        #         "Tom",  # name
        #         "7",  # reading level
        #         "anthropic"   # API choice
        #     ]
        # }
    ]
    
    # Run tests for each configuration
    for config in test_configs:
        print(f"\nRunning test: {config['description']}")
        
        run_results = {
            'initial_decodabilities': [],
            'final_decodabilities': [],
            'runtimes': [],
            'final_stories': []
        }
        
        for run in range(NUM_RUNS):
            print(f"  Run {run + 1}/{NUM_RUNS}")
            initial_decodability, final_decodability, runtime, final_story = run_main_with_inputs(config['inputs'])
            
            run_results['initial_decodabilities'].append(initial_decodability * 100)
            run_results['final_decodabilities'].append(final_decodability * 100)
            run_results['runtimes'].append(runtime)
            run_results['final_stories'].append(final_story)
            
            print(f"    Initial Decodability: {initial_decodability * 100:.2f}%")
            print(f"    Final Decodability: {final_decodability * 100:.2f}%")
            print(f"    Runtime: {runtime:.2f} seconds")
        
        save_test_results(config, run_results)
        print(f"\nTest completed.")
        print(f"Average initial decodability: {mean(run_results['initial_decodabilities']):.2f}%")
        print(f"Average final decodability: {mean(run_results['final_decodabilities']):.2f}%")
        print(f"Average runtime: {mean(run_results['runtimes']):.2f} seconds")
        print("Results saved to main_test_results.txt")

if __name__ == "__main__":
    main() 