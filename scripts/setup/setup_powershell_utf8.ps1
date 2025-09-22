# PowerShell UTF-8 Profile Setup
# This script adds UTF-8 support to your PowerShell profile

Write-Host "Setting up PowerShell UTF-8 profile..." -ForegroundColor Green

# Get PowerShell profile path
$profilePath = $PROFILE.CurrentUserAllHosts
$profileDir = Split-Path $profilePath -Parent

Write-Host "PowerShell profile path: $profilePath" -ForegroundColor Blue

# Create profile directory if it doesn't exist
if (!(Test-Path $profileDir)) {
    Write-Host "Creating PowerShell profile directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

# UTF-8 configuration to add
$utf8Config = @"
# ================================================================
# UTF-8 Encoding Configuration
# Added by setup_powershell_utf8.ps1
# ================================================================

# Set output encoding to UTF-8
`$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Set Python IO encoding
`$env:PYTHONIOENCODING = "utf-8"

# Set locale variables
`$env:LANG = "en_US.UTF-8"
`$env:LC_ALL = "en_US.UTF-8"

# Display confirmation
Write-Host "🌟 UTF-8 encoding enabled for PowerShell session" -ForegroundColor Green

"@

# Check if profile exists and add configuration
if (Test-Path $profilePath) {
    $currentProfile = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue

    if ($currentProfile -and $currentProfile -like "*UTF-8 Encoding Configuration*") {
        Write-Host "ℹ️  UTF-8 configuration already exists in PowerShell profile" -ForegroundColor Blue
    } else {
        # Append to existing profile
        Add-Content -Path $profilePath -Value "`n$utf8Config"
        Write-Host "✅ UTF-8 configuration added to existing PowerShell profile" -ForegroundColor Green
    }
} else {
    # Create new profile with UTF-8 configuration
    Set-Content -Path $profilePath -Value $utf8Config
    Write-Host "✅ New PowerShell profile created with UTF-8 configuration" -ForegroundColor Green
}

# Test the configuration immediately
Write-Host "`nTesting UTF-8 configuration in current session..." -ForegroundColor Yellow

# Apply settings to current session
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# Test Unicode output
try {
    Write-Host "🚀 PowerShell Unicode test: 💻🔥👨‍💻🌟" -ForegroundColor Cyan

    # Test Python Unicode if available
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host "Testing Python Unicode output..." -ForegroundColor Yellow
        python -c "print('🐍 Python Unicode test: 💻🔥👨‍💻🌟')"
    }

    Write-Host "✅ Unicode test successful!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Unicode test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 PowerShell UTF-8 setup complete!" -ForegroundColor Green
Write-Host "Your PowerShell profile will now automatically enable UTF-8 encoding." -ForegroundColor White
Write-Host "`nTo use immediately, restart PowerShell or run:" -ForegroundColor Yellow
Write-Host ". `$PROFILE" -ForegroundColor Cyan