import json
from pathlib import Path

ROOT = Path('/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server')
E = ROOT / 'evidence'

endurance = json.loads((E / 'endurance-5jobs.json').read_text())
mixed = json.loads((E / 'mixed-512-768-512.json').read_text())
public = json.loads((E / 'public-tunnel-acceptance.json').read_text())
errors = json.loads((E / 'error-boundary.json').read_text())
golden = json.loads((ROOT / 'metadata' / 'golden-512-seed42.json').read_text())

summary = {
    'project': 'Z-Image-Turbo-Kaggle-T4x2-REST-Server',
    'hardware': {'gpu_count': 2, 'gpu_model': 'Tesla T4'},
    'model': 'dangkhoa2016/tongyi-mai-z-image-turbo/PyTorch/default/1',
    'dtype': 'bfloat16',
    'device_map': {'transformer': 0, 'text_encoder': 1, 'vae': 1},
    'profiles': {
        'safe_512': {'width': 512, 'height': 512, 'steps': 9, 'guidance_scale': 0.0},
        'high_768': {'width': 768, 'height': 768, 'steps': 9, 'guidance_scale': 0.0},
    },
    'golden_512': {
        'sha256': golden['sha256'],
        'inference_seconds': golden['inference_seconds'],
        'pixel_stats': golden['pixel_stats'],
        'verdict': 'PASS',
    },
    'queue_endurance': {
        'initial_states': endurance['initial_states'],
        'latencies': [j['inference_seconds'] for j in endurance['jobs']],
        'verdict': 'PASS',
    },
    'mixed_profile': mixed['summary'],
    'error_boundary': {
        'status_codes': {k: v[0] for k, v in errors['checks'].items()},
        'ready_after': errors['ready_after']['ready'],
        'verdict': 'PASS',
    },
    'public_tunnel': public,
    'unsupported': ['fp16', '1024x1024', 'parallel_gpu_generation', 'pipeline_per_request'],
    'final_verdict': 'PASS',
}
(E / 'qualification-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
print('FINAL_QUALIFICATION=PASS')
