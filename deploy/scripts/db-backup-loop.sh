#!/bin/sh
# PostgreSQL backup loop for Docker service db_backup.
# Env: PGHOST PGPORT PGUSER PGPASSWORD PGDATABASE
#      BACKUP_INTERVAL_SECONDS (default 86400 = once per day)
#      BACKUP_RETENTION_DAYS     (default 21)
#      BACKUP_RETENTION_MAX_COUNT (default 30, 0 = no cap)

set -eu

INTERVAL="${BACKUP_INTERVAL_SECONDS:-86400}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-21}"
RETENTION_MAX="${BACKUP_RETENTION_MAX_COUNT:-30}"

prune_backups() {
  if [ "$RETENTION_DAYS" -gt 0 ] 2>/dev/null; then
    find /backups -name '*.dump' -type f -mtime +"$RETENTION_DAYS" -print 2>/dev/null |
      while IFS= read -r f; do
        rm -f "$f"
        echo "[db-backup] pruned (age): $f"
      done
  fi

  if [ "$RETENTION_MAX" -gt 0 ] 2>/dev/null; then
    # ls -1t: newest first; tail skips newest N, deletes the rest
    ls -1t /backups/*.dump 2>/dev/null | tail -n +"$((RETENTION_MAX + 1))" |
      while IFS= read -r f; do
        [ -f "$f" ] || continue
        rm -f "$f"
        echo "[db-backup] pruned (cap): $f"
      done
  fi
}

log_disk() {
  count="$(find /backups -name '*.dump' -type f 2>/dev/null | wc -l | tr -d ' ')"
  size="$(du -sh /backups 2>/dev/null | awk '{print $1}' || echo '?')"
  echo "[db-backup] archive: ${count} file(s), total ${size}"
}

mkdir -p /backups
echo "[db-backup] interval=${INTERVAL}s retention=${RETENTION_DAYS}d max=${RETENTION_MAX} -> /backups"

while true; do
  ts="$(date +%Y%m%d_%H%M%S)"
  out="/backups/${PGDATABASE}_${ts}.dump"
  if pg_dump -U "$PGUSER" -Fc -f "$out" "$PGDATABASE"; then
    echo "[db-backup] ok $out"
  else
    echo "[db-backup] FAILED" >&2
    rm -f "$out" 2>/dev/null || true
  fi
  prune_backups
  log_disk
  sleep "$INTERVAL"
done
