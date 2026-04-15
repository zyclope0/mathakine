"""
LibCST codemod: convert logger.*(f"...") to lazy %-formatting (G004 / flake8-logging-format).

Run from repo root (libcst requires ``-x`` so the module is discoverable)::

    python -m libcst.tool codemod -x \\
        scripts.codemods.g004_lazy_logging.G004LazyLoggingCommand app/ server/

Handles ``FormattedString``, implicit ``ConcatenatedString`` (adjacent f-strings / str chunks),
and libcst ``format_spec`` as a sequence (not ``.parts``).

Does not convert f-string fragments that use format-spec mini-language (e.g. ``{x:.2f}``);
fix those manually to ``%.2f`` (or run ``ruff check --select G004`` and edit remaining sites).
"""

from __future__ import annotations

import libcst as cst
from libcst.codemod import CodemodCommand


LOG_METHODS = frozenset(
    {"debug", "info", "warning", "error", "critical", "exception", "trace"}
)


def _escape_percent_for_fmt(s: str) -> str:
    return s.replace("%", "%%")


def _formatted_string_to_args(
    fs: cst.FormattedString,
) -> tuple[str, list[cst.BaseExpression]] | None:
    fmt_chunks: list[str] = []
    exprs: list[cst.BaseExpression] = []
    for part in fs.parts:
        if isinstance(part, cst.FormattedStringText):
            fmt_chunks.append(_escape_percent_for_fmt(part.value))
        elif isinstance(part, cst.FormattedStringExpression):
            # libcst: format_spec is Sequence[BaseFormattedStringContent], not .parts
            if part.format_spec is not None and len(part.format_spec) > 0:
                return None
            if part.expression is None:
                return None
            conv = part.conversion
            if conv is None:
                fmt_chunks.append("%s")
            elif conv in ("r", ord("r")):
                fmt_chunks.append("%r")
            elif conv in ("s", ord("s")):
                fmt_chunks.append("%s")
            elif conv in ("a", ord("a")):
                fmt_chunks.append("%a")
            else:
                return None
            exprs.append(part.expression)
        else:
            return None
    return "".join(fmt_chunks), exprs


def _expression_to_fmt_and_exprs(
    node: cst.BaseExpression,
) -> tuple[str, list[cst.BaseExpression]] | None:
    """Handle FormattedString, implicit concat (ConcatenatedString), and plain literals."""
    if isinstance(node, cst.FormattedString):
        return _formatted_string_to_args(node)
    if isinstance(node, cst.ConcatenatedString):
        left = _expression_to_fmt_and_exprs(node.left)
        right = _expression_to_fmt_and_exprs(node.right)
        if left is None or right is None:
            return None
        return left[0] + right[0], left[1] + right[1]
    if isinstance(node, cst.SimpleString):
        try:
            text = node.evaluated_value
        except Exception:
            return None
        if text is None:
            return None
        return _escape_percent_for_fmt(text), []
    return None


class _LazyFormatLogging(cst.CSTTransformer):
    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        if not isinstance(updated_node.func, cst.Attribute):
            return updated_node
        attr = updated_node.func.attr
        if not isinstance(attr, cst.Name) or attr.value not in LOG_METHODS:
            return updated_node
        if not updated_node.args:
            return updated_node
        first = updated_node.args[0]
        # Already %-formatted or plain string — do not touch (escaping would break %s).
        if isinstance(first.value, cst.SimpleString):
            return updated_node
        if not isinstance(first.value, (cst.FormattedString, cst.ConcatenatedString)):
            return updated_node
        converted = _expression_to_fmt_and_exprs(first.value)
        if converted is None:
            return updated_node
        fmt_str, exprs = converted
        try:
            fmt_node = cst.SimpleString(repr(fmt_str))
        except Exception:
            return updated_node
        new_first = cst.Arg(value=fmt_node)
        new_expr_args = [cst.Arg(value=e) for e in exprs]
        rest = list(updated_node.args[1:])
        new_args = [new_first] + new_expr_args + rest
        return updated_node.with_changes(args=new_args)


class G004LazyLoggingCommand(CodemodCommand):
    DESCRIPTION = "Convert logger f-strings to %-formatting (G004)."

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        return tree.visit(_LazyFormatLogging())
