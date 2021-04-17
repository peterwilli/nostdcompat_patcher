import os
import re
import glob

std_compat_ver = "0.4.1"
std_compat_dependency = f"""
[dependencies.no-std-compat]
version = "{std_compat_ver}"
features = [ "alloc" ]
"""

def patch_crate(crate_folder):
    # Patches this folder according to https://crates.io/crates/no-std-compat
    with open(os.path.join(crate_folder, 'Cargo.toml'), mode='r+') as f:    
        cargo_toml = f.read()
        f.seek(0, 0)
        f.write(cargo_toml + "\n" + std_compat_dependency)
        del cargo_toml

    with open(os.path.join(crate_folder, 'src', 'lib.rs'), mode='r+') as f:    
        lib_rs = f.read()
        f.seek(0, 0)
        f.write("#![no_std]\nextern crate no_std_compat as std;\n" + lib_rs)
        del lib_rs

    for src_filename in glob.iglob(os.path.join(crate_folder, 'src/**/*.rs'), recursive=True):
        with open(src_filename, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            line = "use std::prelude::v1::*;"
            f.write(line + '\n' + content)