import ast
from abc import ABC, abstractmethod
from typing import Any

from app.models.domain import RuleContext

# --- DSL AST Nodes ---


class ConditionNode(ABC):
    @abstractmethod
    def accept(self, evaluator: "ConditionEvaluator", context: RuleContext) -> bool:
        pass


class AndNode(ConditionNode):
    def __init__(self, left: ConditionNode, right: ConditionNode):
        self.left = left
        self.right = right

    def accept(self, evaluator: "ConditionEvaluator", context: RuleContext) -> bool:
        return evaluator.visit_and(self, context)


class OrNode(ConditionNode):
    def __init__(self, left: ConditionNode, right: ConditionNode):
        self.left = left
        self.right = right

    def accept(self, evaluator: "ConditionEvaluator", context: RuleContext) -> bool:
        return evaluator.visit_or(self, context)


class NotNode(ConditionNode):
    def __init__(self, expr: ConditionNode):
        self.expr = expr

    def accept(self, evaluator: "ConditionEvaluator", context: RuleContext) -> bool:
        return evaluator.visit_not(self, context)


class HasOptionNode(ConditionNode):
    def __init__(self, option_id: str):
        self.option_id = option_id

    def accept(self, evaluator: "ConditionEvaluator", context: RuleContext) -> bool:
        return evaluator.visit_has_option(self, context)


class HasComponentNode(ConditionNode):
    def __init__(self, component_id: str):
        self.component_id = component_id

    def accept(self, evaluator: "ConditionEvaluator", context: RuleContext) -> bool:
        return evaluator.visit_has_component(self, context)


# --- Parser ---


class ConditionParser:
    """Parses a DSL string into our custom AST."""

    def parse(self, expression: str) -> ConditionNode:
        if not expression or not expression.strip():
            # An empty condition is generally considered true (always fires if trigger matches)
            # Or we could raise an error. We'll return a stub that evaluates to True.
            raise ValueError("Empty condition expression")

        try:
            tree = ast.parse(expression.strip(), mode="eval")
            return self._transform(tree.body)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in condition: {e.msg}") from e

    def _transform(self, node: ast.AST) -> ConditionNode:
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return self._fold_boolop(AndNode, node.values)
            elif isinstance(node.op, ast.Or):
                return self._fold_boolop(OrNode, node.values)
            else:
                raise ValueError(
                    f"Unsupported boolean operator: {type(node.op).__name__}"
                )

        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return NotNode(self._transform(node.operand))
            else:
                raise ValueError(
                    f"Unsupported unary operator: {type(node.op).__name__}"
                )

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls are supported in DSL")

            func_name = node.func.id
            if len(node.args) != 1 or not isinstance(node.args[0], ast.Constant):
                raise ValueError(
                    f"{func_name}() expects exactly one string literal argument"
                )

            arg_val = node.args[0].value
            if not isinstance(arg_val, str):
                raise ValueError(f"{func_name}() argument must be a string")

            if func_name == "has_option":
                return HasOptionNode(arg_val)
            elif func_name == "has_component":
                return HasComponentNode(arg_val)
            else:
                raise ValueError(f"Unknown DSL function: {func_name}")

        else:
            raise ValueError(f"Unsupported expression node: {type(node).__name__}")

    def _fold_boolop(self, node_class: Any, values: list[ast.AST]) -> ConditionNode:
        """Folds n-ary bool ops from Python AST into binary nodes."""
        if len(values) < 2:
            raise ValueError("Boolean operation must have at least two operands")

        left = self._transform(values[0])
        for val in values[1:]:
            right = self._transform(val)
            left = node_class(left, right)

        return left


# --- Evaluator ---


class ConditionEvaluator:
    """Evaluates a parsed DSL AST against a RuleContext."""

    def evaluate(self, node: ConditionNode, context: RuleContext) -> bool:
        return node.accept(self, context)

    def visit_and(self, node: AndNode, context: RuleContext) -> bool:
        return node.left.accept(self, context) and node.right.accept(self, context)

    def visit_or(self, node: OrNode, context: RuleContext) -> bool:
        return node.left.accept(self, context) or node.right.accept(self, context)

    def visit_not(self, node: NotNode, context: RuleContext) -> bool:
        return not node.expr.accept(self, context)

    def visit_has_option(self, node: HasOptionNode, context: RuleContext) -> bool:
        return node.option_id in context.configuration.selected_feature_options

    def visit_has_component(self, node: HasComponentNode, context: RuleContext) -> bool:
        return node.component_id in context.configuration.resolved_components
