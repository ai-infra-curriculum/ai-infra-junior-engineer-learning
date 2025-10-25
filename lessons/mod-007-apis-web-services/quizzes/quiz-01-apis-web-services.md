# Module 007 Quiz: APIs & Web Services

## Quiz Information

- **Module:** APIs & Web Services
- **Total Questions:** 30
- **Time Limit:** 45 minutes
- **Passing Score:** 80% (24/30 correct)
- **Topics Covered:**
  - API Fundamentals & REST
  - FastAPI Framework
  - Authentication & Security

## Instructions

1. Read each question carefully
2. Select the best answer for multiple choice questions
3. Some questions may have multiple correct answers
4. No negative marking
5. You can review and change answers before submitting

---

## Section 1: REST API Fundamentals (10 questions)

### Question 1
What does REST stand for?

A) Remote Execution State Transfer
B) Representational State Transfer
C) Remote State Transaction
D) Representational Service Technology

**Correct Answer:** B

**Explanation:** REST stands for Representational State Transfer, an architectural style for designing networked applications.

---

### Question 2
Which HTTP method should be used to create a new resource in a RESTful API?

A) GET
B) PUT
C) POST
D) PATCH

**Correct Answer:** C

**Explanation:** POST is used to create new resources. PUT can also create resources but is typically used for updates at a specific URI.

---

### Question 3
Which of the following is NOT one of the six REST constraints?

A) Stateless
B) Client-Server
C) Database-Driven
D) Cacheable

**Correct Answer:** C

**Explanation:** The six REST constraints are: Client-Server, Stateless, Cacheable, Uniform Interface, Layered System, and Code on Demand (optional). Database-Driven is not a REST constraint.

---

### Question 4
What HTTP status code should be returned when a resource is successfully created?

A) 200 OK
B) 201 Created
C) 204 No Content
D) 202 Accepted

**Correct Answer:** B

**Explanation:** 201 Created is the appropriate status code for successful resource creation. It should also include a Location header with the new resource's URI.

---

### Question 5
In REST, what does it mean for a request to be "idempotent"?

A) The request must be encrypted
B) The request can be cached
C) Making the same request multiple times has the same effect as making it once
D) The request requires authentication

**Correct Answer:** C

**Explanation:** Idempotent means that multiple identical requests have the same effect as a single request. GET, PUT, DELETE, HEAD are idempotent; POST is not.

---

### Question 6
Which HTTP status code indicates that the client is not authenticated?

A) 400 Bad Request
B) 401 Unauthorized
C) 403 Forbidden
D) 404 Not Found

**Correct Answer:** B

**Explanation:** 401 Unauthorized means the client must authenticate. 403 Forbidden means the client is authenticated but not authorized.

---

### Question 7
What is the difference between PUT and PATCH?

A) PUT is for creation, PATCH is for deletion
B) PUT replaces the entire resource, PATCH applies partial modifications
C) PUT requires authentication, PATCH doesn't
D) There is no difference

**Correct Answer:** B

**Explanation:** PUT replaces the entire resource with the provided representation, while PATCH applies partial modifications to the resource.

---

### Question 8
Which of the following is the correct RESTful URL structure?

A) `/api/getUsers`
B) `/api/users/get`
C) `/api/users`
D) `/api/user/all`

**Correct Answer:** C

**Explanation:** RESTful URLs use nouns (resources) in plural form, not verbs. The HTTP method indicates the action.

---

### Question 9
What HTTP status code should be returned when rate limiting is exceeded?

A) 400 Bad Request
B) 403 Forbidden
C) 429 Too Many Requests
D) 503 Service Unavailable

**Correct Answer:** C

**Explanation:** 429 Too Many Requests is the standard status code for rate limiting. It should include a Retry-After header.

---

### Question 10
In RESTful design, which is the correct way to represent a hierarchical relationship?

A) `/users/123/posts/456`
B) `/getUserPosts?userId=123&postId=456`
C) `/posts/456?user=123`
D) `/api/user-posts/123-456`

**Correct Answer:** A

**Explanation:** Hierarchical relationships are represented using nested paths: `/resource/{id}/subresource/{id}`.

---

## Section 2: FastAPI Framework (10 questions)

### Question 11
What is the primary advantage of using type hints in FastAPI?

A) Faster code execution
B) Automatic request validation and documentation
C) Smaller code size
D) Better error messages only

