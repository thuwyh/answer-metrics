import json

from common import find_most_similar_substring
from default_processor import default_preprocessor, get_add_gpt_output_as_dict
from gpt import GPTList
from utils import null_or_empty


def prompt_claim_comparison(question, key_points_0, key_points_1, print_func):
    key_points_s_0 = print_func(key_points_0)
    key_points_s_1 = print_func(key_points_1)
    prompt = f"Here is the user's question: {question}\n"
    prompt += f"Below are claim set A. Each claim is relevant to answer the user's question:\n"
    prompt += f"{key_points_s_0}\n"
    prompt += f"Below are claim set B. Each claim is relevant to answer the user's question:\n"
    prompt += f"{key_points_s_1}\n"
    prompt += "Please follow the procedures below to generate the outputs:\n"
    prompt += "Step 1. for each claim in Set A, please evaluate whether the claim is fully or partially covered by claim set B, and assign a corresponding coverage percentage (from 0 to 1).\n"
    prompt += 'Step 2. Please output with the following Json format: {{"output": [{{"claim_id_in_set_A": 1, or 2, or 3, ..., "coverage_percentage_by_set_B": YYY}}]}}.\n'
    prompt += 'Please output now:'
    return prompt


def prompt_key_point_offsets(content, key_points, print_func):
    prompt = f'Input original text content is listed below:\n'
    prompt += f'{content}\n'
    prompt += f"Below are key points relevant to the original input text content:\n"
    prompt += f"{print_func(key_points)}"
    prompt += f'For each of the key point, please check if it can be covered by the original text content. If so, identify the major text chunk in the original text content covering the key point, output the text chunk, and then output its character level offsets (i.e. "from" and "to" fields).\n'
    prompt += 'Please output with the following Json format: {{"output": [{{"key_point_index": 1, 2, 3, ..., "original_text_chunk": ZZZ, "from": XXX, "to": YYY}}]}}\n'
    prompt += 'Please output now:\n'
    return prompt


