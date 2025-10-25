# Module 004: ML Basics for Infrastructure - Comprehensive Quiz

## Overview

This quiz covers all four lectures in Module 004:
- Lecture 01: Machine Learning Overview
- Lecture 02: PyTorch Basics
- Lecture 03: TensorFlow Basics
- Lecture 04: Model Formats and ONNX

**Total Questions**: 28
**Time Estimate**: 45-60 minutes
**Passing Score**: 70% (20/28 correct)

---

## Instructions

1. Read each question carefully
2. Select the best answer for multiple choice questions
3. For code analysis questions, consider what the code actually does
4. Some questions have scenario-based contexts - read them thoroughly
5. Explanations are provided after each question for learning purposes

---

## Section A: ML Overview (6 questions)

### Question 1 (Easy)
**What is the fundamental difference between traditional programming and machine learning?**

A) Traditional programming is faster than machine learning
B) Machine learning learns patterns from data, while traditional programming uses explicit rules
C) Traditional programming requires more memory than machine learning
D) Machine learning doesn't need any code, only data

**Correct Answer**: B

**Explanation**: The core difference is that traditional programming uses explicit, hand-written rules (if/else statements), while machine learning learns patterns from examples (data). ML doesn't replace programming but changes how we solve problems - instead of writing rules, we provide examples and let the model discover patterns.

---

### Question 2 (Medium)
**Your ML team is deploying a new model to production. The training phase took 3 days on 8 GPUs, but the model will serve 10,000 predictions per second in production. Which infrastructure consideration is MOST critical?**

A) Training GPU capacity for regular retraining
B) Inference latency and throughput optimization
C) Data storage for training datasets
D) Model versioning for training checkpoints

**Correct Answer**: B

**Explanation**: While training happens occasionally (days/weeks), inference happens constantly in production (thousands of times per second). The critical infrastructure need is optimizing for low latency and high throughput to handle 10,000 QPS. Training infrastructure is important but not the immediate bottleneck for production serving.

---

### Question 3 (Easy)
**True or False: In machine learning, "inference" refers to the process of training a model on data.**

A) True
B) False

**Correct Answer**: B (False)

**Explanation**: Inference refers to making predictions with an already-trained model on new, unseen data. Training is the process where the model learns patterns from data. This is a critical distinction for infrastructure engineers - training and inference have completely different resource requirements and optimization strategies.

---

### Question 4 (Medium)
**You need to deploy a model that processes images for object detection. Based on the lecture, what are the expected infrastructure needs?**

A) Training: Low compute, Inference: Very fast, Model size: Small (MB)
B) Training: High compute (GPUs required), Inference: Moderate speed (need GPUs for real-time), Model size: Large (hundreds of MB to GB)
C) Training: Moderate compute, Inference: Very fast (microseconds), Model size: Small (MB)
D) Training: Very high compute, Inference: Slow, Model size: TB-scale

**Correct Answer**: B

**Explanation**: Object detection is a complex computer vision task requiring: (1) High compute training with GPUs, (2) GPUs for real-time inference since object detection models are computationally intensive, (3) Large model sizes (hundreds of MB to GB) due to the complexity of detecting and locating multiple objects in images.

---

### Question 5 (Hard)
**A data scientist reports that their model's prediction confidence has dropped from an average of 0.92 to 0.75 over four weeks in production. What is the MOST likely issue and appropriate infrastructure response?**

A) Hardware failure - replace the GPU
B) Data drift or concept drift - trigger model retraining
C) Memory leak - restart the serving container
D) Network latency - add more load balancers

**Correct Answer**: B

**Explanation**: A gradual decline in prediction confidence over time is a classic symptom of data drift (input distribution changes) or concept drift (relationships between inputs and outputs change). The appropriate infrastructure response is to monitor for this pattern, alert the team, and trigger a retraining pipeline with more recent data. Hardware or network issues would cause sudden failures, not gradual degradation.

---

### Question 6 (Medium)
**Which type of machine learning requires labeled training data where each example has a correct answer?**

A) Unsupervised learning
B) Reinforcement learning
C) Supervised learning
D) Self-supervised learning

**Correct Answer**: C

