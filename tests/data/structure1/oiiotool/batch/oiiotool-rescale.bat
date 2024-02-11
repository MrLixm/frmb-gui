@echo off

%OIIOTOOL% -v "%1" --resize:filter=gaussian %2x0 -o "%~n1-%2%~x1"