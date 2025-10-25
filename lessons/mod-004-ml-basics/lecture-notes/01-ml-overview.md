# Lecture 01: Machine Learning Overview for Infrastructure Engineers

## Table of Contents
1. [Introduction](#introduction)
2. [What is Machine Learning?](#what-is-machine-learning)
3. [The ML Workflow](#the-ml-workflow)
4. [Types of Machine Learning](#types-of-machine-learning)
5. [Common ML Tasks](#common-ml-tasks)
6. [ML System Architecture](#ml-system-architecture)
7. [Infrastructure Implications](#infrastructure-implications)
8. [Summary](#summary)

---

## Introduction

### The Infrastructure Engineer's Perspective

You don't need to be a machine learning expert to build ML infrastructure. But you do need to understand what's happening inside those "black boxes" you're deploying.

Think of it like this:
- **Web developers** don't need to understand TCP/IP packet routing, but they need to know HTTP basics
- **Database administrators** don't need to write query optimizers, but they need to understand indexes
- **ML infrastructure engineers** don't need to design neural networks, but they need to understand training vs inference

This lecture gives you the ML knowledge you need—no more, no less—to be effective in AI infrastructure.

### Learning Objectives

By the end of this lecture, you will:
- Understand what machine learning actually does (demystifying the hype)
- Recognize the stages of ML workflows and where infrastructure fits
- Distinguish between training and inference (critically important!)
- Identify different types of ML and their infrastructure needs
- Anticipate resource requirements based on ML task type
- Communicate effectively with data scientists and ML engineers

---

## What is Machine Learning?

### The Traditional Programming Paradigm

Traditional programming is explicit rule-based logic:

```python
def classify_email(email_text: str) -> str:
    """Traditional rule-based spam detection"""
    spam_keywords = ["free money", "click here", "win now"]

    for keyword in spam_keywords:
        if keyword in email_text.lower():
            return "spam"

    return "not spam"
```

**Problems with this approach:**
- Rules are brittle and easily circumvented
- Requires manual updates for new patterns
- Can't handle nuance or context
- Doesn't improve with more data

### The Machine Learning Paradigm

Machine learning learns patterns from data:

```python
# ML approach (conceptual)
training_data = [
    ("free money win now!", "spam"),
    ("meeting tomorrow at 3pm", "not spam"),
    ("click here for prizes", "spam"),
    # ... thousands more examples
]

# Train model to learn patterns
model = train_spam_classifier(training_data)

# Use learned patterns to classify new emails
result = model.predict("limited time offer click now")
# Returns: "spam" (learned pattern, not hardcoded rule)
```

**Advantages:**
- Learns complex patterns humans can't easily articulate
- Improves with more data
- Adapts to new patterns when retrained
- Handles nuance and context

### Core ML Concept: Function Approximation

At its core, ML is **function approximation**:

**Traditional programming:**
```
Rules (written by programmer) + Input → Output
```

**Machine learning:**
```
Examples (data) → Learn Function → Apply to New Input → Output
```

**Concrete example - Image classification:**

```
Traditional: IF pixels match pattern X THEN cat
ML: Here are 10,000 cat images and 10,000 dog images.
    Figure out what makes them different.
    Now tell me if this new image is a cat or dog.
```

### What ML Is Good For

✅ **Pattern recognition** - Identifying cats in images, detecting fraud
✅ **Prediction** - Stock prices, equipment failure, customer churn
✅ **Classification** - Spam detection, sentiment analysis, disease diagnosis
✅ **Generation** - Text generation (GPT), image generation (DALL-E)
✅ **Complex decision-making** - Game playing (AlphaGo), robotics

### What ML Is NOT Good For

❌ **Exact calculations** - Use traditional programming (2 + 2 = 4)
❌ **Guaranteed correctness** - ML is probabilistic, not deterministic
❌ **Explaining decisions** - Many models are "black boxes"
❌ **Tasks without data** - ML needs examples to learn from
❌ **Simple rule-based logic** - Don't use ML when `if/else` suffices

---

## The ML Workflow

### Overview: Data to Deployed Model

```
┌─────────────┐
│ 1. Data     │  Collect and prepare training data
│ Collection  │
└──────┬──────┘
       │
┌──────▼──────┐
│ 2. Data     │  Clean, transform, split data
│ Preparation │
└──────┬──────┘
       │
┌──────▼──────┐
│ 3. Training │  Learn patterns from data
│             │  (This is what "ML" usually refers to)
└──────┬──────┘
       │
┌──────▼──────┐
│ 4. Evaluation│ Test model performance
│             │
└──────┬──────┘
       │
┌──────▼──────┐
│ 5. Deployment│ Deploy model to production
│             │  (THIS IS YOUR PRIMARY FOCUS)
└──────┬──────┘
       │
┌──────▼──────┐
│ 6. Inference│  Make predictions on new data
│             │  (THIS IS ALSO YOUR FOCUS)
└──────┬──────┘
       │
┌──────▼──────┐
│ 7. Monitoring│ Track performance, detect drift
│             │  (THIS TOO)
└─────────────┘
```

### Phase 1: Data Collection

**What happens:**
- Gather training examples
- Label data (for supervised learning)
- Store in databases or data lakes

**Example - Sentiment Analysis:**
```
Tweet                           Label
"I love this product!"          positive
"Worst experience ever"         negative
"It's okay, nothing special"    neutral
```

**Infrastructure role:**
- Provide storage for datasets
- Build data pipelines
- Ensure data access for training

### Phase 2: Data Preparation

**What happens:**
- Clean data (remove duplicates, handle missing values)
- Transform data (normalize, encode categorical variables)
- Split into training/validation/test sets

**Example split:**
```
Total dataset: 10,000 examples
├── Training set:   7,000 (70%)  ← Model learns from this
├── Validation set: 2,000 (20%)  ← Tune hyperparameters
└── Test set:       1,000 (10%)  ← Final evaluation
```

**Infrastructure role:**
- Provide compute for data processing
- Store processed datasets
- Version control datasets

### Phase 3: Training (The "Learning" Part)

**What happens:**
- Model processes training data
- Adjusts internal parameters to minimize errors
- Iterates through data multiple times (epochs)

**Training process (simplified):**
```
for epoch in range(num_epochs):
    for batch in training_data:
        # Make predictions
        predictions = model(batch.inputs)

        # Calculate error (loss)
        loss = calculate_loss(predictions, batch.labels)

        # Update model to reduce error
        model.update_parameters(loss)
```

**Visual representation:**
```
Epoch 1: Loss = 0.8  ████████░░
Epoch 2: Loss = 0.6  ██████░░░░
Epoch 3: Loss = 0.4  ████░░░░░░
Epoch 4: Loss = 0.3  ███░░░░░░░
...
Epoch 20: Loss = 0.1  █░░░░░░░░░ (Model is trained!)
```

**Infrastructure role (CRITICAL):**
- Provide GPU/TPU compute for training
- Manage training job scheduling
- Store model checkpoints
- Monitor resource utilization
- Handle long-running jobs (hours to weeks!)

### Phase 4: Evaluation

**What happens:**
- Test model on unseen data (test set)
- Calculate metrics (accuracy, precision, recall, etc.)
- Decide if model is good enough for production

**Example metrics:**
```
Test Set Results:
├── Accuracy: 92%
├── Precision: 90%
├── Recall: 88%
└── F1 Score: 89%
```

**Infrastructure role:**
- Provide compute for evaluation
- Store evaluation results
- Track model versions and metrics

### Phase 5: Deployment

**What happens:**
- Package trained model
- Deploy to serving infrastructure
- Expose API for predictions
- Implement monitoring and logging

**Infrastructure role (YOUR PRIMARY JOB):**
- Build model serving infrastructure
- Implement CI/CD for models
- Handle model versioning
- Implement A/B testing
- Ensure high availability and low latency

### Phase 6: Inference (Prediction)

**What happens:**
- Receive new input
- Run input through model
- Return prediction

**Example - Image classification:**
```python
# New image arrives
new_image = load_image("cat_photo.jpg")

# Run through deployed model
prediction = model.predict(new_image)
# Returns: {"class": "cat", "confidence": 0.95}
```

**Infrastructure role:**
- Serve predictions with low latency
- Handle concurrent requests
- Batch requests for efficiency
- Monitor prediction quality

### Phase 7: Monitoring and Retraining

**What happens:**
- Monitor model performance in production
- Detect data drift (input distribution changes)
- Detect concept drift (relationships change)
- Trigger retraining when needed

**Example drift detection:**
```
Week 1: Average prediction confidence: 0.92 ✓
Week 2: Average prediction confidence: 0.90 ✓
Week 3: Average prediction confidence: 0.85 ⚠️
Week 4: Average prediction confidence: 0.75 ❌ (Retrain!)
```

**Infrastructure role:**
- Implement monitoring dashboards
- Log predictions and features
- Automate retraining pipelines
- Manage model versioning

---

## Types of Machine Learning

### Supervised Learning

**Definition:** Learning from labeled examples (input + correct output)

**Analogy:** Learning with a teacher who provides answers

**Example:**
```
Training data:
Image of cat   → Label: "cat"
Image of dog   → Label: "dog"

After training:
New image      → Prediction: "cat" (no label needed!)
```

**Common tasks:**
- Classification (output is a category)
- Regression (output is a number)

**Infrastructure considerations:**
- Requires labeled training data (can be expensive to create)
- Training can be compute-intensive
- Inference is typically fast

### Unsupervised Learning

**Definition:** Finding patterns in data without labels

**Analogy:** Learning by exploring on your own

**Example - Clustering:**
```
Training data:
Customer 1: Age=25, Income=$50k, Purchases=10
Customer 2: Age=24, Income=$48k, Purchases=12
Customer 3: Age=55, Income=$90k, Purchases=5
Customer 4: Age=58, Income=$95k, Purchases=4

Algorithm groups similar customers:
Cluster 1: Young, moderate income, frequent buyers
Cluster 2: Older, high income, infrequent buyers
```

**Common tasks:**
- Clustering (group similar examples)
- Dimensionality reduction (compress data)
- Anomaly detection (find outliers)

**Infrastructure considerations:**
- No labels needed (cheaper data)
- Can process large amounts of data
- May require more compute for training

### Reinforcement Learning

**Definition:** Learning through trial and error with rewards

**Analogy:** Training a dog with treats

**Example - Game playing:**
```
Action: Move chess piece → Outcome: Lost the game → Reward: -1
Action: Different move   → Outcome: Won the game  → Reward: +1

After many games: Learns to play chess well!
```

**Common tasks:**
- Game playing (Chess, Go, video games)
- Robotics (learn to walk, grasp objects)
- Resource optimization (data center cooling)

**Infrastructure considerations:**
- Requires simulation environment (expensive)
- Extremely compute-intensive training
- Training can take days to months
- Inference is typically fast

### Semi-Supervised and Self-Supervised Learning

**Semi-supervised:** Mix of labeled and unlabeled data

**Self-supervised:** Create labels from data itself

**Example - Self-supervised:**
```
Original sentence: "The cat sat on the mat"

Training example:
Input:  "The cat ___ on the mat"
Output: "sat"

Model learns language patterns without manual labeling!
```

**Infrastructure considerations:**
- Reduces labeling cost
- Can leverage large unlabeled datasets
- Used by models like BERT, GPT

---

## Common ML Tasks

### Classification

**What it does:** Assigns input to one of several categories

**Examples:**
- Email: spam or not spam
- Image: cat, dog, bird, etc.
- Medical: disease diagnosis
- Sentiment: positive, negative, neutral

**Output:** Class label (category)

**Infrastructure needs:**
- **Training:** Moderate to high compute (GPUs for complex tasks)
- **Inference:** Fast (milliseconds)
- **Model size:** Varies (MB to several GB)

### Regression

**What it does:** Predicts a continuous numerical value

**Examples:**
- House price prediction
- Temperature forecasting
- Stock price prediction
- Equipment failure time estimation

**Output:** Number (e.g., $325,000, 72.5°F, 14.3 days)

**Infrastructure needs:**
- **Training:** Moderate compute
- **Inference:** Very fast (microseconds to milliseconds)
- **Model size:** Typically small (MB)

### Object Detection

**What it does:** Identifies and locates objects in images

**Example:**
```
Input: Image of street scene
Output: [
  {object: "car", bbox: [100, 200, 300, 400], confidence: 0.95},
  {object: "person", bbox: [350, 180, 450, 350], confidence: 0.92},
  {object: "sign", bbox: [500, 100, 600, 200], confidence: 0.88}
]
```

**Infrastructure needs:**
- **Training:** High compute (GPUs required)
- **Inference:** Moderate speed (need GPUs for real-time)
- **Model size:** Large (hundreds of MB to GB)

### Natural Language Processing (NLP)

**What it does:** Understands and generates human language

**Examples:**
- Text classification (sentiment analysis)
- Named entity recognition (extract names, dates, locations)
- Machine translation
- Text generation (ChatGPT, etc.)

**Infrastructure needs:**
- **Training:** Very high compute (large models need multiple GPUs)
- **Inference:** Varies (simple NLP is fast, large language models are slow)
- **Model size:** Varies widely (MB to hundreds of GB)

### Recommendation Systems

**What it does:** Suggests items users might like

**Examples:**
- Netflix movie recommendations
- Amazon product suggestions
- Spotify music playlists
- YouTube video recommendations

**Infrastructure needs:**
- **Training:** High compute and memory (large datasets)
- **Inference:** Fast (must scale to millions of users)
- **Model size:** Can be very large (GB to TB of embeddings)

---

## ML System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      ML System Architecture                   │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│ Data Storage        │
│ - Raw data          │
│ - Processed data    │
│ - Feature store     │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Training Pipeline   │
│ - Data processing   │
│ - Model training    │
│ - Evaluation        │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Model Registry      │
│ - Model artifacts   │
│ - Metadata          │
│ - Versioning        │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Serving Layer       │
│ - Model loading     │
│ - Preprocessing     │
│ - Inference         │
│ - Postprocessing    │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ API Layer           │
│ - REST/gRPC         │
│ - Auth              │
│ - Rate limiting     │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Monitoring          │
│ - Metrics           │
│ - Logs              │
│ - Alerting          │
└─────────────────────┘
```

### Key Components

#### 1. Data Storage
```
Purpose: Store training data and features
Infrastructure:
- Object storage (S3, GCS, Azure Blob)
- Data lakes (Delta Lake, Iceberg)
- Feature stores (Feast, Tecton)

Your role:
- Provision storage
- Implement data versioning
- Ensure data access for training jobs
```

#### 2. Training Infrastructure
```
Purpose: Run training jobs
Infrastructure:
- GPU clusters (NVIDIA A100, H100)
- Job schedulers (Kubernetes, Slurm)
- Experiment tracking (MLflow, W&B)

Your role:
- Provision and manage GPU resources
- Schedule training jobs
- Implement resource quotas
- Handle long-running jobs
```

#### 3. Model Registry
```
Purpose: Store and version trained models
Infrastructure:
- Model storage (S3, GCS)
- Metadata database (PostgreSQL)
- Model registry (MLflow, DVC)

Your role:
- Implement model versioning
- Track model metadata
- Manage model lifecycle
```

#### 4. Serving Infrastructure
```
Purpose: Serve predictions at scale
Infrastructure:
- Model servers (TorchServe, TensorFlow Serving)
- Load balancers
- Auto-scaling groups

Your role:
- Deploy models to production
- Implement auto-scaling
- Optimize latency and throughput
- Handle model updates (blue/green, canary)
```

#### 5. Monitoring and Observability
```
Purpose: Track model and system health
Infrastructure:
- Metrics (Prometheus, Datadog)
- Logs (ELK, Splunk)
- Tracing (Jaeger, Tempo)

Your role:
- Implement monitoring dashboards
- Set up alerting
- Log predictions for debugging
- Track model performance metrics
```

---

## Infrastructure Implications

### Training vs Inference: The Critical Distinction

**Training (happens occasionally):**
- Processes entire dataset (millions of examples)
- Runs for hours, days, or weeks
- Requires massive compute (GPUs/TPUs)
- High memory requirements
- Can tolerate latency
- Happens in batch mode

**Inference (happens constantly):**
- Processes single inputs (or small batches)
- Needs to return results in milliseconds
- Can sometimes use CPUs
- Lower memory requirements
- Latency is critical
- Happens in real-time

**Infrastructure implications:**
```
Training:
├── Infrastructure: High-end GPU clusters
├── Scheduling: Batch job systems
├── Cost model: Pay for reserved capacity
└── Optimization: Throughput over latency

Inference:
├── Infrastructure: Optimized serving layer
├── Scheduling: Real-time request handling
├── Cost model: Pay per prediction
└── Optimization: Latency over throughput
```

### Resource Requirements by Model Type

#### Small Models (< 100MB)
```
Examples: Simple classifiers, regression models
Training:
- CPU often sufficient
- Hours to train
- GB-scale RAM

Inference:
- CPU is fine
- Sub-millisecond latency
- Can handle thousands of QPS per server
```

#### Medium Models (100MB - 5GB)
```
Examples: ResNet, BERT base
Training:
- GPUs recommended
- Hours to days
- 10-100GB RAM

Inference:
- GPUs for real-time, CPUs for batch
- 10-100ms latency
- Hundreds of QPS per GPU
```

#### Large Models (5GB - 100GB)
```
Examples: Large vision models, BERT large
Training:
- Multiple GPUs required
- Days to weeks
- 100-500GB RAM

Inference:
- GPUs required
- 100-1000ms latency
- Tens of QPS per GPU
```

#### Massive Models (> 100GB)
```
Examples: GPT-3, GPT-4, large multimodal models
Training:
- Distributed across 100s-1000s of GPUs
- Weeks to months
- TB-scale RAM

Inference:
- Multiple GPUs per prediction
- 1-10+ seconds latency
- Single-digit QPS per instance
```

### Cost Considerations

**Training costs:**
- GPU hours: $1-$30+ per hour depending on GPU type
- Storage: $0.02-$0.10 per GB/month
- Data processing: CPU compute and I/O costs

**Inference costs:**
- Per-request: $0.0001 - $0.01+ per prediction
- GPU utilization: Keep GPUs busy to amortize cost
- Auto-scaling: Balance cost and latency SLAs

**Example cost calculation:**
```
Model: BERT-base for sentiment analysis
Training (one-time):
- 8 x A100 GPUs × 24 hours × $2.50/hr = $480

Inference (monthly):
- 10M predictions/day
- 100ms per prediction
- 2 GPU instances running 24/7
- 2 × 720 hours × $1.50/hr = $2,160/month
```

---

## Summary

### Key Takeaways

1. **ML learns patterns from data** rather than explicit programming
2. **Training and inference are fundamentally different** - understand this distinction!
3. **Different ML types** (supervised, unsupervised, RL) have different infrastructure needs
4. **Common tasks** (classification, regression, NLP) have predictable resource requirements
5. **ML systems are complex** - many components beyond just "the model"
6. **Infrastructure is critical** - models are useless without good infrastructure

### Infrastructure Engineer's Mental Model

When you encounter an ML project, ask:

✅ **Is this training or inference?**
✅ **What type of ML task is this?**
✅ **What are the resource requirements?**
✅ **What's the latency requirement?**
✅ **How often does the model need to be retrained?**
✅ **What's the expected query volume?**
✅ **What framework is used? (PyTorch, TensorFlow, etc.)**

### What You've Learned

- ✅ What machine learning actually is (function approximation from data)
- ✅ The full ML workflow from data to deployment
- ✅ Training vs inference (critically important!)
- ✅ Types of ML and their infrastructure implications
- ✅ Common ML tasks and resource requirements
- ✅ ML system architecture components
- ✅ How to think about ML infrastructure

### Next Steps

Now that you understand ML fundamentals, you'll dive into:
- **Lecture 02:** PyTorch basics (loading models, running inference)
- **Lecture 03:** TensorFlow basics (alternative framework)
- **Lecture 04:** Model formats and deployment preparation

---

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Word Count**: ~3,800 words
**Estimated Reading Time**: 50-70 minutes

**Ready for hands-on work?** Continue to `02-pytorch-basics.md`
