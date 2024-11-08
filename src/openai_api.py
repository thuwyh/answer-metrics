import datetime
import requests
import json
from time import sleep
import time
from openai import OpenAI, AsyncOpenAI

import uuid
import os

from utils import flush_file


def parse_http_result_json(http_result):
    if http_result is None:
        return 404, "{}"
    status = http_result.status_code
    reply = http_result.content.decode(encoding="utf8")
    try:
        reply_j = json.loads(reply)
        return status, reply_j
    except:
        return status, None


def customized_call_gpt35_mt(qas, system="You are a helpful assistant.",
                             max_tokens=2048, temperature=0.7, try_num=5, model=None):
    count = 0
    while count < try_num:
        sleep(1)
        url = 'http://aigc-gpt-server.k8s.nb-prod.com/chat'
        messages = [{"role": "system", "content": system}]
        for qa in qas:
            messages.append({"role": "user", "content": qa[0]})
            if len(qa) == 2:
                messages.append({"role": "assistant", "content": qa[1]})
        m = {"messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        if model is not None:
            m.update({"model": model})
        try:
            result = requests.post(url, json=m, timeout=300)
        except Exception as e:
            count += 1
            print(f"failed {count} str{e}")
            continue
        status, result = parse_http_result_json(result)
        if status != 200 or result is None:
            return None
        if result.get("status", "") != "success":
            return None
        return result.get("results")


def customized_call_gpt35(prompt, try_num):
    url = 'http://aigc-gpt-server.k8s.nb-prod.com/gpt'
    m = {'prompt': prompt,
         'try_num': try_num}
    st = time.time()
    result = requests.post(url, json=m, timeout=300)
    et = time.time()
    elapsed_time = et - st
    print('customized_call_gpt35 Execution time:', elapsed_time, 'seconds')
    status, result = parse_http_result_json(result)
    if status != 200 or result is None:
        return None
    if result.get("status", "") != "success":
        return None
    return result.get("results")


def customized_call_chatgpt(prompt, try_num=6):
    count = 0
    while count < try_num:
        sleep(1)
        url = 'http://aigc-gpt-server.k8s.nb-prod.com/gpt'
        m = {'prompt': prompt, 'max_tokens': 2048}
        st = time.time()
        result = requests.post(url, json=m, timeout=300)
        et = time.time()
        elapsed_time = et - st
        print('customized_call_chatgpt Execution time:', elapsed_time, 'seconds')
        try:
            status, result = parse_http_result_json(result)
        except:
            count += 1
            continue
        if status != 200 or result is None:
            return None
        return result.get("results")


def rewrite_title_gpt35(title, text, num, max_len):
    url = 'http://aigc-gpt-server.k8s.nb-prod.com/gpt_title_rewrite'
    m = {"title": title, "text": text, 'num': num, 'max_len': max_len}
    st = time.time()
    result = requests.post(url, json=m, timeout=300)
    et = time.time()
    elapsed_time = et - st
    print('rewrite_title_gpt35 Execution time:', elapsed_time, 'seconds')
    status, result = parse_http_result_json(result)
    if status != 200 or result is None:
        return None
    if result.get("status", "") != "success":
        return None
    return result.get("titles")


def split_paragraphs(text):
    max_len = 600
    tokens = text.split(' ')
    paragraphs_result = []
    from_offset = 0
    paragraphs_left = ""
    while from_offset < len(tokens):
        paragraphs_left_len = len(paragraphs_left.split(" "))
        to_offset = min(len(tokens) - 1, from_offset + max_len - 1 - paragraphs_left_len)
        tokens_1 = tokens[from_offset: to_offset + 1]
        print(f"{from_offset}\t{to_offset}\t{len(tokens)}")
        text = paragraphs_left + " " + " ".join(tokens_1)
        text = text.strip()
        prompt = f"please do not rewrite the content below, but just split the content into paragraphs separated by new line:\n{text}\n\nsplit content:"
        qas = [(prompt,)]
        paragraphs = customized_call_gpt35_mt(qas, temperature=0.001)
        if paragraphs is None or len(paragraphs) == 0:
            return None
        print("success")
        paragraphs = paragraphs[0]
        paragraphs_len = len(paragraphs.split(" "))
        paragraphs = paragraphs.replace("\n\n", "\n").split("\n")
        paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 0]
        if len(paragraphs) > 1 and to_offset < len(tokens):
            paragraphs_result += paragraphs[0: -1]
            paragraphs_left = paragraphs[-1]
            if paragraphs_len > max_len + 20:
                paragraphs_left = ""
        else:
            paragraphs_result += paragraphs
            paragraphs_left = ""
        from_offset = to_offset + 1
    return paragraphs_result


