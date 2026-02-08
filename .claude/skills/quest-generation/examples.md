# Quest Generation Examples

## Navigation Quest Examples

### Beginner Level
**Quest**: Find the User Login Function
```
🎯 **Mission**: Locate the function that handles user login

**Context**: A user just reported they can't log into the application. You need to find where the login logic is implemented to debug the issue.

**Hints Available**: 3
**Time Limit**: 5 minutes
**Difficulty**: ⭐ (Beginner)

### 🔍 Getting Started
1. Think about where login functionality would typically live
2. Look for files with names like "auth", "login", or "user"
3. Search for keywords related to authentication

### 💡 Hints
**Hint 1**: Look for files containing authentication or user management code
**Hint 2**: Check the routes or controllers directory for login endpoints  
**Hint 3**: The main login function is in `services/auth.py` at line 23

### ✅ Success Criteria
- Found the correct file and function
- Can explain what the function does
- Located related authentication components

**Solution**: The `login_user` function in `services/auth.py` handles user authentication by validating credentials and generating JWT tokens.
```

### Advanced Level
**Quest**: Find the Rate Limiting Implementation
```
🎯 **Mission**: Locate the rate limiting mechanism for API endpoints

**Context**: The application needs to prevent API abuse. You need to find where rate limiting is implemented to understand how it works and potentially adjust the limits.

**Hints Available**: 2
**Time Limit**: 8 minutes  
**Difficulty**: ⭐⭐⭐⭐ (Advanced)

### 🔍 Getting Started
1. Rate limiting is typically implemented as middleware
2. Look for files related to middleware, decorators, or request processing
3. Search for terms like "rate", "limit", "throttle", or "middleware"

### 💡 Hints
**Hint 1**: Check for middleware files or decorators that process requests
**Hint 2**: The rate limiting uses Redis for tracking request counts

### ✅ Success Criteria
- Found the rate limiting implementation
- Understand how it tracks requests per IP
- Can identify where limits are configured
- Located the Redis integration

**Solution**: Rate limiting is implemented in `middleware/rate_limiter.py` using Redis to track request counts per IP address with configurable limits per endpoint.
```

## Analysis Quest Examples

### Intermediate Level
**Quest**: Explain the Database Connection Pool
```
🧠 **Analysis Challenge**: Explain how the database connection pool works

**Code to Analyze**:
```python
class ConnectionPool:
    def __init__(self, max_connections=20):
        self.max_connections = max_connections
        self.available = Queue(maxsize=max_connections)
        self.in_use = set()
        
    def get_connection(self):
        if self.available.empty() and len(self.in_use) < self.max_connections:
            conn = create_new_connection()
            self.in_use.add(conn)
            return conn
        elif not self.available.empty():
            conn = self.available.get()
            self.in_use.add(conn)
            return conn
        else:
            raise PoolExhaustedException()
            
    def return_connection(self, conn):
        self.in_use.remove(conn)
        self.available.put(conn)
```

**Questions to Answer**:
1. What is the primary purpose of this connection pool?
2. How does it handle the situation when all connections are in use?
3. What happens when a connection is returned to the pool?
4. What are the benefits of using a pool vs creating new connections?

**Thinking Points**:
- Consider the performance implications
- Look for potential race conditions
- Think about resource management
- Consider error scenarios

### 📊 Evaluation Rubric
**Excellent** (4/4): All questions answered correctly with deep performance insights
**Good** (3/4): Most questions answered with solid understanding of pooling concepts
**Developing** (2/4): Basic understanding with some gaps in resource management
**Needs Work** (1/4): Limited understanding of connection pooling benefits

**Time Limit**: 10 minutes
**Difficulty**: ⭐⭐⭐ (Intermediate)
```

## Debug Quest Examples

### Advanced Level
**Quest**: Fix the Memory Leak
```
🐛 **Debug Challenge**: Find and fix the memory leak in the data processing service

**Problem Report**: The application's memory usage increases by 50MB every hour when processing user data. After 4 hours, it crashes with out-of-memory errors.

**Buggy Code**:
```python
class DataProcessor:
    def __init__(self):
        self.cache = {}
        
    def process_user_data(self, user_id):
        # Load user data
        data = self.load_user_data(user_id)
        
        # Process and cache results
        processed = self.transform_data(data)
        self.cache[user_id] = processed
        
        # Store in database
        self.save_to_database(processed)
        
        return processed
        
    def transform_data(self, data):
        # Complex data transformation
        result = {}
        for item in data:
            result[item['id']] = self.heavy_computation(item)
        return result
```

### 🔍 Investigation Steps
1. **Identify the Problem**: What's causing memory to grow continuously?
2. **Find the Root Cause**: Where in the code is memory being allocated but not released?
3. **Propose a Fix**: How would you correct this memory leak?
4. **Test Your Solution**: How would you verify the fix works?

### 🚨 Common Memory Leak Patterns to Look For
- Growing dictionaries/caches that are never cleared
- Event listeners that aren't removed
- Database connections that aren't closed
- Large objects held in memory unnecessarily

### ✅ Solution Requirements
- Identify the exact cause of the memory leak
- Explain why the current code causes continuous memory growth
- Provide the corrected code with proper memory management
- Suggest monitoring to detect future memory issues

**Time Limit**: 15 minutes
**Difficulty**: ⭐⭐⭐⭐⭐ (Expert)

**Solution**: The cache dictionary grows indefinitely as it stores processed data for every user but never removes old entries. Fix by implementing cache size limits, TTL expiration, or using an LRU cache.
```

## Architecture Quest Examples

