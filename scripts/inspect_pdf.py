import argparse
import json
from educational_research.render.inspect import inspect

p = argparse.ArgumentParser()
p.add_argument("pdf")
p.add_argument("--previews")
a = p.parse_args()
result = inspect(a.pdf, a.previews)
print(json.dumps(result, indent=2))
raise SystemExit(bool(result["errors"]))
