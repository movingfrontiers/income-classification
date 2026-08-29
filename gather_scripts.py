import shutil
from pathlib import Path

def gather_all_scripts():
    root_dir = Path(__file__).resolve().parent
    target_dir = root_dir / 'scripts'
    target_dir.mkdir(exist_ok=True)
    
    count = 0
    for py_file in root_dir.rglob('*.py'):
        if target_dir in py_file.parents or py_file.name == 'gather-scripts.py':
            continue
            
        dest_file = target_dir / py_file.name
        shutil.copy2(py_file, dest_file)
        count += 1
        
    print(f"\nSuccess: {count} actual scripts copied to /scripts/")

if __name__ == "__main__":
    gather_all_scripts()
