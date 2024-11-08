from common import print_articles, print_key_points, print_str_list
import requests
import json

from default_processor import default_preprocessor, get_add_gpt_output_as_dict
from gpt import GPTList
from openai_api import parse_http_result_json
from utils import null_or_empty


def prompt_question_answer_extraction_0(doc_list, **kwargs):
    doc_list_str = print_articles(doc_list)

    prompt = f'Below are {len(doc_list)} news article:\n'
    prompt += f'{doc_list_str}\n'
    prompt += 'Please generate the outputs based on the following procedure step by step:\n'
    prompt += '1. Generate a question which can be best answered using the news articles above.\n'
    prompt += '2. Generate top level key points of the answer to the question based on the above news articles.\n'
    prompt += '3. For each top-level key point, generate some supporting key points if necessary.\n'
    prompt += '4. Please output with the following Json format {{"question": XXX, "answer_key_points": [{{"top_level_key_point": XXX, "supporting key_points": [YYY, ...]}}, ...]}}\n'
    prompt += 'Please output now:'
    return prompt


def prompt_question_answer_extraction_1(question, answer_key_points, **kwargs):
    answer_key_points_str = print_str_list(answer_key_points)
    prompt = 'Below is a question and key points of the answer:\n'
    prompt += f'question: {question}\n'
    prompt += f'Answer Key Points: {answer_key_points_str}\n'
    prompt += 'Please generate the outputs based on the following procedure step by step:\n'
    prompt += '1. Review each key point, and assign it a label (either top level key point or supporting key point).\n'
    prompt += '2. For top level key point, recognize the associated supporting key points.\n'
    prompt += '3. Please output with the following Json format {{"output": [{{"top_level_key_point": XXX, "supporting_key_points": [YYY, ...]}}]}}\n'
    prompt += 'Please output now:'
    return prompt


def prompt_question_answer_extraction_2(question, answer_key_points, **kwargs):
    answer_key_points_str = print_key_points(answer_key_points)
    prompt = 'Below is a question and key points of the answer:\n'
    prompt += f'question: {question}\n'
    prompt += f'Answer Key Points: {answer_key_points_str}\n'
    prompt += 'Please reorder the answer key points by considering their relevancy to the question and coherence of the answer:\n'
    prompt += 'Please output with the following Json format {{"output": [{{"top_level_key_point": XXX, "supporting_key_points": [YYY, ...]}}]}}\n'
    prompt += 'Please output now:'
    return prompt


def prompt_answer_key_point_extraction(question, answer):
    prompt = 'Below is a question and the corresponding answer:\n'
    prompt += f'Question: {question}\n'
    prompt += f'Answer: {answer}\n'
    prompt += 'Please extract key points from the answer, and output with the following Json format: {{"key_points": [XXX, YYY, ...]}}\n'
    prompt += 'Output now:'
    return prompt


def get_gpt(prompt_func, output_fields, **kwargs):

    config_question_answer_extraction = [
        {"system": "You are an NLP expert to analyze news article content.",
         "prompt": (prompt_func(**kwargs), output_fields),
         "k": 1,
         "cutoff": 110000,
         "print_out_prompt": True,
         "normalize_newline": True,
         "max_tokens": 4000,
         "temperature": 0.1,
         "model": "gpt-4",
         "response_format": {"type": "json_object"},
         "preprocessor": default_preprocessor,
         "postprocessor": get_add_gpt_output_as_dict([])}]
    return GPTList(config_question_answer_extraction)


def run_answer_key_point_extraction(question, answer):
    gpt = get_gpt(prompt_answer_key_point_extraction, ["key_points"], question=question, answer=answer)
    result = gpt.run({})
    if null_or_empty(result):
        return None
    key_points = result.get('key_points')
    if null_or_empty(key_points):
        return None
    return key_points


def run_gpt(doc_ids, input_fields, prompt_func, output_fields):
    doc_ids_converted = []
    for doc_id in doc_ids:
        try:
            int(doc_id)
            result = requests.get(f"https://tools.n.newsbreak.com/api/utils-docId-decode?id={doc_id}")
            status, output = parse_http_result_json(result)
            if status == 200:
                doc_id = output.get('docId')
        except:
            pass
        if doc_id is not None:
            doc_ids_converted.append(doc_id)

    if null_or_empty(doc_ids_converted) is None:
        return None
    docenter = get_docenter_document()
    other_features = {'date': None, 'url': None}
    doc_list = []
    for doc_id in doc_ids:
        title, content = get_content_from_document_id(docenter, doc_id, other_features=other_features)
        doc_list.append({'title': title, 'content': content, 'publication_date': other_features['date'],
                         'url': other_features['url']})
    if input_fields is None:
        input_fields = {}
    input_fields.update({'doc_list': doc_list})
    gpt = get_gpt(prompt_func, output_fields, **input_fields)
    result = gpt.run({})
    if null_or_empty(result):
        return None
    for key in output_fields:
        value = result.get(key)
        if null_or_empty(value):
            return None
    return result
