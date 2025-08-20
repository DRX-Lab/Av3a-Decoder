import subprocess
import os
import sys
import argparse
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

def run_command(command, description):
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Running: {description}")
    try:
        subprocess.run(command, check=True)
        print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Completed: {description}")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed: {description} ({e})")
        sys.exit(1)

# === Argument Parsing ===
parser = argparse.ArgumentParser(description="Extract audio using ffmpeg_av3a")
parser.add_argument("-i", "--input", required=True, help="Input video file")
args = parser.parse_args()
input_file = args.input

if not os.path.isfile(input_file):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Input file not found: {get_display_name(input_file)}")
    sys.exit(1)

# === Tools ===
ffmpeg_av3a = check_tool(get_executable_name("ffmpeg_av3a"), "FFmpeg AV3A")

# === Paths ===
base_name = os.path.splitext(os.path.basename(input_file))[0]
output_file = f"{base_name}.av3a"

# === Extraction Command ===
command = [
    ffmpeg_av3a,
    "-y",
    "-nostdin",
    "-loglevel", "error",
    "-stats",
    "-strict", "-2",
    "-i", input_file,
    "-vn",
    "-c", "copy",
    output_file
]

run_command(command, f"Audio extraction to {get_display_name(output_file)}")