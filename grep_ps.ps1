$ErrorActionPreference = 'SilentlyContinue'
$patterns = $args[0] -split ','
$root = $args[1]
$sel = if ($args[2]) { [int]$args[2] } else { 20 }
Get-ChildItem -Path $root -Recurse -Include '*.ts','*.tsx' |
  Select-String -Pattern $patterns |
  Select-Object -First $sel |
  ForEach-Object {
    "$($_.Filename):$($_.LineNumber): $($_.Line.Trim())"
  }
