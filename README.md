# Do Generative Transformers Read Like Bidirectional Models
## An Empirical Analysis of Representations

By: Amil Merchant
Date: 12-7-2021

This repository contains the notebooks and data used for Amil Merchant's final project for CS236: Deep Generative Models in Autumn 2021.

### Abstract: 

While many recent papers have studied how linguistic information is embedded in large-scale encoder-only language models such as BERT, relatively little is understood about their generative counterparts. Despite the modelling similarities with Transformer layers, the causal attention structure and disparate objectives may yield fundamentally different representations of language. In this paper, using a suite of analysis techniques (Representational Similarity Analysis, probing classifiers, and attention analysis) we investigate how representations develop in and the linguistic capabilities of the popular GPT-2 generative model. While similarities arise in how layers update representations in comparison to encoder-only models like BERT, the differences when measuring linguistic understanding and attention weights suggest that generative models are too narrowly focused on the next word to create a complete understanding of the entire input.

### File System

As the code mainly originates from colab notebooks; there is little need for a complex file-system and dependencies. Rather we use a simple organization schema to separate the major components:

- Notebooks: contains the notebooks used to create all figures and obtain the corresponding results
- Data: contains the data used for this project in case any experiments need to be replicated
- Paper: contains a draft version of the final paper
- Poster: contains a draft version of the final poster

### Until this project is finalized, please see the draft paper for a summary of results; feel free to reach out to me with any questions or concerns.
