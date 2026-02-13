@echo off
setlocal enabledelayedexpansion

REM Start backend server in new window
cd /d "d:\final project\Stegnography project\Neww Stego Image & Audio\project_image_audio_encryption_decryption\backend"
start "Backend Server" cmd /k python app.py

REM Start frontend server in new window
cd /d "d:\final project\Stegnography project\Neww Stego Image & Audio\project_image_audio_encryption_decryption\frontend"
start "Frontend Server" cmd /k npm run dev

echo Both servers are starting in new windows...
