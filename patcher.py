import os
import re
import glob
import toml

std_compat_ver = "0.4.1"

def patch_crate(crate_folder):
    # Patches this folder according to https://crates.io/crates/no-std-compat
    with open(os.path.join(crate_folder, 'Cargo.toml'), mode='r+') as f:    
        cargo_toml = f.read()
        toml_dict = toml.loads(cargo_toml)
        if not "dependencies" in toml_dict:
            toml_dict["dependencies"] = {}
            
        toml_dict["dependencies"]["no-std-compat"] = {
            "version": std_compat_ver,
            "features": ["alloc"]
        }
        f.seek(0, 0)
        f.write(toml.dumps(toml_dict))
        f.truncate()
        del cargo_toml

    with open(os.path.join(crate_folder, 'src', 'lib.rs'), mode='r+') as f:    
        lib_rs = f.read()
        f.seek(0, 0)
        f.write("#![no_std]\nextern crate no_std_compat as std;\n" + lib_rs)
        f.truncate()
        del lib_rs

    for src_filename in glob.iglob(os.path.join(crate_folder, 'src/**/*.rs'), recursive=True):
        with open(src_filename, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            line = "use std::prelude::v1::*;"
            f.write(line + '\n' + content)
            f.truncate()