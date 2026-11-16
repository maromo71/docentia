@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==================================================
echo   Docentia - Instalador Automatico (Windows)
echo ==================================================
echo.

set "PY_CMD="
python --version >nul 2>&1
if %errorlevel%==0 (
    set "PY_CMD=python"
) else (
    py -3 --version >nul 2>&1
    if %errorlevel%==0 (
        set "PY_CMD=py -3"
    )
)

if "%PY_CMD%"=="" (
    echo [ERRO] Python nao encontrado no computador.
    echo.
    echo 1. Baixe o Python em: https://www.python.org/downloads/
    echo 2. Na primeira tela do instalador, MARQUE a caixa:
    echo    "Add python.exe to PATH"
    echo 3. Conclua a instalacao e execute este arquivo novamente.
    echo.
    pause
    exit /b 1
)

echo [1/3] Python detectado (%PY_CMD%).
if not exist "venv\Scripts\python.exe" (
    echo [1/3] Criando ambiente virtual (venv)...
    %PY_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERRO] Nao foi possivel criar o ambiente virtual.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Ambiente virtual (venv) ja existe.
)

echo.
echo [2/3] Instalando dependencias do Docentia (pode levar alguns minutos)...
"venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao com a internet.
    pause
    exit /b 1
)

echo.
echo [3/3] Verificando arquivo de configuracao de e-mail (.env)...
if not exist ".env" (
    if exist ".env-example" (
        copy ".env-example" ".env" >nul
        echo Arquivo .env criado a partir de .env-example (edite-o se quiser enviar e-mails).
    )
) else (
    echo Arquivo .env ja configurado.
)

echo.
echo ==================================================
echo   Instalacao concluida com sucesso!
echo   Para abrir o Docentia, de dois cliques em:
echo   iniciar.bat
echo ==================================================
echo.
pause
