---
name: curriculum-integration
description: Maps conversations to Notion learning objectives and tracks onboarding progress for RepoBuddy's curriculum-aware guidance. Use when aligning responses with learning goals, tracking progress, or connecting to manager-defined curriculum.
user-invocable: true
allowed-tools: Read, Grep
---

# Curriculum Integration for Onboarding Progress

## Learning Objective Mapping

### 1. Curriculum Structure Analysis
Parse Notion curriculum to understand learning pathways:

#### Core Competency Areas
```
📚 **System Architecture**
- Microservices understanding
- Database design patterns
- API design principles

🔧 **Development Practices** 
- Code review workflows
- Testing strategies
- Deployment processes

🏗️ **Codebase Navigation**
- Project structure comprehension
- Key component identification
- Dependency relationships
```

#### Progress Tracking Levels
```
🟢 **Beginner**: High-level concepts, basic navigation
🟡 **Intermediate**: Detailed understanding, component interaction
🔴 **Advanced**: Deep technical knowledge, architectural decisions
```

### 2. Conversation-to-Curriculum Alignment

#### Topic Classification
```python
# Map conversation topics to curriculum areas
TOPIC_MAPPING = {
    "authentication": ["Security", "User Management", "API Design"],
    "database": ["Data Architecture", "Performance", "Scalability"],
    "api_endpoints": ["REST Principles", "System Integration", "Documentation"],
    "testing": ["Quality Assurance", "Development Practices", "CI/CD"],
    "deployment": ["DevOps", "Infrastructure", "Monitoring"]
}
```

#### Learning Objective Extraction
```
**User Question**: "How does user authentication work?"

**Curriculum Mapping**:
- Primary: Security Fundamentals
- Secondary: API Design Patterns  
- Tertiary: User Experience Considerations

**Learning Objectives**:
1. Understand authentication flow
2. Identify security best practices
3. Recognize token management
4. Locate related security components
```

### 3. Progress Assessment

#### Knowledge Indicators
```
🔍 **Discovery Indicators**:
- Asking "where is..." questions → Navigation skill building
- Requesting "how does..." explanations → Conceptual understanding
- "Why was..." questions → Architectural comprehension

📈 **Comprehension Levels**:
- **Recognition**: Can identify relevant files/components
- **Understanding**: Can explain how parts work together
- **Analysis**: Can discuss design decisions and trade-offs
- **Synthesis**: Can suggest improvements or modifications
```

#### Adaptive Difficulty Adjustment
```
**Performance Tracking**:
- 2+ correct answers in topic area → Level up difficulty
- 2+ incorrect answers → Provide more foundational context
- Mixed results → Maintain current level with more examples

**Curriculum Pacing**:
- Fast learners: Skip ahead to advanced topics
- Steady progress: Follow curriculum sequence
- Struggling areas: Provide additional practice and examples
```

## Notion Integration Patterns

### 1. Learning Trail Logging

#### Conversation Summaries
```
**Session**: [Date] - [Duration]
**Topics Covered**: Authentication, Database Models, API Endpoints
**Files Explored**: auth.py, models/user.py, routes/auth.js
**Progress Indicators**: 
- ✅ Understood authentication flow
- 🔄 Learning database relationships  
- ❓ Questions about token refresh

**Next Steps**: 
- Review session management
- Practice identifying security vulnerabilities
- Explore user role management
```

#### Milestone Tracking
```
🎯 **Milestone: Core System Understanding**
- ✅ Authentication System (Completed)
- ✅ Database Architecture (Completed) 
- 🔄 API Design (In Progress)
- ⏳ Frontend Integration (Not Started)

**Estimated Completion**: 2 more sessions
**Confidence Level**: Growing
```

### 2. Curriculum Alignment

#### Manager-Defined Objectives
```
**Week 1 Goals** (from Notion):
- [ ] Understand project structure
- [ ] Set up development environment  
- [ ] Review authentication system
- [ ] Complete first bug fix

**Current Progress**:
- ✅ Project structure mapped
- ✅ Dev environment configured
- 🔄 Authentication system review (75% complete)
- ⏳ Bug fix (not started)
```

#### Personalized Learning Paths
```
**Adaptive Curriculum**:
**Base Path**: Standard onboarding sequence
**Personalizations**:
- + Extra security focus (background in security)
- + Frontend deep dive (interest in UI/UX)
- - Database basics (already proficient)

**Modified Timeline**: 3 weeks instead of 4
```

## Response Strategy with Curriculum Context

### 1. Context-Aware Explanations

#### Beginner Level Responses
```
**Topic**: Database connections
**Approach**: Start with high-level concepts
"Think of database connections like phone calls. 
When your app needs data, it 'calls' the database.
Let me show you where this happens in the code..."

**Curriculum Link**: "This connects to your learning objective about understanding system architecture."
```

#### Advanced Level Responses
```
**Topic**: Database connection pooling
**Approach**: Technical depth with performance considerations
"The connection pool here uses a max of 20 connections with a 30-second timeout.
Notice how it handles connection validation and automatic reconnection.
This design choice impacts scalability under load..."

**Curriculum Link**: "This demonstrates the performance optimization principles from week 2 of your curriculum."
```

### 2. Progressive Disclosure Based on Curriculum

#### Structured Learning Sequences
```
**Learning Sequence: Authentication**
1. **Discovery**: "Let's find where users log in"
2. **Understanding**: "Here's how the login flow works"  
3. **Analysis**: "Why was JWT chosen over sessions?"
4. **Practice**: "Try finding the token refresh logic"
5. **Assessment**: "Can you explain the security implications?"

**Curriculum Alignment**: Each step maps to specific learning objectives
```

### 3. Reinforcement and Review

#### Spaced Repetition Integration
```
**Previously Covered**: User authentication (Session 1)
**Current Topic**: API authorization (Session 3)
**Connection**: "Remember when we looked at user login? 
This API authorization builds on that same token system.
Let me show you how the JWT token from login is used here..."

**Retention Check**: "Can you recall what the three parts of a JWT token are?"
```

#### Cross-Topic Connections
```
**Database + API**: "The user model we looked at last week
is what this API endpoint is validating. Notice how the
database schema constraints affect the API validation rules."

**Security + Performance**: "This security check adds overhead.
Let me show you where the performance monitoring is set up
to track the impact of security measures."
```

## Assessment and Feedback

### 1. Knowledge Validation

#### Formative Assessment
```
**Quick Checks**: 
- "Can you point to where the error handling happens?"
- "What would happen if this validation was removed?"
- "How would you test this function?"

**Confidence Scoring**: 
- Rate understanding 1-5 after each topic
- Adjust difficulty based on confidence levels
- Flag areas needing additional review
```

#### Summative Assessment
```
**Quest Completion**: 
- Code exploration challenges
- Practical problem solving
- System design scenarios

**Milestone Validation**:
- "Can you trace a user request through the entire system?"
- "Where would you add a new feature to this codebase?"
- "What are the main security considerations here?"
```

### 2. Progress Reporting

#### Real-Time Updates to Notion
```
**Session Log Entry**:
- Timestamp: [Current time]
- Topics: [List of covered topics]
- Progress: [Percentage completion]
- Confidence: [User confidence levels]
- Next Steps: [Recommended next topics]

**Automatic Milestone Detection**:
- Detect when curriculum objectives are met
- Update progress indicators automatically
- Notify manager of key milestones
```

## Additional Resources
- For curriculum mapping examples, see [reference.md](reference.md)
- For progress tracking templates, see [examples.md](examples.md)