def summarize(content, n_words, n_paragraphs, temperature=0.3):
    prompt = f"Summarize the following text in about {n_words} words, and about {n_paragraphs} paragraphs"
    prompt = f"{prompt}: {content}"
    summary = customized_call_gpt35_mt([(prompt,)], try_num=3, temperature=temperature)
    return summary


def summarize_with_title(title, content, n_words, n_paragraphs, temperature=0.3):
    if title is None:
        return summarize(content, n_words, n_paragraphs, temperature)
    prompt = f'Given the title "{title}", summarize the following text in about {n_words} words, and about {n_paragraphs} paragraphs'
    prompt = f"{prompt}: {content}"
    summary = customized_call_gpt35_mt([(prompt,)], try_num=3, temperature=temperature)
    return summary


def summarize_paragraphs(paragraphs, compression_ratio, p_ratio, max_len_per_call=1024, title=None):
    passage_paragraph_ids = []
    passage_len = 0
    passage = []
    for i in range(0, len(paragraphs)):
        p = paragraphs[i]
        p_len = len(p.split(' '))
        passage_len += p_len
        passage.append(i)
        if i == len(paragraphs) - 1:
            passage_paragraph_ids.append(passage)
        elif passage_len + len(paragraphs[i + 1].split(' ')) > max_len_per_call:
            passage_paragraph_ids.append(passage)
            passage = []
            passage_len = 0
    p_id_set = set()
    for passage in passage_paragraph_ids:
        for one in passage:
            p_id_set.add(one)
            assert one >= 0 and one < len(paragraphs)
    assert len(p_id_set) == len(paragraphs)
    summaries = []
    for passage in passage_paragraph_ids:
        text = ""
        for id in passage:
            text += " " + paragraphs[id]
        text = text.strip()
        n_words = int(compression_ratio * len(text.split(" ")) + 0.5)
        n_paragraphs = min(max(2, int(n_words * p_ratio)), 5)
        summary = summarize_with_title(title, text, n_words=n_words,
                                       n_paragraphs=n_paragraphs)
        if summary is None or len(summary) != 1:
            return None, None
        summaries.append(summary[0])
    return summaries, len(passage_paragraph_ids)


def clean_newlines(summaries: [str, list]) -> str:
    if summaries is None:
        return None
    if isinstance(summaries, str):
        summaries = [summaries]
    final_summaries = ''
    for x in summaries:
        x = x.replace("\\n", "\n")
        while "\n\n" in x:
            x = x.replace("\n\n", "\n")
        x = x.split("\n")
        for one in x:
            one = one.strip()
            if len(one) > 0:
                final_summaries += one + "\n"
    return final_summaries.strip()


