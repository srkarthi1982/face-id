<#
.SYNOPSIS
    Deploy the JAI-School `develop` branch on Windows Server 2022.

.DESCRIPTION
    Automates the deploy flow: (optional) clone + branch switch, backend uv
    venv + dependency sync + alembic migrations, frontend npm install +
    generate-types + build, and running the backend as a Windows service via
    NSSM (https://nssm.cc).

    Why a service (NSSM) instead of a detached uvicorn: the Azure DevOps agent
    tags every process a job spawns with VSTS_PROCESS_LOOKUP_ID and kills them
    when the job ends. A plain `start-server.bat` launched from the pipeline is
    therefore reaped moments after deploy. A Windows service is owned by the
    Service Control Manager, so it survives job-end AND server reboots
    (Start=SERVICE_AUTO_START).

    Ordering: the backend service is (re)started BEFORE the frontend build so
    `npm run generate-types` can fetch /openapi.json + /api/v1/access/
    permission-codes from the live backend. The built frontend/dist is then
    served live from disk by the already-running backend (app/main.py mounts
    frontend/dist at startup; dist is committed so the mounts always exist).

    Requires: nssm.exe on PATH, and the agent account must be a local
    Administrator (installing / controlling a Windows service is privileged).

.PARAMETER Clone
    If set, clone RepoUrl into TargetDir and switch to Branch first.

.PARAMETER RepoUrl
    Git URL to clone from. Default: internal JAI-School repo.

.PARAMETER Branch
    Branch to switch to. Default: develop.

.PARAMETER TargetDir
    Clone destination (only used with -Clone). Default: .\JAI-School.

.PARAMETER EnvFile
    Optional path to a backend .env file. If provided, copied to backend\.env.
    If not provided, backend\.env must already exist.

.PARAMETER FrontendEnvFile
    Path to the frontend .env file, copied to frontend\.env.
    Default: C:\qa-env\.env.frontend.

.PARAMETER ServiceName
    Name of the NSSM/Windows service running the backend. Default: JAI-School.

.PARAMETER Nssm
    Path to nssm.exe (or just 'nssm' if on PATH). Default: nssm.

.PARAMETER Host
    Host for health check URLs. Default: localhost.

.PARAMETER Port
    Port for uvicorn to bind. Default: 8000.

.PARAMETER LogDir
    Directory for uvicorn log files. Default: <repo>\logs.

.PARAMETER SslKeyfile
    Path to SSL key file (passed to uvicorn). When set, health checks use https.

.PARAMETER SslCertfile
    Path to SSL certificate file (passed to uvicorn). When set, health checks
    use https.

.PARAMETER TimeoutKeepAlive
    Timeout for keep-alive in seconds (passed to uvicorn).

.PARAMETER TimeoutGracefulShutdown
    Timeout for graceful shutdown in seconds (passed to uvicorn).

.PARAMETER Loop
    Event loop implementation for uvicorn (passed to uvicorn).

.EXAMPLE
    .\scripts\deploy.ps1
    # Setup-only: already in a clone on develop with backend\.env present.

.EXAMPLE
    .\scripts\deploy.ps1 -Clone -EnvFile C:\qa-env\.env -TargetDir C:\apps\jai-school
    # Fresh-machine deploy.
#>

[CmdletBinding()]
param(
    [switch]$Clone,
    [string]$RepoUrl = 'http://192.168.1.59/AI-Team/JAI-School/_git/JAI-School',
    [string]$Branch = 'develop',
    [string]$TargetDir = '.\JAI-School',
    [string]$EnvFile,
    [string]$FrontendEnvFile = 'C:\qa-env\.env.frontend',
    [string]$ServiceName = 'JAI-School',
    [string]$Nssm = 'nssm',
    [alias('Host')]
    [string]$CheckHost = 'localhost',
    [int]$Port = 8000,
    [string]$LogDir,
    [string]$SslKeyfile,
    [string]$SslCertfile,
    [int]$TimeoutKeepAlive,
    [int]$TimeoutGracefulShutdown,
    [string]$Loop
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Write-Banner {
    param([string]$Text)
    Write-Host ''
    Write-Host ('=' * 70) -ForegroundColor Cyan
    Write-Host (' ' + $Text) -ForegroundColor Cyan
    Write-Host ('=' * 70) -ForegroundColor Cyan
}

function Invoke-Native {
    param(
        [Parameter(Mandatory)][string]$File,
        [string[]]$ArgList = @(),
        [string]$WorkingDirectory
    )
    if ($WorkingDirectory) {
        Push-Location $WorkingDirectory
    }
    try {
        Write-Host "> $File $($ArgList -join ' ')" -ForegroundColor DarkGray
        & $File @ArgList
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed (exit $LASTEXITCODE): $File $($ArgList -join ' ')"
        }
    } finally {
        if ($WorkingDirectory) { Pop-Location }
    }
}

# ---------------------------------------------------------------------------
# NSSM service helpers
# ---------------------------------------------------------------------------
function Invoke-NssmQuiet {
    # Run an nssm command tolerantly: swallow its output and any non-zero exit
    # WITHOUT letting native stderr become a terminating error. On PS 5.1,
    # redirecting a native command's stderr while $ErrorActionPreference='Stop'
    # turns each stderr line into a terminating error - so relax it locally.
    param(
        [Parameter(Mandatory)][string]$Nssm,
        [Parameter(Mandatory)][string[]]$NssmArgs
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Nssm @NssmArgs 2>&1 | Out-Null } catch { } finally { $ErrorActionPreference = $prev }
}

function Test-NssmService {
    param(
        [Parameter(Mandatory)][string]$Nssm,
        [Parameter(Mandatory)][string]$Name
    )
    # Use Get-Service (pure PowerShell) instead of `nssm status`: an NSSM service
    # is a normal Windows service, so Get-Service finds it by name, and this
    # avoids the PS 5.1 native-stderr-becomes-terminating-error trap that
    # `nssm status` hits when the service does not exist yet.
    return [bool](Get-Service -Name $Name -ErrorAction SilentlyContinue)
}

function Sync-NssmService {
    param(
        [Parameter(Mandatory)][string]$Nssm,
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$AppPath,
        [Parameter(Mandatory)][string]$AppDir,
        [Parameter(Mandatory)][string]$AppParameters,
        [Parameter(Mandatory)][string]$StdoutLog,
        [Parameter(Mandatory)][string]$StderrLog
    )
    if (Test-NssmService -Nssm $Nssm -Name $Name) {
        Write-Host "NSSM service '$Name' exists; updating configuration."
    } else {
        Write-Host "Installing NSSM service '$Name'..."
        Invoke-Native -File $Nssm -ArgList @('install', $Name, $AppPath)
    }
    # Idempotently (re)apply configuration every run so an agent workspace /
    # path / arg change self-heals on the next deploy.
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'Application', $AppPath)
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'AppDirectory', $AppDir)
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'AppParameters', $AppParameters)
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'AppStdout', $StdoutLog)
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'AppStderr', $StderrLog)
    # 4 = OPEN_ALWAYS (append to existing log rather than truncate on restart).
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'AppStdoutCreationDisposition', '4')
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'AppStderrCreationDisposition', '4')
    # Rotate logs online so they don't grow unbounded (10 MB per file).
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'AppRotateFiles', '1')
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'AppRotateOnline', '1')
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'AppRotateBytes', '10485760')
    # Survive server reboots and restart uvicorn if it crashes.
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'Start', 'SERVICE_AUTO_START')
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'AppExit', 'Default', 'Restart')
    Invoke-Native -File $Nssm -ArgList @('set', $Name, 'AppRestartDelay', '3000')
}

