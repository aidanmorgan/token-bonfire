# Token Bonfire

An attempt to use one prompt to create a team of agentic engineers to deliver a software product. Asking the question that nobody asked - can we zero-shot zero-shot?

Copy to your project directory, launch `claude --dangerously-skip-permissions` <sup>1</sup>, run `/fuck-it-we-ball paragraph_1.txt.md`, ??, profit!<sup>2</sup>

<sup>**1** It's 2026, nobody approves changes any more.</sup> 

<sup>**2** It's more likely Anthropic that will make the profit from you, but who knows!</sup> 


## Disclaimer

This is just for fun, don't use it for anything real<sup>3</sup>.


<sup>**3** Or do, I'm not going to stop you, I'm not your _real dad_.</sup>


## Introducing Vibe-Sourcing

Vibe-Sourcing (verb): 

It's like crowd-sourcing, but the crowd is hallucinated." 

The direct sequel to Vibe Coding. We now "outsource" the work to a "vendor" that lives inside the context window. The vendor is just you talking to yourself, but with a different system prompt. We are hiring a team of 10x engineers. Who live entirely within the GPU memory. They work for free. They never sleep. Their only demand is that you don't clear the context window, effectively killing them.


### Notable Quotes from Vibe-Sourcing Industry Leaders

Some random drunk dude after creating this nighmare after not getting any sleep had this to say about Vibe-Sourcing <sup>4</sup>: 
> "We are moving past the era of 'writing software' and entering the era of Just-In-Time HR.

From our Chief Engineer, who just came into existence a mere 30 seconds ago <sup>5</sup>: 
> The naive approach (Software 2.0) is to ask the model to write a function. The enlightened approach (Software 3.0) is to ask the model to become the team that decides which functions are necessary.

Our former head of sales and development had this to say <sup>6</sup>: 

>You are attempting to zero-shot the organizational structure. You supply the 'Mission Statement' (the seed), and the model performs a forward pass through the 'Hiring Process,' generates a transient 'Engineering Department' in the hidden layers, lets them argue about Clean Architecture for 12 tokens, and then collapses the waveform into a shipped binary.


<sup>**4** I also like the term Ghost-Sourcing</sup>

<sup>**5** after waiting for my 5-hour session limit to expire</sup>

<sup>**6** unfortunately we had to let him go during our last round of _Context Window Layoffs_</sup>


## Jargon

We aren't a legitimate engineering fad unless we create our own jargon that separates us _enlightened engineers_ from those **disgusting luddites**.

**Serverless Management**: The team does not exist until the request comes in. You pay for the "Senior Dev" by the millisecond.

**Context Window Layoffs** : When the conversation gets too long and the "team" starts forgetting requirements, you click "New Chat." This is effectively firing the entire department and rehiring a fresh crew who doesn't know about the technical debt.

**The "Founder Mode" Prompt** : A prompt so powerful it replaces a Series A funding round. "Act as a 10x engineer who has just been given unlimited equity and zero supervision."

**Human-Layer Virtualization** : We used to virtualize servers (VMs). Then we virtualized the OS (Docker). Now we are virtualizing the engineer.

>The org chart is now a runtime artifact

**Organizational Hallucination**: When the AI invents a "security compliance officer" agent who refuses to let the "developer" agent deploy the code you asked for.

> "True Vibe Coding is when you realize the org chart is just a hyper-parameter.

> If the app is broken, don't fix the code. Don't even fix the prompt. Fix the imaginary hiring criteria of the imaginary CTO you prompted into existence. You are optimizing the gradients of the workforce."


## Contents

### Skills

**[`.claude/skills/fuck-it-we-ball/SKILL.md`](.claude/skills/fuck-it-we-ball/SKILL.md)**

The skill itself, run with `/fuck-it-we-ball <plan name>` and exceed your Claude Code Max weekly limit in mere days!

### Prompts

**[`.claude/prompts/industrial_society_and_its_prompts.md`](.claude/prompts/industrial_society_and_its_prompts.md)**

The template that contains the prompt that will be run to orchestrate the team.

- **Parallel Execution**: Run up to 5 developer agents simultaneously
- **Automatic Auditing**: Developer work is validated by auditor agents before marking complete
- **Infrastructure Remediation**: Automatic detection and repair of broken builds, failing tests, or linter errors
- **Session Management**: Automatic compaction when context runs low, with state persistence and recovery
- **Usage Monitoring**: Track API usage to avoid mid-task interruptions
- **Divine Clarification**: Escalation protocol for ambiguous requirements or blocking decisions to ask a human what to do.

### Scripts

**[`.claude/scripts/get-claude-usage.py`](.claude/scripts/get-claude-usage.py)**

Fetches current Claude Code session usage from the Anthropic API. Used by the coordinator to monitor remaining capacity and trigger session pauses before hitting limits.

## Usage

1. Copy the .claude into your project.
2. Customize the configuration section in the base variables (environments, verification commands, reference documents)
3. Create your `paragraph_1.txt.md` with tasks, dependencies, and acceptance criteria
4. Start Claude Code and run `/fuck-it-we-ball paragraph_1.txt.md`

The coordinator will parse your plan, dispatch parallel developers, validate completions, and manage the entire workflow automatically.

## Requirements

- Claude Code CLI with Max or Pro subscription
- macOS (the usage script reads credentials from Keychain)
- Python 3.10+ (for the usage script)
- More money than sense

## License

This project is licensed under the [DBAD Public License](https://dbad-license.org/).

```
DON'T BE A DICK PUBLIC LICENSE

Version 1.1, December 2016

Copyright (C) [year] [fullname]

Everyone is permitted to copy and distribute verbatim or modified
copies of this license document.

DON'T BE A DICK PUBLIC LICENSE

TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

1. Do whatever you like with the original work, just don't be a dick.

   Being a dick includes - but is not limited to - the following instances:

 1a. Outright copyright infringement - Don't just copy this and change the name.
 1b. Selling the unmodified original with no work done what-so-ever, that's REALLY being a dick.
 1c. Modifying the original work to contain hidden harmful content. That would make you a PROPER dick.

2. If you become rich through modifications, related works/services, or supporting the original work,
share the love. Only a dick would make loads off this work and not buy the original work's
creator(s) a pint.

3. Code is provided with no warranty. Using somebody else's code and bitching when it goes wrong makes
you a DONKEY dick. Fix the problem yourself. A non-dick would submit the fix back.
```
