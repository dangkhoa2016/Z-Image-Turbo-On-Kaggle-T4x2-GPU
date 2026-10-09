import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks" / "kaggle-t4x2-rest-server-production.ipynb"


def _cells_text(nb):
    return "\n".join("".join(cell.get("source", [])) for cell in nb["cells"])


def test_production_notebook_contract():
    assert NB.is_file(), "production notebook missing"
    nb = json.loads(NB.read_text(encoding="utf-8"))
    assert nb["nbformat"] == 4
    assert nb["cells"][0]["cell_type"] == "markdown"

    markdown_cells = [
        "".join(cell.get("source", []))
        for cell in nb["cells"]
        if cell.get("cell_type") == "markdown"
    ]
    code_cells = [cell for cell in nb["cells"] if cell.get("cell_type") == "code"]
    first = markdown_cells[0]
    text = _cells_text(nb)

    assert first.startswith("# Z-Image-Turbo on Kaggle T4×2 GPU — Production REST Demo\n")
    assert "**English**" in first and "**Tiếng Việt**" in first
    assert "API-only" in first
    assert "one logical pipeline" in first

    before = next(cell for cell in markdown_cells if cell.startswith("## Before you run / Trước khi chạy"))
    assert "GPU T4 x2" in before
    assert "dangkhoa2016/tongyi-mai-z-image-turbo" in before
    assert "PyTorch / default / Version 1" in before
    assert "Internet = ON" in before
    assert "safe_512" in before and "high_768" in before

    assert "## Workflow map / Sơ đồ quy trình" in text
    assert "FastAPI coordinator :8090" in text
    assert "Internal worker :8101" in text

    step_numbers = []
    for cell in markdown_cells:
        match = re.match(r"## Step (\d+) — ", cell)
        if not match:
            continue
        step_numbers.append(int(match.group(1)))
        assert "**English**" in cell
        assert "**Tiếng Việt**" in cell
        assert "### Expected evidence / Kết quả cần thấy" in cell

    assert step_numbers == list(range(1, 12))
    assert len(code_cells) == 11
    assert "## Phase " not in text
    assert "PREFLIGHT=PASS" in text
    assert "BOOTSTRAP_INTEGRITY=PASS" in text
    assert "STATIC_QUALIFICATION=PASS" in text
    assert "WORKER_READY=PASS" in text
    assert "COORDINATOR_READY=PASS" in text
    assert "GOLDEN_512_DETERMINISM=PASS" in text
    assert "evidence/golden-512-seed42.json" in text
    assert "metadata/golden-512-seed42.json" not in text
    assert "QUEUE_ENDURANCE=PASS" in text
    assert "ERROR_BOUNDARIES=PASS" in text
    assert "MIXED_PROFILE_QUALIFICATION=PASS" in text
    assert "PUBLIC_HTTPS_REST_ACCEPTANCE" in text
    assert "FINAL_QUALIFICATION=PASS" in text
    assert "56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307" in text
    assert "high_1024" in text
    assert "trycloudflare.com" not in text
    assert "test-token-abcdefghijklmnopqrstuvwxyz-123456" not in text
    assert nb["metadata"]["zimage"]["api_only"] is True
    assert nb["metadata"]["zimage"]["payload_sha256"]
    assert nb["metadata"]["zimage"]["payload_manifest_sha256"]


