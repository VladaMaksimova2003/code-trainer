#!/bin/sh
set -eu

now_ms() {
  date +%s%3N
}

CODE='using System;
class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        if (n % 2 == 0) Console.WriteLine("Even");
        else Console.WriteLine("Odd");
    }
}'

echo "=== In-container dotnet-script profile ==="
T0=$(now_ms)
mkdir -p /tmp/home
T1=$(now_ms)
echo "1_mkdir_tmp_home_ms=$((T1 - T0))"

printf '%s' "$CODE" > /tmp/home/source.csx
T2=$(now_ms)
echo "2_write_source_ms=$((T2 - T1))"

T3=$(now_ms)
printf '4\n' | DOTNET_NOLOGO=1 dotnet-script /tmp/home/source.csx
T4=$(now_ms)
echo "3_run1_cold_file_ms=$((T4 - T3))"

T5=$(now_ms)
printf '7\n' | DOTNET_NOLOGO=1 dotnet-script /tmp/home/source.csx
T6=$(now_ms)
echo "4_run2_same_file_ms=$((T6 - T5))"

T7=$(now_ms)
printf '4\n' | DOTNET_NOLOGO=1 dotnet-script /tmp/home/source.csx >/dev/null
T8=$(now_ms)
echo "5_run3_same_file_ms=$((T8 - T7))"

T9=$(now_ms)
DOTNET_NOLOGO=1 dotnet-script --check /tmp/home/source.csx >/dev/null 2>&1 || true
T10=$(now_ms)
echo "6_check_only_ms=$((T10 - T9))"

if command -v /usr/bin/time >/dev/null 2>&1; then
  echo "=== time -p run4 ==="
  /usr/bin/time -p sh -c "printf '4\n' | DOTNET_NOLOGO=1 dotnet-script /tmp/home/source.csx" 2>&1
fi

echo "=== dotnet-script --version ==="
dotnet-script --version 2>&1 || true

echo "=== cache dirs ==="
find /tmp/home /home/runner -maxdepth 5 -type d 2>/dev/null | head -40
