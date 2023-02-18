REM TODO:
REM PLEASE use forward slashes /  not backslash \
REM replace input & output paths.
REM fill in the trailing path to flint.py.
REM make sure the exact output path exists.

REM flags:
REM  -f   single file
REM       project/docs -> project/docs.html 
REM  -d   directory       (recurrsive)
REM  -md  merge directory (recurrsive)

python <absolute path to -> FLint\flint.py> -md \ 
 "<absolute path to input>" "<absolute path to output>/docs"