def test_static_verifier_honors_explicit_notebook_path():
    import subprocess
    import sys

    script = ROOT / "scripts" / "verify_notebook_static.py"
    missing = ROOT / "notebooks" / "definitely-does-not-exist.ipynb"
    result = subprocess.run(
        [sys.executable, str(script), str(missing)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "definitely-does-not-exist.ipynb" in result.stderr


def test_notebook_keeps_english_and_vietnamese_body_content_separate():
    nb = json.loads(NB.read_text(encoding="utf-8"))
    markdown = ["".join(cell.get("source", [])) for cell in nb["cells"] if cell.get("cell_type") == "markdown"]

    workflow = next(text for text in markdown if text.startswith("## Workflow map / Sơ đồ quy trình"))
    assert "**English**" in workflow
    assert "**Tiếng Việt**" in workflow
    assert "runtime. / Notebook" not in workflow

    steps = [text for text in markdown if text.startswith("## Step ")]
    assert len(steps) == 11
    for step in steps:
        assert "**English**" in step
        assert "**Tiếng Việt**" in step
        assert "### Expected evidence / Kết quả cần thấy" in step
        expected = step.split("### Expected evidence / Kết quả cần thấy", 1)[1]
        assert "**English**" in expected
        assert "**Tiếng Việt**" in expected


def test_embedded_payload_matches_repository_sources():
    import ast
    import base64
    import io
    import tarfile

    nb = json.loads(NB.read_text(encoding="utf-8"))
    text = _cells_text(nb)
    match = re.search(r"PAYLOAD_B64 = ('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")", text)
    assert match, "embedded payload missing"
    payload = base64.b64decode(ast.literal_eval(match.group(1)))
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        members = {member.name: archive.extractfile(member).read() for member in archive.getmembers() if member.isfile()}

    required = {"scripts/api_contract_acceptance.py", "scripts/verify_evidence.py"}
    assert required <= members.keys()
    for name, data in members.items():
        source = ROOT / name
        assert source.is_file(), f"payload member missing from repository: {name}"
        assert data == source.read_bytes(), f"stale notebook payload member: {name}"


def test_notebook_embeds_live_generation_images():
    nb = json.loads(NB.read_text(encoding="utf-8"))
    text = _cells_text(nb)
    assert "from IPython.display import Image, Markdown, display" in text
    assert "Image(data=png_bytes" in text
    assert "NOTEBOOK_EVENT" in text
    assert "ZIMAGE_NOTEBOOK_EVENTS" in text
    assert "job_complete" in text
    assert "mixed_complete" in text

    step7 = next("".join(cell.get("source", [])) for cell in nb["cells"] if cell.get("cell_type") == "code" and "endurance_queue_acceptance.py" in "".join(cell.get("source", [])) and "subprocess.Popen" in "".join(cell.get("source", [])))
    step9 = next("".join(cell.get("source", [])) for cell in nb["cells"] if cell.get("cell_type") == "code" and "mixed_profile_acceptance.py" in "".join(cell.get("source", [])) and "subprocess.Popen" in "".join(cell.get("source", [])))
    assert "subprocess.Popen" in step7
    assert "subprocess.Popen" in step9


def test_worker_startup_cell_streams_status_and_fail_closed_diagnostics():
    nb = json.loads(NB.read_text(encoding="utf-8"))
    step4 = next(
        "".join(cell.get("source", []))
        for cell in nb["cells"]
        if cell.get("cell_type") == "code" and "worker readiness" in "".join(cell.get("source", []))
    )
    assert "8101/health" in step4
    assert "time.monotonic()+900" in step4
    assert "WORKER_STATUS=" in step4
    assert "worker.log" in step4
    assert "nvidia-smi" in step4
    assert "loading_model" in step4


def test_preflight_enables_parallel_model_loading_before_diffusers_import():
    nb = json.loads(NB.read_text(encoding="utf-8"))
    step1 = next(
        "".join(cell.get("source", []))
        for cell in nb["cells"]
        if cell.get("cell_type") == "code" and "PREFLIGHT=PASS" in "".join(cell.get("source", []))
    )
    enable = "os.environ['HF_ENABLE_PARALLEL_LOADING'] = 'YES'"
    workers = "os.environ['HF_PARALLEL_LOADING_WORKERS'] = '4'"
    imports = "import torch, diffusers, transformers, accelerate"

    assert enable in step1
    assert workers in step1
    assert step1.index(enable) < step1.index(imports)
    assert step1.index(workers) < step1.index(imports)
    assert "'parallel_loading': os.environ['HF_ENABLE_PARALLEL_LOADING']" in step1
    assert "'parallel_loading_workers': int(os.environ['HF_PARALLEL_LOADING_WORKERS'])" in step1
