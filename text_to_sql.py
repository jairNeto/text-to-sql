# import os
# import torch
# from io import BytesIO
# import base64
# from transformers import LlamaForCausalLM, LlamaTokenizer
# import sentencepiece


from beam import App, Runtime, Image, Volume, VolumeType
import re
import torch
from transformers import (AutoModelForCausalLM,
                          AutoTokenizer,
                          )
from typing import Tuple
from datasets import DatasetDict

# The environment your code will run on
app = App(
    name="TextToSQL",
    runtime=Runtime(
        cpu=8,
        memory="32Gi",
        gpu="A10G",
        image=Image(
            python_version="python3.10",
            python_packages=[
                "accelerate=0.21.0",
                "transformers=4.31.0",
                "torch=2.1.0,",
                "sentencepiece",
                "xformers",
                "protobuf",
                "bitsandbytes"
            ],
        ),
    ),
    volumes=[
        Volume(
            name="model_weights",
            path="./model_weights",
            volume_type=VolumeType.Persistent,
        )
    ],
)
# Cached model
cache_path = "./model_weights"
# Huggingface model
model_name = 'Jairnetojp/sql-classification-llama-2-7b'
def load_models():
    torch.set_default_device('cuda')
    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, torch_dtype="auto", cache_dir=cache_path)
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, torch_dtype="auto", cache_dir=cache_path)
    
    return tokenizer, model

@app.rest_api(loader=load_models)
def generate(**inputs):
    # Retrieve cached model from the loader
    tokenizer, model = inputs["context"]
    question = inputs["question"]
    context = inputs["context"]

    sql = print_inference(model, tokenizer, question, context)
    
    return {"sql": sql}

def print_extracted_answer(raw_answer: str) -> None:
    """
    Print the extracted answer from the model.
    If the model does not extract the answer, print the raw_answer.

    Args:
        raw_answer (str): The raw answer from the model.
    """
    pattern = r'### Response:\s*([\S\s]*?)\s*### End:*'

    # Use re.search to find the match
    match = re.search(pattern, raw_answer)

    # Check if a match was found
    if match:
        # Extract the desired text (group 1 in the match object)
        extracted_text = match.group(1).strip()  # Remove leading/trailing white spaces
        print(f'Model Answer: {extracted_text}')
    else:
        print("No match found.")
        print(raw_answer)


def get_context_question_answer_from_index(valid_ds: DatasetDict, index: int) -> Tuple[str, str, str]:
    """
    Get the context, question, and answer from the dataset.

    Args:
        valid_ds (DatasetDict): The validation dataset.
        index (int): The index of the dataset.

    Returns:
        Tuple[str, str, str]: The context, question, and answer.
    """
    question = valid_ds[index]['question']
    context = valid_ds[index]['context']
    answer = valid_ds[index]['answer']

    return context, question, answer


def print_inference(model: AutoModelForCausalLM, tokenizer: AutoTokenizer, question: str, context: str) -> None:
    """
    Print the inference from the model.

    Args:
        model (AutoModelForCausalLM): Fine-tuned model.
        tokenizer (AutoTokenizer): Tokenizer.
        question (str): The natural language question.
        context (str): The database schema.
        answer (str): The query answer.
    """

    print(f'question: {question}')
    print(f'context: {context}')

    message = f'''
    ### Instructions:
    Your task is to convert a question into a SQL query, given a Postgres database schema.
    Adhere to these rules:
    - **Deliberately go through the question and database schema word by word** to appropriately answer the question
    - **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
    - When creating a ratio, always cast the numerator as float

    ### Input:
    Generate a SQL query that answers the question `{question}`.
    This query will run on a database whose schema is represented in this string:
    {context}

    ### Response:
    '''
    inputs = tokenizer(message, return_tensors="pt", return_attention_mask=False)

    outputs = model.generate(**inputs, max_length=400)

    print_extracted_answer(tokenizer.batch_decode(outputs)[0])
