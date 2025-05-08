"""
Docker initialization helper script.
This script helps with Python path setup in Docker.
"""

import os
import sys
import importlib.util
import traceback

def setup_paths():
    """Set up Python paths for Docker environment."""
    print("Setting up paths for Docker environment...")
    
    # Add the current directory to the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Add src directory
    src_dir = os.path.join(current_dir, 'src')
    if os.path.exists(src_dir) and src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    print(f"Current Python path: {sys.path}")
    
    # Check if modules can be found
    modules_to_check = [
        'src.agent',
        'src.agent.graph',
        'agent',
        'agent.graph'
    ]
    
    for module_name in modules_to_check:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                print(f"✅ Module '{module_name}' can be found at: {spec.origin}")
            else:
                print(f"❌ Module '{module_name}' cannot be found.")
        except (ImportError, AttributeError, ValueError) as e:
            print(f"❌ Error checking module '{module_name}': {str(e)}")

if __name__ == "__main__":
    try:
        setup_paths()
        print("Path setup complete.")
    except Exception as e:
        print(f"Error during path setup: {str(e)}")
        traceback.print_exc()