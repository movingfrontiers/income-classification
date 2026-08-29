import shutil
from pathlib import Path

def gather_all_scripts():
    # Define your repository root and the target folder
    root_dir = Path.cwd()
    target_dir = root_dir / 'scripts'
    
    # Create the target folder if it doesn't exist
    target_dir.mkdir(exist_ok=True)
    
    count = 0
    # Search for all .py files in all subfolders
    for py_file in root_dir.rglob('*.py'):
        
        # Skip files already in the compiled-scripts folder to prevent infinite loops
        if target_dir in py_file.parents:
            continue
            
        # Skip this automation script itself
        if py_file.name == 'gather_scripts.py':
            continue
            
        # Copy the file to the target directory (overwriting older versions)
        dest_file = target_dir / py_file.name
        shutil.copy2(py_file, dest_file)
        print(f"Mirrored: {py_file.name}")
        count += 1
        
    print(f"\nSuccess: {count} scripts mirrored to /scripts/")

if __name__ == "__main__":
    gather_all_scripts()