function Stop-NssmService {
    param(
        [Parameter(Mandatory)][string]$Nssm,
        [Parameter(Mandatory)][string]$Name
    )
    if (Test-NssmService -Nssm $Nssm -Name $Name) {
        Write-Host "Stopping service '$Name'..." -ForegroundColor DarkGray
        # Returns non-zero if it was already stopped; that's fine.
        Invoke-NssmQuiet -Nssm $Nssm -NssmArgs @('stop', $Name)
    }
}

function Start-NssmService {
    param(
        [Parameter(Mandatory)][string]$Nssm,
        [Parameter(Mandatory)][string]$Name
    )
    Invoke-Native -File $Nssm -ArgList @('start', $Name)
}

# Legacy cleanup: kill any pre-NSSM detached uvicorn still holding the port
# (relevant only on the first deploy that migrates off start-server.bat).
function Stop-LegacyBackend {
    param([int]$Port)
    $candidates = @()
    $bd = Get-Variable -Name backendDir -ValueOnly -ErrorAction SilentlyContinue
    if ($bd) { $candidates += (Join-Path $bd 'stop-server.ps1') }
    $candidates += (Join-Path (Split-Path -Parent $PSScriptRoot) 'backend\stop-server.ps1')

    $stopScript = $candidates | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -First 1
    if (-not $stopScript) {
        Write-Host "  (no stop-server.ps1 found; skipping legacy port cleanup)" -ForegroundColor DarkGray
        return
    }
    try {
        & $stopScript -Port $Port
    } catch {
        Write-Warning "Stop-LegacyBackend: $($_.Exception.Message)"
    }
}

