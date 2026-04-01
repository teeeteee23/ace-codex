@echo off
echo =============================
echo Whisper Urdu Transcriber
echo =============================
set /p url="Paste YouTube URL here: "
set /p name="Enter a name for this lecture: "
echo Downloading audio...
yt-dlp -x --audio-format mp3 -o "C:\Users\Talha Tanveer\Transcripts\%name%.mp3" "%url%"
echo Transcribing...
whisper "C:\Users\Talha Tanveer\Transcripts\%name%.mp3" --language ur --model medium --device cuda --output_dir "C:\Users\Talha Tanveer\Transcripts"
echo Done! Check your Transcripts folder.
pause