**Explanation**: Supervised learning requires labeled examples (input + correct output) for training. For example, images labeled as "cat" or "dog". This is the most common ML type in production systems. Unsupervised learning finds patterns without labels, and reinforcement learning learns from rewards. Labels can be expensive to create, which is an important infrastructure cost consideration.

---

## Section B: PyTorch Basics (8 questions)

### Question 7 (Easy)
**What does the `.eval()` method do when called on a PyTorch model before inference?**

A) Evaluates the model's accuracy on a test dataset
B) Sets the model to evaluation mode, disabling dropout and batch normalization training behavior
C) Deletes the model from memory
D) Exports the model to ONNX format

**Correct Answer**: B

**Explanation**: The `.eval()` method sets the model to evaluation mode, which changes the behavior of layers like dropout (disabled during inference) and batch normalization (uses running statistics instead of batch statistics). Forgetting to call `.eval()` is a common mistake that causes inconsistent predictions. This is critical for production inference.

---

### Question 8 (Medium)
**You receive this error: "RuntimeError: Expected all tensors to be on the same device, but found at least two devices, cuda:0 and cpu!" What is the issue?**

A) PyTorch is not installed correctly
B) The model and input tensors are on different devices (one on GPU, one on CPU)
C) The GPU is out of memory
D) The model architecture is incompatible with the input

**Correct Answer**: B

**Explanation**: This error occurs when the model is on one device (e.g., GPU) and the input tensor is on another device (e.g., CPU). PyTorch requires all tensors in a computation to be on the same device. The fix is to ensure both model and inputs are moved to the same device using `.to(device)`.

---

### Question 9 (Easy)
**Which context manager should ALWAYS be used when running PyTorch inference in production to save memory and computation?**

A) `with torch.cuda.empty_cache():`
B) `with torch.no_grad():`
C) `with torch.autograd.profiler():`
D) `with torch.jit.optimize():`

**Correct Answer**: B

**Explanation**: `torch.no_grad()` disables gradient computation, which is only needed during training. Using it during inference saves significant memory (no need to store gradients) and computation time. This should always be used in production inference code. It's one of the most important optimizations for PyTorch inference.

---

### Question 10 (Hard)
**Analyze this code. What is the PRIMARY performance issue?**

```python
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
model = model.to('cuda')

for image in image_list:  # 1000 images
    input_tensor = preprocess(image)  # Returns shape [3, 224, 224]
    input_tensor = input_tensor.to('cuda')
    with torch.no_grad():
        output = model(input_tensor)
    results.append(output)
```

A) The model is not set to eval mode
B) Processing one image at a time instead of batching
C) Using CUDA instead of CPU
D) The input tensor doesn't have a batch dimension

**Correct Answer**: B (though D is also technically an issue)

**Explanation**: The main performance issue is processing images one at a time. Batching would significantly improve GPU utilization and throughput. While the missing batch dimension (D) would cause an immediate error, the performance issue is the lack of batching. In production, you should batch requests to maximize GPU efficiency - processing 32 images at once can be 10-20x faster than processing them individually.

---

### Question 11 (Medium)
**What is the difference between saving a PyTorch model with `torch.save(model.state_dict(), path)` versus `torch.save(model, path)`?**

A) state_dict saves only weights, full model saves weights + architecture
B) state_dict is larger, full model is smaller
C) state_dict requires CUDA, full model works on CPU
D) There is no difference

**Correct Answer**: A

**Explanation**: `state_dict()` saves only the model weights (parameters), requiring you to have the model architecture code separately. `torch.save(model, path)` saves the entire model including architecture. Best practice for production is to use state_dict because it's more portable and flexible - you can modify the architecture code without being locked into the saved structure.

---

### Question 12 (Medium)
**Your GPU shows "CUDA out of memory" errors during inference. Which is NOT a valid solution?**

A) Reduce the batch size
B) Call torch.cuda.empty_cache() to free unused memory
C) Use mixed precision (float16 instead of float32)
D) Increase the learning rate

**Correct Answer**: D

**Explanation**: Learning rate is a training hyperparameter and has nothing to do with memory usage during inference. Valid solutions for OOM errors include: reducing batch size (less data in memory), clearing cache (free unused allocations), using mixed precision (float16 uses half the memory of float32), or ensuring torch.no_grad() is used.

