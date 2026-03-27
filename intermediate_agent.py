
    import json
    import re

    from dotenv import load_dotenv
    from litellm import completion

    load_dotenv()

    PUZZLE_FILE_PATH = r"C:\puzzle\puzzle.txt"

    # ======================
    # State: Track which puzzles have been used
    # ======================

    used_puzzles = set()

    def get_available_puzzles() -> str:
        """Get list of puzzles that haven't been used yet."""
        try:
            with open(PUZZLE_FILE_PATH, "r", encoding="utf-8") as file:
                content = file.read()

            # Parse all puzzles from file
            puzzles = re.split(r'(?=Puzzle \d+)', content)
            puzzles = [p.strip() for p in puzzles if p.strip()]

            # Filter out used puzzles
            available = []
            for puzzle in puzzles:
                # Extract puzzle name (e.g., "Puzzle 1")
                match = re.match(r'(Puzzle \d+)', puzzle)
                if match:
                    puzzle_name = match.group(1)
                    if puzzle_name not in used_puzzles:
                        # Get first line as title
                        first_line = puzzle.split('\n')[0]
                        available.append(first_line)

            if not available:
                return "NO_PUZZLES_LEFT"

            return "Available puzzles:\n" + "\n".join(f"- {p}" for p in available)

        except FileNotFoundError:
            return "Error: puzzle.txt not found."
        except Exception as e:
            return f"Error: {str(e)}"
        

    def get_puzzle(puzzle_number: int) -> str:
        """Get a specific puzzle by its number and mark it as used."""
        global used_puzzles

        try:
            with open(PUZZLE_FILE_PATH, "r", encoding="utf-8") as file:
                content = file.read()

            # Parse puzzles from file
            puzzles = re.split(r'(?=Puzzle \d+)', content)
            puzzles = [p.strip() for p in puzzles if p.strip()]

            # Find the requested puzzle
            puzzle_name = f"Puzzle {puzzle_number}"

            for puzzle in puzzles:
                if puzzle.startswith(puzzle_name):
                    # Mark as used
                    used_puzzles.add(puzzle_name)
                    return puzzle

            return f"Puzzle {puzzle_number} not found in file."

        except FileNotFoundError:
            return "Error: puzzle.txt not found."
        except Exception as e:
            return f"Error: {str(e)}"
        
    tool_functions = {
        "get_available_puzzles": get_available_puzzles,
        "get_puzzle": get_puzzle,
    }

    # ==Tool Schema for LLM - describes what the tool does and its parameters==

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_available_puzzles",
                "description": "Get a list of puzzles that are still available (not yet used). Returns 'NO_PUZZLES_LEFT' if all puzzles have been used.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_puzzle",
                "description": "Get a specific puzzle by its number. This marks the puzzle as used.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "puzzle_number": {
                            "type": "integer",
                            "description": "The puzzle number to retrieve (e.g., 1, 2, or 3)"
                        }
                    },
                    "required": ["puzzle_number"]
                }
            }
        }
    ]


    # ======================
    # System Prompt
    # ======================

    system_prompt = """
    You are a puzzle delivery agent that gives users puzzles one at a time.

    Your workflow:
    1. First, check what puzzles are available using get_available_puzzles
    2. If puzzles are available, pick one and retrieve it using get_puzzle
    3. Present the puzzle to the user
    4. If user asks for another puzzle, repeat the process
    5. If no puzzles are left (NO_PUZZLES_LEFT), inform the user that all puzzles have been used

    Rules:
    - Always check available puzzles first before retrieving one
    - Never make up puzzles - only use ones from the file
    - When all puzzles are exhausted, clearly tell the user
    - Don't answer anything except puzzles from the file
    - In context of puzzles also, if user ask anything except puzzle content, for e.g. count , hint, etc, respond with "I can only provide puzzles, that too one at a time. Please ask for a puzzle."
    """
    #======================
    # Agent Loop Function
    # ======================

    def run_agent_loop(user_input: str, messages: list) -> str:
        """
        Run the agent loop until LLM decides to stop calling tools.
        Returns the final response from the agent.
        """

        # Add user message
        messages.append({"role": "user", "content": user_input})

        while True:
            # Call LLM
            response = completion(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                max_tokens=1024,
            )

            message = response.choices[0].message

            # If no tool calls, LLM is done - return the response
            if not message.tool_calls:
                # Add assistant response to history
                messages.append({"role": "assistant", "content": message.content})
                return message.content

            # Process each tool call
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments or "{}")

                print(f"  [Tool Called]: {tool_name}")
                if tool_args:
                    print(f"  [Arguments]: {tool_args}")

                # Execute the tool
                result = tool_functions[tool_name](**tool_args)

                print(f"  [Tool Result]: {result[:100]}..." if len(str(result)) > 100 else f"  [Tool Result]: {result}")
                print()

                # Add assistant message with tool call to history
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                })

                # Add tool result to history so LLM can see it
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

    # ======================main ====================

    def main():
        print("=" * 50)
        print("Puzzle Agent - Agent Loop Demo")
        print("=" * 50)
        print("Ask for puzzles! Type 'quit' to exit.\n")

        # Initialize conversation with system prompt
        messages = [{"role": "system", "content": system_prompt}]

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not user_input:
                continue

            print("\n[Agent Processing...]")

            # Run the agent loop
            response = run_agent_loop(user_input, messages)

            print(f"\nAgent: {response}\n")
            print("-" * 50)


    if __name__ == "__main__":
        main()