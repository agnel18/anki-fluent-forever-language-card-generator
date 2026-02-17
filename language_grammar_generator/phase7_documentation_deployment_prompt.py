# language_grammar_generator/phase7_documentation_deployment_prompt.py
"""
Phase 7: Documentation & Deployment Prompt

This prompt creates deployment and documentation materials for a language analyzer.
Final phase for production readiness.
"""

# language_grammar_generator/phase7_documentation_deployment_prompt.py
"""
Phase 7: Documentation & Deployment Prompt

This prompt creates deployment and documentation materials for a language analyzer.
Final phase for production readiness.

UPDATED: Incorporates production deployment practices from French analyzer v2.0 including:
- Comprehensive monitoring and observability
- Performance optimization with caching strategies
- Automated deployment validation
- Production maintenance procedures
- Security and compliance documentation
"""

PHASE7_DOCUMENTATION_DEPLOYMENT_PROMPT = """
You are a technical documentation expert specializing in production-ready language analyzer deployment. Your task is to create deployment and documentation materials for a language analyzer with enterprise-grade operations and monitoring.

LANGUAGE: {LANGUAGE_NAME} ({LANGUAGE_CODE})

Create the complete deployment package with production-ready documentation:

1. PRODUCTION DEPLOYMENT CHECKLIST:
- File structure verification with automated validation
- Configuration file validation and environment-specific setup
- Registry integration confirmation with automated testing
- Test execution and validation with CI/CD integration
- Performance benchmarking against production targets
- Security review and API key management validation
- Monitoring and alerting configuration verification

2. COMPREHENSIVE USAGE DOCUMENTATION:
- Analyzer capabilities and features with performance metrics
- Configuration options and customization with validation rules
- Integration with existing systems and API specifications
- Troubleshooting guide with common issues and solutions
- Performance tuning guidelines and optimization strategies
- Monitoring and maintenance procedures

3. ADVANCED PERFORMANCE OPTIMIZATION:
- Multi-level caching strategies (memory, disk, distributed)
- Batch processing optimization with parallel execution
- Memory usage optimization with profiling and leak detection
- API rate limiting and quota management strategies
- Database query optimization and connection pooling
- CDN integration for static asset delivery

4. ENTERPRISE MONITORING AND OBSERVABILITY:
- Structured logging with correlation IDs and performance metrics
- Application Performance Monitoring (APM) integration
- Error tracking and alerting with escalation procedures
- API usage monitoring with cost optimization
- User experience monitoring and quality metrics
- Infrastructure monitoring (CPU, memory, disk, network)

5. PRODUCTION MAINTENANCE PROCEDURES:
- Regular maintenance schedules and automated tasks
- Backup and recovery procedures with disaster recovery plans
- Configuration management and version control
- Security updates and patch management procedures
- Performance monitoring and optimization routines
- Incident response and post-mortem procedures

6. SECURITY AND COMPLIANCE:
- API key management and rotation procedures
- Data privacy and GDPR compliance documentation
- Security audit procedures and vulnerability assessments
- Access control and authentication mechanisms
- Data encryption and secure communication protocols

7. SCALING AND HIGH AVAILABILITY:
- Horizontal scaling strategies and load balancing
- Database scaling and read/write splitting
- CDN and edge computing integration
- Multi-region deployment strategies
- Failover and redundancy procedures

PRODUCTION READINESS CHECKLIST:
- [ ] Security review completed with no critical vulnerabilities
- [ ] Performance benchmarking meets targets (P95 <2s single, <5s batch)
- [ ] Error handling validation with comprehensive test coverage
- [ ] Documentation completeness with user and admin guides
- [ ] Monitoring and alerting fully configured
- [ ] Backup and recovery procedures tested
- [ ] Scalability testing completed for expected load
- [ ] Compliance requirements verified (GDPR, accessibility, etc.)

TECHNICAL DEPLOYMENT SPECIFICATIONS:
- **Infrastructure**: Docker containers with Kubernetes orchestration
- **Database**: PostgreSQL with connection pooling and read replicas
- **Caching**: Redis cluster with LRU eviction and TTL management
- **Monitoring**: Prometheus + Grafana with custom dashboards
- **Logging**: ELK stack with structured JSON logging
- **Security**: OAuth2 authentication with JWT tokens
- **CDN**: CloudFront/Akamai with global edge locations

PERFORMANCE TARGETS:
- **Latency**: P50 <1s, P95 <2s, P99 <5s for single sentence analysis
- **Throughput**: 1000+ requests per minute per instance
- **Availability**: 99.9% uptime with automated failover
- **Accuracy**: 95%+ grammatical analysis accuracy
- **Memory**: <200MB per instance under normal load
- **CPU**: <50% utilization under peak load

MONITORING DASHBOARDS:
- Real-time performance metrics and latency histograms
- Error rate monitoring with automatic alerting
- API usage tracking with cost monitoring
- Cache hit rates and performance optimization
- User experience quality metrics and satisfaction scores
- Infrastructure health and resource utilization

LANGUAGE-SPECIFIC ADAPTATION: Include {LANGUAGE_NAME}-specific usage examples, common issues, performance characteristics, and maintenance procedures tailored to the language's grammatical complexity and learner challenges.
"""