@echo off
echo Starting SkillPath AI Server...
py -m uvicorn main:app --reload
pause
