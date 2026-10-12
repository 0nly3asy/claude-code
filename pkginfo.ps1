$path = $args[0]
$p = Get-Content $path -Raw | ConvertFrom-Json
Write-Output "version=$($p.version)"
$exp = $p.exports
if ($exp -is [string]) {
  Write-Output "exports=$exp"
} else {
  Write-Output "exports=$($exp | ConvertTo-Json -Compress -Depth 5)"
}
