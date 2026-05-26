# Module 010 — Cloud Platforms Resources

## Official documentation

### AWS

- **AWS documentation** — [docs.aws.amazon.com](https://docs.aws.amazon.com/). The authoritative reference.
- **AWS Well-Architected Framework** — [aws.amazon.com/architecture/well-architected](https://aws.amazon.com/architecture/well-architected/). Reads like a textbook on production-grade cloud architecture.
- **AWS Machine Learning Lens** — [docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens](https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/). Well-Architected applied to ML workloads.

### GCP

- **GCP documentation** — [cloud.google.com/docs](https://cloud.google.com/docs).
- **GCP Architecture Framework** — [cloud.google.com/architecture/framework](https://cloud.google.com/architecture/framework). GCP's equivalent to AWS Well-Architected.

### Azure

- **Azure documentation** — [learn.microsoft.com/en-us/azure](https://learn.microsoft.com/en-us/azure/).
- **Azure Well-Architected Framework** — [learn.microsoft.com/en-us/azure/architecture/framework](https://learn.microsoft.com/en-us/azure/architecture/framework/).

## Certifications

Worth knowing the certifications exist; some employers value them. Don't chase them for their own sake.

- **AWS Certified Cloud Practitioner** — entry-level, broad.
- **AWS Solutions Architect Associate** — the standard mid-level cert.
- **AWS Machine Learning Specialty** — ML-specific.
- **GCP Associate Cloud Engineer** — equivalent to the AWS Solutions Architect Associate level.
- **Azure Fundamentals (AZ-900)** — entry-level Azure.

## Books

- **AWS Cookbook (2nd ed.)** by John Culkin & Mike Zazon. Recipe-style. Excellent reference.
- **Cloud Native Patterns** by Cornelia Davis. Architectural patterns that apply across clouds.
- **Architecting Modern Data Platforms** (O'Reilly). Cross-cloud data architecture.

## ML-specific cloud services

- **AWS SageMaker documentation** — [docs.aws.amazon.com/sagemaker](https://docs.aws.amazon.com/sagemaker/). AWS's managed ML platform.
- **GCP Vertex AI documentation** — [cloud.google.com/vertex-ai/docs](https://cloud.google.com/vertex-ai/docs). GCP's managed ML platform.
- **Azure ML documentation** — [learn.microsoft.com/en-us/azure/machine-learning](https://learn.microsoft.com/en-us/azure/machine-learning/). Azure's managed ML platform.

The trade-off across all three: faster time-to-value, but vendor lock-in for the managed pieces (training pipelines, model registry, monitoring). Decide deliberately; don't drift in.

## Infrastructure as Code

- **Terraform documentation** — [developer.hashicorp.com/terraform/docs](https://developer.hashicorp.com/terraform/docs). The de facto IaC tool across clouds.
- **AWS CDK** — [aws.amazon.com/cdk](https://aws.amazon.com/cdk/). AWS's IaC framework in your language of choice (Python, TypeScript, etc.).
- **Pulumi** — [pulumi.com/docs](https://www.pulumi.com/docs/). Multi-cloud IaC in real programming languages.
- **OpenTofu** — [opentofu.org](https://opentofu.org/). Community fork of Terraform after the license change.

## Cost management

- **AWS Cost Explorer + Budgets** — built-in tools.
- **GCP Cost Management** — [cloud.google.com/cost-management](https://cloud.google.com/cost-management).
- **OpenCost** — [opencost.io](https://www.opencost.io/). Open standard for Kubernetes cost attribution.
- **Vantage / Kubecost** — commercial cost-visibility tools.

For ML workloads, cost surprises usually come from: idle GPU instances, egress traffic, S3 storage classes, untracked dev environments. Set alarms.

## Multi-cloud and cross-cloud

- **Cilium ClusterMesh** — [docs.cilium.io/en/stable/network/clustermesh](https://docs.cilium.io/en/stable/network/clustermesh/). Multi-cluster networking.
- **Karpenter** — [karpenter.sh](https://karpenter.sh/). AWS-native node autoscaler; good for ML burst capacity.
- **Crossplane** — [crossplane.io](https://www.crossplane.io/). Kubernetes-native IaC across clouds.

## Cross-references in this curriculum

- Module 006 (Kubernetes) — orchestration layer that runs on top of every cloud.
- Engineer track's `mod-102-cloud-computing` covers production cloud patterns in depth.
- Engineer track's `mod-109-infrastructure-as-code` for Terraform + GitOps.
- Senior-engineer track's `mod-205-multi-cloud` for cross-cloud architecture.

## A note on "which cloud should I learn"

If you're starting fresh: **AWS** has the largest market share and the broadest job market. Learn AWS first. Add GCP / Azure once you're comfortable with cloud fundamentals — most concepts transfer; the specifics differ.
