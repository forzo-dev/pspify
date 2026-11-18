# PSPify 🎮

Turn any video into a PSP-ready MP4. Drag a file onto the exe, copy the result to your PSP. No installs, no settings.

## Download

Get the latest `PSPify.exe` from the [Releases page](https://github.com/forzo-dev/pspify/releases/latest).

## How to use

1. Drag one or more videos onto `PSPify.exe` (or double-click it to pick files).
2. Wait for the conversion to finish.
3. Copy the files from the `PSP_Ready` folder to the `VIDEO` folder on your PSP's memory card.

## Features

- One file, nothing else to install (ffmpeg is bundled inside)
- Settings tuned for the PSP: H.264, AAC audio, 480x272, ~30 fps
- Automatically removes black bars baked into widescreen videos
- Batch conversion: drop many files at once
- Optional fill mode: `PSPify.exe --fill` from a terminal zooms the picture to fill the screen

## Build from source

Requires Python 3.10+ and `ffmpeg.exe` in a `vendor` folder.

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements-dev.txt
    .\build.ps1

The exe appears in `dist\PSPify.exe`.

## Notes

- Windows may show a SmartScreen warning because the exe is unsigned. Click **More info**, then **Run anyway**. The full source is in this repo.
- Not affiliated with or endorsed by Sony. "PSP" is a trademark of Sony Interactive Entertainment.
- Uses [FFmpeg](https://ffmpeg.org). See `THIRD_PARTY_NOTICES.md`.

## License

MIT, see `LICENSE`.