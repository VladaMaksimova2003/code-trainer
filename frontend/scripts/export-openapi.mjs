/**
 * Dump OpenAPI JSON from the running dev API container into openapi/openapi.json.
 * Requires: docker compose dev stack with service code_trainer_dev-api-1 (or set OPENAPI_DOCKER_CONTAINER).
 */
import { execSync } from "node:child_process"
import { writeFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = dirname(fileURLToPath(import.meta.url))
const outPath = join(__dirname, "../openapi/openapi.json")
const container = process.env.OPENAPI_DOCKER_CONTAINER ?? "code_trainer_dev-api-1"
const py = [
  "from main import app",
  "import json",
  "print(json.dumps(app.openapi()))",
].join("; ")
const cmd = `docker exec ${container} python -c "${py}"`

const json = execSync(cmd, { encoding: "utf8", maxBuffer: 16 * 1024 * 1024 })
writeFileSync(outPath, json.endsWith("\n") ? json : `${json}\n`, "utf8")
console.log(`Wrote ${outPath}`)