---

### Question 13 (Easy)
**What is TorchServe?**

A) A PyTorch training optimization library
B) PyTorch's official model serving framework for production deployments
C) A tool for converting PyTorch models to TensorFlow
D) A cloud storage service for PyTorch models

**Correct Answer**: B

**Explanation**: TorchServe is PyTorch's official serving framework designed for production ML model deployment. It provides REST/gRPC APIs, model versioning, auto-scaling, metrics, and other production features. You should use TorchServe rather than building your own serving infrastructure from scratch.

---

### Question 14 (Hard)
**You're benchmarking inference speed. With batch size 1, you get 80 samples/sec. With batch size 32, you get 430 samples/sec. What is the approximate latency per sample at batch size 32?**

A) 2.3 ms
B) 12.5 ms
C) 74.4 ms
D) 430 ms

**Correct Answer**: A

**Explanation**: Latency per sample = 1 / (throughput / batch_size) = 1 / (430/32) = 1 / 13.44 = 0.074 seconds = 74.4 ms total batch latency. But per sample: 74.4 ms / 32 = 2.3 ms. This demonstrates the trade-off: batching increases throughput but also increases per-request latency since requests wait for a full batch.

---

## Section C: TensorFlow Basics (8 questions)

### Question 15 (Easy)
**What is the RECOMMENDED model format for deploying TensorFlow models to TensorFlow Serving?**

A) HDF5 (.h5)
B) SavedModel
C) TFLite
D) Checkpoint files

**Correct Answer**: B

**Explanation**: SavedModel is the recommended format for production TensorFlow deployments with TensorFlow Serving. It's a directory-based format that includes the computation graph and weights, works across languages, and is fully compatible with TF Serving. H5 is convenient but not compatible with TF Serving.

---

### Question 16 (Medium)
**What is the difference between TensorFlow's data format and PyTorch's for images?**

A) No difference, both use the same format
B) TensorFlow uses channels-first [N, C, H, W], PyTorch uses channels-last [N, H, W, C]
C) TensorFlow uses channels-last [N, H, W, C], PyTorch uses channels-first [N, C, H, W]
D) TensorFlow requires RGB, PyTorch requires BGR

**Correct Answer**: C

**Explanation**: TensorFlow uses channels-last format [batch, height, width, channels], while PyTorch uses channels-first [batch, channels, height, width]. This is a common source of errors when converting models or data between frameworks. A (1, 224, 224, 3) TensorFlow tensor needs to be transposed to (1, 3, 224, 224) for PyTorch.

---

### Question 17 (Easy)
**You're running TensorFlow and getting OOM errors. Which command enables memory growth to prevent TensorFlow from allocating all GPU memory at once?**

A) `tf.config.set_memory_limit(gpu, 4096)`
B) `tf.config.experimental.set_memory_growth(gpu, True)`
C) `tf.cuda.empty_cache()`
D) `tf.config.enable_memory_saving()`

**Correct Answer**: B

**Explanation**: `tf.config.experimental.set_memory_growth(gpu, True)` tells TensorFlow to allocate GPU memory as needed rather than grabbing all available memory at startup. This is especially important when running multiple models or processes on the same GPU. This should be set early in your code, before creating any TensorFlow operations.

---

### Question 18 (Medium)
**Which TensorFlow Serving API is faster for high-throughput scenarios?**

A) REST API
B) gRPC API
C) HTTP/2 API
D) WebSocket API

**Correct Answer**: B

**Explanation**: gRPC is significantly faster than REST for high-throughput scenarios because it uses binary protocol buffers instead of JSON, has lower overhead, and supports features like streaming. REST is more convenient for testing and human-readable debugging, but production systems serving millions of requests should use gRPC for better performance.

---

### Question 19 (Hard)
**Analyze this TensorFlow Serving configuration. What does it enable?**

```yaml
model_config_list {
  config {
    name: 'my_model'
    base_path: '/models/my_model'
    model_version_policy {
      specific {
        versions: 1
        versions: 2
      }
    }
  }
}
```

