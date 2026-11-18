# Builds a single-file PSPify.exe with ffmpeg bundled inside
if (-not (Test-Path .\vendor\ffmpeg.exe)) {
    Write-Error "Put ffmpeg.exe in .\vendor\ first"
    exit 1
}
pyinstaller --noconfirm --clean --onefile --name PSPify --add-binary "vendor\ffmpeg.exe;." pspify.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed"
    exit 1
}
Write-Host "Done: dist\PSPify.exe"