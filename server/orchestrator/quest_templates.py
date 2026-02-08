"""10 generic quest templates for codebase exploration."""

QUEST_TEMPLATES = [
    {
        "id": "http_entrypoint",
        "template": "Find the HTTP entrypoint or server start. Where does the application begin listening for requests?",
    },
    {
        "id": "config_loader",
        "template": "Locate the main config or environment variable loader. How does the app load its configuration?",
    },
    {
        "id": "database_connection",
        "template": "Find where the database connects. What database is used and how is the connection established?",
    },
    {
        "id": "auth_middleware",
        "template": "Identify the auth middleware, decorator, or guard. How does the app authenticate or authorize requests?",
    },
    {
        "id": "request_trace",
        "template": "Trace a request from a route definition to its handler and response. Pick any endpoint and follow the flow.",
    },
    {
        "id": "error_handling",
        "template": "Find where errors are caught, logged, or handled globally. How does the app deal with exceptions?",
    },
    {
        "id": "test_setup",
        "template": "Locate the test setup, test runner config, or test utilities. How are tests organized and run?",
    },
    {
        "id": "data_model",
        "template": "Find a data model, schema definition, or type definition. What entities does the app work with?",
    },
    {
        "id": "background_job",
        "template": "Identify a background job, worker, cron task, or async queue. Does the app do any work outside the request cycle?",
    },
    {
        "id": "build_deploy",
        "template": "Find the build or deploy config (Dockerfile, CI pipeline, Makefile). How is the app built and deployed?",
    },
]
