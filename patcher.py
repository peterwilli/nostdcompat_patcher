import os
import re
import glob
import toml
import re

std_compat_ver = "0.4.1"
regex_last_outer_attribute = re.compile('(\s*(\/\/!.*|#!\[.*])$)(?![\s\S]*(\/\/!.*|#!\[.*])$)', re.MULTILINE)
        
def patch_crate(crate_folder):
    # Patches this folder according to https://crates.io/crates/no-std-compat
    with open(os.path.join(crate_folder, 'src', 'lib.rs'), 'r') as f:
        content = f.read()
        if "no_std" in content:
            print(f"{crate_folder} already has no_std support! Skipping.")
            return

    with open(os.path.join(crate_folder, 'Cargo.toml'), mode='r+') as f:    
        cargo_toml = f.read()
        toml_dict = toml.loads(cargo_toml)
        if not "dependencies" in toml_dict:
            toml_dict["dependencies"] = {}
            
        toml_dict["dependencies"]["no-std-compat"] = {
            "path": os.path.abspath(os.path.join(os.path.realpath(__file__), '..', 'no-std-compat-custom')),
            "features": ["alloc"]
        }
        f.seek(0, 0)
        f.write(toml.dumps(toml_dict))
        f.truncate()
        del cargo_toml

    for src_filename in glob.iglob(os.path.join(crate_folder, 'src/**/*.rs'), recursive=True):
        with open(src_filename, 'r+') as f:
            content = f.read()
            prelude = "use std::prelude::v1::*;"
            if regex_last_outer_attribute.search(content):
                content = regex_last_outer_attribute.sub(f"\\1\n{prelude}\n", content)
            else:
                content = f"{prelude}\n{content}"
            f.seek(0, 0)
            f.write(content)
            f.truncate()

    with open(os.path.join(crate_folder, 'src', 'lib.rs'), 'r+') as f:
        content = f.read()
        extern_crate = "#![no_std]\nextern crate no_std_compat as std;\n"
        if regex_last_outer_attribute.search(content):
            content = regex_last_outer_attribute.sub(f"\\1\n{extern_crate}\n", content)
        else:
            content = f"{extern_crate}\n{content}"
        f.seek(0, 0)
        f.write(content)
        f.truncate()