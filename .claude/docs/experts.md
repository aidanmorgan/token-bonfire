# Expert Framework

The coordinator creates experts dynamically based on plan analysis. These agents extend the capabilities of baseline
agents (developer, auditor, remediation) by providing domain expertise, advisory guidance, task execution, or quality
assurance.

## Contents

This documentation has been split into focused sections for easier navigation:

1. **[Expert Framework Overview](./experts/index.md)**
    - Agent categories and their purposes
    - Plan analysis for identifying expert needs
    - Prioritization framework

2. **[Universal Agent Template](./experts/universal-template.md)**
    - Base template structure that all experts extend
    - Prompt engineering principles
    - Standard protocols for input, output, and signals
    - Quality standards and boundary handling

3. **[Domain Expert & Advisor Templates](./experts/domain-advisor.md)**
    - Domain Expert template for specialized technical work
    - Advisor template for guidance and recommendations

4. **[Task Executor & Quality Reviewer Templates](./experts/task-quality.md)**
    - Task Executor template for well-defined subtasks
    - Quality Reviewer template for quality assessments

5. **[Pattern Specialist & Methodology Expert Templates](./experts/methodology.md)**
    - Pattern Specialist template for code patterns
    - Methodology Expert template for project-specific workflows

6. **[Expert Management](./experts/management.md)**
    - Recording experts in state
    - Agent spawning strategies
    - Example experts for common scenarios

---

## Quick Start

To create a new expert:

1. Review the **[Overview](./experts/index.md)** to understand agent categories
2. Select the appropriate category-specific template from the sections above
3. Follow the **[Universal Template](./experts/universal-template.md)** structure
4. Record the expert using the **[Management](./experts/management.md)** guidelines

---

[View Full Expert Framework →](./experts/index.md)
