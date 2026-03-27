import json
import re

from dotenv import load_dotenv
from litellm import completion

load_dotenv()


# Actual development work should be done here.

PUZZLE_FILE_PATH = r"C:\puzzle\puzzle.txt"

# ======================
# Puzzle categories mapping (simple: 3 puzzles, 3 categories)
# ======================

PUZZLE_CATEGORIES = {
    "math": "Puzzle 1",
    "logic": "Puzzle 3",
    "time": "Puzzle 2",
}


def get_puzzle(category: str) -> str:
    """Get a puzzle based on the category requested by analyzing user intent."""
    try:
        # Check if category is valid
        category_lower = category.lower()
        if category_lower not in PUZZLE_CATEGORIES:
            return f"Error: Unknown category '{category}'. Valid categories are: math, logic, time."

        with open(PUZZLE_FILE_PATH, "r", encoding="utf-8") as file:
            content = file.read()

        # Parse puzzles from file (split by "Puzzle X" pattern)
        puzzles = re.split(r'(?=Puzzle \d+)', content)
        puzzles = [p.strip() for p in puzzles if p.strip()]

        # Find matching puzzle based on category
        puzzle_name = PUZZLE_CATEGORIES[category_lower]
        for puzzle in puzzles:
            if puzzle.startswith(puzzle_name):
                return puzzle

        return "No matching puzzle found in file."

    except FileNotFoundError:
        return "Error: puzzle.txt not found."
    except Exception as e:
        return f"Error: {str(e)}"

# Mapping of tool functions

tool_functions = {
    "get_puzzle": get_puzzle,
}


# ======================
# Tool schema for LLM - describes what the tool does and its parameters
# ======================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_puzzle",
            "description": "Get a puzzle from the puzzle file based on category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["math", "logic", "time"],
                        "description": "The puzzle category. Must be one of: math (number/money puzzles), logic (reasoning puzzles), time (time measurement puzzles)."
                    }
                },
                "required": ["category"]
            }
        }
    }
]

system_prompt = """
You are a puzzle retrieval agent.

Your job is to UNDERSTAND what type of puzzle the user wants and fetch the right one.

Available categories (you MUST choose one of these):
- math: Number, calculation, or money-related puzzles
- logic: Reasoning and deduction puzzles
- time: Time measurement puzzles

Rules:
1. Analyze the user's request to determine which category fits best.
2. Call get_puzzle with one of the three categories: math, logic, or time.
3. You MUST NOT generate puzzles yourself - only retrieve from file.
4. Don't answer anything except puzzles from the file.
5. In context of puzzles also, if user ask anything except puzzle content, for e.g. count , hint, etc, respond with "I can only provide puzzles, that too one at a time. Please ask for a puzzle."

Examples:
- "I want a math puzzle" → math
- "Give me something with logic" → logic
- "A puzzle about measuring time" → time
- "Something with numbers or money" → math
- "A reasoning challenge" → logic
"""
user_task = input("What kind of puzzle would you like? ")

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_task},
]

response = completion(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    max_tokens=512,
)

message = response.choices[0].message

if not message.tool_calls:
    print("\n[Agent Response]:", message.content)
else:
    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments or "{}")  # argument can be like `'{"category": "math"}'` =>  (category='math')

        print(f"\n[Agent Decision]: User wants a '{tool_args.get('category', 'unknown')}' puzzle")
        print(f"[Tool Called]: {tool_name}")

        result = tool_functions[tool_name](**tool_args)

        print(f"\n[Puzzle Retrieved]:\n{result}")