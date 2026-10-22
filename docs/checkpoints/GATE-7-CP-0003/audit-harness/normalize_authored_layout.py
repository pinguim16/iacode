"""Mechanical import-bootstrap and literal wrapping; no lint-rule changes."""

import ast
import copy
import re
from pathlib import Path

from authored_python_quality import authored_paths

ROOT = Path(__file__).resolve().parents[4]


def import_layout(source):
    tree = ast.parse(source)
    prefix = []
    for node in tree.body:
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
                ast.If,
                ast.Try,
                ast.With,
                ast.For,
            ),
        ):
            break
        prefix.append(node)
    imports = [node for node in prefix if isinstance(node, (ast.Import, ast.ImportFrom))]
    if not imports:
        return source
    last = imports[-1].end_lineno
    assignments = [node for node in prefix if isinstance(node, ast.Assign) and node.lineno < last]
    if not assignments:
        return source
    for node in prefix:
        if (
            node.lineno < last
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and ast.unparse(node.value.func) != "sys.path.insert"
        ):
            raise ValueError("Move dynamic module execution explicitly after imports first")
    definitions = {}
    for node in assignments:
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            raise ValueError("Only simple bootstrap assignments may move")
        definitions[node.targets[0].id] = node.value

    class Expand(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in definitions:
                return self.visit(copy.deepcopy(definitions[node.id]))
            return node

    lines = source.splitlines(keepends=True)
    replacements = []
    for node in prefix:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and ast.unparse(node.value.func) == "sys.path.insert"
        ):
            rewritten = Expand().visit(copy.deepcopy(node))
            replacements.append((node.lineno - 1, node.end_lineno, ast.unparse(rewritten) + "\n"))
    moved = "".join("".join(lines[node.lineno - 1 : node.end_lineno]) for node in assignments)
    replacements.append((last, last, "\n" + moved))
    replacements.extend((node.lineno - 1, node.end_lineno, "") for node in assignments)
    for begin, end, value in sorted(replacements, reverse=True):
        lines[begin:end] = [value]
    return "".join(lines)


def wrap_literals(source):
    tree = ast.parse(source)
    original = ast.dump(tree, include_attributes=False)
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    changes = []
    for parent in ast.walk(tree):
        if isinstance(parent, ast.JoinedStr):
            continue
        for node in ast.iter_child_nodes(parent):
            if (
                not isinstance(node, ast.Constant)
                or not isinstance(node.value, (str, bytes))
                or len(node.value) < 60
                or not any(
                    len(line.rstrip()) > 100 for line in lines[node.lineno - 1 : node.end_lineno]
                )
            ):
                continue
            value = node.value
            chunks = [repr(value[index : index + 60]) for index in range(0, len(value), 60)]
            indent = re.match(r"\s*", lines[node.lineno - 1]).group(0)
            replacement = "(\n" + "".join(indent + "    " + chunk + "\n" for chunk in chunks)
            replacement += indent + ")"
            # AST columns are UTF-8 byte offsets, not Python string offsets.
            begin = offsets[node.lineno - 1] + len(
                lines[node.lineno - 1].encode("utf-8")[: node.col_offset].decode("utf-8")
            )
            end = offsets[node.end_lineno - 1] + len(
                lines[node.end_lineno - 1].encode("utf-8")[: node.end_col_offset].decode("utf-8")
            )
            changes.append((begin, end, replacement))
    result = source
    for begin, end, value in sorted(changes, reverse=True):
        result = result[:begin] + value + result[end:]
    if ast.dump(ast.parse(result), include_attributes=False) != original:
        raise ValueError("Literal wrapping must preserve the exact executable AST")
    return result


def mark_framework_overrides(source):
    tree = ast.parse(source)
    methods = [
        node
        for parent in ast.walk(tree)
        if isinstance(parent, ast.ClassDef)
        for node in parent.body
        if isinstance(node, ast.FunctionDef) and node.name == "setUp" and not node.decorator_list
    ]
    if not methods:
        return source
    lines = source.splitlines(keepends=True)
    for node in sorted(methods, key=lambda node: node.lineno, reverse=True):
        lines.insert(node.lineno - 1, " " * node.col_offset + "@override\n")
    tree = ast.parse("".join(lines))
    first_import = next(
        node
        for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
        and not (isinstance(node, ast.ImportFrom) and node.module == "__future__")
    )
    lines.insert(first_import.lineno - 1, "from typing import override\n")
    return "".join(lines)


def main():
    changed = []
    for name in authored_paths():
        path = ROOT / name
        source = path.read_text(encoding="utf-8")
        try:
            updated = mark_framework_overrides(wrap_literals(import_layout(source)))
        except ValueError as error:
            raise ValueError(name + ": " + str(error)) from error
        if source != updated:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed.append(name)
    print({"mechanically_normalized_paths": len(changed), "lintRulesChanged": False})
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
