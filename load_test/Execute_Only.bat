:begin
echo "wait for signal"
:START
timeout 1 > nul
for /f "tokens=*" %%a in ( 
'curl -s -k https://vmedix-cs.nimaws.com/test.txt' 
) do ( 
set myvar=%%a
) 
if "%myvar%"=="no" GOTO START

:begin
set BASEPATH=%~dp0
cd "%BASEPATH%..\VMedix\VMedixAutomation"
call ant runAutomation
echo "Execution is DONE"
:end


:begin
cd "%BASEPATH%"
echo "DONE"
:end