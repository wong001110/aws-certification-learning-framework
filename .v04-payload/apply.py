from __future__ import annotations
import base64,bz2,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
parts=[]
for path in sorted((root/".v04-payload").glob("chunk-*.txt")):
    parts.append(path.read_text(encoding="utf-8"))
data=json.loads(bz2.decompress(base64.b85decode("".join(parts).encode())).decode())
for name,content in data.items():
    target=root/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(content,encoding="utf-8")
shutil.rmtree(root/".v04-payload")
(root/".github/workflows/apply-v04.yml").unlink(missing_ok=True)
print(f"Applied AWS Certification Learning Framework v0.4: {len(data)} files")
