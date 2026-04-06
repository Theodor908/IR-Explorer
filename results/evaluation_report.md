# Evaluation Report

### Baseline

| Query | P@5 | P@10 | AP | Retrieved | Relevant |
|-------|-----|------|----|-----------|----------|
| q1: neural network deep learning backpropaga | 0.800 | 0.700 | 0.862 | 25 | 8 |
| q2: transformer self-attention mechanism enc | 0.800 | 0.400 | 1.000 | 27 | 4 |
| q3: language model pre-training fine-tuning  | 0.800 | 0.700 | 0.924 | 33 | 7 |
| q4: quantum mechanics measurement observatio | 0.800 | 0.500 | 0.967 | 18 | 5 |
| q5: DNA molecular structure double helix nuc | 0.800 | 0.500 | 0.943 | 26 | 5 |
| q6: natural selection evolution adaptation s | 0.800 | 0.400 | 0.709 | 36 | 6 |
| q7: global warming climate change temperatur | 1.000 | 0.600 | 0.976 | 29 | 6 |
| q8: carbon dioxide atmosphere concentration  | 0.600 | 0.500 | 0.651 | 14 | 7 |
| q9: information entropy channel capacity cod | 0.800 | 0.500 | 0.856 | 21 | 6 |
| q10: computing machine intelligence imitation | 1.000 | 0.600 | 0.976 | 23 | 6 |
| q11: relativity time space light electrodynam | 0.800 | 0.600 | 0.672 | 52 | 6 |
| q12: probability uncertainty determinism bran | 0.200 | 0.200 | 0.267 | 21 | 5 |

**MAP = 0.8168**

### +Stopwords

| Query | P@5 | P@10 | AP | Retrieved | Relevant |
|-------|-----|------|----|-----------|----------|
| q1: neural network deep learning backpropaga | 1.000 | 0.600 | 0.885 | 25 | 8 |
| q2: transformer self-attention mechanism enc | 0.600 | 0.400 | 0.875 | 27 | 4 |
| q3: language model pre-training fine-tuning  | 1.000 | 0.700 | 0.957 | 33 | 7 |
| q4: quantum mechanics measurement observatio | 0.800 | 0.500 | 0.967 | 18 | 5 |
| q5: DNA molecular structure double helix nuc | 0.800 | 0.500 | 0.943 | 26 | 5 |
| q6: natural selection evolution adaptation s | 0.800 | 0.400 | 0.612 | 36 | 6 |
| q7: global warming climate change temperatur | 1.000 | 0.600 | 1.000 | 29 | 6 |
| q8: carbon dioxide atmosphere concentration  | 0.800 | 0.600 | 0.731 | 14 | 7 |
| q9: information entropy channel capacity cod | 1.000 | 0.500 | 0.883 | 21 | 6 |
| q10: computing machine intelligence imitation | 1.000 | 0.500 | 0.910 | 23 | 6 |
| q11: relativity time space light electrodynam | 0.800 | 0.600 | 0.883 | 52 | 6 |
| q12: probability uncertainty determinism bran | 0.200 | 0.200 | 0.267 | 21 | 5 |

**MAP = 0.8261**

### +Stemming

| Query | P@5 | P@10 | AP | Retrieved | Relevant |
|-------|-----|------|----|-----------|----------|
| q1: neural network deep learning backpropaga | 1.000 | 0.600 | 0.876 | 29 | 8 |
| q2: transformer self-attention mechanism enc | 0.600 | 0.400 | 0.893 | 36 | 4 |
| q3: language model pre-training fine-tuning  | 1.000 | 0.700 | 1.000 | 34 | 7 |
| q4: quantum mechanics measurement observatio | 0.800 | 0.500 | 0.967 | 32 | 5 |
| q5: DNA molecular structure double helix nuc | 0.800 | 0.500 | 0.943 | 27 | 5 |
| q6: natural selection evolution adaptation s | 0.800 | 0.400 | 0.742 | 42 | 6 |
| q7: global warming climate change temperatur | 0.800 | 0.600 | 0.948 | 31 | 6 |
| q8: carbon dioxide atmosphere concentration  | 0.800 | 0.600 | 0.748 | 18 | 7 |
| q9: information entropy channel capacity cod | 0.800 | 0.500 | 0.851 | 23 | 6 |
| q10: computing machine intelligence imitation | 1.000 | 0.600 | 0.976 | 27 | 6 |
| q11: relativity time space light electrodynam | 0.800 | 0.500 | 0.896 | 53 | 6 |
| q12: probability uncertainty determinism bran | 0.200 | 0.200 | 0.250 | 22 | 5 |

**MAP = 0.8408**

### Full

| Query | P@5 | P@10 | AP | Retrieved | Relevant |
|-------|-----|------|----|-----------|----------|
| q1: neural network deep learning backpropaga | 1.000 | 0.600 | 0.858 | 29 | 8 |
| q2: transformer self-attention mechanism enc | 0.600 | 0.400 | 0.893 | 36 | 4 |
| q3: language model pre-training fine-tuning  | 1.000 | 0.700 | 1.000 | 34 | 7 |
| q4: quantum mechanics measurement observatio | 0.800 | 0.500 | 0.967 | 32 | 5 |
| q5: DNA molecular structure double helix nuc | 0.800 | 0.500 | 0.943 | 27 | 5 |
| q6: natural selection evolution adaptation s | 0.800 | 0.400 | 0.726 | 42 | 6 |
| q7: global warming climate change temperatur | 0.800 | 0.600 | 0.873 | 31 | 6 |
| q8: carbon dioxide atmosphere concentration  | 0.800 | 0.600 | 0.748 | 18 | 7 |
| q9: information entropy channel capacity cod | 1.000 | 0.500 | 0.879 | 23 | 6 |
| q10: computing machine intelligence imitation | 1.000 | 0.600 | 0.976 | 27 | 6 |
| q11: relativity time space light electrodynam | 0.800 | 0.600 | 0.897 | 53 | 6 |
| q12: probability uncertainty determinism bran | 0.200 | 0.200 | 0.250 | 22 | 5 |

**MAP = 0.8341**

## MAP Comparison

| Configuration | MAP |
|---------------|-----|
| Baseline | 0.8168 |
| +Stopwords | 0.8261 |
| +Stemming | 0.8408 |
| Full | 0.8341 |
