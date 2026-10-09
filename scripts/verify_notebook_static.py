from __future__ import annotations
import ast, base64, hashlib, io, json, re, sys, tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NB=Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT/'notebooks/kaggle-t4x2-rest-server-production.ipynb'
FORBIDDEN_PREFIXES=('.runtime/','outputs/','metadata/','evidence/','.pytest_cache/','logs/')
FORBIDDEN_TEXT=('https://internet-encourage-universal-ate.trycloudflare.com',)
STEPS=[f'Step {i} —' for i in range(1,12)]

nb=json.loads(NB.read_text(encoding='utf-8'))
z=nb['metadata']['zimage']
assert z['schema_version']=='1', 'missing zimage.schema_version=1'
assert z['api_only'] is True
text='\n'.join(''.join(c.get('source',[])) for c in nb['cells'])
for bad in FORBIDDEN_TEXT:
    assert bad not in text, f'forbidden stale runtime value: {bad}'
assert '## Phase ' not in text, 'legacy Phase headings remain'
positions=[text.index(step) for step in STEPS]
assert positions==sorted(positions), positions
assert text.count('### Expected evidence / Kết quả cần thấy')==11
for i,c in enumerate(nb['cells']):
    if c.get('cell_type')=='code':
        compile(''.join(c.get('source',[])), f'<cell-{i}>', 'exec')

m=re.search(r"PAYLOAD_B64 = ('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")", text)
assert m, 'embedded payload not found'
payload=base64.b64decode(ast.literal_eval(m.group(1)))
assert hashlib.sha256(payload).hexdigest()==z['payload_sha256']
with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as tf:
    members={member.name: tf.extractfile(member).read() for member in tf.getmembers() if member.isfile()}
names=list(members)
assert names, 'empty payload'
required={'scripts/api_contract_acceptance.py','scripts/verify_evidence.py'}
assert required <= members.keys(), f'missing required payload files: {sorted(required-members.keys())}'
for name,data in members.items():
    assert not name.startswith(FORBIDDEN_PREFIXES), f'forbidden payload member: {name}'
    assert 'cloudflared' not in Path(name).name
    source=ROOT/name
    assert source.is_file(), f'payload member missing from repository: {name}'
    assert source.read_bytes()==data, f'stale notebook payload member: {name}'
assert z['payload_files']==len(names)
print(json.dumps({'cells':len(nb['cells']),'payload_files':len(names),'payload_sha256':z['payload_sha256'],'verdict':'PASS'}, indent=2))
print('NOTEBOOK_STATIC_VERIFY=PASS')
