import subprocess
import os
import sys
import argparse
from colorama import Fore, Style, init
init(autoreset=True)

def check_executable(filename, display_name):
    path = os.path.join(os.getcwd(), filename)
    if not os.path.isfile(path):
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {display_name} not found: {filename}")
        sys.exit(1)
    else:
        print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {display_name} found.")
    return path

parser = argparse.ArgumentParser(description="Extract audio using ffmpeg_av3a.exe")
parser.add_argument("-i", "--input", required=True, help="Input video file")
args = parser.parse_args()

input_file = args.input
ffmpeg_path = check_executable("ffmpeg_av3a.exe", "FFmpeg AV3A")

if not os.path.isfile(input_file):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Input file not found: {input_file}")
    sys.exit(1)

base_name = os.path.splitext(os.path.basename(input_file))[0]
output_file = f"{base_name}.av3a"

command = [
    ffmpeg_path,
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

try:
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Running command: {' '.join(command)}")
    subprocess.run(command, check=True)
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Audio extracted: {output_file}")
except subprocess.CalledProcessError as e:
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Extraction failed: {e}")
    sys.exit(1)