A) Load balancing across multiple servers
B) Serving two specific versions simultaneously (A/B testing)
C) Automatic model retraining
D) Model compression

**Correct Answer**: B

**Explanation**: This configuration tells TensorFlow Serving to serve both version 1 and version 2 of the model simultaneously. This is commonly used for A/B testing - you can route a percentage of traffic to v1 and the rest to v2 to compare performance before fully rolling out the new version. The `specific` policy explicitly lists which versions to serve.

---

### Question 20 (Medium)
**What is TensorFlow Lite (TFLite) optimized for?**

A) Large-scale distributed training
B) Mobile and edge device deployment
C) Cloud-based model serving
D) Data preprocessing pipelines

**Correct Answer**: B

**Explanation**: TensorFlow Lite is specifically optimized for mobile (Android, iOS) and edge devices (Raspberry Pi, microcontrollers). It creates smaller model files, has faster inference, and includes optimizations for resource-constrained devices. However, not all TensorFlow operations are supported in TFLite, so conversion may require model modifications.

---

### Question 21 (Easy)
**True or False: In TensorFlow, you need to explicitly call model.eval() before inference like in PyTorch.**

A) True
B) False

**Correct Answer**: B (False)

**Explanation**: TensorFlow/Keras doesn't require an explicit eval() call. Training-specific behaviors (dropout, batch normalization) are automatically controlled by the `training` argument in model.predict() or model() calls. When you use model.predict(), training mode is automatically False. This is a key difference from PyTorch's explicit mode switching.

---

### Question 22 (Medium)
**You want to enable mixed precision for 2x faster inference in TensorFlow. Which command accomplishes this?**

A) `tf.config.set_precision('float16')`
B) `tf.keras.mixed_precision.set_global_policy('mixed_float16')`
C) `model.compile(mixed_precision=True)`
D) `tf.experimental.enable_float16()`

**Correct Answer**: B

**Explanation**: `tf.keras.mixed_precision.set_global_policy('mixed_float16')` enables mixed precision training/inference, using float16 for computations (faster) and float32 for numerical stability where needed. This can provide ~2x speedup on modern GPUs with minimal accuracy loss. It's one of the easiest optimization techniques with significant impact.

---

## Section D: Model Formats and ONNX (6 questions)

### Question 23 (Easy)
**What is the primary benefit of ONNX format for infrastructure teams?**

A) It trains models faster than PyTorch or TensorFlow
B) It enables framework-independent model deployment
C) It automatically optimizes model accuracy
D) It provides better data augmentation

**Correct Answer**: B

**Explanation**: ONNX (Open Neural Network Exchange) is a framework-independent format that allows you to train in any framework (PyTorch, TensorFlow, etc.) and deploy anywhere. This solves the problem of vendor lock-in and allows infrastructure teams to standardize on one serving infrastructure (ONNX Runtime) regardless of which framework data scientists use for training.

---

### Question 24 (Medium)
**Which parameter in PyTorch's ONNX export allows the batch size to be variable at inference time?**

A) `variable_batch=True`
B) `dynamic_axes={'input': {0: 'batch_size'}}`
C) `batch_size=None`
D) `flexible_input=True`

**Correct Answer**: B

**Explanation**: The `dynamic_axes` parameter specifies which dimensions should be dynamic (variable) rather than fixed. `{'input': {0: 'batch_size'}}` means the first dimension (index 0) of the input tensor is dynamic and represents batch size. This is important for production where you might want to process different batch sizes efficiently.

---

### Question 25 (Hard)
**Your team wants to deploy models trained in both PyTorch and TensorFlow. What is the BEST infrastructure approach?**

A) Build separate serving systems for PyTorch (TorchServe) and TensorFlow (TF Serving)
B) Convert all models to ONNX and use ONNX Runtime for unified serving
C) Force data scientists to only use PyTorch
D) Manually rewrite all models in a single framework

**Correct Answer**: B

**Explanation**: Converting all models to ONNX and using ONNX Runtime provides a unified serving infrastructure, reducing complexity and maintenance burden. While option A works, it requires maintaining two separate systems. ONNX Runtime often performs as well or better than native frameworks, and the operational simplicity of a single serving stack is valuable for infrastructure teams.

