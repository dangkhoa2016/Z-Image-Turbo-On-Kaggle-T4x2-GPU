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
