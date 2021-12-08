# -*- coding: utf-8 -*-
"""Jiant Edge Probing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CNQnwCEpkDY9y2-CAWfQhINEsciI1qhp

# CS236 Final Project

# Do Generative Transformers Read Like Bidirectional Models (BERT)?

Last edit: 12-7-2021

By: Amil Merchant

This notebook is used to re-produce main results for the paper, specifically those regarding edge probing. Additional functionality can be obtained by modifying the Jiant files, but be careful as progress is lost once a session is deleted on Colab.

Notes:
- This notebook is written and tested for GPU runtime on colab. An equivalent setup for Jupyter notebook and local evaluation could be created based on these schemas.
- Based on the example notebook from Jiant NLP.

## Install necessary libraries
"""

# Please relaunch the runtime once the installation completes
!rm jiant -r
!git clone --branch mybranch https://github.com/amil5/jiant.git
!cd jiant && pip install -r requirements.txt
!pip install allennlp==0.8.4
!pip install --upgrade google-cloud-storage

import os
import sys
sys.path.insert(0, "/content/jiant")

# Import the installed Jiant library
import jiant.proj.main.tokenize_and_cache as tokenize_and_cache
import jiant.proj.main.export_model as export_model
import jiant.proj.main.scripts.configurator as configurator
import jiant.proj.main.runscript as main_runscript
import jiant.shared.caching as caching
import jiant.utils.python.io as py_io
import jiant.utils.display as display
import json

model_name = 'bert-base-cased' #@param ['bert-base-cased', 'gpt2']

# Example data provide to examine the structure of the input:
# Recreated from https://github.com/nyu-mll/jiant/blob/master/examples/notebooks/jiant_EdgeProbing_Example.ipynb

# example = {
#   "text": "The current view is that the chronic inflammation in the distal part of the stomach caused by Helicobacter pylori infection results in an increased acid production from the non-infected upper corpus region of the stomach.",
#   "info": {"id": 7},
#   "targets": [
#     {
#       "label": "Cause-Effect(e2,e1)",
#       "span1": [7,8],
#       "span2": [19, 20],
#       "info": {"comment": ""}
#     }
#   ]
# }
# # Simulate a training set of 1000 examples
# train_data = [example] * 1000
# # Simulate a validation set of 100 examples
# val_data = [example] * 100

# py_io.write_jsonl(
#     data=train_data,
#     path="/content/jiant/content/tasks/data/semeval/train.all.json",
# )
# py_io.write_jsonl(
#     data=val_data,
#     path="/content/jiant/content/tasks/data/semeval/val.jsonl",
# )

"""## Utility for uploading files to colab.

Please ensure that data files have either been placed in the appropriate locations or upload via this utility. 

This code path will block until an upload; please comment out if you are uploading data in any other way.
"""

# from google.colab import files
# uploaded = files.upload()
# for fn in uploaded.keys():
#   print('User uploaded file "{name}" with length {length} bytes'.format(
#       name=fn, length=len(uploaded[fn])))

"""## Configure data paths"""

os.makedirs("/content/tasks/configs/", exist_ok=True)
os.makedirs("/content/tasks/data/semeval", exist_ok=True)
os.makedirs("/content/tasks/data/dep", exist_ok=True)

"""## Ensure that the path to the Relations data is correct"""

# Configure the Semeval-2010 Relations Classification Task-8
py_io.write_json({
  "task": "semeval",
  "paths": {
    "train": "/content/jiant/content/tasks/data/semeval/train.all.json",
    "val": "/content/jiant/content/tasks/data/semeval/test.json",
  },
  "name": "semeval"
}, "/content/tasks/configs/semeval_config.json")

# Recreate the smaller version of the test set used in our experiments
# This is currently commented out as we provide the smaller version in the Github repository
# but note that it can be easily re-created
# !head -250 en_ewt-ud-test.json > en_ewt-ud-test-small.json

"""## Ensure that the path to the Dependencies data is correct"""

# Due to training limitations, we use the dev set for training and the smaller 
# test set for evaluation
py_io.write_json({
  "task": "dep",
  "paths": {
    "train": "/content/en_ewt-ud-dev.json",
    "val": "/content/en_ewt-ud-test-small.json",
  },
  "name": "dep"
}, "/content/tasks/configs/dep_config.json")

# Download the desired model (i.e. BERT or GPT-2)
export_model.export_model(
    hf_pretrained_model_name_or_path=f"{model_name}",
    output_base_path=f"./models/{model_name}",
)

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# 
# # For a given task, tokenize and cache the required data
# # This ensures that the text does not need to repeatedly be processed upon input
# task_name = "semeval"
# tokenize_and_cache.main(tokenize_and_cache.RunConfiguration(
#     task_config_path=f"./tasks/configs/{task_name}_config.json",
#     hf_pretrained_model_name_or_path=f"{model_name}",
#     output_dir=f"./cache/{task_name}",
#     phases=["train", "val"],
# ))

# Examine a row of the input
row = caching.ChunkedFilesDataCache(f"./cache/{task_name}/train").load_chunk(0)[0]["data_row"]
print(row.input_ids)
print(row.tokens)
print(row.tokens[row.spans[0][0]: row.spans[0][1]+1])
print(row.tokens[row.spans[1][0]: row.spans[1][1]+1])

# Configuration for the edge probing run
jiant_run_config = configurator.SimpleAPIMultiTaskConfigurator(
    task_config_base_path="./tasks/configs",
    task_cache_base_path="./cache",
    train_task_name_list=[task_name],
    val_task_name_list=[task_name],
    train_batch_size=8,
    eval_batch_size=16,
    epochs=3,
    num_gpus=1,
).create_config()
os.makedirs("./run_configs/", exist_ok=True)
py_io.write_json(jiant_run_config, f"./run_configs/{task_name}_run_config.json")
display.show_json(jiant_run_config)

# Run the edge probe
run_args = main_runscript.RunConfiguration(
    jiant_task_container_config_path=f"./run_configs/{task_name}_run_config.json",
    output_dir=f"./runs/{task_name}",
    hf_pretrained_model_name_or_path=f"{model_name}",
    model_path=f"./models/{model_name}/model/model.p",
    model_config_path=f"./models/{model_name}/model/config.json",
    learning_rate=1e-4,
    eval_every_steps=500,
    do_train=True,
    do_val=True,
    do_save=True,
    force_overwrite=True,
)
main_runscript.run_loop(run_args)