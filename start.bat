start "frontend" cmd /k "cd /d .\frontend\ & cnpm run dev"

start "backend" cmd /k "cd /d .\backend\ & conda activate py312 & python server.py"
