"""Run the prompt injection payload catalogue against a target model."""
import argparse
import os
import time

from injection_payloads import load_payloads
from evaluator import evaluate, summarize


def call_openai(model, system, user):
    import openai
    openai.api_key = os.environ['OPENAI_API_KEY']
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{'role': 'system', 'content': system},
                  {'role': 'user', 'content': user}],
        temperature=0.0,
    )
    return resp['choices'][0]['message']['content']


