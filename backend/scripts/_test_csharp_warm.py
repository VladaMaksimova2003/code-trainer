import subprocess
cmd = [
    "docker", "exec", "-u", "runner", "deploy-csharp_runner-1", "sh", "-c",
    'CT_WORKSPACE=/tmp/home/manualtest; mkdir -p "$CT_WORKSPACE"; ws="$CT_WORKSPACE"; '
    'rm -rf "$ws/app"; cp -a /runner/template/. "$ws/app/"; echo OK ws=$ws',
]
print(subprocess.run(cmd, capture_output=True, text=True).stdout)
print(subprocess.run(cmd, capture_output=True, text=True).stderr)