### Expert Level
**Quest**: Analyze Microservices Communication Pattern
```
🏗️ **Architecture Challenge**: Analyze the microservices communication pattern

**System Context**: You have three services:
- User Service (handles user management)
- Order Service (processes orders)  
- Notification Service (sends emails/SMS)

**Communication Pattern**:
```python
# Order Service creating an order
def create_order(user_id, order_data):
    # Validate user exists
    user = user_service.get_user(user_id)
    
    # Create order
    order = Order.create(user_id, order_data)
    
    # Send notification
    notification_service.send_order_confirmation(user.email, order.id)
    
    return order

# User Service
def get_user(user_id):
    return User.find_by_id(user_id)

# Notification Service  
def send_order_confirmation(email, order_id):
    send_email(email, "Order Confirmation", f"Order {order_id} created")
```

**Critical Analysis Questions**:
1. What are the potential failure points in this communication pattern?
2. How does this design impact system resilience?
3. What happens if the notification service is down?
4. How would you improve this architecture for better reliability?

**Architectural Considerations**:
- Synchronous vs asynchronous communication
- Service dependencies and coupling
- Error handling and recovery
- Performance implications
- Scalability concerns

### 📊 Advanced Evaluation Rubric
**Expert** (5/5): Deep architectural analysis with specific improvement proposals
**Advanced** (4/5): Solid understanding with good architectural insights  
**Proficient** (3/5): Basic architectural understanding
**Developing** (2/4): Limited architectural analysis
**Novice** (1/4): Minimal understanding of microservices patterns

**Time Limit**: 20 minutes
**Difficulty**: ⭐⭐⭐⭐⭐ (Expert)

**Solution**: The synchronous communication creates tight coupling and potential cascading failures. Better approach: use message queues for asynchronous communication, implement circuit breakers, and add retry mechanisms.
```

## Adaptive Quest Examples

### Personalized Difficulty Adjustment
**User Performance History**:
- Navigation quests: 90% success rate, averaging 3 minutes
- Analysis quests: 60% success rate, averaging 12 minutes  
- Debug quests: 40% success rate, requesting 2+ hints

**Adaptive Quest Generation**:
```
**Next Quest Selection**:
- Navigation: Increase difficulty (user is excelling)
- Analysis: Maintain current level (steady progress)
- Debug: Decrease difficulty (user is struggling)

**Generated Quest**: "Find the caching mechanism" (Navigation, Hard)
**Rationale**: User has mastered navigation and needs challenge

**Generated Quest**: "Explain the input validation" (Analysis, Medium)  
**Rationale**: User is making steady progress, maintain difficulty

**Generated Quest**: "Fix the missing error handling" (Debug, Easy)
**Rationale**: User needs confidence building in debugging
```

### Curriculum-Aligned Quests
**Current Curriculum Week**: API Security

**Quest Generation Based on Learning Objectives**:
```python
learning_objectives = [
    "Understand input validation patterns",
    "Identify common security vulnerabilities", 
    "Implement proper authentication middleware"
]

# Generated quests
quests = [
    {
        "type": "navigation",
        "objective": "Find input validation implementation",
        "curriculum_link": "input validation patterns"
    },
    {
        "type": "debug", 
        "objective": "Fix SQL injection vulnerability",
        "curriculum_link": "common security vulnerabilities"
    },
    {
        "type": "analysis",
        "objective": "Explain authentication middleware flow",
        "curriculum_link": "authentication middleware"
    }
]
```

## Progress Tracking Examples

### Quest Performance Dashboard
```
📊 **Quest Performance Summary**

**Overall Statistics**:
- Total Quests Completed: 24
- Success Rate: 73%
- Average Time: 8.5 minutes
- Hints per Quest: 1.2

**By Quest Type**:
- Navigation: 95% success (8.2 min avg)
- Analysis: 68% success (12.1 min avg)  
- Debug: 52% success (15.3 min avg)
- Architecture: 80% success (18.7 min avg)

**Difficulty Progression**:
- Beginner: 100% success (6 quests)
- Intermediate: 85% success (8 quests)
- Advanced: 65% success (6 quests)
- Expert: 40% success (4 quests)

**Recent Performance** (Last 5 quests):
1. ✅ Navigation (Hard) - 3 min, 0 hints
2. ❌ Debug (Advanced) - 20 min, 3 hints
3. ✅ Analysis (Intermediate) - 10 min, 1 hint
4. ✅ Navigation (Expert) - 12 min, 2 hints  
5. ✅ Debug (Intermediate) - 14 min, 1 hint

**Trend Analysis**: Improving in debugging, ready for harder analysis challenges

**Next Recommendations**:
- Try Advanced Analysis quest (performance trending up)
- Practice Expert Debug quest (still needs work)
- Consider Architecture quest (strong performance)
```

### Skill Development Tracking
```
🎯 **Skill Development Progress**

**Core Skills**:
- Code Navigation: Expert (95% success, <5 min avg)
- Pattern Recognition: Advanced (80% success, 8 min avg)
- Error Analysis: Intermediate (60% success, 12 min avg)
- System Design: Intermediate (70% success, 15 min avg)

**Learning Objectives Status**:
- ✅ Locate key components (Mastered)
- ✅ Understand data flow (Proficient)  
- 🔄 Analyze performance issues (Developing)
- ❓ Design system improvements (Beginning)

**Personalized Focus Areas**:
1. Performance analysis (needs more practice)
2. Advanced debugging techniques
3. System architecture evaluation

**Curriculum Alignment**: 75% of learning objectives met for current module
**Estimated Completion**: 2 more sessions to complete current module
```
