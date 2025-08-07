import argparse
import subprocess
import os
import sys
import re
import time
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

ffmpeg_path = check_executable("ffmpeg.exe", "FFmpeg")
decoder_path = check_executable("av3a_decoder.exe", "AV3A Decoder")

parser = argparse.ArgumentParser(description="Decode AV3A to WAV with real-time progress bar.")
parser.add_argument("-i", "--input", required=True, help="Path to input .av3a file")
args = parser.parse_args()

input_av3a = args.input
if not os.path.isfile(input_av3a):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Input file not found: {input_av3a}")
    sys.exit(1)

input_dir = os.path.dirname(os.path.abspath(input_av3a))
base_name = os.path.splitext(os.path.basename(input_av3a))[0]

output_wav = os.path.join(input_dir, base_name + ".wav")
output_8ch = os.path.join(input_dir, base_name + "_8ch.wav")
output_6ch = os.path.join(input_dir, base_name + "_6ch.wav")

av3a_command = [decoder_path, input_av3a, output_wav]

progress_pattern = r"Decoding::\s+(\d+)%\|.*?<([0-9:]+),"
start_time = time.time()
print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Decoding started...\n")

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

        match = re.search(progress_pattern, line)
        if match:
            percent_str, eta_str = match.groups()
            progress = int(percent_str) / 100
            filled = int(60 * progress)
            elapsed_seconds = int(time.time() - start_time)

            h, m, s = map(int, eta_str.split(":"))
            eta_seconds = h * 3600 + m * 60 + s

            elapsed_formatted = time.strftime('%H:%M:%S', time.gmtime(elapsed_seconds))
            eta_formatted = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))

            print(
                f"[{'■' * filled}{' ' * (60 - filled)}] "
                f"{int(progress * 100)}% "
                f"Elapsed: {elapsed_formatted} | "
                f"Remaining: {eta_formatted}",
                end='\r'
            )

        if "done" in line.lower():
            elapsed_seconds = int(time.time() - start_time)
            elapsed_formatted = time.strftime('%H:%M:%S', time.gmtime(elapsed_seconds))
            print(
                f"\n[{'■' * 60}] 100% "
                f"Elapsed: {elapsed_formatted} | Remaining: 00:00:00"
            )

    process.wait()
    if process.returncode == 0:
        print(f"\n{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Decoding completed successfully.")
    else:
        print(f"\n{Fore.RED}[ERROR]{Style.RESET_ALL} Decoder exited with code {process.returncode}")
        sys.exit(1)

except Exception as e:
    print(f"\n{Fore.RED}[EXCEPTION]{Style.RESET_ALL} {str(e)}")
    sys.exit(1)

print(f"\n{Fore.CYAN}[INFO]{Style.RESET_ALL} Creating 7.1 WAV from decoded output...")
print(f"{Fore.YELLOW}→ Mapping to FL+FR+FC+LFE+SL+SR+BL+BR (8 channels)\n")
map_8ch = "channelmap=0|1|2|3|4|5|6|7:FL+FR+FC+LFE+SL+SR+BL+BR"

ffmpeg_cmd_8ch = [
    ffmpeg_path,
    "-y", "-nostdin", "-loglevel", "error", "-stats", "-strict", "-2",
    "-i", output_wav,
    "-filter", map_8ch,
    output_8ch
]

try:
    subprocess.run(ffmpeg_cmd_8ch, check=True)
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Output created: {output_8ch}")
except subprocess.CalledProcessError:
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} FFmpeg failed to create 8ch output.")
    sys.exit(1)

print(f"\n{Fore.CYAN}[INFO]{Style.RESET_ALL} Creating 5.1 WAV from decoded output...")
print(f"{Fore.YELLOW}→ Mapping to FL+FR+FC+LFE+SL+SR (6 channels)\n")
map_6ch = "channelmap=0|1|2|3|4|5:FL+FR+FC+LFE+SL+SR"

ffmpeg_cmd_6ch = [
    ffmpeg_path,
    "-y", "-nostdin", "-loglevel", "error", "-stats", "-strict", "-2",
    "-i", output_wav,
    "-filter", map_6ch,
    output_6ch
]

try:
    subprocess.run(ffmpeg_cmd_6ch, check=True)
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Output created: {output_6ch}")
except subprocess.CalledProcessError:
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} FFmpeg failed to create 6ch output.")
    sys.exit(1)