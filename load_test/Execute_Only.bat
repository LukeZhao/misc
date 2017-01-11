:begin
echo "deleting old files..."
if exist C:\load_tests rmdir /S /Q C:\load_tests
echo "getting new files..."
if not exist "C:\apache-ant-1.9.6" xcopy /S /Q \\AVPCHBT5RL1LZHA\public\apache-ant-1.9.6 C:\apache-ant-1.9.6\
xcopy /S /Q \\AVPCHBT5RL1LZHA\public\Automation\VirtuMedixAutomation_1.0 C:\load_tests\
cd C:\load_tests\Batch_File

for /f "tokens=*" %%a in ( 
'curl -s -k https://api-virtumedix-vm2.nimaws.com/lt/number' 
) do ( 
set number=%%a
)
set /A number=number%20
echo %number%
set /A start_number=(number-1)*15 + 1
set /A end_number=start_number+14
echo %start_number%
echo %end_number%

@echo off
setlocal EnableDelayedExpansion
rename "c:\load_tests\Configuration\environment_config.properties" "environment_config.properties.tmp"
for /f "tokens=*" %%a in (c:\load_tests\Configuration\environment_config.properties.tmp) do (
    set foo=%%a
    if "!foo!"=="test.perf.consults.start.count = 1" set foo=test.perf.consults.start.count = %start_number%
    if "!foo!"=="test.perf.consults.end.count = 20" set foo=test.perf.consults.start.count = %end_number%
    @echo !foo! >> "c:\load_tests\Configuration\environment_config.properties"
)
del c:\load_tests\Configuration\environment_config.properties.tmp
endlocal
@echo on
:end

:begin
echo "wait for signal"
:START
timeout 2 > nul
for /f "tokens=*" %%a in ( 
'curl -s -k https://api-virtumedix-vm2.nimaws.com/lt/canstart' 
) do ( 
set myvar=%%a
) 
if "%myvar%"=="no" GOTO START
echo "%myvar%"

:begin
set BASEPATH=C:\load_tests\Batch_File
cd "%BASEPATH%..\VMedix\VMedixAutomation"
REM call ant runAutomation
echo "Execution is DONE"
:end


:begin
cd "%BASEPATH%"
echo "DONE"
pause >nul
:end
