# Distributing OpenClaw

OpenClaw is a Python package. There are three ways to distribute it: as a
standalone executable (via PyInstaller), as a pip-installable wheel, or as a
Docker image.

---

## Option 1 — Standalone executable (PyInstaller)

Produces a single binary that works on macOS, Linux, or Windows without a
Python interpreter installed.

### Prerequisites

```bash
pip install pyinstaller
```

### Build

```bash
cd OpenClaw
pyinstaller --onefile \
  --name openclaw \
  --add-data "prompts:prompts" \
  __main__.py
```

The binary is written to `dist/openclaw` (or `dist/openclaw.exe` on Windows).

### Run

```bash
./dist/openclaw --local --local-model llama3.1:8b
```

### Notes

- The binary is self-contained but still requires Ollama (or an
  `ANTHROPIC_API_KEY`) at runtime.
- Build on the same OS+architecture you intend to run on. macOS ARM binaries
  will not run on Intel or Linux.
- Sign with `codesign` if distributing to other macOS machines:
  ```bash
  codesign --sign - dist/openclaw
  ```

---

## Option 2 — pip wheel

Install directly from source, or publish to PyPI.

### Build the wheel

```bash
cd OpenClaw
pip install build
python -m build --wheel
# Output: dist/openclaw-*.whl
```

### Install locally

```bash
pip install dist/openclaw-*.whl
openclaw --local --local-model llama3.1:8b
```

### Publish to PyPI

```bash
pip install twine
twine upload dist/*
```

> Requires an account at https://pypi.org and an API token.

---

## Option 3 — Docker image

Best for Linux servers or CI environments.

### Build

```bash
docker build -f Dockerfile.openclaw -t openclaw:latest .
```

Create `Dockerfile.openclaw`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY OpenClaw/ ./OpenClaw/
RUN pip install --no-cache-dir -r OpenClaw/requirements.txt
ENTRYPOINT ["python", "-m", "OpenClaw"]
```

### Run

```bash
docker run --rm \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -v "$(pwd)":/workspace \
  openclaw:latest --task "Fix the authentication bug"
```

For local LLMs, point the container at the host Ollama:

```bash
docker run --rm \
  -e OPENCLAW_PROVIDER=local \
  -e OPENCLAW_LOCAL_API_BASE=http://host.docker.internal:11434/v1 \
  -v "$(pwd)":/workspace \
  openclaw:latest --local --local-model llama3.1:8b
```