function Wait-ForUrl {
    param(
        [Parameter(Mandatory)][string]$Url,
        [int]$TimeoutSeconds = 60
    )
    Write-Host "Waiting for $Url ..." -ForegroundColor DarkGray
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
            if ($resp.StatusCode -eq 200) {
                Write-Host "  ready ($Url)" -ForegroundColor Green
                return
            }
        } catch {
            Start-Sleep -Milliseconds 800
        }
    }
    throw "Timed out after ${TimeoutSeconds}s waiting for $Url"
}

# Health checks hit the backend over its own TLS cert (self-signed / internal
# CA). Trust it for these localhost probes so Invoke-WebRequest doesn't fail
# cert validation on 5.1 (which has no -SkipCertificateCheck).
if ($SslCertfile) {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    [Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
}
$scheme = if ($SslCertfile) { 'https' } else { 'http' }

# If the script is aborted or throws mid-deploy, try to leave the service
# running on the last-good build rather than leaving the site down.
trap {
    Write-Warning "Aborted ($($_.Exception.Message))."
    try {
        if (Test-NssmService -Nssm $Nssm -Name $ServiceName) {
            Write-Warning "Attempting to start '$ServiceName' to restore availability..."
            Invoke-NssmQuiet -Nssm $Nssm -NssmArgs @('start', $ServiceName)
        }
    } catch { }
    break
}

# ---------------------------------------------------------------------------
# Step 1: Resolve repo root
# ---------------------------------------------------------------------------
Write-Banner 'Step 1/8  Prep'

if ($Clone) {
    $repoRoot = (Resolve-Path -LiteralPath $TargetDir -ErrorAction SilentlyContinue)
    if (-not $repoRoot) {
        $repoRoot = $TargetDir
    } else {
        $repoRoot = $repoRoot.Path
    }
} else {
    $repoRoot = Split-Path -Parent $PSScriptRoot
}
Write-Host "Repo root: $repoRoot"

if (-not $LogDir) {
    $LogDir = Join-Path $repoRoot 'logs'
}
if (-not (Test-Path -LiteralPath $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
Write-Host "Log dir:   $LogDir"

# Fail fast if nssm isn't available - the whole deploy depends on it.
$nssmCmd = Get-Command $Nssm -ErrorAction SilentlyContinue
if (-not $nssmCmd) {
    throw "nssm not found (looked for '$Nssm'). Install NSSM and ensure it is on PATH, or pass -Nssm <path-to-nssm.exe>."
}

# ---------------------------------------------------------------------------
# Step 2: Clone + branch switch (optional)
# ---------------------------------------------------------------------------
Write-Banner 'Step 2/8  Clone + branch switch'

if ($Clone) {
    if (Test-Path -LiteralPath (Join-Path $repoRoot '.git')) {
        Write-Host "Repo already cloned at $repoRoot, skipping clone."
    } else {
        Invoke-Native -File 'git' -ArgList @('clone', $RepoUrl, $repoRoot)
    }
    Invoke-Native -File 'git' -ArgList @('-C', $repoRoot, 'switch', $Branch)
} else {
    Write-Host "Skipping clone (no -Clone flag). Assuming $repoRoot is already on $Branch."
}

$backendDir  = Join-Path $repoRoot 'backend'
$frontendDir = Join-Path $repoRoot 'frontend'

foreach ($d in @($backendDir, $frontendDir)) {
    if (-not (Test-Path -LiteralPath $d)) {
        throw "Expected directory not found: $d"
    }
}

# ---------------------------------------------------------------------------
# Step 3: Place .env files
# ---------------------------------------------------------------------------
Write-Banner 'Step 3/8  Place backend\.env + frontend\.env'

# Skip-if-exists (both env files): a .env already in the workspace is used
# as-is and never overwritten. Only when it's absent do we copy from the
# provided source. In CI the pipeline force-copies fresh env files from
# C:\qa-env before this script runs, so "existing" there means "just placed".
$backendEnv = Join-Path $backendDir '.env'
if (Test-Path -LiteralPath $backendEnv) {
    Write-Host "Using existing $backendEnv"
} elseif ($EnvFile) {
    if (-not (Test-Path -LiteralPath $EnvFile)) {
        throw "-EnvFile not found: $EnvFile"
    }
    Copy-Item -LiteralPath $EnvFile -Destination $backendEnv -Force
    Write-Host "Copied $EnvFile -> $backendEnv"
} else {
    throw "No backend\.env present and -EnvFile not supplied. Provide one or place a .env at $backendEnv."
}

$frontendEnv = Join-Path $frontendDir '.env'
if (Test-Path -LiteralPath $frontendEnv) {
    Write-Host "Using existing $frontendEnv"
} elseif (Test-Path -LiteralPath $FrontendEnvFile) {
    Copy-Item -LiteralPath $FrontendEnvFile -Destination $frontendEnv -Force
    Write-Host "Copied $FrontendEnvFile -> $frontendEnv"
} else {
    throw "No frontend\.env present and -FrontendEnvFile not found ($FrontendEnvFile). Provide one or place a .env at $frontendEnv."
}

# ---------------------------------------------------------------------------
# Step 4: Stop the backend so uv can overwrite the locked .venv python.exe
# ---------------------------------------------------------------------------
Write-Banner "Step 4/8  Stop backend service on :$Port"
Stop-NssmService -Nssm $Nssm -Name $ServiceName
# Belt-and-suspenders for the first migration deploy: clear any legacy detached
# uvicorn still bound to the port (does nothing once fully on the service model).
Stop-LegacyBackend -Port $Port


# ---------------------------------------------------------------------------
# Step 5: Backend setup (uv venv + sync + alembic)
# ---------------------------------------------------------------------------
Write-Banner 'Step 5/8  Backend setup (uv venv + sync + alembic)'

$venvPython = Join-Path $backendDir '.venv\Scripts\python.exe'
if (Test-Path -LiteralPath $venvPython) {
    Write-Host ".venv already present, skipping 'uv venv'."
} else {
    Invoke-Native -File 'uv' -ArgList @('venv') -WorkingDirectory $backendDir
}

Invoke-Native -File 'uv' -ArgList @('sync') -WorkingDirectory $backendDir

# Load .env into PowerShell environment so Python/Alembic can read it
$loadedEnvVars = @()
if (Test-Path -LiteralPath $backendEnv) {
    foreach ($line in Get-Content $backendEnv -ErrorAction SilentlyContinue) {
        if ($line -match '^\s*([^#\s][^=]+)\s*=\s*(.*)') {
            $key = $Matches[1].Trim()
            $val = $Matches[2].Trim().Trim('"', "'")
            Set-Item -Path "env:$key" -Value $val
            $loadedEnvVars += $key
        }
    }
    Write-Host "Loaded .env variables: $($loadedEnvVars -join ', ')"
} else {
    throw "backend\.env not found at $backendEnv"
}

$env:PYTHONUNBUFFERED = '1'
try {
    # -v prints connection string & migration steps; 2>&1 captures stderr
    $alembicOut = & $venvPython -m alembic upgrade head 2>&1
    Write-Host $alembicOut
    
    if ($LASTEXITCODE -ne 0) {
        throw "Alembic failed (exit $LASTEXITCODE):`n$($alembicOut -join [Environment]::NewLine)"
    }
} finally {
    Remove-Item Env:PYTHONUNBUFFERED -ErrorAction SilentlyContinue
}


# ---------------------------------------------------------------------------
# Step 6: (Re)configure and start the backend service, then wait until ready
# ---------------------------------------------------------------------------
Write-Banner 'Step 6/8  Configure + start backend service'

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Expected venv python not found after uv sync: $venvPython"
}

# start-server.bat runs `.venv\Scripts\python.exe -m uvicorn app.main:app %*`,
# so the service runs the same python with the same uvicorn flags directly.
$appParams = @('-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', "$Port")
if ($SslKeyfile)  { $appParams += '--ssl-keyfile', $SslKeyfile }
if ($SslCertfile) { $appParams += '--ssl-certfile', $SslCertfile }
if ($TimeoutKeepAlive -gt 0)        { $appParams += '--timeout-keep-alive', "$TimeoutKeepAlive" }
if ($TimeoutGracefulShutdown -gt 0) { $appParams += '--timeout-graceful-shutdown', "$TimeoutGracefulShutdown" }
if ($Loop) { $appParams += '--loop', $Loop }
# NSSM stores AppParameters as one string; quote any token containing spaces.
$appParamStr = ($appParams | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }) -join ' '

$stdoutLog = Join-Path $LogDir 'uvicorn.log'
$stderrLog = Join-Path $LogDir 'uvicorn.err.log'

Sync-NssmService -Nssm $Nssm -Name $ServiceName `
    -AppPath $venvPython -AppDir $backendDir -AppParameters $appParamStr `
    -StdoutLog $stdoutLog -StderrLog $stderrLog

Start-NssmService -Nssm $Nssm -Name $ServiceName

# Backend must be live here so `npm run generate-types` can reach it.
Wait-ForUrl -Url "${scheme}://${CheckHost}:$Port/openapi.json" -TimeoutSeconds 90

# ---------------------------------------------------------------------------
# Step 7: Frontend build (served live from disk by the running backend)
# ---------------------------------------------------------------------------
Write-Banner 'Step 7/8  Frontend (npm install + generate-types + build)'

$env:NODE_TLS_REJECT_UNAUTHORIZED = '0'
$env:HUSKY = '0'
try {
    Invoke-Native -File 'npm' -ArgList @('install') -WorkingDirectory $frontendDir
    Invoke-Native -File 'npm' -ArgList @('run', 'generate-types') -WorkingDirectory $frontendDir
    Invoke-Native -File 'npm' -ArgList @('run', 'build') -WorkingDirectory $frontendDir
} finally {
    Remove-Item Env:NODE_TLS_REJECT_UNAUTHORIZED -ErrorAction SilentlyContinue
    Remove-Item Env:HUSKY -ErrorAction SilentlyContinue
}

# ---------------------------------------------------------------------------
# Step 8: Health check + summary
# ---------------------------------------------------------------------------
Write-Banner 'Step 8/8  Health check + summary'

Wait-ForUrl -Url "${scheme}://${CheckHost}:$Port/health" -TimeoutSeconds 60

Write-Host ''
Write-Host 'Deploy complete.' -ForegroundColor Green
Write-Host ''
Write-Host "  URL:       ${scheme}://${CheckHost}:$Port/"
Write-Host "  Health:    ${scheme}://${CheckHost}:$Port/health"
Write-Host "  Service:   $ServiceName (NSSM, Start=SERVICE_AUTO_START)"
Write-Host "  Logs:      $stdoutLog"
Write-Host "             $stderrLog"
Write-Host ''
Write-Host 'Manage the backend service:'
Write-Host "  $Nssm status  $ServiceName"
Write-Host "  $Nssm restart $ServiceName"
Write-Host "  $Nssm stop    $ServiceName"
