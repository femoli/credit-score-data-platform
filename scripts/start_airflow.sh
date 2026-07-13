#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export PROJECT_ROOT
export AIRFLOW_HOME="${PROJECT_ROOT}/.airflow"
export AIRFLOW__CORE__DAGS_FOLDER="${PROJECT_ROOT}/orchestration/airflow/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES="False"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

AIRFLOW_URL="http://localhost:8080"
PASSWORD_FILE="${AIRFLOW_HOME}/simple_auth_manager_passwords.json.generated"

# Prevent Airflow from opening its internal log server in the browser.
export BROWSER=true

if ! command -v airflow >/dev/null 2>&1; then
    echo "Apache Airflow was not found."
    echo
    echo "Activate the Airflow virtual environment first:"
    echo "source .venv-airflow/bin/activate"
    exit 1
fi

mkdir -p "${AIRFLOW_HOME}"

echo
echo "Starting Apache Airflow..."
echo "AIRFLOW_HOME: ${AIRFLOW_HOME}"
echo "DAGS_FOLDER: ${AIRFLOW__CORE__DAGS_FOLDER}"
echo

airflow standalone &
AIRFLOW_PID=$!

cleanup() {
    echo
    echo "Stopping Apache Airflow..."
    kill "${AIRFLOW_PID}" 2>/dev/null || true
    wait "${AIRFLOW_PID}" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Waiting for the Airflow interface..."

until curl --silent --fail "${AIRFLOW_URL}" >/dev/null 2>&1; do
    if ! kill -0 "${AIRFLOW_PID}" 2>/dev/null; then
        echo
        echo "Apache Airflow stopped before the interface became available."
        exit 1
    fi

    sleep 2
done

echo
echo "========================================"
echo " Apache Airflow is ready"
echo "========================================"
echo " URL:      ${AIRFLOW_URL}"
echo " Username: admin"

if [[ -f "${PASSWORD_FILE}" ]]; then
    PASSWORD="$(
        python -c "
import json
from pathlib import Path

data = json.loads(Path('${PASSWORD_FILE}').read_text())
print(data.get('admin', 'Password not found'))
"
    )"

    echo " Password: ${PASSWORD}"
else
    echo " Password file not found: ${PASSWORD_FILE}"
fi

echo "========================================"
echo

if command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -NoProfile -Command \
        "Start-Process '${AIRFLOW_URL}'" >/dev/null 2>&1
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "${AIRFLOW_URL}" >/dev/null 2>&1
fi

wait "${AIRFLOW_PID}"