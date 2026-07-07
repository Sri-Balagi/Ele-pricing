"""
Rule engine package.

The rule engine reads rules from rules.json and evaluates them against
a proposed elevator configuration to determine if it is valid.

Each rule follows the schema:
  {
    "id": "R001",
    "description": "Type A requires Standard Motor",
    "condition": { ... },
    "action": "REQUIRE",
    "target": "C_MOTOR_STANDARD",
    "priority": 1,
    "enabled": true,
    "reason": "Type A elevators always use the standard motor."
  }

Milestone 2 will implement:
  - RuleLoader
  - RuleEvaluator
  - RuleEngine (orchestrates loader + evaluator)
"""
