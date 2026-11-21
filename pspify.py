"""
PSPify - turn any video into a PSP-ready MP4.
Drop one or more video files onto PSPify.exe (or double-click it to pick files).
Converted files appear in a "PSP_Ready" folder next to each source video.
Copy them to the VIDEO folder on your PSP's memory card.
Add --fill when running from a psp media player to zoom the picture to fill the whole screen.
"""
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ---- Tweakable settings -----------------------------------------------------
WIDTH, HEIGHT = 480, 272        # PSP native screen
FPS = "30000/1001"              # 29.97 fps (PSP max is 30)
VIDEO_BITRATE = "1000k"
MAX_BITRATE = "1500k"
AUDIO_BITRATE = "128k"
OUT_DIR_NAME = "PSP_Ready"
AUTO_CROP = True                # remove black bars that are baked into the video
FILL_SCREEN = False             # True = fill the whole screen (cuts the sides off widescreen movies)
VERSION = "beta 0.2"
BAR_WIDTH = 30                  # progress bar length in characters
# -----------------------------------------------------------------------------

# Use block characters for the bar if the console supports them, else plain ASCII
try:
    "█░".encode(sys.stdout.encoding or "utf-8")
    BAR_FULL, BAR_EMPTY = "█", "░"
except (UnicodeEncodeError, LookupError):
    BAR_FULL, BAR_EMPTY = "#", "-"


def app_dir() -> Path:
    if getattr(sys, "frozen", False):          # running as a PyInstaller .exe
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def find_ffmpeg() -> str | None:
    candidates = []
    if getattr(sys, "frozen", False):
        # ffmpeg bundled inside the exe (PyInstaller unpacks it to _MEIPASS)
        candidates.append(Path(getattr(sys, "_MEIPASS", "")) / "ffmpeg.exe")
    candidates.append(app_dir() / "ffmpeg.exe")   # next to the script/exe
    for c in candidates:
        if c.exists():
            return str(c)
    return shutil.which("ffmpeg")                 # fallback: installed on PATH


