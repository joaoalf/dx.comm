@echo off
del dist
del build
c:\python23\python.exe setup.py py2exe -c
cd dist
rem zip *.* ..\dxcommd.zip
copy *.* c:\dxcomm\
cd ..

