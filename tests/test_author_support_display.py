import ast
from pathlib import Path

import pandas as pd

SCRIPT = Path("src/main_analysis_mechanism.py")
tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
fn = next(
    (
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "select_top_author_support"
    ),
    None,
)
assert fn is not None, "select_top_author_support not found in main analysis script"

module = ast.Module(body=[fn], type_ignores=[])
ast.fix_missing_locations(module)
namespace = {}
exec(compile(module, str(SCRIPT), "exec"), namespace, namespace)
select = namespace["select_top_author_support"]

cols = ["edge_index", "window_side", "balanced_rank", "share_of_edge_pair_mass"]
all_nan = pd.DataFrame(
    [
        [1, "left", 1, float("nan")],
        [1, "left", 1, float("nan")],
    ],
    columns=cols,
)
out = select(all_nan)
assert out.empty

mixed = pd.DataFrame(
    [
        [1, "left", 1, 0.25],
        [1, "left", 1, 0.75],
        [1, "right", 1, float("nan")],
        [1, "right", 1, float("nan")],
        [2, "left", 2, 0.60],
        [2, "left", 2, 0.40],
    ],
    columns=cols,
)
out = select(mixed)
got = {
    (int(row.edge_index), row.window_side): float(row.share_of_edge_pair_mass)
    for row in out.itertuples(index=False)
}
assert got == {(1, "left"): 0.75, (2, "left"): 0.60}, got
assert not out["share_of_edge_pair_mass"].isna().any()

print("Author-support NaN regression: PASS")
