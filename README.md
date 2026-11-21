# PSPify 🎮

![Status](https://img.shields.io/badge/status-beta%200.2-orange)
![Platform](https://img.shields.io/badge/platform-Windows-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Turn any video into a PSP-ready MP4. Open one file, pick your videos, copy the result to your PSP. No installs, no settings.

> **Beta 0.2:** this is an early version. It has been tested on a PSP 2000. Feedback and bug reports are welcome in the [Issues](https://github.com/YOUR_USERNAME/pspify/issues) tab.

## Download
python pspify.py
Get the latest `PSPify.exe` from the [Releases page](https://github.com/forzo-dev/pspify/releases).

## How to use

1. Open `PSPify.exe` and choose **1**, then pick one or more videos (hold **Ctrl** or **Shift** to select several), or drag videos onto the exe.
2. Wait for the conversion to finish. A summary shows where the files were saved.
3. Press **0** to return to the menu, then convert more files or choose **2** to exit.
4. Copy the files from the `PSP_Ready` folder to the `VIDEO` folder on your PSP's memory card.

## Features

- One file, nothing else to install (ffmpeg is bundled inside)
- Settings tuned for the PSP: H.264, AAC audio, 480x272 max, ~30 fps
- Automatically removes black bars baked into widescreen videos
- Convert several files in one go, with a live `[2/5]` counter and a progress bar for each video
- Optional fill mode: run `PSPify.exe --fill` from a terminal to zoom the picture to fill the whole screen

## Roadmap

- [ ] Simple graphical interface (GUI)
- [x] Progress bar
- [ ] Remember settings between runs

## Build from source

Requires Python 3.10+ and `ffmpeg.exe` in a `vendor` folder.

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements-dev.txt
    .\build.ps1

The exe appears in `dist\PSPify.exe`.

## Notes

- Windows may show a SmartScreen warning because the exe is unsigned. Click **More info**, then **Run anyway**. The full source is in this repo.
- Some antivirus programs flag unsigned PyInstaller exes by mistake. You can build it yourself with the steps above.
- Not affiliated with or endorsed by Sony. "PSP" is a trademark of Sony Interactive Entertainment.
- Uses [FFmpeg](https://ffmpeg.org). See `THIRD_PARTY_NOTICES.md`.

## License

MIT, see `LICENSE`.