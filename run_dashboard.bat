@echo off
REM Launches the Spin dashboard (already built in spin_dashboard\). Re-run the notebook to rebuild its data.
cd /d "%~dp0spin_dashboard"
python -m streamlit run app.py --server.port 8501
pause
