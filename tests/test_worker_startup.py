import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "src" / "zimage_server" / "worker_api.py"


def _worker_source():
    return WORKER.read_text(encoding="utf-8")


def test_runtime_loader_is_started_without_blocking_lifespan():
    source = _worker_source()
    tree = ast.parse(source)
    start_fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_start_runtime_load")
    lifespan = next(node for node in tree.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "lifespan")
    start_text = ast.get_source_segment(source, start_fn)
    lifespan_text = ast.get_source_segment(source, lifespan)

    assert "threading.Thread" in start_text
    assert "daemon=True" in start_text
    assert "thread.start()" in start_text
    assert "_start_runtime_load()" in lifespan_text
    assert "_load_runtime()" not in lifespan_text


def test_worker_health_exposes_loading_progress():
    source = _worker_source()
    assert 'status="loading_model"' in source
    assert '"elapsed_seconds": elapsed' in source
    assert '"error": _state.get("error")' in source
    assert '"finished_at"' in source


def test_start_script_waits_on_health_with_diagnostics():
    text = (ROOT / "scripts" / "start.sh").read_text(encoding="utf-8")
    assert "8101/health" in text
    assert "end=time.time()+900" in text
    assert "WORKER_STATUS=" in text
    assert "tail -n 120 logs/worker.log" in text
    assert "nvidia-smi" in text