**Correct Answer:** B

**Explanation:** FastAPI uses Python type hints to automatically validate requests, serialize responses, and generate API documentation.

---

### Question 12
Which library does FastAPI use for data validation?

A) Marshmallow
B) Cerberus
C) Pydantic
D) Voluptuous

**Correct Answer:** C

**Explanation:** FastAPI uses Pydantic for data validation and serialization based on Python type hints.

---

### Question 13
How do you mark a query parameter as required in FastAPI?

A) Add `required=True` to the parameter
B) Don't provide a default value
C) Use `Query(...)`
D) Both B and C

**Correct Answer:** D

**Explanation:** A parameter is required if it has no default value. You can also explicitly mark it required using `Query(...)`.

---

### Question 14
What is dependency injection in FastAPI used for?

A) Only for database connections
B) Sharing logic, managing state, handling authentication, and reducing code duplication
C) Only for authentication
D) Injecting bugs into code

**Correct Answer:** B

**Explanation:** Dependency injection is a powerful FastAPI feature for sharing logic, managing resources, authentication, and more.

---

### Question 15
Which decorator is used to mark a function as a startup event handler in FastAPI?

A) `@app.startup()`
B) `@app.on_event("startup")`
C) `@app.before_start()`
D) `@app.init()`

**Correct Answer:** B

**Explanation:** `@app.on_event("startup")` marks a function to run when the application starts, useful for loading models.

---

### Question 16
What is the correct way to add a background task in FastAPI?

A) Using `threading.Thread()`
B) Using `background_tasks.add_task()`
C) Using `asyncio.create_task()`
D) Using `multiprocessing.Process()`

**Correct Answer:** B

**Explanation:** FastAPI provides BackgroundTasks for running tasks after returning a response without blocking it.

---

### Question 17
How does FastAPI automatically generate API documentation?

A) By reading code comments
B) By using docstrings only
C) By using type hints, Pydantic models, and endpoint metadata
D) By manual configuration only

**Correct Answer:** C

**Explanation:** FastAPI uses type hints, Pydantic models, and endpoint metadata to automatically generate OpenAPI (Swagger) documentation.

---

### Question 18
What is the purpose of `response_model` in FastAPI?

A) To validate the request body
B) To filter and validate response data
C) To set the HTTP status code
D) To enable CORS

**Correct Answer:** B

**Explanation:** `response_model` validates and serializes response data, ensuring only specified fields are returned.

---

### Question 19
Which HTTP server is recommended for running FastAPI in production?

A) Flask's built-in server
B) Uvicorn or Gunicorn with Uvicorn workers
C) Django's runserver
D) SimpleHTTPServer

**Correct Answer:** B

**Explanation:** Uvicorn (ASGI server) or Gunicorn with Uvicorn workers are recommended for production FastAPI deployments.

---

### Question 20
What does the `async def` keyword enable in FastAPI endpoints?

A) Faster code execution
B) Concurrent handling of I/O-bound operations
C) Parallel processing
D) Automatic caching

**Correct Answer:** B

**Explanation:** `async def` enables asynchronous handling of I/O-bound operations, allowing concurrent request processing.

---

## Section 3: Authentication & Security (10 questions)

### Question 21
What is the difference between authentication and authorization?

A) There is no difference
B) Authentication verifies identity, authorization determines permissions
C) Authentication is for APIs, authorization is for websites
D) Authorization verifies identity, authentication determines permissions

**Correct Answer:** B

**Explanation:** Authentication answers "Who are you?" while authorization answers "What can you do?".

---

### Question 22
Which of the following is the most secure way to store passwords?

A) Plain text
B) MD5 hash
C) bcrypt or argon2 hash
D) Base64 encoding

**Correct Answer:** C

**Explanation:** bcrypt and argon2 are designed for password hashing with built-in salting. MD5 is broken, and plain text/base64 are not secure.

---

### Question 23
What are the three parts of a JWT token?

A) Username, password, timestamp
B) Header, payload, signature
C) Token, refresh, expiry
D) Key, value, hash

**Correct Answer:** B

**Explanation:** JWT consists of three parts separated by dots: header (algorithm and type), payload (claims/data), and signature (verification).

---

### Question 24
Why should JWT access tokens have short expiration times?

A) To save server memory
B) To reduce security risk if token is compromised
C) To improve performance
D) To generate more revenue

**Correct Answer:** B

