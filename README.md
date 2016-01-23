# python-fsb5
Python library and tool to extract FSB5 (FMOD Sample Bank) files.

### Supported formats

- MPEG
- Vorbis
- WAVE (PCM8, PCM16, PCM32)

Other formats can be identified but will be extracted as `.dat` files and may not play as the headers may be missing.

## Tool Usage

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
  -q, --quiet           suppress output of header and sample information
                        (samples that failed to decode will still be printed)
 ```

#### Resource files
Unity3D packs multiple FSB5 files each containing a single sample into it's `.resource` files.
python-fsb5 will automatically extract all samples if multiple FSB5s are found within one file.
Output files will be prefixed with the (0 based) index of their FSB container within the resource file e.g. `out/sounds-15-track1.wav` is the path for a WAVE sample named track1 which is contained within the 16th FSB file within sounds.resource.

#### Unnamed samples
FSB5 does not require samples to store a name. If samples are stored without a name they will use their index within the FSB e.g. `sounds-0000.mp3` is the first sample in sounds.fsb.

## Requirements

`libogg` and `libvorbis` are required to decode ogg samples. For linux simply install from your package manager. For windows either ensure the dlls are installed or download the appropriate release.

If ogg files are not required to be decoded then the libraries are not required.

## Library usage

```python
import fsb5

# read the file into a FSB5 object
with open('sample.fsb', 'rb') as f:
  fsb = fsb5.FSB5(f.read())

print(fsb.header)

# get the extension of samples based off the sound format specified in the header
ext = fsb.get_sample_extension()

# iterate over samples
for sample in fsb.samples:
  # print sample properties
  print('''\t{sample.name}.{extension}:
  Frequency: {sample.frequency}
  Channels: {sample.channels}
  Samples: {sample.samples}'''.format(sample=sample, extension=ext))

  # rebuild the sample and save
  with open('{0}.{1}'.format(sample.name, ext), 'wb') as f:
    rebuilt_sample = fsb.rebuild_sample(sample)
    f.write(rebuilt_sample)
```

#### Useful header properties

- `numSamples`: The number of samples contained in the file
- `mode`: The audio format of all samples. Can be one of:
 * `fsb5.SoundFormat.NONE`
 * `fsb5.SoundFormat.PCM8`
 * `fsb5.SoundFormat.PCM16`
 * `fsb5.SoundFormat.PCM24`
 * `fsb5.SoundFormat.PCM32`
 * `fsb5.SoundFormat.PCMFLOAT`
 * `fsb5.SoundFormat.GCADPCM`
 * `fsb5.SoundFormat.IMAADPCM`
 * `fsb5.SoundFormat.VAG`
 * `fsb5.SoundFormat.HEVAG`
 * `fsb5.SoundFormat.XMA`
 * `fsb5.SoundFormat.MPEG`
 * `fsb5.SoundFormat.CELT`
 * `fsb5.SoundFormat.AT9`
 * `fsb5.SoundFormat.XWMA`
 * `fsb5.SoundFormat.VORBIS`


#### Useful sample properties

- `name` : The name of the sample, or a 4 digit number if names are not provided.
- `frequency` : The sample rate of the audio
- `channels` : The number of channels of audio (either 1 or 2)
- `samples` : The number of samples in the audio
- `metadata` : A dictionary of `fsb5.MetadataChunkType` to tuple (sometimes namedtuple) or bytes.

All contents of sample.metadata is optional and often not provided. Several metadata types seem to override sample properties.

Supported `fsb5.MetadataChunkType`s are:
 * `CHANNELS`: A 1-tuple containing the number of channels
 * `FREQUENCY`: A 1-tuple containing the sample rate
 * `LOOP`: A 2-tuple of the loop start and end
 * `XMASEEK`: Raw bytes
 * `DSPCOEFF`: Raw bytes
 * `XWMADATA`: Raw bytes
 * `VORBISDATA`: A named tuple with properties `crc32` (int) and `unknown` (bytes)

If a metadata chunk is unrecognized it will be included in the dictionary as an interger mapping to a bytes.

#### Rebuilding samples

Samples also have the `data` property.
This contains the raw, unprocessed audio data for that sample from the FSB file.
To reconstruct a playable version of the audio use `rebuild_sample` on the FSB5 object passing the sample desired to be rebuilt.


## License

python-fsb5 is licensed under the terms of the MIT license.
The full text of the license is available in the LICENSE file.
