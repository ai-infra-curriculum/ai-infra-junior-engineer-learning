# Module 004: Machine Learning Basics for Infrastructure Engineers

## Module Overview

Welcome to the Machine Learning Basics module! This module bridges the gap between traditional infrastructure engineering and the specialized world of AI/ML systems. You won't become a data scientist here—instead, you'll learn exactly what infrastructure engineers need to know about ML to effectively build, deploy, and maintain ML systems.

## Why ML Knowledge for Infrastructure Engineers?

As an AI infrastructure engineer, you're not training cutting-edge models or tuning hyperparameters. But you ARE:

- **Deploying models** that data scientists train
- **Building infrastructure** that supports ML workloads
- **Troubleshooting** when models fail in production
- **Optimizing** model serving performance
- **Managing** model lifecycles and versions
- **Monitoring** model behavior and resource usage

To do this effectively, you need to understand:
- What ML models actually are (not just black boxes)
- How models are trained and saved
- Different model formats and their implications
- Resource requirements (CPU, GPU, memory)
- Common failure modes and debugging strategies

## Target Audience Reality Check

**You are NOT**:
- Expected to implement ML algorithms from scratch
- Required to understand advanced mathematical theory
- Responsible for model architecture design
- Tuning hyperparameters or improving model accuracy

**You ARE**:
- Building infrastructure that runs ML code
- Deploying models to production safely
- Monitoring ML system health
- Collaborating with data scientists
- Making infrastructure decisions that affect ML workflows

## Learning Objectives

By the end of this module, you will:

### ML Fundamentals
- Understand core ML concepts: training, inference, features, labels
- Distinguish between supervised, unsupervised, and reinforcement learning
- Recognize common ML tasks: classification, regression, clustering
- Understand the ML workflow from data to deployed model

### PyTorch Essentials
- Load and save PyTorch models
- Understand tensors and basic operations
- Run inference with pre-trained models
- Identify PyTorch model requirements (dependencies, hardware)
- Debug common PyTorch issues in production

### TensorFlow Essentials
- Load and save TensorFlow/Keras models
- Understand TensorFlow model formats (SavedModel, H5)
- Run inference with pre-trained TensorFlow models
- Identify TensorFlow model requirements
- Compare TensorFlow vs PyTorch from infrastructure perspective

### Model Formats and Interoperability
- Understand ONNX (Open Neural Network Exchange)
- Convert models between formats
- Recognize when format conversion is needed
- Choose appropriate format for deployment scenarios

### Infrastructure Considerations
- Estimate model resource requirements
- Understand GPU vs CPU tradeoffs
- Recognize model size and latency constraints
- Plan for batch vs real-time inference
- Handle model versioning and rollback

## Module Structure

This module includes **5 comprehensive lectures** covering ML fundamentals for infrastructure engineers:

### Lecture 01: Machine Learning Overview for Infrastructure (Week 1)
**Duration**: 6-8 hours
**File**: `lecture-notes/01-ml-overview.md`
- What is machine learning?
- The ML workflow: data → training → inference
- Types of ML: supervised, unsupervised, reinforcement
- Common ML tasks and use cases
- ML system components and dependencies
- Infrastructure implications of different ML approaches

### Lecture 02: PyTorch Basics for Infrastructure (Week 1-2)
**Duration**: 8-10 hours
**File**: `lecture-notes/02-pytorch-basics.md`
- PyTorch architecture and ecosystem
- Tensors, devices (CPU/GPU), and data types
- Loading pre-trained models
- Running inference
- Model serialization (state_dict, torch.save)
- PyTorch requirements and dependencies
- Common issues and troubleshooting

### Lecture 03: TensorFlow Basics for Infrastructure (Week 2-3)
**Duration**: 8-10 hours
**File**: `lecture-notes/03-tensorflow-basics.md`
- TensorFlow/Keras architecture
- TensorFlow model formats (SavedModel, H5, TFLite)
- Loading pre-trained models
- Running inference
- Model serving with TensorFlow Serving
- TensorFlow requirements and dependencies
- Comparing TensorFlow and PyTorch