def get_gpt_key_point_offsets(content, key_points, print_func):
    config_key_point_offsets = [
        {"system": "You are an NLP expert to analyze news article content.",
         "prompt": (prompt_key_point_offsets(content, key_points, print_func), ["output"]),
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
    return GPTList(config_key_point_offsets)


def calculate_recall(coverage, n):
    if n == 0:
        return None
    coverage = coverage.get('output')
    if null_or_empty(coverage):
        return 0
    if len(coverage) > n:
        return None
    cover = 0
    for one in coverage:
        claim_id_in_set_A = one.get('claim_id_in_set_A')
        if claim_id_in_set_A is None:
            continue
        coverage_percentage_by_set_B = one.get('coverage_percentage_by_set_B')
        if coverage_percentage_by_set_B is None:
            continue
        cover += coverage_percentage_by_set_B
    return cover / n


def update_offsets(offsets, kps, coverage_gpt, omni_answer):
    if null_or_empty(offsets):
        return
    offsets = offsets.get('output')
    if null_or_empty(offsets):
        return
    coverage_gpt = coverage_gpt.get('output')
    if null_or_empty(coverage_gpt):
        return
    coverage = {}
    [coverage.update({x['claim_id_in_set_A']: x['coverage_percentage_by_set_B']})
     for x in coverage_gpt
     if x.get('claim_id_in_set_A') is not None
     and x.get('coverage_percentage_by_set_B') is not None]
    for x in offsets:
        key_point_index = x.get('key_point_index')
        original_text_chunk = x.get('original_text_chunk')
        if key_point_index is None or null_or_empty(original_text_chunk) or coverage.get(
                key_point_index) is None or coverage.get(key_point_index) < 0.2:
            x.update({'from': None, 'to': None})
            continue
        start, end, best_similarity, _, _ = find_most_similar_substring(omni_answer, original_text_chunk)
        if start >= 0 and end >= 0 and end - start > 0 and best_similarity >= 0.5:
            x.update({'from': start, 'to': end, 'kp': kps[key_point_index - 1]})


def calculate_Kendalls_Tau(offsets):
    if null_or_empty(offsets):
        return None
    offsets = offsets.get('output')
    if null_or_empty(offsets):
        return None
    offsets = [x for x in offsets if x.get('key_point_index') is not None and x.get('from') is not None and x.get('to') is not None]
    if null_or_empty(offsets):
        return None
    offsets = [x for x in offsets if x.get('key_point_index', 0) > 0 and x.get('from', -1) >= 0 and x.get('to', -1) >= 0 and x.get('to') - x.get('from') >= 1]
    n = len(offsets)
    if n == 0:
        return None
    if n == 1:
        return 1
    offsets = sorted(offsets, key=lambda x: x['from'])
    C = 0
    D = 0
    for i, one in enumerate(offsets):
        x = min(i, one['key_point_index'] - 1)
        y = max(i, one['key_point_index'] - 1)
        C += x + (n - 1) - y
        D += y - x
    tau = (C - D) / (n * (n - 1))
    return tau


def calculate_supporting_association(gold_answer, top_level_offsets, supporting_offsets):
    if null_or_empty(gold_answer):
        return None
    kp_mapping = {}
    supporting_id = 0
    for top_level_id, one in enumerate(gold_answer):
        [kp_mapping.update({supporting_id + i: top_level_id}) for i in range(0, len(one.get('supporting_key_points', [])))]
        supporting_id += len(one.get('supporting_key_points', []))

    if null_or_empty(top_level_offsets):
        return None
    top_level_offsets = top_level_offsets.get('output')
    if null_or_empty(top_level_offsets):
        return None
    if len(top_level_offsets) == 1:
        return 1

    top_level_offsets = [x for x in top_level_offsets if
                         x.get('key_point_index') is not None and x.get('from') is not None and x.get('to') is not None]
    if null_or_empty(top_level_offsets):
        return None
    top_level_offsets = sorted(top_level_offsets, key=lambda x: x.get('from', -1))
    top_level_offsets = [x for x in top_level_offsets if x.get('key_point_index', 0) >= 1 and x.get('from', -1) >= 0 and x.get('to', -1) >= 0 and x.get('to') - x.get('from') >= 1]
    if len(top_level_offsets) == 0:
        return None
    if len(top_level_offsets) == 1:
        return 1
    top_level_mapping = {}
    for i, one in enumerate(top_level_offsets):
        id = one['key_point_index']
        x = one['from']
        y = float('inf') if i + 1 == len(top_level_offsets) else top_level_offsets[i+1]['from']
        y = max(y, one['to'])
        top_level_mapping.update({id: [x, y]})

    if null_or_empty(supporting_offsets):
        return None
    supporting_offsets = supporting_offsets.get('output')
    if null_or_empty(supporting_offsets):
        return None
    supporting_offsets = [x for x in supporting_offsets if
                          x.get('key_point_index') is not None and x.get('from') is not None and x.get('to') is not None]
    if null_or_empty(supporting_offsets):
        return None
    supporting_offsets = sorted(supporting_offsets, key=lambda x: x.get('from', -1))

    match = 0
    total = 0
    for x in supporting_offsets:
        if x.get('key_point_index', 0) >= 1 and x.get('from', -1) >= 0 and x.get('to', -1) >= 0 and x.get(
                'to') - x.get('from') >= 1:
            total += 1
            key_point_index = x['key_point_index']
            top_level_id = kp_mapping.get(key_point_index - 1)
            if top_level_id is not None:
                offsets = top_level_mapping.get(top_level_id + 1)
                if offsets is not None:
                    offset = x['from']
                    if offsets[0] <= offset <= offsets[1]:
                        match += 1

    match_ratio = match / total if total > 0 else None
    return match_ratio

