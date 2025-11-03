# Module 009: Monitoring and Observability Basics

## Module Overview

Monitoring and observability are critical skills for infrastructure engineers, enabling you to understand system behavior, detect issues early, and maintain reliability. This module provides comprehensive training in monitoring fundamentals, metrics collection with Prometheus, visualization with Grafana, logging strategies, and basic alerting.

You'll learn the three pillars of observability (metrics, logs, traces), how to instrument applications, build dashboards, set up alerts, and establish monitoring best practices. These skills are essential for maintaining production AI/ML infrastructure and ensuring system reliability.

By the end of this module, you'll be confident setting up monitoring systems, collecting metrics, building dashboards, analyzing logs, and establishing alerting workflows for infrastructure and applications.

## Learning Objectives

By completing this module, you will be able to:

1. **Understand observability fundamentals** including metrics, logs, and traces
2. **Collect metrics with Prometheus** and understand the Prometheus data model
3. **Build dashboards with Grafana** for visualizing system and application metrics
4. **Implement structured logging** with proper log levels and formatting
5. **Query logs effectively** using grep, awk, and log aggregation tools
6. **Set up alerting** with Prometheus Alertmanager
7. **Monitor applications** including instrumenting Python code
8. **Monitor infrastructure** including servers, containers, and services
9. **Apply SLIs, SLOs, and SLAs** for defining reliability targets
10. **Monitor ML systems** including model performance and data drift

## Prerequisites

- Completion of Module 002 (Linux Essentials) required
- Completion of Module 005 (Docker and Containers) recommended
- Completion of Module 007 (APIs and Web Services) recommended
- Basic understanding of networking
- Comfort with command-line interfaces

**Recommended Setup:**
- Docker and Docker Compose installed
- Python 3.9+ with virtual environment
- 8GB+ RAM for running monitoring stack
- 20GB+ available disk space
- Web browser for dashboards
- Text editor or IDE

## Time Commitment

- **Total Estimated Time:** 35-45 hours
- **Lectures & Reading:** 12-15 hours
- **Hands-on Exercises:** 18-22 hours
- **Projects:** 5-8 hours

**Recommended Pace:**
- Part-time (5-10 hrs/week): 4-5 weeks
- Full-time (20-30 hrs/week): 2 weeks

Monitoring mastery requires hands-on experience. Expect to spend time setting up systems, analyzing metrics, and troubleshooting issues.

## Module Structure

### Week 1: Monitoring Fundamentals
- **Topics:** Observability concepts, monitoring basics, metrics types
- **Key Skills:** Understanding observability, metric types, monitoring strategy
- **Practice:** Analyzing existing monitoring systems

### Week 2: Prometheus and Metrics
- **Topics:** Prometheus architecture, PromQL, exporters, instrumentation
- **Key Skills:** Collecting metrics, writing queries, instrumenting applications
- **Practice:** Setting up Prometheus, collecting metrics

### Week 3: Grafana and Visualization
- **Topics:** Grafana dashboards, panels, alerting, best practices
- **Key Skills:** Building dashboards, visualization techniques, dashboard design
- **Practice:** Creating comprehensive dashboards

### Week 4: Logging, Alerting, and ML Monitoring
- **Topics:** Structured logging, log aggregation, alerting, ML metrics
- **Key Skills:** Log management, alert configuration, ML system monitoring
- **Practice:** Complete monitoring stack implementation

## Detailed Topic Breakdown

### 1. Observability Fundamentals (5-6 hours)

#### 1.1 Introduction to Observability
- What is observability?
- Monitoring vs observability
- Why observability matters
- The three pillars: metrics, logs, traces
- Observability in distributed systems
- Observability maturity model
- Cost-benefit analysis

#### 1.2 Metrics
- What are metrics?
- Metric types (counters, gauges, histograms, summaries)
- Time-series data
- Cardinality considerations
- Choosing what to measure
- The four golden signals (latency, traffic, errors, saturation)
- RED method (Rate, Errors, Duration)
- USE method (Utilization, Saturation, Errors)

