@echo off
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python main.py
pause
