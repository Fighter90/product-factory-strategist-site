import json
d = json.load(open("vendor/meta.json", encoding="utf-8"))
def fix(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "N_TESTS": o[k] = 969
            if isinstance(v, (dict, list)): fix(v)
    elif isinstance(o, list):
        for x in o: fix(x)
fix(d)
json.dump(d, open("vendor/meta.json","w"), ensure_ascii=False, indent=2)
print("meta.json: N_TESTS 969")