#### 1.3 Logging
- What are logs?
- Log levels (DEBUG, INFO, WARN, ERROR, FATAL)
- Structured vs unstructured logging
- Log aggregation
- Log retention policies
- Logging best practices
- Security and compliance considerations

#### 1.4 Distributed Tracing
- What is tracing?
- Spans and traces
- Tracing distributed systems
- OpenTelemetry introduction
- Trace sampling
- Trace analysis
- When to use tracing

#### 1.5 Monitoring Strategy
- What to monitor
- Setting baselines
- Defining normal behavior
- Identifying key metrics
- Monitoring layers (infrastructure, application, business)
- Monitoring in development vs production
- Team responsibilities

### 2. Prometheus (8-10 hours)

#### 2.1 Prometheus Fundamentals
- What is Prometheus?
- Prometheus architecture
- Pull vs push model
- Time-series database
- Data model (metrics, labels)
- Prometheus components (server, exporters, alertmanager)
- Prometheus ecosystem

#### 2.2 Installing and Configuring Prometheus
- Installation methods
- Configuration file (prometheus.yml)
- Scrape configurations
- Service discovery
- Relabeling
- Recording rules
- Federation basics
- Storage configuration

#### 2.3 Metrics Collection
- Exporters (node_exporter, blackbox_exporter)
- Application instrumentation
- Prometheus client libraries
- Custom exporters
- Pushgateway (when to use)
- Service discovery mechanisms
- Scraping intervals and configuration

#### 2.4 PromQL (Prometheus Query Language)
- PromQL basics
- Selecting metrics
- Label matching
- Range vectors vs instant vectors
- Operators (arithmetic, comparison, logical)
- Aggregation operators (sum, avg, max, min, count)
- Functions (rate, irate, increase, histogram_quantile)
- Subqueries
- Query performance considerations

#### 2.5 Recording Rules
- What are recording rules?
- Creating recording rules
- Pre-aggregating queries
- Performance optimization
- Rule evaluation
- Best practices
- Naming conventions

#### 2.6 Prometheus for Applications
- Instrumenting Python applications
- Counter metrics
- Gauge metrics
- Histogram metrics
- Summary metrics
- Custom metrics
- Labeling strategies
- Performance impact

### 3. Grafana (7-9 hours)

#### 3.1 Grafana Fundamentals
- What is Grafana?
- Grafana architecture
- Installation and setup
- Data sources
- Organizations and users
- Dashboards and panels
- Grafana ecosystem

#### 3.2 Creating Dashboards
- Dashboard basics
- Adding panels
- Panel types (graph, stat, gauge, table, heatmap)
- Time range controls
- Variables and templating
- Annotations
- Dashboard organization
- Dashboard JSON model

#### 3.3 Visualization Types
- Time series graphs
- Bar charts and histograms
- Single stat and gauge
- Tables
- Heatmaps
- Pie charts and donut charts
- Logs panel
- Choosing appropriate visualizations

#### 3.4 Query Building
- Prometheus query builder
- Writing PromQL in Grafana
- Query variables
- Multiple queries per panel
- Query transformations
- Overrides and thresholds
- Query performance

#### 3.5 Dashboard Design Best Practices
- Dashboard layout principles
- Information hierarchy
- Color usage
- Thresholds and alerts visualization
- Dashboard for different audiences
- Mobile-friendly dashboards
- Dashboard templates
- Reusable panels

#### 3.6 Variables and Templating
- Dashboard variables
- Query variables
- Constant variables
- Custom variables
- Variable chaining
- Multi-value variables
- Dynamic dashboards
- Variable best practices

#### 3.7 Grafana Alerting
- Alert rules in Grafana
- Alert conditions
- Notification channels
- Alert routing
- Silences and muting
- Alert testing
- Alert best practices
- Migration from legacy alerting

### 4. Logging and Log Management (6-8 hours)

#### 4.1 Logging Fundamentals
- Purpose of logging
- What to log
- What not to log (secrets, PII)
- Log levels and when to use them
- Logging frequency considerations
- Performance impact
- Log security

