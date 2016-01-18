# python-fsb5
Python library to extract FSB5 (FMOD Sample Bank) files


## Usage

```
usage: extract.py [-h] [-o OUTPUT_DIRECTORY] [-p] [-q]
                  [fsb_file [fsb_file ...]]

Extract audio samples from FSB5 files

positional arguments:
  fsb_file              FSB5 container to extract audio from (defaults to
                        stdin)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        output directory to write extracted samples into
  -p, --prefix-samples  prefix extracted samples with the filename of the FSB
                        container they where extracted from
  -q, --quiet           suppress output of header and sample information
                        (samples that failed to decode will still be printed)
  -r, --resource        read multiple FSB5 files packed into the same file
                        (e.g. Unity3D's .resource files)
 ```

## Requirements

`libogg` and `libvorbis` are required to decode ogg samples. For linux simply install from your package manager. For windows either ensure the dlls are installed or download the appropriate release.

## Resource files

Unity3D packs multiple FSB5 files each containing a single sample into it's `.resource` files.
To extract all samples across all FSB5 files packed into the `.resource` file use `--resource`.

Output files will be prefixed with the index of their FSB container within the resource file.
