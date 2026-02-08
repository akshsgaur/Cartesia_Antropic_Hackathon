---
name: quest-generation
description: Creates adaptive code exploration challenges with progressive difficulty for RepoBuddy's practice mode. Use when generating quests, calibrating difficulty, or creating interactive learning experiences.
user-invocable: true
allowed-tools: Read, Grep
---

# Quest Generation for Code Exploration

## Quest Template Framework

### 1. Core Quest Types

#### 📍 **Navigation Quests** - Find specific code locations
```
**Objective**: Locate and identify key components
**Template**: "Find the [component] that handles [functionality]"
**Example**: "Find the function that processes user payments"
**Skills Tested**: Codebase navigation, pattern recognition
**Difficulty Factors**: 
- Easy: Direct function names
- Medium: Related functionality hints  
- Hard: Abstract problem descriptions
```

#### 🔍 **Analysis Quests** - Understand code behavior
```
**Objective**: Explain how code works and why
**Template**: "Explain how [component] handles [scenario]"
**Example**: "Explain how the system handles concurrent user requests"
**Skills Tested**: Code comprehension, system understanding
**Difficulty Factors**:
- Easy: Single function analysis
- Medium: Multi-file interaction
- Hard: Complex system behavior
```

#### 🐛 **Debug Quests** - Identify and fix issues
```
**Objective**: Find bugs and suggest solutions
**Template**: "Identify the problem in [component] and fix it"
**Example**: "Find the security vulnerability in the authentication code"
**Skills Tested**: Error analysis, problem solving
**Difficulty Factors**:
- Easy: Obvious syntax/logic errors
- Medium: Subtle logic bugs
- Hard: Complex system issues
```

#### 🏗️ **Architecture Quests** - Understand system design
```
**Objective**: Analyze design patterns and decisions
**Template**: "Why was [pattern] used instead of [alternative]?"
**Example**: "Why was JWT chosen over session-based authentication?"
**Skills Tested**: Architectural understanding, trade-off analysis
**Difficulty Factors**:
- Easy: Simple design choices
- Medium: Pattern recognition
- Hard: Complex architectural decisions
```

#### 🔧 **Modification Quests** - Implement changes
```
**Objective**: Add or modify functionality
**Template**: "Add [feature] to [component]"
**Example**: "Add input validation to the user registration form"
**Skills Tested**: Code modification, testing
**Difficulty Factors**:
- Easy: Simple additions
- Medium: Feature integration
- Hard: Complex modifications
```

### 2. Adaptive Difficulty System

#### Performance Tracking
```python
# User performance metrics
performance_metrics = {
    'accuracy': 0.0,      # Correct answer rate
    'speed': 0.0,         # Time to complete quests
    'hints_needed': 0,    # Number of hints requested
    'confidence': 0.0,    # Self-reported confidence
    'streak': 0           # Consecutive correct answers
}

# Difficulty adjustment rules
difficulty_rules = {
    'level_up': 'accuracy >= 0.8 and streak >= 2',
    'level_down': 'accuracy < 0.5 or hints_needed > 3',
    'maintain': '0.5 <= accuracy < 0.8'
}
```

#### Quest Complexity Parameters
```python
complexity_factors = {
    'file_count': 1,          # Number of files involved
    'function_depth': 1,      # Call stack complexity
    'concept_count': 1,       # Number of concepts to understand
    'abstraction_level': 1,    # High-level vs low-level
    'dependencies': 1          # External dependencies
}

# Difficulty calculation
difficulty_score = sum(complexity_factors.values()) / len(complexity_factors)
```

### 3. Quest Generation Process

#### Step 1: Codebase Analysis
```
**Discovery Phase**:
- Scan for key components (APIs, models, services)
- Identify common patterns (authentication, database, error handling)
- Map file relationships and dependencies
- Detect complexity hotspots

**Classification**:
- Categorize files by functionality
- Tag components by difficulty level
- Identify learning opportunities
```

#### Step 2: Quest Template Selection
```
**User Assessment**:
- Current skill level (beginner/intermediate/advanced)
- Previous quest performance
- Learning objectives from curriculum
- User preferences and interests

**Template Matching**:
- Select appropriate quest type
- Adjust complexity parameters
- Customize for specific codebase
- Align with curriculum goals
```

#### Step 3: Quest Customization
```
**Codebase-Specific Adaptation**:
- Replace generic placeholders with actual file/function names
- Use real code snippets and examples
- Reference actual system behavior
- Include relevant error messages or logs

**Personalization**:
- Consider user's background knowledge
- Build on previously covered topics
- Include areas of user interest
- Adjust for learning pace
```