#### 4.2 Structured Logging
- JSON logging
- Key-value pairs
- Log context
- Correlation IDs
- Structured logging in Python
- Logging libraries (logging, structlog)
- Schema design for logs
- Parsing structured logs

#### 4.3 Application Logging
- Python logging module
- Logger configuration
- Log handlers
- Log formatters
- Logging in APIs
- Logging errors and exceptions
- Request/response logging
- Logging best practices

#### 4.4 Log Aggregation
- Why aggregate logs?
- Centralized logging architecture
- ELK Stack introduction (Elasticsearch, Logstash, Kibana)
- Loki (Grafana Loki) for logs
- Log shipping (Fluentd, Filebeat)
- Log retention and rotation
- Log storage considerations

#### 4.5 Log Analysis
- Searching logs (grep, awk, jq)
- Log patterns and anomalies
- Error investigation
- Performance analysis from logs
- Correlation with metrics
- Log-based metrics
- Common log analysis scenarios

#### 4.6 Logging in Containers
- Container logging strategies
- Docker logs
- Logging drivers
- stdout/stderr logging
- Sidecar pattern for logging
- Kubernetes logging
- Log collection from containers

### 5. Alerting (5-7 hours)

#### 5.1 Alerting Fundamentals
- Why alert?
- Alert fatigue
- Actionable alerts
- Alert severity levels
- On-call considerations
- Escalation policies
- Alert documentation

#### 5.2 Prometheus Alertmanager
- Alertmanager architecture
- Installing Alertmanager
- Alert rules in Prometheus
- Alertmanager configuration
- Routing tree
- Receivers and integrations
- Grouping and throttling
- Silences and inhibition

#### 5.3 Writing Alert Rules
- Alert rule syntax
- Alert conditions
- Threshold-based alerts
- Rate-of-change alerts
- Absence alerts
- Alert labels and annotations
- Alert severity
- Testing alert rules

#### 5.4 Alert Design
- SLO-based alerting
- Symptom vs cause alerting
- Alert context and runbooks
- Alert naming conventions
- Multi-window alerts
- Reducing false positives
- Alert tuning
- Alert review process

#### 5.5 Notification Channels
- Email notifications
- Slack integration
- PagerDuty integration
- Webhook notifications
- Multiple channels
- Escalation workflows
- Notification formatting
- Testing notifications

#### 5.6 Incident Response
- On-call procedures
- Incident triage
- Using alerts for diagnosis
- Post-incident reviews
- Alert improvement
- Incident documentation
- Learning from incidents

### 6. Infrastructure Monitoring (5-6 hours)

#### 6.1 Server Monitoring
- CPU metrics
- Memory metrics
- Disk metrics
- Network metrics
- Node Exporter
- System health checks
- Capacity planning
- Performance baselines

#### 6.2 Container Monitoring
- Docker metrics
- cAdvisor for containers
- Container resource usage
- Container health checks
- Docker events
- Container performance
- Multi-container monitoring

#### 6.3 Service Monitoring
- Service health checks
- Endpoint monitoring
- Blackbox monitoring
- Response time metrics
- Error rates
- Service dependencies
- Synthetic monitoring

#### 6.4 Database Monitoring
- Database metrics
- Connection pool monitoring
- Query performance
- Slow query detection
- Database exporters
- Replication lag
- Database capacity

#### 6.5 Network Monitoring
- Network traffic metrics
- Bandwidth utilization
- Packet loss
- Latency monitoring
- DNS monitoring
- SSL certificate monitoring
- Network topology awareness

### 7. Application Performance Monitoring (4-5 hours)

#### 7.1 APM Fundamentals
- What is APM?
- APM vs infrastructure monitoring
- Application instrumentation
- Transaction tracing
- Dependency mapping
- User experience monitoring
- Real user monitoring vs synthetic

#### 7.2 Python Application Monitoring
- Instrumenting Python apps
- Request/response metrics
- Database query tracking
- External API monitoring
- Background job monitoring
- Memory profiling
- Performance profiling

