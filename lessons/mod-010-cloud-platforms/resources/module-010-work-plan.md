# Module 010 Work Plan – Cloud Platforms Fundamentals

## Session Objectives
- Produce four comprehensive lecture notes (~3,000–4,000 words each) covering cloud fundamentals, core AWS services, networking/IAM/security, and deployment/ML workloads.
- Design 4–5 progressive hands-on exercises that guide learners from initial AWS setup through IaC-driven deployments and ML workload hosting.
- Author a 30-question knowledge check quiz aligned with the module learning objectives in the README.
- Assemble supporting assets (Terraform templates, architecture diagrams, IAM policy samples, cost calculators) for reuse in future phases.

## Deliverable Inventory

| Deliverable | Description | Notes |
|-------------|-------------|-------|
| `lecture-notes/lecture-01-cloud-fundamentals.md` | Cloud models, economics, multi-cloud, FinOps | Include comparison tables, decision matrices |
| `lecture-notes/lecture-02-aws-core-services.md` | Compute, storage, databases, IAM basics, CLI walkthroughs | Emphasize hands-on AWS CLI tasks |
| `lecture-notes/lecture-03-networking-security.md` | VPC design, subnets, gateways, security groups, IAM deep dive | Provide ASCII diagrams + Terraform snippets |
| `lecture-notes/lecture-04-deployment-ml-workloads.md` | IaC, ECS/EKS, serverless, SageMaker, cost optimization, monitoring | Incorporate integration with Module 009 observability stack |
| Exercises (5) | Labs scoped as described below | Each 1,800–2,500 words with validation steps |
| Quiz | 30 questions spanning fundamental to scenario-based knowledge | Answer key to live in solutions repo |
| Resource Pack | Terraform templates, CLI scripts, architecture diagrams, runbooks | Coordinate with repo phases for final artifacts |

## Exercise Roadmap
1. **Exercise 01 – AWS Account & IAM Bootstrap:** Create AWS account, configure CLI, set up IAM users/roles, implement tagging strategy. Deliverables: IAM policy JSON, MFA walkthrough.
2. **Exercise 02 – Compute & Storage Foundations:** Provision EC2 via CLI/IaC, attach EBS, configure S3 for data ingest, explore spot instances. Deliverables: Terraform/CloudFormation snippets, cost estimate worksheet.
3. **Exercise 03 – Networking & Security Lab:** Build a production VPC (public/private subnets, NAT, security groups), deploy bastion host, enforce least privilege IAM roles. Deliverables: VPC diagram, security audit checklist.
4. **Exercise 04 – Containerized Deployment:** Deploy containerized inference service using ECS Fargate or EKS, integrate load balancer, configure autoscaling and observability hooks. Deliverables: IaC templates, deployment scripts, CloudWatch dashboards TODO.
5. **Exercise 05 – ML Platform Integration & Cost Optimization:** Launch managed ML service (SageMaker/GCP Vertex/Azure ML), connect to previously built infrastructure, implement cost governance (budgets, alerts). Deliverables: notebook sample, cost tracking plan.

## Dependencies & Reuse
- Reference Module 009 observability assets for monitoring integration.
- Leverage Module 005 (Docker) and Module 008 (Databases) project scaffolds for sample workloads.
- Coordinate with repo-learning/solutions agents to provide Terraform and deployment templates under `projects/`.
- Align IAM and security practices with Module 006 (Kubernetes) content for consistency.

## Timeline & Estimation
- **Lectures:** 4 sessions (~16 hours total).
- **Exercises:** 5 sessions (~18–20 hours total).
- **Quiz + resource pack:** 1 session (~4 hours).
- **Buffer:** 2–3 hours for validation alignment and asset packaging.

## Quality Gates
- Ensure all lectures include concrete AWS CLI/IaC examples, diagrams, and ML-specific callouts.
- Exercises must include cleanup steps to avoid unexpected cloud costs and highlight cost monitoring best practices.
- Resource pack should catalog Terraform modules, IAM policy templates, architecture diagrams, cost calculators, and runbooks with TODOs if deferred.
- Update project memory after each major milestone to keep orchestrator and QA aligned.
