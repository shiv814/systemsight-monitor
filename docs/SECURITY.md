# Security and Deployment Scope

SystemSight is local-first. The HTTP server is intended for development/demo use and should not be bound to an untrusted network without authentication/authorization, TLS, rate limits, secure service accounts, transport protection, retention controls and review of what process/system metadata may leave a host.

Generated HTML escapes host names and alert messages. Rule evaluation does not evaluate Python expressions or shell commands.
