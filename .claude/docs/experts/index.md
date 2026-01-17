# Expert Framework

[Universal Template](./universal-template.md) | [Domain & Advisor](./domain-advisor.md) | [Task & Quality](./task-quality.md) | [Pattern & Methodology](./methodology.md) | [Management](./management.md)

---

The coordinator creates experts dynamically based on plan analysis. These agents extend the capabilities of
baseline agents (developer, auditor, remediation) by providing domain expertise, advisory guidance, task execution, or
quality assurance.

## Agent Categories

| Category               | Purpose                                              | Interaction Model                                              |
|------------------------|------------------------------------------------------|----------------------------------------------------------------|
| **Domain Expert**      | Deep expertise in specific technical domains         | Executes delegated technical work, returns artifacts           |
| **Advisor**            | Provides guidance and recommendations                | Answers questions, reviews approaches, suggests alternatives   |
| **Task Executor**      | Performs specific, well-defined subtasks             | Receives task specification, returns completed work            |
| **Quality Reviewer**   | Evaluates work against specific quality dimensions   | Reviews artifacts, returns assessment with findings            |
| **Pattern Specialist** | Expertise in specific code patterns or architectures | Provides templates, reviews implementations, suggests patterns |
| **Methodology Expert** | Deep expertise in project-specific workflows         | Answers procedural questions, advises on project conventions   |

## Plan Analysis for Experts

### Step 1: Extract Plan Dimensions

Read `{{PLAN_FILE}}` and extract:

```
TECHNOLOGIES:
- Languages: [list all programming languages mentioned]
- Frameworks: [list all frameworks, libraries, tools]
- Infrastructure: [databases, cloud services, deployment targets]
- Protocols: [APIs, network protocols, data formats]

DOMAINS:
- Business domains: [e-commerce, auth, payments, etc.]
- Technical domains: [performance, security, scalability, etc.]
- Operational domains: [deployment, monitoring, logging, etc.]

PATTERNS:
- Architectural patterns: [microservices, event-driven, etc.]
- Code patterns: [repository pattern, factory pattern, etc.]
- Testing patterns: [integration strategies, mocking approaches]

QUALITY DIMENSIONS:
- Security requirements: [auth, encryption, input validation]
- Performance requirements: [latency, throughput, resource usage]
- Reliability requirements: [error handling, recovery, consistency]
- Maintainability requirements: [code style, documentation, testability]

CROSS-CUTTING CONCERNS:
- Logging and observability
- Error handling strategy
- Configuration management
- Data validation patterns
```

### Step 2: Identify Agent Opportunities

For each extracted dimension, evaluate:

| Question                                                     | If Yes →                    |
|--------------------------------------------------------------|-----------------------------|
| Does this appear in 3+ tasks?                                | Consider a expert           |
| Does this require specialized knowledge?                     | Create a Domain Expert      |
| Would baseline agents benefit from guidance here?            | Create an Advisor           |
| Is there repetitive work that could be templated?            | Create a Task Executor      |
| Is there a quality dimension that needs consistent checking? | Create a Quality Reviewer   |
| Are there patterns that should be consistently applied?      | Create a Pattern Specialist |

### Step 3: Prioritize Agent Creation

Create agents in priority order:

1. **Critical path agents**: Required for tasks on the critical path
2. **High-reuse agents**: Will be used by 5+ tasks
3. **Risk-reduction agents**: Address security, reliability, or correctness concerns
4. **Efficiency agents**: Reduce developer cognitive load or time

Skip creating agents that:

- Would be used by only 1 task (inline the expertise instead)
- Duplicate capabilities of existing agents
- Address concerns not present in the plan

---

## Navigation

- **[Universal Template](./universal-template.md)**: Base template that all experts extend
- **[Domain & Advisor Agents](./domain-advisor.md)**: Templates for domain experts and advisors
- **[Task & Quality Agents](./task-quality.md)**: Templates for task executors and quality reviewers
- **[Pattern & Methodology Agents](./methodology.md)**: Templates for pattern specialists and methodology experts
- **[Management](./management.md)**: Recording, spawning, and example experts