---

### Question 26 (Medium)
**Quantization reduces model size by approximately how much?**

A) 10%
B) 50%
C) 75%
D) 90%

**Correct Answer**: C (or approximately 4x reduction)

**Explanation**: Quantization typically converts float32 (32 bits) to int8 (8 bits), achieving a ~4x size reduction or about 75% smaller size. For example, a 100MB model becomes ~25MB. This also speeds up inference, especially on CPU, with minimal accuracy loss (typically <1%). It's one of the most effective optimization techniques for model deployment.

---

### Question 27 (Easy)
**What tool is used to convert TensorFlow models to ONNX format?**

A) torch.onnx
B) tf2onnx
C) onnx-tf
D) tensorflow-converter

**Correct Answer**: B

**Explanation**: `tf2onnx` is the official tool for converting TensorFlow models to ONNX format. You can use it as a command-line tool (`python -m tf2onnx.convert`) or as a Python library. PyTorch has built-in ONNX export (`torch.onnx.export`), but TensorFlow requires the separate tf2onnx package.

---

### Question 28 (Hard)
**In a production model serving system, you want to gradually roll out a new model version. Which infrastructure pattern should you implement?**

A) Blue/green deployment - switch all traffic instantly
B) A/B testing with traffic splitting (e.g., 90% old version, 10% new version)
C) Canary deployment - deploy to one server first
D) Rolling restart - update servers one by one

**Correct Answer**: B

**Explanation**: A/B testing with gradual traffic splitting is the safest approach for ML model deployment. Start by routing 5-10% of traffic to the new model version while monitoring metrics (latency, accuracy, error rate). Gradually increase traffic to the new version if metrics are good. This allows you to catch issues before they affect all users and compare model versions with real production data. This is more sophisticated than simple blue/green or canary deployments.

---

## Scoring Guide

### Score Interpretation

- **24-28 (86-100%)**: Excellent! You have a strong understanding of ML infrastructure fundamentals. Ready for hands-on projects.
- **20-23 (71-85%)**: Good! You understand the core concepts. Review questions you missed and try the exercises.
- **16-19 (57-70%)**: Fair. You grasp basic concepts but need more practice. Re-read lecture sections for missed questions.
- **Below 16 (<57%)**: Needs improvement. Review all lectures thoroughly and retake the quiz.

### Difficulty Breakdown

Your quiz contained:
- **Easy questions (40%)**: 11 questions - Testing basic recall and understanding
- **Medium questions (40%)**: 11 questions - Testing application and analysis
- **Hard questions (20%)**: 6 questions - Testing synthesis and problem-solving

### Topic Breakdown

- **ML Overview (Section A)**: 6 questions (21%)
- **PyTorch Basics (Section B)**: 8 questions (29%)
- **TensorFlow Basics (Section C)**: 8 questions (29%)
- **Model Formats/ONNX (Section D)**: 6 questions (21%)

---

## Next Steps

Based on your score:

### If you scored 70% or higher:
1. Move on to hands-on exercises: `exercises/exercise-01-pytorch-inference.md`
2. Start building the module project
3. Consider helping others who are struggling with concepts

### If you scored below 70%:
1. Review the lecture notes for questions you missed
2. Focus on the sections where you had the most errors
3. Try the practical exercises to reinforce learning
4. Retake the quiz after studying

### Key Concepts to Master

Before moving forward, ensure you understand:
- [ ] Training vs Inference distinction
- [ ] PyTorch device management (CPU/GPU)
- [ ] TensorFlow model formats (SavedModel, H5, TFLite)
- [ ] ONNX for framework interoperability
- [ ] Model optimization techniques (quantization)
- [ ] Production serving considerations

---

## Additional Resources

- PyTorch Documentation: https://pytorch.org/docs/
- TensorFlow Guide: https://www.tensorflow.org/guide
- ONNX Format Spec: https://onnx.ai/
- TorchServe: https://pytorch.org/serve/
- TensorFlow Serving: https://www.tensorflow.org/tfx/guide/serving

---

**Quiz Version**: 1.0
**Last Updated**: October 2025
**Estimated Completion Time**: 45-60 minutes
