# Let the model think (chain of thought prompting) to increase performance

When faced with complex tasks like research, analysis, or problem-solving, giving the model space to think can dramatically improve its performance. This technique, known as chain of thought (CoT) prompting, encourages the model to break down problems step-by-step, leading to more accurate and nuanced outputs.

## Before implementing CoT

### Why let the model think?
- **Accuracy:** Stepping through problems reduces errors, especially in math, logic, analysis, or generally complex tasks.
- **Coherence:** Structured thinking leads to more cohesive, well-organized responses.
- **Debugging:** Seeing the model's thought process helps you pinpoint where prompts may be unclear.

### Why not let the model think?
- Increased output length may impact latency.
- Not all tasks require in-depth thinking.

## How to prompt for thinking
- **Basic prompt**: Include "Think step-by-step" in your prompt.
- **Guided prompt**: Outline specific steps for the model to follow in its thinking process.
- **Structured prompt**: Use XML tags like `<thinking>` and `<answer>` to separate reasoning from the final answer.

# Use examples (multishot prompting) to guide the model's behavior

Examples are your secret weapon shortcut for getting the model to generate exactly what you need. By providing a few well-crafted examples in your prompt, you can dramatically improve the accuracy, consistency, and quality of the model's outputs.

## Why use examples?
- **Accuracy**: Examples reduce misinterpretation of instructions.
- **Consistency**: Examples enforce uniform structure and style.
- **Performance**: Well-chosen examples boost the model's ability to handle complex tasks.

## Crafting effective examples
For maximum effectiveness, make sure that your examples are:
- **Relevant**: Mirror your actual use case.
- **Diverse**: Cover edge cases and potential challenges.
- **Clear**: Wrap your examples in `<example>` tags.

# Be clear, direct, and detailed

When interacting with the model, think of it as a brilliant but very new employee (with amnesia) who needs explicit instructions.
- **Give the model contextual information:** What the task results will be used for, audience, workflow, end goal.
- **Be specific about what you want the model to do.**
- **Provide instructions as sequential steps.**

# Chain complex prompts for stronger performance

When working with complex tasks, break down actions into manageable subtasks.
1. **Identify subtasks**: Break down into single sequence steps.
2. **Structure with XML for clear handoffs**: Pass outputs using XML tags.
3. **Have a single-task goal**
4. **Iterate**

## Advanced: Self-correction chains
You can chain prompts to have the model review its own work! This catches errors and refines outputs, especially for high-stakes tasks.

# Long context prompting tips

- **Put longform data at the top**: Place your long documents and inputs near the top of your prompt, above your query, instructions, and examples.
- **Structure document content and metadata with XML tags**.
- **Ground responses in quotes**: For long document tasks, ask the model to quote relevant parts.

# Extended thinking tips
- Thinking tokens have a minimum budget of 1024 tokens.
- Start with general instructions to think deeply about a task rather than step-by-step prescriptive guidance.
- Allow for structured execution when needed, but first give general instructions.
