# Lecture 05: LLM and Transformer Basics for Infrastructure Engineers

## Table of Contents
1. [Introduction](#introduction)
2. [Transformer Architecture Fundamentals](#transformer-architecture-fundamentals)
3. [Large Language Models Overview](#large-language-models-overview)
4. [Hugging Face Ecosystem](#hugging-face-ecosystem)
5. [Running Inference with Transformers](#running-inference-with-transformers)
6. [Tokenization and Text Processing](#tokenization-and-text-processing)
7. [Prompt Engineering Basics](#prompt-engineering-basics)
8. [Building LLM APIs](#building-llm-apis)
9. [Infrastructure Considerations](#infrastructure-considerations)
10. [Summary and Best Practices](#summary-and-best-practices)

---

## Introduction

### The LLM Revolution

Large Language Models (LLMs) like GPT, BERT, and LLaMA have transformed AI applications:
- **Natural language understanding** (sentiment analysis, classification)
- **Text generation** (chatbots, content creation)
- **Code generation** (GitHub Copilot, code completion)
- **Question answering** (search, support automation)
- **Translation and summarization**

As an infrastructure engineer, you'll deploy and serve these models, manage their compute resources, and ensure they run efficiently in production.

### Why Infrastructure Engineers Need to Know LLMs

1. **Resource management**: LLMs are massive (1GB to 100GB+ model files)
2. **Compute requirements**: Need GPUs for reasonable inference speed
3. **Latency optimization**: Inference can take seconds without optimization
4. **Cost management**: Running LLMs can be expensive
5. **API design**: Building reliable serving infrastructure

### Learning Objectives

By the end of this lecture, you will:
- Understand transformer architecture at a high level
- Work with Hugging Face transformers library
- Load and run inference with pretrained LLMs
- Understand tokenization and its importance
- Build basic LLM-powered APIs
- Identify infrastructure challenges specific to LLMs

---

## Transformer Architecture Fundamentals

### What Are Transformers?

**Transformers** are neural network architectures that process sequences (text, audio, etc.) using **attention mechanisms**. They replaced older RNN/LSTM architectures and became dominant after the 2017 paper "Attention Is All You Need."

### Key Components

#### 1. Self-Attention Mechanism

Self-attention allows the model to weigh the importance of different words when processing each word.

**Example**: In "The animal didn't cross the street because **it** was too tired", self-attention helps the model understand "it" refers to "animal", not "street".

```
Attention weights for "it":
- The: 0.05
- animal: 0.82  ← High attention!
- didn't: 0.03
- cross: 0.02
- the: 0.01
- street: 0.04
- because: 0.01
- it: 0.00
- was: 0.01
- too: 0.00
- tired: 0.01
```

#### 2. Multi-Head Attention

Instead of one attention mechanism, use multiple "heads" that learn different relationships:
- Head 1: Subject-verb relationships
- Head 2: Noun-adjective relationships
- Head 3: Semantic similarity
- etc.

#### 3. Positional Encoding

Since transformers process all words simultaneously (not sequentially like RNNs), they need positional information:

```python
# Simplified positional encoding concept
position = [0, 1, 2, 3, 4]  # Word positions
tokens = ["The", "cat", "sat", "on", "mat"]

# Each position gets a unique encoding
# Combined with word embeddings
```

#### 4. Feed-Forward Networks

After attention layers, simple neural networks process each position independently.

### Transformer Architecture Variants

#### Encoder-Only (BERT-style)
- **Purpose**: Understanding text (classification, NER, Q&A)
- **Models**: BERT, RoBERTa, DistilBERT
- **Use case**: "Is this email spam?" (classification)

```python
# BERT processes both directions
Input: "I love [MASK] learning"
Output: Predicts "machine" for [MASK] using context from both sides
```

#### Decoder-Only (GPT-style)
- **Purpose**: Generating text (chat, completion, creative writing)
- **Models**: GPT-2, GPT-3, LLaMA, Mistral
- **Use case**: "Complete this code: def hello()..."

```python
# GPT generates left-to-right
Input: "Once upon a time"
Output: "Once upon a time, there was a brave knight..."
```

#### Encoder-Decoder (T5-style)
- **Purpose**: Sequence-to-sequence tasks (translation, summarization)
- **Models**: T5, BART, mT5
- **Use case**: Translate English to French

```python
Input (Encoder): "Hello, how are you?"
Output (Decoder): "Bonjour, comment allez-vous ?"
```

### Why Transformers Dominate

1. **Parallelization**: Process entire sequence at once (vs RNN's sequential processing)
2. **Long-range dependencies**: Attention mechanism connects distant words
3. **Scalability**: Performance improves with more data and parameters
4. **Transfer learning**: Pretrain once, fine-tune for many tasks

---

## Large Language Models Overview

### What Makes a Model "Large"?

| Model Class | Parameters | Model Size | Example Models |
|-------------|-----------|-----------|----------------|
| Small | < 500M | < 2GB | DistilBERT, DistilGPT-2 |
| Medium | 500M - 7B | 2GB - 28GB | BERT-Large, GPT-2, Mistral-7B |
| Large | 7B - 70B | 28GB - 280GB | LLaMA-2-13B, Falcon-40B |
| Extra Large | > 70B | > 280GB | LLaMA-2-70B, GPT-3.5, GPT-4 |

**Note**: Parameter count ≠ model file size. FP32 (4 bytes/param), FP16 (2 bytes/param), INT8 (1 byte/param).

### Popular LLM Families

#### BERT Family (Encoder-Only)
```python
# Good for: Classification, NER, sentence similarity
- BERT: Original transformer encoder (2018)
- RoBERTa: Optimized BERT training
- DistilBERT: Smaller, faster BERT (60% smaller, 95% performance)
- ALBERT: Parameter-efficient BERT
```

#### GPT Family (Decoder-Only)
```python
# Good for: Text generation, chat, completion
- GPT-2: 117M to 1.5B parameters (open source)
- GPT-3: 175B parameters (OpenAI API only)
- GPT-3.5: ChatGPT base model
- GPT-4: Most capable (API only)
```

#### LLaMA Family (Decoder-Only, Open Source)
```python
# Good for: Open-source alternatives to GPT
- LLaMA: Meta's foundational models (7B, 13B, 30B, 65B)
- LLaMA-2: Improved version, commercial-friendly license
- Alpaca: Stanford's instruction-tuned LLaMA
- Vicuna: UC Berkeley's chatbot model
```

#### Specialized Models
```python
# Code generation
- CodeLLaMA: LLaMA fine-tuned for code
- StarCoder: Open-source code model
- Codex: OpenAI's code model (powers Copilot)

# Multilingual
- mBERT: Multilingual BERT (104 languages)
- XLM-RoBERTa: Cross-lingual RoBERTa
- mT5: Multilingual T5

# Efficient models
- Mistral-7B: High performance, small size
- Falcon: Efficient open-source LLMs
- Phi-2: Microsoft's small but powerful model (2.7B)
```

---

## Hugging Face Ecosystem

### What Is Hugging Face?

**Hugging Face** is the central hub for:
1. **Model Hub**: 200,000+ pretrained models
2. **Transformers Library**: Easy-to-use Python library
3. **Datasets**: 10,000+ datasets for training/evaluation
4. **Spaces**: Demo and deploy ML applications

### Installing Transformers

```bash
# Basic installation
pip install transformers

# With PyTorch
pip install transformers torch

# With TensorFlow
pip install transformers tensorflow

# Full installation with all extras
pip install transformers[torch,sentencepiece,vision]
```

### The Transformers Library Architecture

```python
from transformers import (
    AutoTokenizer,      # Handles text → tokens
    AutoModel,          # Generic model loader
    AutoModelForCausalLM,  # For GPT-style generation
    AutoModelForSequenceClassification,  # For classification
    pipeline            # High-level API
)
```

**Key Design Principles**:
1. **Auto Classes**: Automatically load correct model/tokenizer for architecture
2. **Pipelines**: Simple high-level API for common tasks
3. **Pretrained Models**: Easy access to thousands of models
4. **Consistent Interface**: Same API across different models

---

## Running Inference with Transformers

### Method 1: Pipeline API (Easiest)

```python
from transformers import pipeline

# Text generation
generator = pipeline("text-generation", model="gpt2")
result = generator(
    "Once upon a time",
    max_length=50,
    num_return_sequences=1
)
print(result[0]["generated_text"])

# Sentiment analysis
classifier = pipeline("sentiment-analysis")
result = classifier("I love this product!")
print(result)  # [{'label': 'POSITIVE', 'score': 0.9998}]

# Question answering
qa = pipeline("question-answering")
context = "Paris is the capital of France. It has a population of 2.2 million."
question = "What is the capital of France?"
result = qa(question=question, context=context)
print(result)  # {'answer': 'Paris', 'score': 0.98}

# Text summarization
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
article = "Very long article text here..."
summary = summarizer(article, max_length=130, min_length=30)
print(summary[0]["summary_text"])
```

### Method 2: Manual Model Loading (More Control)

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load model and tokenizer
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Move to GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# Tokenize input
prompt = "The future of AI is"
inputs = tokenizer(prompt, return_tensors="pt").to(device)

# Generate
with torch.no_grad():  # No gradient computation (inference only)
    outputs = model.generate(
        inputs["input_ids"],
        max_length=50,
        num_return_sequences=1,
        temperature=0.7,  # Randomness (0=deterministic, 1=very random)
        top_p=0.9,        # Nucleus sampling
        do_sample=True    # Enable sampling
    )

# Decode output
generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(generated_text)
```

### Understanding Generation Parameters

```python
# Temperature (controls randomness)
# Low (0.1-0.5): More focused, deterministic
# Medium (0.7-0.9): Balanced creativity
# High (1.0-2.0): More random, creative

# Top-p (nucleus sampling)
# Keep tokens with cumulative probability p
# 0.9 = keep top 90% probable tokens

# Top-k
# Keep only k most likely tokens at each step
# Lower k = more focused, Higher k = more diverse

outputs = model.generate(
    input_ids,
    max_length=100,
    temperature=0.8,      # Moderate randomness
    top_p=0.9,           # Nucleus sampling
    top_k=50,            # Consider top 50 tokens
    num_beams=5,         # Beam search (better quality)
    no_repeat_ngram_size=2,  # Avoid repetition
    early_stopping=True  # Stop when all beams finish
)
```

### Example: Building a Simple Chatbot

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class SimpleChatbot:
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.chat_history_ids = None

        # Set padding token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)

    def chat(self, user_input: str) -> str:
        """Send message and get response."""
        # Encode user input
        new_input_ids = self.tokenizer.encode(
            user_input + self.tokenizer.eos_token,
            return_tensors="pt"
        ).to(self.device)

        # Append to chat history
        if self.chat_history_ids is not None:
            bot_input_ids = torch.cat([self.chat_history_ids, new_input_ids], dim=-1)
        else:
            bot_input_ids = new_input_ids

        # Generate response
        with torch.no_grad():
            self.chat_history_ids = self.model.generate(
                bot_input_ids,
                max_length=1000,
                pad_token_id=self.tokenizer.eos_token_id,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )

        # Decode response (only new tokens)
        response = self.tokenizer.decode(
            self.chat_history_ids[:, bot_input_ids.shape[-1]:][0],
            skip_special_tokens=True
        )

        return response

    def reset(self):
        """Clear chat history."""
        self.chat_history_ids = None

# Usage
bot = SimpleChatbot()

print("User: Hello!")
print(f"Bot: {bot.chat('Hello!')}")

print("\nUser: How are you?")
print(f"Bot: {bot.chat('How are you?')}")

print("\nUser: What's the weather like?")
print(f"Bot: {bot.chat('What\\'s the weather like?')}")

# Reset conversation
bot.reset()
```

---

## Tokenization and Text Processing

### What Is Tokenization?

**Tokenization** converts text into numerical IDs that models can process.

```python
Text: "Hello, world!"
   ↓ Tokenization
Tokens: ["Hello", ",", "world", "!"]
   ↓ Encoding
Token IDs: [15496, 11, 995, 0]
```

### Tokenization Strategies

#### 1. Word-Level Tokenization
```python
# Split by spaces
"I love machine learning" → ["I", "love", "machine", "learning"]

# Problems:
# - Large vocabulary
# - Can't handle unknown words (OOV)
# - Languages without spaces?
```

#### 2. Character-Level Tokenization
```python
"AI" → ["A", "I"]

# Problems:
# - Very long sequences
# - Lose semantic meaning
```

#### 3. Subword Tokenization (Modern Approach)
```python
"unhappiness" → ["un", "happiness"]
"GPT" → ["G", "PT"] or ["GPT"]

# Benefits:
# - Fixed vocabulary size
# - Handle rare/unknown words
# - Capture morphology (un-, -ing, -ed)
```

### Common Tokenization Algorithms

#### BPE (Byte Pair Encoding) - Used by GPT
```python
from transformers import GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
text = "I love machine learning!"

# Tokenize
tokens = tokenizer.tokenize(text)
print(tokens)
# ['I', 'Ġlove', 'Ġmachine', 'Ġlearning', '!']
# Note: Ġ = space prefix

# Get token IDs
token_ids = tokenizer.encode(text)
print(token_ids)
# [40, 1842, 4572, 4673, 0]

# Decode back
decoded = tokenizer.decode(token_ids)
print(decoded)
# "I love machine learning!"
```

#### WordPiece - Used by BERT
```python
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
text = "I love machine learning!"

tokens = tokenizer.tokenize(text)
print(tokens)
# ['i', 'love', 'machine', 'learning', '!']

# BERT adds special tokens
encoded = tokenizer.encode(text)
print(encoded)
# [101, 1045, 2293, 3698, 4083, 999, 102]
# 101 = [CLS] (classification token)
# 102 = [SEP] (separator token)
```

### Tokenization Best Practices

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Always use return_tensors for model input
inputs = tokenizer(
    "Hello, how are you?",
    return_tensors="pt",  # Return PyTorch tensors
    padding=True,         # Pad to longest sequence
    truncation=True,      # Truncate if too long
    max_length=512        # Maximum sequence length
)

print(inputs.keys())
# dict_keys(['input_ids', 'attention_mask'])

# input_ids: Token IDs
# attention_mask: 1 for real tokens, 0 for padding

# Batch processing
texts = [
    "First sentence.",
    "Second sentence is longer.",
    "Third."
]

batch_inputs = tokenizer(
    texts,
    return_tensors="pt",
    padding=True,        # Pad all to same length
    truncation=True,
    max_length=512
)

print(batch_inputs["input_ids"].shape)
# torch.Size([3, max_length_in_batch])
```

### Special Tokens

```python
# Common special tokens
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

print(f"PAD token: {tokenizer.pad_token}")      # [PAD] - padding
print(f"UNK token: {tokenizer.unk_token}")      # [UNK] - unknown
print(f"CLS token: {tokenizer.cls_token}")      # [CLS] - classification
print(f"SEP token: {tokenizer.sep_token}")      # [SEP] - separator
print(f"MASK token: {tokenizer.mask_token}")    # [MASK] - for MLM

# Sentence pair example (for BERT)
text_a = "This is the first sentence."
text_b = "This is the second sentence."

# BERT format: [CLS] text_a [SEP] text_b [SEP]
encoded = tokenizer(
    text_a,
    text_b,
    return_tensors="pt",
    padding=True
)
```

---

## Prompt Engineering Basics

### What Is Prompt Engineering?

**Prompt engineering** is the art of crafting input text to get desired outputs from LLMs.

### Basic Prompting Strategies

#### 1. Zero-Shot Prompting
```python
# No examples provided
prompt = "Translate to French: Hello, how are you?"
# Model generates: "Bonjour, comment allez-vous ?"
```

#### 2. Few-Shot Prompting
```python
# Provide examples
prompt = """Translate to French:
English: Hello
French: Bonjour

English: Goodbye
French: Au revoir

English: Thank you
French: Merci

English: How are you?
French:"""
# Model generates: "Comment allez-vous ?"
```

#### 3. Chain-of-Thought Prompting
```python
# Encourage step-by-step reasoning
prompt = """Q: A store has 15 apples. They sell 7 and get 12 more. How many apples do they have?
A: Let's think step by step:
1. Start with 15 apples
2. Sell 7: 15 - 7 = 8 apples
3. Get 12 more: 8 + 12 = 20 apples
Answer: 20 apples

Q: A train travels 60 km in 30 minutes. How fast is it going in km/h?
A: Let's think step by step:"""
# Model generates step-by-step solution
```

### Prompt Templates for Common Tasks

```python
# Classification
def create_classification_prompt(text: str, labels: list) -> str:
    return f"""Classify the following text into one of these categories: {', '.join(labels)}

Text: {text}

Category:"""

# Summarization
def create_summary_prompt(text: str, max_words: int = 50) -> str:
    return f"""Summarize the following text in {max_words} words or less:

{text}

Summary:"""

# Question Answering
def create_qa_prompt(context: str, question: str) -> str:
    return f"""Answer the question based on the context below.

Context: {context}

Question: {question}

Answer:"""

# Code generation
def create_code_prompt(task: str, language: str = "Python") -> str:
    return f"""Write a {language} function that {task}.

Include:
- Function signature with type hints
- Docstring
- Error handling
- Example usage

Code:"""
```

### Prompt Engineering Tips

```python
# 1. Be specific and clear
# ❌ Bad: "Tell me about dogs"
# ✅ Good: "List 5 popular dog breeds suitable for families with children, including size and temperament"

# 2. Use formatting
prompt = """Task: Extract key information from the text below.

Text: John Doe, 30 years old, software engineer at TechCorp, email: john@techcorp.com

Extract in JSON format:
{
  "name": "...",
  "age": ...,
  "occupation": "...",
  "company": "...",
  "email": "..."
}

Output:"""

# 3. Constrain output format
prompt = "List 3 benefits of exercise. Format: 1. ... 2. ... 3. ..."

# 4. Provide context and role
prompt = """You are an expert ML infrastructure engineer.
Explain the difference between batch and online inference to a junior engineer in 2-3 sentences.

Explanation:"""

# 5. Handle edge cases
prompt = """Sentiment analysis. Classify as POSITIVE, NEGATIVE, or NEUTRAL.

Text: "{user_input}"

If the text is empty or unclear, respond with "NEUTRAL".

Sentiment:"""
```

---

## Building LLM APIs

### Simple FastAPI LLM Server

```python
# llm_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import uvicorn

app = FastAPI(title="LLM API Server")

# Load model at startup
generator = None

@app.on_event("startup")
async def load_model():
    """Load model when server starts."""
    global generator
    print("Loading model...")
    generator = pipeline(
        "text-generation",
        model="gpt2",
        device=0 if torch.cuda.is_available() else -1  # GPU if available
    )
    print("Model loaded successfully!")

# Request model
class GenerationRequest(BaseModel):
    prompt: str
    max_length: int = 50
    temperature: float = 0.7
    top_p: float = 0.9
    num_return_sequences: int = 1

# Response model
class GenerationResponse(BaseModel):
    generated_text: str
    prompt: str

@app.post("/generate", response_model=GenerationResponse)
async def generate_text(request: GenerationRequest):
    """Generate text from prompt."""
    if generator is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        result = generator(
            request.prompt,
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p,
            num_return_sequences=request.num_return_sequences,
            do_sample=True
        )

        return GenerationResponse(
            generated_text=result[0]["generated_text"],
            prompt=request.prompt
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": generator is not None
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Client Usage

```python
import requests

# Generate text
response = requests.post(
    "http://localhost:8000/generate",
    json={
        "prompt": "The future of AI is",
        "max_length": 100,
        "temperature": 0.8
    }
)

result = response.json()
print(result["generated_text"])
```

### Production-Ready LLM API

```python
# production_llm_server.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import Optional, List
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Production LLM API")

# Global model instances
model = None
tokenizer = None

class Config:
    """Server configuration."""
    MODEL_NAME = "gpt2"
    MAX_LENGTH = 512
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    LOG_REQUESTS = True

@app.on_event("startup")
async def load_model():
    """Load model and tokenizer."""
    global model, tokenizer

    logger.info(f"Loading model: {Config.MODEL_NAME}")
    logger.info(f"Using device: {Config.DEVICE}")

    try:
        tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(Config.MODEL_NAME)
        model = model.to(Config.DEVICE)
        model.eval()  # Set to evaluation mode

        # Set padding token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        logger.info("Model loaded successfully")

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

class GenerationRequest(BaseModel):
    """Request model with validation."""
    prompt: str = Field(..., min_length=1, max_length=1000)
    max_length: int = Field(50, ge=10, le=512)
    temperature: float = Field(0.7, ge=0.1, le=2.0)
    top_p: float = Field(0.9, ge=0.0, le=1.0)
    top_k: int = Field(50, ge=0, le=100)
    num_return_sequences: int = Field(1, ge=1, le=5)

class GenerationResponse(BaseModel):
    """Response model."""
    generated_texts: List[str]
    prompt: str
    generation_time: float
    model_name: str

def log_request(request: GenerationRequest, response: GenerationResponse):
    """Log request details."""
    if Config.LOG_REQUESTS:
        logger.info(f"Prompt: {request.prompt[:50]}...")
        logger.info(f"Generated {len(response.generated_texts)} sequences in {response.generation_time:.3f}s")

@app.post("/generate", response_model=GenerationResponse)
async def generate_text(
    request: GenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate text with production-grade error handling."""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start_time = time.time()

    try:
        # Tokenize input
        inputs = tokenizer(
            request.prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=Config.MAX_LENGTH
        ).to(Config.DEVICE)

        # Generate
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_length=request.max_length,
                temperature=request.temperature,
                top_p=request.top_p,
                top_k=request.top_k,
                num_return_sequences=request.num_return_sequences,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        # Decode outputs
        generated_texts = [
            tokenizer.decode(output, skip_special_tokens=True)
            for output in outputs
        ]

        generation_time = time.time() - start_time

        response = GenerationResponse(
            generated_texts=generated_texts,
            prompt=request.prompt,
            generation_time=generation_time,
            model_name=Config.MODEL_NAME
        )

        # Log in background
        background_tasks.add_task(log_request, request, response)

        return response

    except torch.cuda.OutOfMemoryError:
        raise HTTPException(
            status_code=507,
            detail="GPU out of memory. Try shorter prompt or lower max_length"
        )
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check with model info."""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model": Config.MODEL_NAME,
        "device": Config.DEVICE,
        "gpu_available": torch.cuda.is_available()
    }

@app.get("/metrics")
async def get_metrics():
    """Get GPU memory usage."""
    metrics = {"model_name": Config.MODEL_NAME}

    if torch.cuda.is_available():
        metrics["gpu_memory_allocated_mb"] = torch.cuda.memory_allocated() / 1024**2
        metrics["gpu_memory_reserved_mb"] = torch.cuda.memory_reserved() / 1024**2

    return metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Infrastructure Considerations

### 1. Model Size and Storage

```python
# Check model size
import os
from transformers import AutoModel

def get_model_size(model_name: str) -> dict:
    """Get model size information."""
    from transformers import AutoConfig

    config = AutoConfig.from_pretrained(model_name)

    # Estimate size (parameters * 4 bytes for FP32)
    params = config.num_parameters if hasattr(config, 'num_parameters') else None

    if params:
        size_fp32_gb = (params * 4) / (1024**3)
        size_fp16_gb = (params * 2) / (1024**3)
        size_int8_gb = params / (1024**3)

        return {
            "parameters": f"{params/1e6:.1f}M" if params < 1e9 else f"{params/1e9:.1f}B",
            "size_fp32_gb": round(size_fp32_gb, 2),
            "size_fp16_gb": round(size_fp16_gb, 2),
            "size_int8_gb": round(size_int8_gb, 2)
        }

    return {"error": "Could not determine model size"}

# Examples
print(get_model_size("gpt2"))  # 117M params, ~0.5GB
print(get_model_size("gpt2-large"))  # 774M params, ~3GB
print(get_model_size("meta-llama/Llama-2-7b-hf"))  # 7B params, ~28GB
```

### 2. GPU Memory Management

```python
import torch

def check_gpu_memory():
    """Check GPU memory availability."""
    if not torch.cuda.is_available():
        return {"gpu_available": False}

    return {
        "gpu_available": True,
        "gpu_count": torch.cuda.device_count(),
        "current_device": torch.cuda.current_device(),
        "device_name": torch.cuda.get_device_name(0),
        "memory_allocated_gb": torch.cuda.memory_allocated() / 1024**3,
        "memory_reserved_gb": torch.cuda.memory_reserved() / 1024**3,
        "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3
    }

# Clear GPU memory
def clear_gpu_memory():
    """Free GPU memory."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
```

### 3. Batching for Throughput

```python
from typing import List

def batch_generate(
    prompts: List[str],
    model,
    tokenizer,
    batch_size: int = 4
) -> List[str]:
    """Generate text for multiple prompts efficiently."""
    results = []

    for i in range(0, len(prompts), batch_size):
        batch_prompts = prompts[i:i + batch_size]

        # Tokenize batch
        inputs = tokenizer(
            batch_prompts,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(model.device)

        # Generate batch
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_length=50,
                pad_token_id=tokenizer.eos_token_id
            )

        # Decode batch
        batch_results = [
            tokenizer.decode(output, skip_special_tokens=True)
            for output in outputs
        ]

        results.extend(batch_results)

    return results
```

### 4. Model Quantization (Reduce Size)

```python
# Load quantized model (8-bit)
from transformers import AutoModelForCausalLM

# Standard loading (FP32/FP16)
model = AutoModelForCausalLM.from_pretrained("gpt2")  # ~500MB

# 8-bit quantization (requires bitsandbytes)
model_8bit = AutoModelForCausalLM.from_pretrained(
    "gpt2",
    load_in_8bit=True,  # Load with 8-bit quantization
    device_map="auto"   # Automatically distribute across GPUs
)
# ~125MB, 4x smaller!

# 4-bit quantization (even smaller)
model_4bit = AutoModelForCausalLM.from_pretrained(
    "gpt2",
    load_in_4bit=True,
    device_map="auto"
)
# ~62MB, 8x smaller!
```

### 5. Caching for Performance

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_generate(prompt: str, max_length: int) -> str:
    """Cache common prompts."""
    # Only works if prompt and params are identical
    return generate_text(prompt, max_length)
```

---

## Summary and Best Practices

### Key Takeaways

1. **Transformers** use attention mechanisms to process sequences
2. **LLMs** come in three main types: encoder-only (BERT), decoder-only (GPT), encoder-decoder (T5)
3. **Hugging Face** provides easy access to 200,000+ pretrained models
4. **Tokenization** converts text to numbers; use proper padding and truncation
5. **Prompt engineering** is critical for getting good outputs from LLMs
6. **Infrastructure** challenges include model size, GPU memory, and latency

### Best Practices for LLM Infrastructure

```python
# 1. Always check GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# 2. Use appropriate data types
model = model.half()  # FP16 for faster inference

# 3. Batch requests when possible
results = batch_generate(prompts, model, tokenizer, batch_size=8)

# 4. Clear GPU memory periodically
torch.cuda.empty_cache()

# 5. Add proper error handling
try:
    result = model.generate(inputs)
except torch.cuda.OutOfMemoryError:
    logger.error("GPU OOM - reduce batch size or max_length")
    # Fallback strategy

# 6. Monitor metrics
logger.info(f"GPU memory: {torch.cuda.memory_allocated() / 1024**2:.2f}MB")

# 7. Use caching for common requests
@lru_cache(maxsize=100)
def cached_inference(prompt: str):
    return model.generate(tokenizer(prompt, return_tensors="pt"))

# 8. Implement rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/generate")
@limiter.limit("10/minute")
async def generate(request: GenerationRequest):
    pass
```

### Resource Requirements Cheat Sheet

| Model Size | Parameters | Storage (FP16) | GPU Memory | Use Case |
|-----------|-----------|----------------|------------|----------|
| Small | < 500M | < 1GB | 2-4GB | Development, testing |
| Medium | 500M-3B | 1-6GB | 6-12GB | Production (simple tasks) |
| Large | 3B-13B | 6-26GB | 16-32GB | Production (complex tasks) |
| X-Large | 13B-70B | 26-140GB | 40-80GB+ | Specialized/research |

### Next Steps

You now understand LLM basics! Practice by:
1. Loading different models from Hugging Face
2. Experimenting with generation parameters
3. Building simple LLM-powered APIs
4. Optimizing inference performance

Continue to **Exercise 04: LLM Basics** to build your first LLM application!

---

**Word Count**: ~5,800 words
**Estimated Reading Time**: 30-35 minutes
