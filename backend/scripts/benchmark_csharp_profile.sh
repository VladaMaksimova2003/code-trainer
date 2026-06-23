#!/bin/sh
# Profile C# execution stages inside csharp_runner (mirrors docker_executor.run_shell).
set -eu

CODE='using System;
class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        if (n % 2 == 0) Console.WriteLine("Even");
        else Console.WriteLine("Odd");
    }
}'

now_ms() { date +%s%3N 2>/dev/null || python3 -c 'import time; print(int(time.time()*1000))'; }

log_stage() {
  label="$1"
  t="$2"
  echo "STAGE|$label|${t}ms"
}

T0=$(now_ms)
mkdir -p /tmp/home
T1=$(now_ms)
log_stage "mkdir_tmp_home" "$((T1 - T0))"

printf '%s' "$CODE" > /tmp/home/source.csx
T2=$(now_ms)
log_stage "write_source_file" "$((T2 - T1))"

# dotnet-script with verbose timing via /usr/bin/time if available
if command -v /usr/bin/time >/dev/null 2>&1; then
  TIMEFORMAT='DOTNET_TIME|%R real|%U user|%S sys'
  { time -p sh -c 'DOTNET_NOLOGO=1 dotnet-script /tmp/home/source.csx' <<< '4' ; } 2>&1 | tee /tmp/home/run1.log
else
  T3=$(now_ms)
  printf '4\n' | DOTNET_NOLOGO=1 dotnet-script /tmp/home/source.csx
  T4=$(now_ms)
  log_stage "dotnet_script_run1_total" "$((T4 - T3))"
fi

T5=$(now_ms)
printf '7\n' | DOTNET_NOLOGO=1 dotnet-script /tmp/home/source.csx >/dev/null
T6=$(now_ms)
log_stage "dotnet_script_run2_same_file" "$((T6 - T5))"

# Check restore activity
T7=$(now_ms)
DOTNET_NOLOGO=1 dotnet-script --check /tmp/home/source.csx >/dev/null 2>&1 || true
T8=$(now_ms)
log_stage "dotnet_script_check_only" "$((T8 - T7))"

# List cache dirs
echo "CACHE_DIRS|$(find /tmp/home /home/runner -maxdepth 4 -type d \( -name nuget -o -name .dotnet -o -name cache -o -name dotnet-script \) 2>/dev/null | tr '\n' ';')"
