#!/usr/bin/env bash
# Confere que todo o código das lições compila, passa no type checker e roda.
#   ./verificar.sh            (usa "python" do PATH; PY=... para outro)
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python}

echo "== TypeScript: tsc (strict) =="
npx tsc
for f in dist/*.js; do
  case "$f" in *test.js|*13_api.js) continue ;; esac
  echo "-- node $f"; node "$f"
done
echo "-- node --test (12)"; node --test dist/12_testes.test.js | grep -E "^# (pass|fail)"
echo "-- 13_api"
node --input-type=module -e '
  import { app } from "./dist/13_api.js";
  const s = app.listen(0, async () => {
    const url = `http://127.0.0.1:${s.address().port}/usuarios`;
    const post = (b) => fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(b) });
    console.log((await post({ nome: "Ana", email: "ana@x.com" })).status, (await post({ nome: "", email: "x" })).status);
    s.close();
  });'

echo "== Python: mypy --strict =="
$PY -m mypy --strict licoes/py
for f in licoes/py/m*.py; do
  case "$f" in *m13_api.py) continue ;; esac
  echo "-- python $f"; $PY "$f"
done
echo "-- pytest (12)"; $PY -m pytest -q licoes/py/test_m12_testes.py | tail -1
echo "-- 13_api"
(cd licoes/py && $PY -c '
from fastapi.testclient import TestClient
from m13_api import app
c = TestClient(app)
print(c.post("/usuarios", json={"nome": "Ana", "email": "ana@x.com"}).status_code,
      c.post("/usuarios", json={"nome": "", "email": "x"}).status_code)')
echo "OK"
