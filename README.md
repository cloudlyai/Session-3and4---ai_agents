# AI Agents - Sessions 3 & 4

Code from Sessions 3 and 4 of the AI Engineering course. We built two versions of a puzzle agent that uses tool calling to fetch puzzles from a local file instead of making them up.

## What's in here

**basic_agent.py** : single-turn agent. You tell it what kind of puzzle you want (math, logic, or time), it figures out the category and pulls the right one from `puzzle.txt`. That's it, one request and done.

**intermediate_agent.py** : multi-turn agent with an actual loop. Keeps track of which puzzles have already been shown so it doesn't repeat them. You can keep asking for more puzzles in the same session until they run out.

## Concepts covered

- Tool / function calling with LiteLLM
- How the agent loop works (LLM calls tool → gets result → decides what to do next)
- Maintaining state across turns (tracking used puzzles)
- Writing tool schemas and system prompts that actually constrain agent behavior

## Setup

```bash
pip install litellm python-dotenv
```

Create a `.env` file with your OpenAI key:

```
OPENAI_API_KEY=your_key_here
```

You also need a `puzzle.txt` file at `C:\puzzle\puzzle.txt`. Format it like:

```
Puzzle 1
<puzzle text>

Puzzle 2
<puzzle text>

Puzzle 3
<puzzle text>
```

## Running

```bash
python basic_agent.py
python intermediate_agent.py
```