**Explanation:** Short-lived access tokens limit the window of opportunity if a token is stolen. Refresh tokens allow getting new access tokens.

---

### Question 25
What is CORS and why is it important?

A) A way to encrypt data
B) A security mechanism that controls which origins can access your API
C) A type of authentication
D) A database technology

**Correct Answer:** B

**Explanation:** CORS (Cross-Origin Resource Sharing) is a security feature that controls which domains can make requests to your API.

---

### Question 26
Which header should contain the JWT token in API requests?

A) `X-API-Key`
B) `Authorization: Bearer <token>`
C) `Access-Token`
D) `X-Auth-Token`

**Correct Answer:** B

**Explanation:** The standard is to use the Authorization header with the "Bearer" scheme: `Authorization: Bearer <token>`.

---

### Question 27
What is the purpose of rate limiting?

A) To make APIs faster
B) To prevent abuse and ensure fair resource allocation
C) To encrypt data
D) To authenticate users

**Correct Answer:** B

**Explanation:** Rate limiting prevents API abuse, protects infrastructure, and ensures fair resource allocation among users.

---

### Question 28
Which of the following is NOT a recommended security header?

A) X-Frame-Options
B) X-Content-Type-Options
C) X-Database-Password
D) Content-Security-Policy

**Correct Answer:** C

**Explanation:** X-Database-Password is not a real security header. Never expose passwords in headers!

---

### Question 29
What is the principle of least privilege?

A) Making everything public by default
B) Granting only the minimum permissions necessary
C) Giving admin access to all users
D) Removing all security measures

**Correct Answer:** B

**Explanation:** Principle of least privilege means granting users/systems only the minimum permissions required for their tasks.

---

### Question 30
Why should APIs always use HTTPS instead of HTTP?

A) HTTPS is faster
B) HTTPS encrypts data in transit, protecting credentials and sensitive data
C) HTTPS is required by law
D) HTTPS uses less bandwidth

**Correct Answer:** B

**Explanation:** HTTPS encrypts all data in transit using TLS/SSL, protecting credentials, tokens, and sensitive data from interception.

---

## Answer Key

### Section 1: REST API Fundamentals
1. B - Representational State Transfer
2. C - POST for creating resources
3. C - Database-Driven is not a REST constraint
4. B - 201 Created for successful creation
5. C - Same effect with multiple requests
6. B - 401 for unauthenticated
7. B - PUT replaces, PATCH modifies
8. C - `/api/users` is correct
9. C - 429 for rate limiting
10. A - Nested paths for hierarchy

### Section 2: FastAPI Framework
11. B - Automatic validation and docs
12. C - Pydantic
13. D - No default or Query(...)
14. B - Multiple uses for DI
15. B - @app.on_event("startup")
16. B - background_tasks.add_task()
17. C - Type hints and Pydantic
18. B - Filter and validate responses
19. B - Uvicorn/Gunicorn
20. B - Concurrent I/O handling

### Section 3: Authentication & Security
21. B - Authentication=identity, Authorization=permissions
22. C - bcrypt or argon2
23. B - Header, payload, signature
24. B - Reduce compromise window
25. B - Control cross-origin access
26. B - Authorization: Bearer <token>
27. B - Prevent abuse
28. C - X-Database-Password (not real)
29. B - Minimum permissions
30. B - Encryption in transit

---

## Scoring Guide

- **27-30 correct (90-100%):** Excellent! You have a strong understanding of APIs and web services.
- **24-26 correct (80-86%):** Good! You passed with a solid grasp of the concepts.
- **20-23 correct (67-76%):** Fair. Review the material, especially areas where you struggled.
- **Below 20 (< 67%):** Needs improvement. Revisit the lectures and exercises before retaking.

## Next Steps

After completing this quiz:

1. **Review incorrect answers** and understand why
2. **Revisit relevant lecture sections** for topics you missed
3. **Complete all exercises** for hands-on practice
4. **Build a project** combining all concepts learned
5. **Move to Module 008: Databases & SQL**

---

## Additional Practice Questions

Practice with these scenarios:

1. Design a RESTful API for a book library system
2. Implement JWT authentication for an ML model API
3. Configure CORS for a frontend-backend application
4. Design rate limiting strategy for different user tiers
5. Create comprehensive API documentation with examples

**Time to Review:** 15-20 minutes
**Recommended Retake Interval:** 3-5 days if score < 80%