### Lecture 04: Model Formats and Deployment Preparation (Week 3-4)
**Duration**: 6-8 hours
**File**: `lecture-notes/04-model-formats.md`
- ONNX overview and benefits
- Converting PyTorch models to ONNX
- Converting TensorFlow models to ONNX
- Model optimization techniques (quantization, pruning)
- Choosing deployment formats
- Model packaging best practices

### Lecture 05: LLM and Transformers Basics (Week 4)
**Duration**: 6-8 hours
**File**: `lecture-notes/05-llm-transformers-basics.md`
- Introduction to Large Language Models (LLMs)
- Transformer architecture overview
- Popular LLM frameworks (Hugging Face Transformers)
- Loading and using pre-trained LLMs
- LLM inference considerations (memory, latency)
- Infrastructure requirements for LLMs
- LLM deployment patterns

## Prerequisites

### Required Knowledge
- Python programming (Module 001)
- Basic command-line skills (Module 002)
- File operations and package management

### Recommended Background
- Awareness of what neural networks are (conceptually)
- Familiarity with arrays/matrices (conceptual, not mathematical)
- Understanding that ML involves "training" and "prediction"

### Technical Requirements
- Python 3.11+ environment
- 8GB+ RAM (16GB recommended)
- (Optional but recommended) NVIDIA GPU with CUDA
- 10GB+ free disk space for model downloads

## Learning Timeline

### Week 1: ML Fundamentals and PyTorch Introduction
- **Day 1-2**: Lecture 01 (ML Overview)
- **Day 3-4**: Lecture 02 (PyTorch Basics)
- **Day 5**: Exercise 01 (Load and run PyTorch model)

### Week 2: PyTorch Deep Dive and TensorFlow Introduction
- **Day 1-2**: Complete PyTorch exercises
- **Day 3-4**: Lecture 03 (TensorFlow Basics)
- **Day 5**: Exercise 02 (Load and run TensorFlow model)

### Week 3: Model Formats and Conversion
- **Day 1-2**: Lecture 04 (Model Formats)
- **Day 3-4**: Exercise 03 (Convert models to ONNX)
- **Day 5**: Integration practice

### Week 4: Practical Application and Assessment
- **Day 1-3**: Build end-to-end model serving prototype
- **Day 4**: Module 004 Quiz
- **Day 5**: Review and prepare for Module 005

**Total Estimated Time**: 30-40 hours

## Topics Covered

### 1. ML Fundamentals
- Supervised learning (classification, regression)
- Unsupervised learning (clustering, dimensionality reduction)
- Training process: loss functions, optimization, epochs
- Inference process: predictions, batching, throughput
- Overfitting, underfitting, and generalization
- Train/validation/test splits

### 2. PyTorch Ecosystem
- PyTorch core architecture
- Tensor operations and device management
- torch.nn.Module and model structure
- Checkpoints and state dictionaries
- TorchServe for production deployment
- Common PyTorch model architectures (ResNet, BERT, GPT)

### 3. TensorFlow Ecosystem
- TensorFlow and Keras relationship
- tf.keras Sequential and Functional APIs
- SavedModel format structure
- TensorFlow Serving protocol
- TFLite for mobile/edge deployment
- Common TensorFlow model architectures

### 4. ONNX and Model Interoperability
- ONNX format specification
- ONNX Runtime for inference
- Model conversion workflows
- Supported operations and limitations
- Performance implications

### 5. Infrastructure Considerations
- CPU vs GPU inference
- Batch size optimization
- Model loading time and memory footprint
- Latency vs throughput tradeoffs
- Model versioning strategies
- A/B testing infrastructure needs

## Hands-On Exercises

This module includes **6 hands-on exercises** that build practical ML infrastructure skills:

### Exercise 01: PyTorch Model Inference
**Difficulty**: Beginner
**Duration**: 2-3 hours
**File**: `exercises/exercise-01-pytorch-inference.md`

Load a pre-trained PyTorch image classification model (ResNet50), run inference on sample images, and measure performance metrics.

### Exercise 02: TensorFlow Model Inference
**Difficulty**: Beginner
**Duration**: 2-3 hours
**File**: `exercises/exercise-02-tensorflow-inference.md`

Load a pre-trained TensorFlow/Keras model, run inference, and compare with PyTorch implementation from Exercise 01.

### Exercise 03: Model Format Conversion
**Difficulty**: Intermediate
**Duration**: 3-4 hours
**File**: `exercises/exercise-03-model-conversion.md`

Convert both PyTorch and TensorFlow models to ONNX format, verify outputs match original models, and measure performance differences.

### Exercise 04: LLM Inference with Hugging Face
**Difficulty**: Intermediate
**Duration**: 3-4 hours
**File**: `exercises/exercise-04-llm-inference.md`

Work with pre-trained language models using Hugging Face Transformers:
- Load and run inference with GPT-2 or similar LLM
- Understand tokenization and decoding
- Measure inference latency and memory usage
- Compare different model sizes

### Exercise 05: End-to-End Model Serving
**Difficulty**: Advanced
**Duration**: 4-5 hours
**File**: `exercises/exercise-05-model-serving.md`

Build a complete model serving solution:
- Deploy model as REST API
- Handle multiple model formats
- Implement batch inference
- Add logging and monitoring
- Performance optimization

### Exercise 06: ML System Design and Architecture
**Difficulty**: Advanced
**Duration**: 3-4 hours
**Related to**: Lecture 01
**File**: `exercises/exercise-06-ml-system-design.md`

Design end-to-end ML systems for three real-world scenarios:
- Recommendation system architecture
- Fraud detection system design
- Image moderation pipeline
- Serving infrastructure planning
- Data pipeline design
- Cost and performance optimization

## Quizzes & Assessments

### Module 004 Quiz
**Format**: 20 multiple-choice and short-answer questions
**Duration**: 30-45 minutes
**Passing Score**: 80% (16/20 correct)

**Topics Covered**:
- ML workflow and terminology (4 questions)
- PyTorch fundamentals (5 questions)
- TensorFlow fundamentals (5 questions)
- Model formats and conversion (4 questions)
- Infrastructure considerations (2 questions)

### Practical Assessment
Build a simple model serving API that:
- Loads a pre-trained model (PyTorch or TensorFlow)
- Exposes a REST endpoint for inference
- Handles batch requests
- Includes health checks and metrics
- Logs predictions and latency

## Real-World Context

Everything in this module relates directly to infrastructure engineering:

### Model Deployment
- **Load models**: Understanding save formats is crucial for deployment
- **Version management**: Different formats affect versioning strategies
- **Rollback procedures**: Know how to quickly switch model versions

### Resource Management
- **GPU allocation**: Understanding which operations need GPUs
- **Memory planning**: Model size impacts infrastructure sizing
- **Batch optimization**: Balance latency and throughput

### Troubleshooting
- **Debug model loading errors**: Dependency version mismatches
- **Fix inference failures**: Input shape mismatches, device errors
- **Diagnose performance issues**: Identify GPU underutilization

### Collaboration
- **Talk with data scientists**: Understand their requirements
- **Document infrastructure**: ML-specific constraints and capabilities
- **Bridge teams**: Translate between ML and infra terminology

## What This Module Is NOT

### We will NOT cover:
- ❌ Deep learning theory and backpropagation math
- ❌ Training models from scratch
- ❌ Hyperparameter tuning strategies
- ❌ Model architecture design
- ❌ Advanced ML algorithms
- ❌ Data preprocessing and feature engineering
- ❌ Becoming a machine learning engineer

