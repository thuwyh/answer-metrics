import string
import requests
from uuid import UUID
from trafilatura import extract as trafilatura_extract
from bs4 import BeautifulSoup, NavigableString, Comment
from urllib.parse import urlparse
import difflib
import re
import random
from gpt import GPTList
from openai_api import parse_http_result_json
import pygtrie
from utils import null_or_empty


def extract_domain(url, default_value=None):
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain
    except:
        return default_value


def print_str_list(l):
    s = ''
    for i, one in enumerate(l):
        s += f"{i+1}. {str(one)}\n"
    return s


def remove_dropdowns(soup):
    dropdowns = identify_dropdown_elements(soup)
    [x.extract() for x in dropdowns]
    return soup


def remove_clinks(soup, min_n=3):
    clinks = identify_continuous_outlinks(soup, min_n)
    for x in clinks:
        for elem in x[1]:
            elem.extract()
    return soup


def parse_html_source(page_source, use_trafilatura_extract):
    if use_trafilatura_extract:
        text = trafilatura_extract(page_source)
        return text
    try:
        soup = BeautifulSoup(page_source, "html.parser")
    except:
        return None

    for func in [remove_dropdowns, remove_clinks]:
        soup = func(soup)
    text = soup.get_text(separator='\n', strip=True)
    if text is not None:
        texts = text.split("\n")
        texts = [x.strip() for x in texts if len(x.strip()) > 0]
        text = "\n".join(texts)
    return text


def get_xpath(elem, attributes=None):
    xpath = ""
    while elem is not None:
        if isinstance(elem, NavigableString):
            s = "text"
        else:
            s = elem.name
            if attributes is not None:
                for attr in attributes:
                    value = elem.get(attr)
                    if value is not None:
                        if isinstance(value, list):
                            value = " ".join(value)
                        s += f" {attr}={value.lower().strip()}"
        if len(xpath) > 0:
            xpath = " " + xpath
        xpath = s + xpath
        elem = elem.parent
    return xpath


def identify_dropdown_elements(soup, attributes_to_check=None):
    keywords = ['drop down', 'dropdown']
    iter = dom_depth_first_iterator(soup)
    dropdowns = []
    for element in iter:
        if element.name:
            if attributes_to_check is None or len(attributes_to_check) == 0:
                arr = element.attrs
            else:
                arr = attributes_to_check
            if arr is None:
                continue
            match = False
            for attr in arr:
                v = element[attr]
                if v:
                    if isinstance(v, list):
                        v = " ".join(v)
                    for kw in keywords:
                        if kw in v.lower():
                            match = True
                            break
                    if match:
                        break
            if match:
                dropdowns.append(element)
    return dropdowns


def dom_depth_first_iterator(element):
    if not isinstance(element, Comment) and element.name not in ['style', 'script', 'head', 'title', 'meta']:
        yield element
        if element.name:
            for child in element:
                yield from dom_depth_first_iterator(child)

def identify_continuous_outlinks(soup, min_n=3):
    clinks = []
    iter = dom_depth_first_iterator(soup)
    for elem in iter:
        if isinstance(elem, NavigableString) and len(elem.strip()) > 0:
            xpath = get_xpath(elem, ['class', 'id'])
            if len(clinks) == 0:
                clinks.append([xpath, [elem]])
            else:
                l = clinks[-1]
                if l[0] == xpath:
                    l[1].append(elem)
                else:
                    clinks.append([xpath, [elem]])
    clinks = [x for x in clinks if (" a " in x[0] or x[0].startswith("a ") or x[0].endswith(" a") or x[0] == "a")
              and len(x[1]) >= min_n]
    return clinks


def print_out_clinks(soup, min_n=3):
    clinks = identify_continuous_outlinks(soup, min_n)
    for x in clinks:
        print("------------------------------------")
        for one in x[1]:
            print(f"{one.get_text()}")


def have_to_be_true(flag, message):
    if not flag:
        import os
        print(f"have_to_be_true: {message}")
        os.abort()


def print_articles(doc_list):
    s = ''
    for i, doc in enumerate(doc_list):
        s += f'Article {i+1}. URL: {doc.get("url", "")}\n'
        s += f'Title: {doc.get("title", "")}\n'
        s += f'Content: {doc.get("content", "")}\n'
        s += f'Publication date: {doc.get("publication_date", "")}\n'
    return s


