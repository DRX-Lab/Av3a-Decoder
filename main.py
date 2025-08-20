import os
import sys
import subprocess
import re
import argparse
import time
import platform
from colorama import Fore, Style, init

init(autoreset=True)

# === Helper Functions ===
def get_executable_name(name):
    return f"{name}.exe" if platform.system().lower() == "windows" else name

def check_tool(filename, display_name):
    path = os.path.join(os.getcwd(), filename)
    display_file = get_display_name(path)
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Checking for {display_name}...")
    if not os.path.isfile(path):
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {display_name} not found: {display_file}")
        sys.exit(1)
    print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {display_name} found: {display_file}")
    return path

def get_display_name(path):
    return os.path.basename(path) if os.path.isfile(path) else os.path.basename(os.path.abspath(path))

def remove_temp_file(path):
    if os.path.exists(path):
        os.remove(path)
        print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} Deleted temporary file: {get_display_name(path)}")

def run_command(command, description):
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Running: {description}")
    try:
        subprocess.run(command, check=True)
        print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Completed: {description}")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed: {description} ({e})")
        sys.exit(1)

def format_hhmmss(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(int(seconds)))

# === Progress Bar Function ===
def display_progress_bar_av3a(line, start_time, bar_length=60):
    progress_pattern = r"Decoding::\s+(\d+)%\|.*?<([0-9:]+),"
    match = re.search(progress_pattern, line)
    if not match:
        return
    percent_str, eta_str = match.groups()
    progress = int(percent_str) / 100
    filled = int(bar_length * progress)
    elapsed_seconds = time.time() - start_time

    h, m, s = map(int, eta_str.split(":"))
    eta_seconds = h * 3600 + m * 60 + s

    print(
        f"[{'■' * filled}{' ' * (bar_length - filled)}] "
        f"{int(progress * 100)}% "
        f"Elapsed: {format_hhmmss(elapsed_seconds)} | "
        f"Remaining: {format_hhmmss(eta_seconds)}",
        end='\r'
    )

# === FFmpeg Mapping Function ===
def run_ffmpeg_mapping(ffmpeg_path, input_file, output_file, map_filter, description):
    print(f"\n{Fore.CYAN}[INFO]{Style.RESET_ALL} {description}...")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} → Mapping: {map_filter.split(':')[-1]}")
    cmd = [
        ffmpeg_path,
        "-y", "-nostdin", "-loglevel", "error", "-stats", "-strict", "-2",
        "-i", input_file,
        "-filter", map_filter,
        output_file
    ]
    run_command(cmd, f"{description} ({get_display_name(output_file)})")

# === Argument Parsing ===
parser = argparse.ArgumentParser(description="Decode AV3A to WAV with real-time progress bar.")
parser.add_argument("-i", "--input", required=True, help="Path to input .av3a file")
args = parser.parse_args()
input_av3a = args.input

if not os.path.isfile(input_av3a):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Input file not found: {get_display_name(input_av3a)}")
    sys.exit(1)

# === Tools ===
ffmpeg = check_tool(get_executable_name("ffmpeg"), "FFmpeg")
decoder = check_tool(get_executable_name("av3a_decoder"), "AV3A Decoder")

# === Paths ===
input_dir = os.path.dirname(os.path.abspath(input_av3a))
base_name = os.path.splitext(os.path.basename(input_av3a))[0]

output_wav = os.path.join(input_dir, f"{base_name}.wav")
output_8ch = os.path.join(input_dir, f"{base_name}_8ch.wav")
output_6ch = os.path.join(input_dir, f"{base_name}_6ch.wav")

# === AV3A Decoding ===
av3a_command = [decoder, input_av3a, output_wav]

print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Decoding started...\n")
start_time = time.time()

try:
    process = subprocess.Popen(
        av3a_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True
    )

    for line in process.stdout:
        line = line.strip()
        display_progress_bar_av3a(line, start_time)

        if "done" in line.lower():
            elapsed_seconds = time.time() - start_time
            print(
                f"\n[{'■' * 60}] 100% "
                f"Elapsed: {format_hhmmss(elapsed_seconds)} | Remaining: 00:00:00"
            )

    process.stdout.close()
    process.wait()
    if process.returncode == 0:
        print(f"\n{Fore.GREEN}[OK]{Style.RESET_ALL} Decoding completed: {get_display_name(output_wav)}")
    else:
        print(f"\n{Fore.RED}[ERROR]{Style.RESET_ALL} Decoder exited with code {process.returncode}")
        sys.exit(1)

except Exception as e:
    print(f"\n{Fore.RED}[EXCEPTION]{Style.RESET_ALL} {str(e)}")
    sys.exit(1)

# === FFmpeg 8ch & 6ch Mapping ===
run_ffmpeg_mapping(ffmpeg, output_wav, output_8ch,
                   "channelmap=0|1|2|3|4|5|6|7:FL+FR+FC+LFE+SL+SR+BL+BR",
                   "Creating 7.1 WAV from decoded output")

run_ffmpeg_mapping(ffmpeg, output_wav, output_6ch,
                   "channelmap=0|1|2|3|4|5:FL+FR+FC+LFE+SL+SR",
                   "Creating 5.1 WAV from decoded output")