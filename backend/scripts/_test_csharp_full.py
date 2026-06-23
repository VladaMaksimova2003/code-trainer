import subprocess

prefix = (
    'CT_WORKSPACE="/tmp/home/deadbeef12345678"; '
    'mkdir -p "$CT_WORKSPACE" && '
    'trap \'rm -rf "$CT_WORKSPACE"\' EXIT INT TERM; '
)
csharp = (
    'ws="$CT_WORKSPACE" && rm -rf "$ws/app" && cp -a /runner/template/. "$ws/app/" && '
    'echo test > "$CT_WORKSPACE/source.cs" && cp "$CT_WORKSPACE/source.cs" "$ws/app/Program.cs" && '
    'cd "$ws/app" && DOTNET_NOLOGO=1 dotnet build --no-restore -v q 2>&1 | tail -3'
)
cmd = ["docker", "exec", "-i", "deploy-csharp_runner-1", "sh", "-c", prefix + csharp]
r = subprocess.run(cmd, capture_output=True, text=True)
print("rc", r.returncode)
print("out", r.stdout[-500:])
print("err", r.stderr[-500:])
