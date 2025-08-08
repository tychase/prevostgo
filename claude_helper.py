"""
Example script for using Claude Opus 4.1 with PrevostGo
"""
import anthropic
import os

# Initialize with the specific model
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def get_claude_help(prompt):
    """Get help from Claude Opus 4.1"""
    
    # Read the context file
    with open("claude.md", "r") as f:
        context = f.read()
    
    response = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=4000,
        temperature=0.7,
        system="You are helping with the PrevostGo project. Use the provided context to give specific, actionable advice.",
        messages=[
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nTask: {prompt}"
            }
        ]
    )
    
    return response.content[0].text

# Example usage
if __name__ == "__main__":
    help_needed = "Fix the search functionality to include fuzzy matching"
    result = get_claude_help(help_needed)
    print(result)
