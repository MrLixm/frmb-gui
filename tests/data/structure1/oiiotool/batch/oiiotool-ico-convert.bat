@echo off
%OIIOTOOL% -v -i "%1" --fit 256x256 --dup --resize 128x0 --dup --resize 64x0 --dup --resize 48x0 --dup --resize 32x0 --dup --resize 24x0 --dup --resize 16x0 --siappendall -o "%~n1.ico"