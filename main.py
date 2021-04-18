import sys
import tempfile
import os
import pathlib
import subprocess
import textwrap
from distutils.dir_util import copy_tree
import toml
import time

# Local stuff
from patcher import patch_crate

def fix_version(v):
    split = v.split(".")
    if len(split) == 1:
        return v + ".0.0"
    if len(split) == 2:
        return v + ".0"
    return v

def main():
    crate = sys.argv[1]
    version = sys.argv[2]
    output_folder = sys.argv[3]

    def patch_toml(toml_path, dependency_folders):
        with open(toml_path, mode='r+') as f:
            cargo_toml = f.read()
            toml_dict = toml.loads(cargo_toml)
            if 'dependencies' in toml_dict:
                for k in toml_dict['dependencies']:
                    if k in ["no-std-compat", "syn", "proc-macro2", "proc-macro", "quote"]:
                        continue
                    
                    # Find closest dependency folder (since version numbers in Cargo.toml can differ from the actual folder name)
                    dependency_folders_filtered = [x for x in dependency_folders if x.startswith(k)]
                    if len(dependency_folders_filtered) > 0:
                        dependency_folder = dependency_folders_filtered[0]
                        toml_dict['dependencies'][k]['path'] = os.path.join(registry_path, dependency_folder)
                        toml_dict['dependencies'][k]['default-features'] = False
                        del toml_dict['dependencies'][k]['version']
                        
                        # update dev dependency as well if needed
                        if 'dev-dependencies' in toml_dict and k in toml_dict['dev-dependencies']:
                            toml_dict['dev-dependencies'][k]['path'] = toml_dict['dependencies'][k]['path']

                f.seek(0, 0)
                f.write(toml.dumps(toml_dict))
                f.truncate()
            
    rust_project_path = os.path.join(output_folder, "rust_project")
    pathlib.Path(os.path.join(rust_project_path, "src")).mkdir(parents=True, exist_ok=True)
    print(f"Making new project depending on crate '{crate} v{version}' to download the crates required...")
    
    with open(os.path.join(rust_project_path, "Cargo.toml"), "w") as f:
        f.write(textwrap.dedent("""
        [package]
        edition = "2018"
        name = "crate_download"
        version = "0.1.0"

        [dependencies]
        rune = "0.9.0"
        """))

    with open(os.path.join(rust_project_path, "src", "main.rs"), "w") as f:
        f.write(textwrap.dedent("""
        fn main() {
            println!("I'm just a stub!");
        }
        """))

    cargo_project_folder = os.path.join(output_folder, "rust_project")
    cargo_root_folder = os.path.join(output_folder, 'cargo_root')
    pathlib.Path(cargo_root_folder).mkdir(parents=True, exist_ok=True)
    rust_env = {**os.environ, 'CARGO_HOME': cargo_root_folder}
    
    p = subprocess.Popen(["cargo", "run"], cwd=cargo_project_folder, env=rust_env)
    p.wait()
    
    registry_path = os.path.join(cargo_root_folder, 'registry', 'src', 'github.com-1ecc6299db9ec823')
    dependency_folders = os.listdir(registry_path)

    for dependency_folder in dependency_folders:
        print(f"Patching {dependency_folder}...")
        dependency_path = os.path.join(registry_path, dependency_folder)
        patch_crate(dependency_path)
        
        # Patch the dependencies to link to local (patched) dependencies only
        patch_toml(os.path.join(dependency_path, "Cargo.toml"), dependency_folders)
        
    print("Done! Add:")
    main_crate_path = os.path.join(registry_path, f"{crate}-{version}")
    print(f"{crate} = {{ path = \"{main_crate_path}\" }}")
    print("To your dependencies and hope for the best!")

if __name__ == "__main__":
    main()