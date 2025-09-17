# Windows UTF-8 System Setup - Run as Administrator
# This script permanently sets UTF-8 encoding for all Python processes on Windows

Write-Host "Setting up UTF-8 encoding for Windows system..." -ForegroundColor Green

# Set system environment variable for PYTHONIOENCODING
Write-Host "Setting PYTHONIOENCODING=utf-8 for current user..." -ForegroundColor Yellow
[Environment]::SetEnvironmentVariable("PYTHONIOENCODING", "utf-8", "User")

# Optional: Set for all users (requires admin rights)
# [Environment]::SetEnvironmentVariable("PYTHONIOENCODING", "utf-8", "Machine")

# Set console code page to UTF-8 in registry (persistent)
Write-Host "Setting console code page to UTF-8..." -ForegroundColor Yellow
try {
    # Set code page for Command Prompt
    $regPath = "HKCU:\Console"
    if (!(Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
    }
    Set-ItemProperty -Path $regPath -Name "CodePage" -Value 65001 -Type DWord

    Write-Host "✅ Console code page set to 65001 (UTF-8)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not set console code page: $($_.Exception.Message)" -ForegroundColor Red
}

# Configure PowerShell for UTF-8
Write-Host "Configuring PowerShell for UTF-8..." -ForegroundColor Yellow
$profilePath = $PROFILE.CurrentUserAllHosts
$profileDir = Split-Path $profilePath -Parent

# Create profile directory if it doesn't exist
if (!(Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

# Add UTF-8 configuration to PowerShell profile
$utf8Config = @"

# UTF-8 Encoding Configuration - Added by setup_windows_utf8.ps1
`$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
`$env:PYTHONIOENCODING = "utf-8"
Write-Host "Unicode/UTF-8 encoding enabled for PowerShell session" -ForegroundColor Green

"@

# Add configuration if not already present
if (Test-Path $profilePath) {
    $currentProfile = Get-Content $profilePath -Raw
    if ($currentProfile -notlike "*UTF-8 Encoding Configuration*") {
        Add-Content -Path $profilePath -Value $utf8Config
        Write-Host "✅ UTF-8 configuration added to PowerShell profile" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  UTF-8 configuration already exists in PowerShell profile" -ForegroundColor Blue
    }
} else {
    Set-Content -Path $profilePath -Value $utf8Config
    Write-Host "✅ PowerShell profile created with UTF-8 configuration" -ForegroundColor Green
}

# Verify the settings
Write-Host "`nVerifying UTF-8 setup..." -ForegroundColor Yellow
$pythonIOEncoding = [Environment]::GetEnvironmentVariable("PYTHONIOENCODING", "User")
if ($pythonIOEncoding -eq "utf-8") {
    Write-Host "✅ PYTHONIOENCODING is set to: $pythonIOEncoding" -ForegroundColor Green
} else {
    Write-Host "❌ PYTHONIOENCODING is not set correctly" -ForegroundColor Red
}

Write-Host "`n🎉 UTF-8 setup complete!" -ForegroundColor Green
Write-Host "Please restart your terminals/command prompts to use the new settings." -ForegroundColor Yellow
Write-Host "`nTo test Unicode support, run:" -ForegroundColor Blue
Write-Host "python -c `"print('🚀 Unicode test: 💻🔥👨‍💻🌟')`"" -ForegroundColor Cyan

# Test Unicode immediately
Write-Host "`nTesting Unicode support in current session..." -ForegroundColor Yellow
try {
    $env:PYTHONIOENCODING = "utf-8"
    $OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8

    python -c "print('🚀 Unicode test: 💻🔥👨‍💻🌟 SUCCESS!')"
    Write-Host "✅ Unicode test successful!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Unicode test failed - restart terminal may be needed" -ForegroundColor Yellow
}