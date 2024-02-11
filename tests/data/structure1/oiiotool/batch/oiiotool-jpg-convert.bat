@echo off
%OIIOTOOL% -v -i "%1" --subimage 0 --compression jpeg:95 --attrib "jpeg:subsampling" "4:4:4" -o "%~n1.jpg"