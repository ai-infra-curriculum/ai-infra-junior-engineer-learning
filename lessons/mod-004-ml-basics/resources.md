# Module 004 — ML Basics Resources

## Foundational books

- **Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow (3rd ed.)** by Aurélien Géron. The most-recommended starting point for practitioners. Covers classical ML through deep learning with worked code.
- **Pattern Recognition and Machine Learning** by Christopher Bishop. The math-heavier classic. Read for the theory after you've shipped a few models.
- **The Hundred-Page Machine Learning Book** by Andriy Burkov. What it says on the tin. Good for orientation.
- **Designing Machine Learning Systems** by Chip Huyen. ML systems engineering rather than algorithms; foundational for AI infrastructure roles.

## Online courses

- **Andrew Ng's Machine Learning Specialization** (Coursera). The most-watched ML course in history. Updated 2022 to use Python (was Octave). The right place to start.
- **Fast.ai Practical Deep Learning for Coders** — [course.fast.ai](https://course.fast.ai/). Top-down approach; build first, theorize later. Good complement to Ng.
- **MIT 6.036 Introduction to Machine Learning** — free on OCW. More rigorous.
- **Hugging Face NLP Course** — [huggingface.co/learn/nlp-course](https://huggingface.co/learn/nlp-course). Free, modern, hands-on with transformers.

## Libraries to know

- **scikit-learn** — [scikit-learn.org](https://scikit-learn.org/). The canonical classical-ML library. Read the documentation; it's a teaching reference too.
- **PyTorch** — [pytorch.org/tutorials](https://pytorch.org/tutorials/). The dominant deep-learning framework in research and increasingly in production.
- **TensorFlow / Keras** — [tensorflow.org/tutorials](https://www.tensorflow.org/tutorials). Still common, especially in mobile/edge deployments.
- **Hugging Face Transformers** — [huggingface.co/docs/transformers](https://huggingface.co/docs/transformers/). Pretrained models for NLP/CV/audio.

## ML systems references

- **Rules of Machine Learning** by Google — [developers.google.com/machine-learning/guides/rules-of-ml](https://developers.google.com/machine-learning/guides/rules-of-ml). 43 short rules. Required reading.
- **Hidden Technical Debt in Machine Learning Systems** (Sculley et al., NeurIPS 2015) — [papers.nips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf](https://papers.nips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf). The original "ML is 5% ML and 95% glue code" paper.
- **Reliable Machine Learning** (Chen et al., O'Reilly) — SRE patterns applied to ML.

## Practice + datasets

- **Kaggle** — [kaggle.com](https://www.kaggle.com/). Competitions, datasets, kernels. The standard first-mile practice ground.
- **Papers with Code** — [paperswithcode.com](https://paperswithcode.com/). Papers paired with implementations and benchmarks.
- **UCI ML Repository** — [archive.ics.uci.edu/ml](https://archive.ics.uci.edu/ml/). Classic small datasets, good for learning.

## Communities

- **r/MachineLearning** — research-leaning subreddit. Useful for keeping up with new papers.
- **Towards Data Science** — Medium publication. Quality is mixed; the best posts are excellent.
- **The Gradient** — [thegradient.pub](https://thegradient.pub/). Long-form ML thought.

## Cross-references in this curriculum

- Module 001 (Python) — the language ML runs on.
- Module 005 (Docker) — packaging ML models.
- Module 007 (APIs) — serving ML models.
- Engineer track's `mod-105` (data pipelines) and `mod-106` (MLOps) — the production-ML layer.

## A note on ML "fundamentals" vs. AI infrastructure

This module covers ML fundamentals because AI infrastructure
engineers need to read ML code, understand model lifecycles, and
talk to ML engineers fluently. The career trajectory of this
track focuses on the *infrastructure* layer (serving, training,
data, observability), not on becoming an ML researcher. Use these
resources to develop fluency, not depth.