#### 7.3 API Monitoring
- API endpoint metrics
- Response time distribution
- Error rate tracking
- Request rate monitoring
- Status code distribution
- Endpoint-specific dashboards
- API SLO monitoring

#### 7.4 Business Metrics
- Application-level metrics
- User activity metrics
- Feature usage
- Business KPIs
- Conversion funnels
- Custom business metrics
- Metric-driven development

### 8. Monitoring ML Systems (4-5 hours)

#### 8.1 ML-Specific Monitoring
- Why ML monitoring differs
- Model performance metrics
- Prediction latency
- Prediction throughput
- Model versioning in metrics
- A/B test metrics
- Champion/challenger monitoring

#### 8.2 Data Quality Monitoring
- Input data validation
- Feature distribution
- Missing value detection
- Data schema changes
- Data freshness
- Data volume monitoring
- Outlier detection

#### 8.3 Model Performance Monitoring
- Online vs offline metrics
- Accuracy, precision, recall in production
- Model drift detection
- Concept drift
- Feature drift
- Performance degradation alerts
- Retraining triggers

#### 8.4 ML Pipeline Monitoring
- Training pipeline metrics
- Data processing metrics
- Training duration
- Resource utilization during training
- Model deployment metrics
- Pipeline failures
- End-to-end pipeline observability

### 9. SLIs, SLOs, and SLAs (3-4 hours)

#### 9.1 Service Level Indicators (SLIs)
- What are SLIs?
- Choosing SLIs
- Request-based SLIs
- Window-based SLIs
- Measuring SLIs
- SLI implementation
- SLI best practices

#### 9.2 Service Level Objectives (SLOs)
- What are SLOs?
- Setting realistic SLOs
- Error budget concept
- SLO calculation
- SLO monitoring
- SLO-based alerting
- Iterating on SLOs

#### 9.3 Service Level Agreements (SLAs)
- SLAs vs SLOs
- SLA components
- Negotiating SLAs
- SLA monitoring
- SLA violations
- Internal vs external SLAs
- Legal considerations

#### 9.4 Error Budgets
- Error budget concept
- Calculating error budget
- Error budget policies
- Using error budgets
- Error budget exhaustion
- Balancing velocity and reliability
- Error budget culture

## Lecture Outline

> **Status Update (2025-10-29):** All 5 comprehensive lecture notes are now complete and available! This module includes the new Lecture 05 on Airflow workflow monitoring, essential for ML pipeline observability.

This module includes **5 lectures** and **8 exercises** covering monitoring and observability:

### Lecture 1: Observability Fundamentals (90 min)
- Introduction to observability
- Metrics, logs, traces
- Monitoring strategy
- The four golden signals
- Observability culture
- **Lab:** Analyzing existing systems

### Lecture 2: Prometheus Fundamentals (120 min)
- Prometheus architecture
- Installation and configuration
- Metrics collection
- Exporters
- Basic PromQL
- **Lab:** Setting up Prometheus

### Lecture 3: PromQL and Recording Rules (90 min)
- PromQL deep dive
- Query building
- Aggregations and functions
- Recording rules
- Query optimization
- **Lab:** Writing complex queries

### Lecture 4: Application Instrumentation (90 min)
- Instrumenting Python applications
- Custom metrics
- Labeling strategies
- Best practices
- Performance considerations
- **Lab:** Instrumenting an API

### Lecture 5: Grafana and Dashboards (120 min)
- Grafana fundamentals
- Building dashboards
- Visualization types
- Variables and templating
- Dashboard design
- **Lab:** Creating comprehensive dashboards

### Lecture 6: Logging and Analysis (90 min)
- Structured logging
- Log aggregation
- Log analysis techniques
- Logging in containers
- Best practices
- **Lab:** Implementing structured logging

### Lecture 7: Alerting and Incident Response (90 min)
- Alerting fundamentals
- Prometheus Alertmanager
- Writing alert rules
- Notification channels
- Incident response
- **Lab:** Setting up alerts

