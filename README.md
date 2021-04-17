> “If you automate a process that has errors, all you’ve done is automate the generation of those errors.”
― W.L.W. Borowiecki 

⬆ Probably what I just did, be aware, here be dragons!

----

This script allows one to patch crates of any choice with the no_std_compat-crate, automating the process [described here](https://crates.io/crates/no-std-compat), but over every dependency, including the one you wish to patch, and their dependnecies. Depending on how complex your crate is, this could take a while.

The script works by creating a second rust cache on your computer so your main rust cache is not changed, and then gives you a full path to get the patched dependency on.

I only work on Linux, and haven't used Windows since Windows XP, if you wish to run this project on Windows, that's fine by me, but I can't help you if it doesn't work.

## How to run it

- Install the dependencies from "requirements.txt" by running `pip install -r requirements.txt`

- Pick a crate you wish to patch, for example, Rune 0.9.0: `python main.py rune 0.9.0 output`

- Sit back and relax, then the output will come to you eventually:

    > Done! Add:
    > rune = { path = "/tmp/hcu1UURV/cargo_root/registry/src/> github.com-1ecc6299db9ec823/rune-0.9.0" }
To your dependencies and hope for the best!

If you managed to get this far, then you can include it and hope it'll compile!