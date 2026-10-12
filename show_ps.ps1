$path = $args[0]
$start = if ($args[1]) { [int]$args[1] } else { 1 }
$count = if ($args[2]) { [int]$args[2] } else { 60 }
$lines = Get-Content -Path $path
$begin = $start - 1
$end = [Math]::Min($begin + $count, $lines.Count)
for ($i = $begin; $i -lt $end; $i++) {
  "$($i + 1): $($lines[$i])"
}