## Quest Templates with Examples

### Navigation Quest Template
```markdown
## 🎯 Code Navigation Challenge

**Mission**: Find the [component] that handles [functionality]

**Context**: [Brief scenario explaining why this is important]

**Hints Available**: 3
**Time Limit**: [Difficulty-based time limit]

### 🔍 Getting Started
1. Think about where this functionality would logically live
2. Look for relevant file names and directory structure
3. Search for key terms related to this functionality

### 💡 Hints
**Hint 1**: [General direction or file type]
**Hint 2**: [Specific directory or file name pattern]  
**Hint 3**: [Exact file location]

### ✅ Success Criteria
- Found the correct file/function
- Can explain what it does
- Located related components

**Example Implementation**:
```

### Analysis Quest Template
```markdown
## 🧠 Code Analysis Challenge

**Mission**: Explain how [component] handles [scenario]

**Code to Analyze**:
```python
[Relevant code snippet]
```

**Questions to Answer**:
1. What is the primary purpose of this code?
2. How does it handle [specific scenario]?
3. What are the key steps in the process?
4. What might be potential edge cases?

**Thinking Points**:
- Consider the input and output
- Look for error handling
- Identify any assumptions made
- Think about performance implications

### 📊 Evaluation Rubric
**Excellent** (4/4): All questions answered correctly with deep insights
**Good** (3/4): Most questions answered with solid understanding
**Developing** (2/4): Basic understanding with some gaps
**Needs Work** (1/4): Limited understanding of the code
```

### Debug Quest Template
```markdown
## 🐛 Debug Challenge

**Mission**: Find and fix the bug in [component]

**Problem Report**: [Description of what's going wrong]

**Buggy Code**:
```python
[Code with bug]
```

### 🔍 Investigation Steps
1. **Reproduce the Issue**: What triggers the bug?
2. **Identify the Root Cause**: Where is the logic error?
3. **Propose a Fix**: How would you correct it?
4. **Test Your Solution**: How would you verify the fix works?

### 🚨 Common Bug Patterns to Look For
- Null/undefined reference errors
- Off-by-one errors in loops
- Missing error handling
- Race conditions in async code
- Incorrect data validation

### ✅ Solution Requirements
- Identify the exact line(s) with the bug
- Explain why the current code fails
- Provide the corrected code
- Suggest how to prevent similar bugs

**Difficulty Adjustment**: 
- Easy: Obvious syntax/logic errors
- Medium: Subtle logic or edge case bugs
- Hard: Complex system interactions
```

## Adaptive Quest Generation

### Dynamic Difficulty Adjustment
```python
def adjust_difficulty(user_performance, current_difficulty):
    """
    Adjust quest difficulty based on user performance
    """
    if user_performance['accuracy'] >= 0.8 and user_performance['streak'] >= 2:
        return min(current_difficulty + 1, 5)  # Level up
    elif user_performance['accuracy'] < 0.5:
        return max(current_difficulty - 1, 1)  # Level down
    else:
        return current_difficulty  # Maintain level
```

### Personalized Quest Selection
```python
def select_quest_template(user_profile, curriculum_objectives):
    """
    Select appropriate quest template based on user and curriculum
    """
    # Consider user's current skill level
    skill_level = user_profile['skill_level']
    
    # Consider curriculum priorities
    priority_topics = curriculum_objectives['current_focus']
    
    # Consider user's interests and background
    interests = user_profile['interests']
    
    # Select best matching template
    return match_template(skill_level, priority_topics, interests)
```

## Progress Tracking and Feedback

### Performance Metrics
```python
quest_metrics = {
    'completion_rate': 0.0,
    'average_time': 0.0,
    'hint_usage': 0.0,
    'difficulty_progression': [],
    'topic_mastery': {},
    'learning_objectives_met': []
}
```

### Feedback Generation
```markdown
## 📈 Quest Results

**Performance Summary**:
- ✅ **Accuracy**: [percentage]%
- ⏱️ **Time**: [time taken]
- 💡 **Hints Used**: [number]/[available]
- 🎯 **Difficulty**: [current level]

**Strengths Demonstrated**:
- [Specific skills shown during quest]

**Areas for Improvement**:
- [Topics that need more practice]

**Next Recommendations**:
- [Suggested next quest type]
- [Topics to review]
- [Difficulty adjustment]

**Curriculum Progress**:
- [How this quest contributes to learning objectives]
- [Milestones achieved]
```

## Additional Resources
- For quest examples, see [examples.md](examples.md)
- For difficulty calibration algorithms, see [reference.md](reference.md)