### Lecture 4: Logging and Alerting (90 min)
**File**: `lecture-notes/lecture-04-logging-alerting-ml-monitoring.md`
- Structured logging
- Log aggregation
- Logging in containers
- Alerting fundamentals
- Prometheus Alertmanager
- ML system monitoring basics
- **Lab:** Complete logging and alerting setup

### Lecture 5: Airflow Workflow Monitoring (90 min)
**File**: `lecture-notes/lecture-05-airflow-workflow-monitoring.md`
- Introduction to Apache Airflow
- DAG monitoring and observability
- Task-level metrics and logging
- Airflow UI and monitoring tools
- Integration with Prometheus/Grafana
- ML pipeline monitoring with Airflow
- Troubleshooting failed workflows
- **Lab:** Monitoring Airflow ML pipelines

## Hands-On Exercises

> **Status Update (2025-10-29):** All 8 comprehensive exercises are now complete! Each exercise includes practical monitoring scenarios for ML infrastructure.

This module includes **8 exercises** building comprehensive monitoring skills:

### Exercise Categories

#### Monitoring Fundamentals (2 exercises)
1. Identifying key metrics for systems
2. Analyzing monitoring strategy
3. Metric type selection
4. Monitoring layer design
5. Baseline establishment

#### Prometheus (10 exercises)
6. Prometheus installation and configuration
7. Setting up exporters
8. Writing PromQL queries
9. Instrumenting Python application
10. Custom metrics implementation
11. Recording rules creation
12. Service discovery configuration
13. Prometheus performance tuning
14. Multi-target scraping
15. Federation setup

#### Grafana (8 exercises)
16. First dashboard creation
17. Panel types exploration
18. Dashboard variables
19. Alert configuration
20. Dashboard for API monitoring
21. Infrastructure dashboard
22. Template dashboard creation
23. Advanced visualization techniques

#### Logging (5 exercises)
24. Structured logging implementation
25. Log aggregation setup
26. Log analysis scenarios
27. Container logging
28. Log-based metrics

#### Alerting (4 exercises)
29. Alert rule creation
30. Alertmanager configuration
31. Alert routing setup
32. Incident response simulation

#### ML Monitoring (3 exercises)
33. Model performance dashboard
34. Data drift detection
35. Complete ML monitoring stack

### Exercise 07: PromQL and Recording Rules
**Difficulty**: Intermediate to Advanced
**Duration**: 3-4 hours
**File**: `exercises/exercise-07-promql-recording-rules.md`

Master Prometheus Query Language and optimize performance:
- Write effective PromQL queries for ML metrics
- Use rate(), increase(), histogram_quantile() for time-series analysis
- Implement recording rules to pre-compute expensive queries
- Design alert rules with proper thresholds and inhibition
- Optimize Prometheus performance with aggregation
- Monitor ML-specific metrics (inference latency, prediction accuracy, model drift)

### Exercise 08: SLO and Error Budget Management
**Difficulty**: Advanced
**Duration**: 3-4 hours
**File**: `exercises/exercise-08-slo-error-budgets.md`

Implement SLOs and error budgets for ML services:
- Define Service Level Indicators (SLIs) for ML serving APIs
- Set achievable Service Level Objectives (SLOs) with business justification
- Calculate and track error budgets (30-day rolling windows)
- Implement multi-window multi-burn-rate alerting (Google SRE approach)
- Create SLO dashboards for stakeholder communication
- Design error budget policy for decision-making (feature freeze, etc.)

## Assessment and Evaluation

### Knowledge Checks
- **2 comprehensive quizzes** covering all module content
  - Quiz 1: Observability, Prometheus, and Grafana (Lectures 1-3)
  - Quiz 2: Logging, Alerting, and Workflow Monitoring (Lectures 4-5)
- PromQL comprehension
- Dashboard design principles
- Alert design best practices
- ML monitoring concepts

