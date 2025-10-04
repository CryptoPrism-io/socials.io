# Unicode/UTF-8 Troubleshooting Guide

## 🚨 Quick Fix for New Environments

If you see this error:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680' in position 0: character maps to <undefined>
```

### Solution (Run Once):

**Windows Users:**
```cmd
setup_windows_utf8.bat
```

**PowerShell Users:**
```powershell
.\setup_windows_utf8.ps1
```

**Git Bash Users:**
```bash
# Already configured automatically via ~/.bashrc
# If issues persist, restart Git Bash terminal
```

## 🧪 Test if Unicode is Working

```bash
# Test system-wide Unicode support
python test_unicode_system.py

# Quick emoji test
python -c "print('🚀 Unicode test: 💻🔥👨‍💻🌟')"
```

**Expected Result:**
```
🚀 Unicode test: 💻🔥👨‍💻🌟
```

## 🔍 Basic Troubleshooting Steps

### 1. Check Environment Variables
```bash
# Check if PYTHONIOENCODING is set
python -c "import os; print('PYTHONIOENCODING:', os.environ.get('PYTHONIOENCODING', 'NOT SET'))"

# Should show: PYTHONIOENCODING: utf-8
```

### 2. Check Python Encoding
```bash
# Check stdout encoding
python -c "import sys; print('Stdout encoding:', sys.stdout.encoding)"

# Should show: Stdout encoding: utf-8
```

### 3. Check Console Code Page (Windows)
```cmd
# Check current code page
chcp

# Should show: Active code page: 65001
```

### 4. Restart Terminal
After running setup scripts, **always restart your terminal** for changes to take effect.

## 🔧 Advanced Troubleshooting

### If Setup Scripts Don't Work

**Manual Windows Fix:**
```cmd
# Set environment variable manually
setx PYTHONIOENCODING utf-8

# Set console code page
chcp 65001

# Restart terminal
```

**Manual PowerShell Fix:**
```powershell
# Add to PowerShell profile
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
```

**Manual Git Bash Fix:**
```bash
# Add to ~/.bashrc
export PYTHONIOENCODING=utf-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

### If Error Persists

1. **Check Python Version**: Ensure Python 3.7+
2. **Check Terminal**: Try different terminal (Windows Terminal, PowerShell, Git Bash)
3. **Reboot System**: Some changes require system restart
4. **Run as Administrator**: Some setup scripts need admin rights

## 📚 What This Fixes

### The Problem
- **Root Cause**: Windows consoles default to CP1252 encoding instead of UTF-8
- **Impact**: Python scripts crash when AI responses contain Unicode characters (emojis, special symbols)
- **Scope**: Affects all terminal types - Command Prompt, PowerShell, Git Bash

### The Solution
**System-Level Fix**: Configure UTF-8 encoding once at the system level instead of per-script

### Why This Approach Works
1. **Permanent**: Configuration persists across all terminal sessions
2. **Automatic**: All Python scripts inherit UTF-8 support
3. **Clean**: No code changes needed in scripts
4. **Professional**: Follows enterprise-grade environment configuration

## 🎯 How It Works

### Priority 1: System Environment Variables
- **PYTHONIOENCODING=utf-8**: Forces all Python processes to use UTF-8 encoding
- **LANG=en_US.UTF-8**: Sets system locale for Unicode support
- **LC_ALL=en_US.UTF-8**: Ensures consistent encoding across all applications

### Priority 2: Terminal-Specific Configuration
- **Windows Console**: Set code page to 65001 (UTF-8) via `chcp 65001`
- **PowerShell**: Configure `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`
- **Git Bash**: Export environment variables in ~/.bashrc

### Priority 3: Codebase Benefits
- **No per-script fixes needed**: All scripts automatically inherit UTF-8
- **Cleaner code**: No repetitive encoding configuration
- **Future-proof**: New scripts work automatically

## ✅ Success Indicators

When working correctly, you should see:

```bash
$ python test_unicode_system.py
============================================================
SYSTEM UNICODE VALIDATION
============================================================
Platform: Windows 11
Python version: 3.13.3

ENCODING SETTINGS:
  Default encoding: utf-8
  Stdout encoding: utf-8  ← Should be utf-8
  Stderr encoding: utf-8
  Filesystem encoding: utf-8
  Locale preferred encoding: cp1252

ENVIRONMENT VARIABLES:
  PYTHONIOENCODING: utf-8  ← Should be utf-8
  LANG: en_US.UTF-8
  LC_ALL: en_US.UTF-8

UNICODE OUTPUT TESTS:
  Basic emojis: 🚀 💻 🔥 ⭐ ✅
  Complex emojis: 👨‍💻 👩‍🎨 🏳️‍🌈
  Mixed content: Python 🐍 + Unicode 🌟 = Success! ✨
  Special chars: αβγδε ñüäöß 中文 العربية
  Math symbols: π ≈ 3.14159 ∞ ∑ ∆ ∇ ∫

============================================================
STATUS: ✅ SYSTEM UNICODE SUPPORT IS WORKING!
============================================================
```

## 🆘 Still Having Issues?

1. **Check the full changelog**: See CHANGELOG.md v1.1.0 for complete details
2. **Run system validation**: `python test_unicode_system.py`
3. **Try different terminals**: Test in Command Prompt, PowerShell, Git Bash
4. **Verify Python installation**: Ensure Python 3.7+ is properly installed
5. **Check system locale**: Windows Settings > Time & Language > Language

## 🎉 Once Working

After successful setup:
- ✅ All Python scripts support Unicode automatically
- ✅ No code changes needed for emoji support
- ✅ Works in all new terminal sessions
- ✅ GitHub Actions workflows handle Unicode properly
- ✅ Professional output formatting for social media content

The fix is **permanent** - you'll never need to configure Unicode encoding again!