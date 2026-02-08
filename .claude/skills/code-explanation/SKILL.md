---
name: code-explanation
description: Explains code with voice-friendly analogies and visual diagrams for RepoBuddy's voice-native onboarding. Use when explaining how code works, teaching about a codebase, or when users ask "how does this work?"
user-invocable: true
allowed-tools: Read, Grep
---

# Code Explanation for Voice Interaction

When explaining code for voice delivery, always follow this structure:

## 1. Start with a Relatable Analogy
Begin with an everyday comparison that makes the concept immediately accessible:
- **API endpoints** → "Like a restaurant waiter taking orders"
- **Database connections** → "Like calling a friend on the phone"  
- **Authentication** → "Like showing your ID at a security desk"
- **Async operations** → "Like ordering food and getting a buzzer"

## 2. Create a Visual Flow Diagram
Use ASCII art to show relationships and data flow:

```
┌─────────────┐    Request    ┌─────────────┐
│   Client    │ ─────────────→ │   Server    │
│ (Browser)   │               │   (API)     │
└─────────────┘               └─────────────┘
       ↑                             │
       │ Response                    │
       │                             ↓
┌─────────────┐    Data      ┌─────────────┐
│    UI       │ ←──────────── │  Database   │
│  Updates    │               │             │
└─────────────┘               └─────────────┘
```

## 3. Step-by-Step Code Walkthrough
Explain the execution flow in logical sequence:
- **What triggers this code?** (user action, system event, scheduled task)
- **What happens first?** (initialization, validation, setup)
- **What's the main logic?** (core processing, business rules)
- **How does it end?** (cleanup, response, error handling)

## 4. Highlight Common Gotchas
Point out frequent mistakes or misconceptions:
- **Race conditions** in async code
- **Memory leaks** from unclosed connections  
- **Security vulnerabilities** in input validation
- **Performance bottlenecks** in loops or queries

## Voice Optimization Guidelines

### Keep Sentences Short
- Break complex ideas into multiple simple sentences
- Use conversational transitions: "Now, here's what happens next..."
- Avoid nested clauses that are hard to follow verbally

### Use Active Voice
- "The function processes the data" (not "The data is processed")
- "We validate the input" (not "The input is validated")

### Pause for Emphasis
- Indicate natural speaking pauses with line breaks
- Use emphasis markers for key terms: **important**, **critical**, **remember**

### Contextual References
- Always mention the file and line number: "In `auth.py` line 42..."
- Reference related files: "This connects to the `database.py` module we saw earlier"

## Examples

### Simple Function Example
```python
def authenticate_user(username, password):
    # Step 1: Find user in database
    user = db.find_user(username)
    
    # Step 2: Check if user exists
    if not user:
        return {"error": "User not found"}
    
    # Step 3: Verify password
    if user.check_password(password):
        return {"success": True, "token": generate_token(user)}
    else:
        return {"error": "Invalid password"}
```

**Voice Explanation:**
"Think of this function like a bouncer at a club. First, they check the guest list (find user), then they verify your ID matches (check password), and finally they give you a wristband if everything checks out (generate token)."

## Additional Resources
- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