def gpt4_prompt(messages, k, max_tokens=256, temperature=0.7, timeout=None, stream=False, model='gpt-4',
                skip_cache=False, try_num=10, print_out=False, backoff_to_16k=True, retry_sleep=2,
                api_key = ['nb-Ynz8MfbDirnGCg1v49k2by2B27QZskqiNPNRz6GlL43Yce4jk0XXyJGwY2LYu62a73g'],
                api_base = ["http://cooper.k8s.nb-prod.com/v1"],
                count_model_backoff=3, backoff_model='gpt-4', model_db=None, use_latest_turbo=True,
                json_format=False,
                gpt_log_f=None):
    # model should be 'gpt-4' or 'gpt-3.5-turbo'
    if model in ['gpt-4o', 'gpt-4o-mini']:
        pass
    elif model.startswith('gpt-4') and use_latest_turbo:
        model = 'gpt-4-turbo'
    elif model == 'gpt4':
        model = 'gpt-4-turbo'
    model_0 = model
    model_db = model if model_db is None else model_db
    if print_out:
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(f"calling {model} with the following messages")
        for message in messages:
            print(f"{message['role']}:\n{message['content']}")
    messages_str = json.dumps(messages)
    messages_str += json.dumps({"k": k, "max_tokens": max_tokens, "temperature": temperature})
    messages_str += json.dumps({'model': model_db})
    str_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, messages_str))

    if gpt_log_f is not None:
        gpt_log_f.write("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        gpt_log_f.write(f"calling {model} with the following messages\n")
        for message in messages:
            gpt_log_f.write(f"{message['role']}:\n{message['content']}\n")
        flush_file(gpt_log_f)

    completion = None
    count = 0
    api_id = 0
    client = OpenAI(api_key=api_key[api_id], base_url=api_base[api_id], timeout=timeout)
    while count < try_num:
        try:
            print(f"using {model}")
            completion = client.chat.completions.create(model=model,
                                                        messages=messages, max_tokens=max_tokens,
                                                        temperature=temperature,
                                                        n=k, stream=stream,
                                                        response_format={"type":"json_object"} if json_format else {"type": "text"})
        except Exception as e:
            count += 1
            print(f"gpt4_prompt failed {count} {str(e)}")
            time.sleep(retry_sleep)
            if 'maximum context length' in str(e):
                if backoff_to_16k:
                    model = 'gpt-4-1106-preview' if model_0 != 'gpt-4-1106-preview' else 'gpt-3.5-turbo-16k'
                else:
                    max_tokens = int(0.75 * max_tokens)
            elif count >= count_model_backoff:
                model = backoff_model
            api_id = (api_id + 1) % len(api_key)
            continue

        if stream:
            return completion
        if completion is None or isinstance(completion, str) or len(completion.choices) == 0:
            count += 1
            if print_out:
                print(f"gpt4_prompt failed {count} {completion}")
            time.sleep(retry_sleep)
        else:
            break
    if completion is None:
        return None
    if print_out:
        print(f"gpt4_prompt succeeds")
    results = []

    for choice in completion.choices:
        is_cutoff = choice.finish_reason != "stop"
        if is_cutoff:
            gpt_answer = choice.message.content
            message_next = messages.copy()
            message_next.append({"role":"assistant", "content": gpt_answer})
            message_next.append({"role": "user", "content": "Continue"})
            results_next = gpt4_prompt(message_next, k=1,
                                       max_tokens=max_tokens,
                                       temperature=temperature,
                                       timeout=timeout,
                                       stream=False,
                                       model=model,
                                       skip_cache=True,
                                       try_num=try_num,
                                       print_out=False,
                                       backoff_to_16k=backoff_to_16k,
                                       retry_sleep=retry_sleep,
                                       api_key=api_key,
                                       count_model_backoff=count_model_backoff,
                                       backoff_model=backoff_model,
                                       model_db=model_db,
                                       use_latest_turbo=use_latest_turbo,
                                       json_format=False,
                                       gpt_log_f=gpt_log_f)
            if results_next is None or len(results_next) == 0:
                return None
            gpt_answer = append_with_suffix_prefix_overlap_removal(gpt_answer, results_next[0])
            gpt_answer = gpt_answer.strip()
            gpt_answer = gpt_answer.strip("```json").strip("```").strip()
        else:
            gpt_answer = choice.message.content.strip()
            gpt_answer = gpt_answer.strip("```json").strip("```").strip()
        results.append(gpt_answer)
    return results


async def gpt4_prompt_async(messages, k, max_tokens=256, temperature=0.7, timeout=None, stream=False, model='gpt-4',
                skip_cache=False, try_num=10, print_out=False, backoff_to_16k=True, retry_sleep=2,
                api_key = ['nb-Ynz8MfbDirnGCg1v49k2by2B27QZskqiNPNRz6GlL43Yce4jk0XXyJGwY2LYu62a73g'],
                api_base = ["http://cooper.k8s.nb-prod.com/v1"], is_json=False,
                count_model_backoff=3, backoff_model='gpt-4', model_db=None, use_latest_turbo=True,
                gpt_log_f=None):
    # model should be 'gpt-4' or 'gpt-3.5-turbo'
    if model in ['gpt-4o', 'gpt-4o-mini']:
        pass
    elif model.startswith('gpt-4') and use_latest_turbo:
        model = 'gpt-4-turbo'
    elif model == 'gpt4':
        model = 'gpt-4-turbo'
    model_0 = model
    model_db = model if model_db is None else model_db
    if print_out:
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(f"calling {model} with the following messages")
        for message in messages:
            print(f"{message['role']}:\n{message['content']}")
    messages_str = json.dumps(messages)
    messages_str += json.dumps({"k": k, "max_tokens": max_tokens, "temperature": temperature})
    messages_str += json.dumps({'model': model_db})
    str_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, messages_str))

    if gpt_log_f is not None:
        gpt_log_f.write("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        gpt_log_f.write(f"calling {model} with the following messages\n")
        for message in messages:
            gpt_log_f.write(f"{message['role']}:\n{message['content']}\n")
        flush_file(gpt_log_f)

    completion = None
    count = 0
    api_id = 0

    real_openai_key = os.getenv("OPENAI_KEY")
    if real_openai_key:
        print("OPENAI_KEY is set, call openai directly.")
        base_url = None
        real_api_key = real_openai_key
    else:
        print("OPENAI_KEY is not set, use cooper.")
        base_url = api_base[api_id]
        real_api_key = api_key[api_id]

    client = AsyncOpenAI(api_key=real_api_key, base_url=base_url, timeout=timeout)
    while count < try_num:
        try:
            print(f"using {model}")
            if is_json:
                completion = await client.chat.completions.create(model=model,
                                                            messages=messages, max_tokens=max_tokens,
                                                            temperature=temperature,
                                                            response_format={"type": "json_object"},
                                                            n=k, stream=stream)
            else:
                completion = await client.chat.completions.create(model=model,
                                                            messages=messages, max_tokens=max_tokens,
                                                            temperature=temperature,
                                                            n=k, stream=stream)
            print("async done")
        except Exception as e:
            count += 1
            print(f"gpt4_prompt failed {count} {str(e)}")
            time.sleep(retry_sleep)
            if 'maximum context length' in str(e):
                if backoff_to_16k:
                    model = 'gpt-4-1106-preview' if model_0 != 'gpt-4-1106-preview' else 'gpt-3.5-turbo-16k'
                else:
                    max_tokens = int(0.75 * max_tokens)
            elif count >= count_model_backoff:
                model = backoff_model
            api_id = (api_id + 1) % len(api_key)
            continue
        finally:
            if client:
                await client.close()

        if stream:
            return completion
        if completion is None or isinstance(completion, str) or len(completion.choices) == 0:
            count += 1
            if print_out:
                print(f"gpt4_prompt failed {count} {completion}")
            time.sleep(retry_sleep)
        else:
            break
    if completion is None:
        return None
    if print_out:
        print(f"gpt4_prompt succeeds")
    results = []
    for choice in completion.choices:
        gpt_answer = choice.message.content.strip()
        gpt_answer = gpt_answer.strip("```json").strip("```").strip()
        print("gptanswer: ", gpt_answer)
        results.append(gpt_answer)
    return results

def append_with_suffix_prefix_overlap_removal(s0, s1):
    s0 = s0.strip()
    s1 = s1.strip()
    max_overlap = 0
    for i in range(0, len(s1)):
        s = s1[0: i + 1]
        if s0.endswith(s):
            max_overlap = i + 1
    if max_overlap > 0:
        return s0 + s1[max_overlap:]
    return s0 + s1


if __name__ == '__main__':
    text = open('./test.txt').read()
    messages = [{'role': 'system', 'content': 'You are a professional journalist.'},
                {'role': 'user', 'content': text}]
    result = gpt4_prompt(messages, k=1, max_tokens=100,
                         model='gpt-4o',
                         json_format=False)
    print(result[0])
