# [SEALED] tools/lifecycle_graph.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/lifecycle_graph.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
"""Total, iterative validation of the canonical replacement graph."""


def lifecycle_errors(records):
    errors = []
    graph = {}
    relations = {}
    for rid, data in records.items():
        relations[rid] = {}
        for field in ("related", "supersedes", "superseded_by"):
            values = data.get(field, [])
            if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
                errors.append(f"{rid}: {field} must be a list of record IDs")
                values = []
            if field != "related" and len(values) != len(set(values)):
                errors.append(f"{rid}: duplicate {field} relation")
            relations[rid][field] = values
        successors = relations[rid]["superseded_by"]
        if data.get("status") == "superseded" and not successors:
            errors.append(f"{rid}: superseded record requires superseded_by provenance")
        if data.get("status") != "superseded" and successors:
            errors.append(f"{rid}: only superseded records may declare superseded_by")
        graph[rid] = relations[rid]["supersedes"]
    for rid, fields in relations.items():
        for field, values in fields.items():
            for ref in values:
                if ref not in records:
                    errors.append(f"{rid}: broken internal relation {field} -> {ref}")
                    continue
                if field == "related":
                    continue
                if rid == ref:
                    errors.append(f"{rid}: self supersession is forbidden")
                reciprocal = "superseded_by" if field == "supersedes" else "supersedes"
                if rid not in relations[ref][reciprocal]:
                    errors.append(f"{rid}: non-reciprocal {field} relation {rid} -> {ref}")
                if field == "supersedes" and records[ref].get("status") != "superseded":
                    errors.append(f"{rid}: supersedes target {ref} is not superseded")
    # Explicit frames avoid recursion limits on valid, long replacement chains.
    colors = {}
    for root in sorted(graph):
        if colors.get(root):
            continue
        colors[root] = 1
        stack = [(root, iter(graph[root]))]
        while stack:
            rid, children = stack[-1]
            ref = next(children, None)
            if ref is None:
                colors[rid] = 2
                stack.pop()
            elif ref in graph:
                if colors.get(ref) == 1:
                    errors.append(f"supersession cycle: {rid} -> {ref}")
                elif not colors.get(ref):
                    colors[ref] = 1
                    stack.append((ref, iter(graph[ref])))
    return errors

````