### We WILL cover:
- ✅ Running existing trained models
- ✅ Understanding model files and formats
- ✅ Deploying models to production infrastructure
- ✅ Monitoring and debugging deployed models
- ✅ Resource requirements and optimization
- ✅ Working effectively with ML engineers

## Success Criteria

You will have successfully completed this module when you can:

✅ Explain the difference between training and inference
✅ Load a PyTorch model and run predictions
✅ Load a TensorFlow model and run predictions
✅ Convert models to ONNX format
✅ Identify whether a model requires GPU or can run on CPU
✅ Estimate model memory requirements
✅ Troubleshoot common model loading errors
✅ Choose appropriate model format for deployment
✅ Measure model inference latency and throughput
✅ Score 80% or higher on the module quiz

## Connection to AI Infrastructure

This module is foundational for:

- **Module 005: Docker Containers** - Package ML models in containers
- **Module 006: Kubernetes** - Deploy models at scale
- **Module 007: APIs & Web Services** - Build model serving endpoints
- **Module 009: Monitoring** - Monitor model performance
- **Future Projects**: All projects involve deploying or managing ML models

## What's Next?

After completing this module, you'll move on to:
- **Module 005**: Docker Containers (packaging ML models)
- **Module 006**: Kubernetes Introduction (orchestrating ML workloads)
- **Module 007**: APIs & Web Services (building serving endpoints)

The ML knowledge from this module will be applied throughout the rest of the curriculum.

## Getting Help

### During the Module
- Review lecture notes multiple times—ML concepts take repetition
- Run all code examples in the lectures
- Don't skip exercises—hands-on practice is essential
- Use print statements to inspect tensors and model outputs
- Read error messages carefully—they often indicate version mismatches

### External Resources
- PyTorch documentation and tutorials
- TensorFlow official guides
- ONNX Runtime documentation
- Model zoos: HuggingFace Hub, TorchHub, TensorFlow Hub
- Stack Overflow for specific errors

### Common Pitfalls
- Version mismatches between PyTorch/TensorFlow and models
- CUDA version incompatibilities
- Input shape mismatches during inference
- Device errors (model on GPU, input on CPU)
- Missing model files or checkpoints

## Tools and Resources

### Essential Tools
- **PyTorch**: 2.1.0+
- **TensorFlow**: 2.13.0+
- **ONNX**: Latest version
- **ONNX Runtime**: Latest version
- **NumPy**: For array operations
- **Pillow**: For image processing

### Model Sources
- **HuggingFace Hub**: Pre-trained transformers (BERT, GPT, etc.)
- **TorchHub**: Pre-trained PyTorch models
- **TensorFlow Hub**: Pre-trained TensorFlow models
- **ONNX Model Zoo**: Pre-converted ONNX models

### Development Tools
- **Jupyter notebooks**: Interactive experimentation
- **tensorboard**: Visualization (TensorFlow)
- **netron**: Visualize model architectures
- **nvidia-smi**: GPU monitoring

## Important Notes

### GPU Access
While many exercises can run on CPU, having GPU access significantly improves the learning experience. If you don't have a local GPU:

- Use Google Colab (free GPU access)
- Use AWS EC2 g4dn instances (pay per hour)
- Use Paperspace Gradient (ML-focused cloud)
- Focus on understanding concepts; run inference on CPU

### Download Requirements
Pre-trained models can be large (100MB to several GB). Ensure you have:
- Stable internet connection
- Sufficient disk space
- Patience for initial downloads (cached afterward)

### Framework Installation
CUDA-enabled PyTorch and TensorFlow require specific CUDA versions. Follow official installation guides carefully for your system.

---

**Module Version**: 1.0
**Last Updated**: October 2025
**Estimated Completion Time**: 30-40 hours
**Difficulty Level**: Beginner to Intermediate

**Ready to begin?** Start with `lecture-notes/01-ml-overview.md`