### Practical Assessments
- **Prometheus Setup:** Configure complete Prometheus stack
- **Dashboard Creation:** Build comprehensive monitoring dashboards
- **Application Instrumentation:** Add metrics to Python application
- **Alert Configuration:** Set up actionable alerts
- **ML Monitoring:** Implement model monitoring system

### Competency Criteria
To complete this module successfully, you should be able to:
- Set up Prometheus and Grafana
- Write PromQL queries
- Instrument applications with metrics
- Build effective dashboards
- Implement structured logging
- Configure alerting systems
- Monitor infrastructure and applications
- Apply SLIs and SLOs
- Monitor ML systems
- Respond to incidents using monitoring data

### Capstone Project
**Complete Monitoring Stack:**
Deploy comprehensive monitoring for ML application:
- Prometheus metrics collection
- Application instrumentation
- Infrastructure monitoring
- Grafana dashboards (infrastructure, application, ML model)
- Structured logging
- Alert rules with Alertmanager
- SLI/SLO definition
- Documentation and runbooks

## Resources and References

> **Note:** See `resources/recommended-reading.md` for a comprehensive list of learning materials, books, and online resources.

### Essential Resources
- Prometheus documentation
- Grafana documentation
- SRE Book (Google)
- Observability Engineering book

### Recommended Books
- "Site Reliability Engineering" by Google
- "The Art of Monitoring" by James Turnbull
- "Practical Monitoring" by Mike Julian
- "Observability Engineering" by Charity Majors et al.

### Online Learning
- Prometheus tutorials
- Grafana tutorials
- PromLabs training
- Monitoring Weekly newsletter

### Tools
- Prometheus
- Grafana
- Alertmanager
- cAdvisor
- Node Exporter
- Promtool

## Getting Started

### Step 1: Set Up Monitoring Stack
1. Install Docker and Docker Compose
2. Deploy Prometheus using Docker
3. Deploy Grafana
4. Verify connectivity
5. Explore sample metrics

### Step 2: Explore Existing Metrics
1. Browse Prometheus UI
2. Experiment with PromQL
3. Create simple Grafana dashboard
4. Understand metric structure

### Step 3: Begin with Lecture 1
- Learn observability fundamentals
- Understand monitoring strategy
- Complete initial exercises

### Step 4: Build Progressively
- Instrument sample application
- Create dashboards
- Set up alerts
- Monitor complete system

## Tips for Success

1. **Start Simple:** Begin with basic metrics, add complexity gradually
2. **Practice PromQL:** Query language proficiency comes with practice
3. **Design Dashboards:** Focus on usability and clarity
4. **Alert Wisely:** Avoid alert fatigue with actionable alerts
5. **Monitor Everything:** Instrument applications from day one
6. **Use Labels:** Leverage labels for flexible querying
7. **Document Dashboards:** Add descriptions and annotations
8. **Test Alerts:** Verify alerts trigger correctly
9. **Learn from Incidents:** Use monitoring data for root cause analysis
10. **Iterate:** Continuously improve monitoring strategy

## Next Steps

After completing this module, you'll be ready to:
- **Module 010:** Cloud Platforms (cloud-native monitoring)
- Advanced topics: Distributed tracing, advanced APM, chaos engineering
- Apply monitoring to all future projects

## Development Status

**Current Status:** Template phase - comprehensive structure in place

**Available Now:**
- Complete module structure
- Detailed topic breakdown
- Lecture outline
- Exercise framework

**In Development:**
- Full lecture notes
- PromQL exercises
- Dashboard templates
- Alert rule examples
- ML monitoring patterns
- Complete monitoring stack examples

**Planned Updates:**
- Distributed tracing deep dive
- Advanced PromQL patterns
- Multi-cluster monitoring
- Cost optimization
- Observability platforms comparison

## Feedback and Contributions

Help improve this module:
- Report issues
- Share dashboard designs
- Contribute PromQL queries
- Suggest monitoring patterns

---

**Module Maintainer:** AI Infrastructure Curriculum Team
**Contact:** ai-infra-curriculum@joshua-ferguson.com
**Last Updated:** 2025-10-18
**Version:** 1.0.0-template