def print_key_points(key_points):
    s = ''
    for i, one in enumerate(key_points):
        s += f'{i+1}. top_level_key_point: {one.get("top_level_key_point", "")}\n'
        s += f'supporting_key_points: {one.get("supporting_key_points", "")}\n'
    return s


def print_key_points_1(key_points):
    s = ''
    n = 1
    for x in key_points:
        s += f'{n}. {x.get("top_level_key_point", "")}\n'
        n += 1
        for y in x.get('supporting_key_points', []):
            s += f'{n}. {y.get("supporting_key_points", "")}\n'
            n += 1
    return s


def call_omni_agents(query, url='http://nb-llm-web-server.k8s.nb-stage.com/v2/agent/qa'):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer newsbreak_internal_user_token#internal_user_002'
    }
    data = {
        "query": query
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200 and not null_or_empty(response.text):
        return response.text
    return None


def get_full_coverage(doc_id):
    try:
        int(doc_id)
        result = requests.get(f"https://tools.n.newsbreak.com/api/utils-docId-decode?id={doc_id}")
        status, output = parse_http_result_json(result)
        if status == 200:
            doc_id = output.get('docId')
    except:
        pass
    if doc_id is None:
        return None
    doc_ids = [doc_id]
    try:
        result = requests.get(
            f"http://fake-news-detection.k8s.nb-prod.com/full_coverage_detection?doc_id={doc_id}&debug=True", timeout=120)
        if result is not None:
            status, output = parse_http_result_json(result)
            if status == 200:
                same_event = output.get('result', {}).get('same_event', [])
                for one in same_event:
                    doc_id = one.get('docid')
                    if null_or_empty(doc_id):
                        url = one.get('url')
                        if url is not None:
                            result = requests.get(f'http://docid-gen.ha.nb.com:6001/id/find?url={url}')
                            status, output = parse_http_result_json(result)
                            if status == 200:
                                doc_id = output.get('result', {}).get('_id')
                    if not null_or_empty(doc_id):
                        doc_ids.append(doc_id)
    except:
        pass
    return doc_ids

def _find_most_similar_substring_fast(A: str, B: str):
    # Use regular expressions to split A into words and punctuation marks
    words = re.findall(r'\w+|[^\w\s]', A)

    # Create word boundaries list to store the start and end indices of each word/punctuation
    word_boundaries = []
    start_idx = 0

    # Build the list of word boundaries
    A = ''

    has_space_after = False
    for word in words:
        if word in string.punctuation:
            has_space_before, has_space_after = space_placement(word)
        else:
            has_space_before = has_space_after
            has_space_after = True
        if has_space_before:
            A += ' '
            start_idx += 1
        end_idx = start_idx + len(word)
        word_boundaries.append((start_idx, end_idx))
        start_idx = end_idx
        A += word

    best_start = -1
    best_end = -1
    best_similarity = -1
    max_length_delta_ratio = 0.2
    pattern_len = len(B)

    # Compare substrings of A formed by complete words
    for i in range(len(word_boundaries)):
        for j in range(i, len(word_boundaries)):
            # Extract the substring formed by words from index i to j
            start_idx = word_boundaries[i][0]
            end_idx = word_boundaries[j][1]
            candidate_substring = A[start_idx: end_idx]
            if abs(len(candidate_substring)-pattern_len)/pattern_len>max_length_delta_ratio:
                continue

            # Calculate similarity between candidate substring and B
            similarity = difflib.SequenceMatcher(None, candidate_substring, B).ratio()

            # If we found a better match, update the best result
            if similarity > best_similarity:
                best_similarity = similarity
                best_start = start_idx
                best_end = end_idx
                if best_similarity == 1.0:
                    break

    return best_start, best_end, best_similarity, A, word_boundaries

def _find_most_similar_substring(A: str, B: str):
    # Use regular expressions to split A into words and punctuation marks
    words = re.findall(r'\w+|[^\w\s]', A)

    # Create word boundaries list to store the start and end indices of each word/punctuation
    word_boundaries = []
    start_idx = 0

    # Build the list of word boundaries
    A = ''

    has_space_after = False
    for word in words:
        if word in string.punctuation:
            has_space_before, has_space_after = space_placement(word)
        else:
            has_space_before = has_space_after
            has_space_after = True
        if has_space_before:
            A += ' '
            start_idx += 1
        end_idx = start_idx + len(word)
        word_boundaries.append((start_idx, end_idx))
        start_idx = end_idx
        A += word

    best_start = -1
    best_end = -1
    best_similarity = -1

    # Compare substrings of A formed by complete words
    for i in range(len(word_boundaries)):
        for j in range(i, len(word_boundaries)):
            # Extract the substring formed by words from index i to j
            start_idx = word_boundaries[i][0]
            end_idx = word_boundaries[j][1]
            candidate_substring = A[start_idx: end_idx]

            # Calculate similarity between candidate substring and B
            similarity = difflib.SequenceMatcher(None, candidate_substring, B).ratio()

            # If we found a better match, update the best result
            if similarity > best_similarity:
                best_similarity = similarity
                best_start = start_idx
                best_end = end_idx
                if best_similarity == 1.0:
                    break

    return best_start, best_end, best_similarity, A, word_boundaries


def find_most_similar_substring(A: str, B: str):
    print("running find_most_similar_substring")
    best_start, best_end, best_similarity, A_1, word_boundaries = _find_most_similar_substring_fast(A, B)
    return best_start, best_end, best_similarity, A_1[best_start:best_end], A_1

def space_placement(punctuation: str):
    # Define punctuation marks that follow different spacing rules
    no_space_before = {".", ",", ":", ";", "?", "!", ")", "]", '"', "'"}
    no_space_after = {"(", "[", '"', "'"}
    space_both_sides = {"—", "–", "..."}

    if punctuation in no_space_before:
        return False, True
    elif punctuation in no_space_after:
        return True, False
    elif punctuation in space_both_sides:
        return True, True
    else:
        return False, False


def get_gpt_config_default(model, prompt_func, output_fields, **kwargs):
    config = {"system": "You are an NLP expert to analyze article content.",
             "prompt": (prompt_func(**kwargs), output_fields),
             "k": 1,
             "cutoff": 110000,
             "print_out_prompt": True,
             "normalize_newline": True,
             "max_tokens": 4000,
             "temperature": 0.1,
             "model": model,
             "response_format": {"type": "json_object"},
             "preprocessor": default_preprocessor,
             "postprocessor": get_add_gpt_output_as_dict([])}
    if config['prompt'][0] is None:
        return None
    return config


def run_gpt(doc_features, get_prompt, output_fields, model='gpt-4o'):
    gpt = GPTList([get_gpt_config_default(model, get_prompt, output_fields, **doc_features)])
    if gpt is None:
        return None
    response = gpt.run({})
    if response is None:
        return None
    result = {}
    for key in output_fields:
        result.update({key: response.get(key)})
    return result


def next(l: list, element, k, n):
    """
    update the stream sampling given the new element
    :param l: the stream sampling output
    :param element: new element
    :param k: max sampling count
    :param n: the current stream length (not including the new element)
    :return:
    """
    assert len(l) <= k
    if len(l) + 1 <= k:
        l.append(element)
    else:
        p = random.random()
        if p <= float(k) / (n + 1):
            offset = random.randint(0, k - 1)
            l[offset] = element


NAMESPACE_MCTS = UUID('6ba9c811-9eaf-12d1-80b4-00c04fd591c7')

NAMESPACE_MCTS_Google = UUID('6ba9c611-8cef-11d1-80b4-00c04fd581c7')

NAMESPACE_MCTS_GoogleMap = UUID('5ab8c611-8cef-11d1-82b4-00c04fd581c7')

NAMESPACE_MCTS_NewsSearch = UUID('6cb4c611-8cef-11e3-82b4-00c04fd581c7')

import time

class StepTimer:
    def __init__(self):
        self.start_time = None
        self.steps = []

    def start(self):
        self.start_time = time.perf_counter()
        self.steps = []

    def step(self, step_name=''):
        if self.start_time is None:
            raise ValueError("Timer has not been started. Call start() before step().")
        current_time = time.perf_counter()
        elapsed_time = current_time - self.start_time
        self.steps.append((step_name, elapsed_time))
        self.start_time = current_time
        return elapsed_time

    def report(self):
        for i, (step_name, elapsed_time) in enumerate(self.steps):
            print(f"Step {i+1} ({step_name}): {elapsed_time:.4f} seconds")

if __name__ == '__main__':
    # Example usage
    A = "this is an example   string, not  an ample string."
    B = "ample"
    start_offset, end_offset, A_2, A_1 = find_most_similar_substring(A, B)
    print(f"The most similar substring in A to B is from {start_offset} to {end_offset}: '{A_2}'")
    print(A_1)