def pick_files() -> list[str]:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)   # show the file window in front
        files = filedialog.askopenfilenames(
            parent=root,
            title="Select one or more videos (hold Ctrl or Shift to select several)",
            filetypes=[("Video files", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v *.mpg *.mpeg *.ts"),
                       ("All files", "*.*")],
        )
        root.destroy()
        return list(files)
    except Exception:
        return []


def get_duration(ffmpeg: str, src: Path) -> float:
    p = subprocess.run([ffmpeg, "-hide_banner", "-i", str(src)],
                       capture_output=True, text=True, errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", p.stderr)
    if not m:
        return 0.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def detect_crop(ffmpeg: str, src: Path, duration: float) -> str | None:
    """Sample a few short clips and find the real picture area (without black bars)."""
    points = [duration * f for f in (0.2, 0.5, 0.8)] if duration > 30 else [0.0]
    best, best_area = None, 0
    for t in points:
        p = subprocess.run(
            [ffmpeg, "-hide_banner", "-ss", f"{t:.1f}", "-i", str(src), "-t", "5",
             "-vf", "cropdetect=limit=24:round=2:reset=0", "-an", "-f", "null", "-"],
            capture_output=True, text=True, errors="replace",
        )
        found = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", p.stderr)
        if found:
            w, h, x, y = map(int, found[-1])
            # keep the largest area so dark scenes never cut into the real picture
            if w * h > best_area:
                best, best_area = (w, h, x, y), w * h
    if best:
        w, h, x, y = best
        return f"crop={w}:{h}:{x}:{y}"
    return None


def draw_bar(percent: float) -> None:
    percent = max(0.0, min(100.0, percent))
    filled = int(BAR_WIDTH * percent / 100)
    bar = BAR_FULL * filled + BAR_EMPTY * (BAR_WIDTH - filled)
    print(f"\r  [{bar}] {percent:5.1f}%", end="", flush=True)


def convert(ffmpeg: str, src: Path) -> Path | None:
    out_dir = src.parent / OUT_DIR_NAME
    out_dir.mkdir(exist_ok=True)
    dst = out_dir / f"{src.stem}_PSP.mp4"

    duration = get_duration(ffmpeg, src)

    filters = []
    if AUTO_CROP:
        print("  Checking for black bars...")
        crop = detect_crop(ffmpeg, src, duration)
        if crop:
            print(f"  Using {crop}")
            filters.append(crop)

    if FILL_SCREEN:
        # zoom until the screen is full, then cut off whatever sticks out
        filters.append(f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase")
        filters.append(f"crop={WIDTH}:{HEIGHT}")
    else:
        # keep the true picture shape (no padding), like HandBrake does
        filters.append(f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease:force_divisible_by=2")
    filters.append("setsar=1")
    vf = ",".join(filters)

    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-nostats",
        "-progress", "pipe:1",
        "-i", str(src),
        "-map", "0:v:0", "-map", "0:a:0?", "-sn",
        "-vf", vf, "-r", FPS,
        "-c:v", "libx264", "-profile:v", "main", "-level", "3.0",
        "-pix_fmt", "yuv420p", "-preset", "medium",
        "-b:v", VIDEO_BITRATE, "-maxrate", MAX_BITRATE, "-bufsize", "2000k",
        "-refs", "3", "-bf", "0",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", "48000", "-ac", "2",
        "-f", "psp",
        str(dst),
    ]

    started = time.monotonic()
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", bufsize=1,
    )
    errors: list[str] = []
    if duration > 0:
        draw_bar(0)
    else:
        print("  Converting... (progress not available for this file)")

    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        if line.startswith(("out_time_us=", "out_time_ms=")):
            value = line.split("=", 1)[1]
            if value.isdigit() and duration > 0:
                draw_bar(int(value) / 1_000_000 / duration * 100)
        elif not re.match(r"^\w+=", line):
            errors.append(line)          # anything that isn't a progress line is an error message
    proc.wait()

    if proc.returncode == 0:
        if duration > 0:
            draw_bar(100)
        print(f"\n  Done in {time.monotonic() - started:.0f}s")
        return dst

    print("\n  FAILED")
    for e in errors[-3:]:
        print(f"  {e}")
    return None


def run_conversions(ffmpeg: str, files: list[str]) -> None:
    total = len(files)
    print(f"\nSelected {total} file(s):")
    for n, f in enumerate(files, 1):
        print(f"  {n}. {Path(f).name}")

    done, failed = [], []
    for i, f in enumerate(files, 1):
        src = Path(f)
        print(f"\n[{i}/{total}] Converting: {src.name}")
        out = convert(ffmpeg, src) if src.is_file() else None
        if out:
            done.append(out)
        else:
            failed.append(src.name)

    print("\n" + "=" * 50)
    if done:
        print(f"  SUCCESS: {len(done)} of {total} video(s) converted!")
        print()
        for out in done:
            print(f"  - {out.name}")
        print()
        print("  Saved in:")
        for folder in dict.fromkeys(out.parent for out in done):
            print(f"    {folder}")
        print()
        print("  Copy them to the VIDEO folder on your PSP's memory card.")
    if failed:
        print()
        print(f"  FAILED: {len(failed)} video(s) could not be converted:")
        for name in failed:
            print(f"  - {name}")
    print("=" * 50)

    while input("\nPress 0 and Enter to go back to the menu: ").strip() != "0":
        print("Please type 0.")
    os.system("cls" if os.name == "nt" else "clear")


def show_menu() -> str:
    print("\n==============================")
    print(f"        PSPify ({VERSION})")
    print("==============================")
    print("  1. Convert file(s)")
    print("  2. Exit")
    return input("\nChoose an option (1-2): ").strip()


def main() -> None:
    global FILL_SCREEN
    args = [a for a in sys.argv[1:] if a != "--fill"]
    if "--fill" in sys.argv[1:]:
        FILL_SCREEN = True

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("ffmpeg.exe not found. Put ffmpeg.exe in the same folder as this program.")
        input("Press Enter to exit...")
        return

    if args:                       # files were dragged onto the exe
        run_conversions(ffmpeg, args)

    while True:
        choice = show_menu()
        if choice == "1":
            print("\nA file window will open. Hold Ctrl or Shift to select several videos.")
            files = pick_files()
            if files:
                run_conversions(ffmpeg, files)
            else:
                print("No files selected.")
        elif choice == "2":
            print("Bye!")
            break
        else:
            print("Please type 1 or 2.")


if __name__ == "__main__":
    main()