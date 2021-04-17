import sys
import tempfile
import os
import pathlib
import subprocess
import textwrap
from distutils.dir_util import copy_tree

# Local stuff
from patcher import patch_crate

def main():
    registry_path = sys.argv[1]
    crate = sys.argv[2]
    version = sys.argv[3]
    output_folder = sys.argv[4]
    tmp = tempfile.mkdtemp()
    pathlib.Path(os.path.join(tmp, "src")).mkdir(parents=True, exist_ok=True)
    print(f"Making new project depending on crate '{crate} v{version}' to download the crates required...")
    
    with open(os.path.join(tmp, "Cargo.toml"), "w") as f:
        f.write(textwrap.dedent("""
        [package]
        edition = "2018"
        name = "crate_download"
        version = "0.1.0"

        [dependencies]
        rune = "0.9.0"
        """))

    with open(os.path.join(tmp, "src", "main.rs"), "w") as f:
        f.write(textwrap.dedent("""
        fn main() {
            println!("I'm just a stub!");
        }
        """))

    p = subprocess.Popen(["cargo", "run"], cwd=tmp)
    p.wait()
    
    # Start with the first package, 
    # copy it to the output directory and do the patching
    crate_folder = f"{crate}-{version}"
    crate_copy = os.path.join(output_folder, crate_folder)
    copy_tree(os.path.join(registry_path, crate_folder), crate_copy)
    patch_crate(crate_copy)

if __name__ == "__main__":
    main()