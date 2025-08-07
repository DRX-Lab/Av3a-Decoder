# Av3a-Decoder

**Av3a-Decoder** is a tool designed to decode `.av3a` audio files into WAV format with real-time progress feedback. After decoding, it generates multi-channel WAV outputs, including 7.1 (8 channels) and 5.1 (6 channels) audio files using FFmpeg.

---

## Features

- Decodes `.av3a` files to standard WAV format  
- Real-time progress bar displaying decoding status  
- Generates 7.1 (8-channel) and 5.1 (6-channel) WAV files from the decoded audio  
- Uses `av3a_decoder.exe` for decoding  
- Uses `ffmpeg.exe` for channel mapping and WAV conversion  
- Provides clear success and error messages with colorized terminal output  

---

## Requirements

- `ffmpeg.exe` (must be in the same directory as the script)  
- `av3a_decoder.exe` (must be in the same directory as the script) — available at [https://github.com/nilaoda/av3a_decoder](https://github.com/nilaoda/av3a_decoder)  
- A modified version of FFmpeg to extract `.av3a` audio streams: `ffmpeg_av3a.exe` — can be downloaded from [https://github.com/nilaoda/FFmpeg-Builds/releases](https://github.com/nilaoda/FFmpeg-Builds/releases)  
- Python 3.7 or higher  
- Python module `colorama` (`pip install colorama`)  

---

## Usage

### Extract `.av3a` audio from video files

To extract `.av3a` audio streams from video files, use the modified FFmpeg (`ffmpeg_av3a.exe`) which supports `.av3a` extraction without re-encoding.

Example command:

```bash
python extract_av3a.py -i input_video.mkv

```

This will generate an `.av3a` audio file in the same directory as the input.

---

### Decode `.av3a` audio and create multi-channel WAV outputs

Once you have an `.av3a` file, decode it and generate WAV outputs:

```bash
python main.py -i input_file.av3a
```

* The decoded WAV file will be saved alongside the input file.
* Additional WAV files with 8 channels (7.1) and 6 channels (5.1) will also be created in the same directory.

---

## How it works

1. The script verifies the presence of required executables: `ffmpeg.exe` and `av3a_decoder.exe`.
2. It decodes the input `.av3a` file, displaying a real-time progress bar with percentage, elapsed time, and estimated time remaining.
3. Upon successful decoding, it generates an 8-channel WAV (7.1) and a 6-channel WAV (5.1) by mapping audio channels using FFmpeg filters.
4. Success or error messages are printed with color highlights for clarity.

---

## Error Handling

* If any required executable or input file is missing, the script will terminate with an error message.
* If decoding or FFmpeg channel mapping fails, the script reports the failure and exits.

---

## Example Workflow

1. Extract `.av3a` audio from your video:

```bash
python extract_av3a.py -i movie.mkv
```

2. Decode `.av3a` audio and generate multi-channel WAVs:

```bash
python main.py -i movie.av3a
```

---
