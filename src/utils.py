import asyncio
import inspect
import json
import os

def null_or_empty(o):
    return o is None or len(o) == 0

def cutoff_normalize(text_content, cutoff, normalize):
    tokens = text_content.split(' ')
    if len(tokens) > int(cutoff * 0.75 + 0.5):
        text_content = " ".join(tokens[0: int(cutoff * 0.75 + 0.5)])
    if normalize:
        text_content = text_content.replace("\n", "\\n")
    return text_content

def flush_file(f):
    f.flush()
    os.fsync(f.fileno())

def _next_json_delimiter(json_str, start):
    for i in range(start, len(json_str)):
        c = json_str[i]
        if c == '{':
            return '{', '}', i
        if c == '[':
            return '[', ']', i
        if c == '"':
            return '"', '"', i
    return None, None, -1


def parse_json_key(json_str, key):
    try:
        m = json.loads(json_str)
        value = m.get(key)
        return value
    except:
        n_key = json_str.count(f'"{key}":')
        if n_key != 1:
            return None
        offset_key = json_str.find(f'"{key}":')
        dl_0, dl_1, offset_key = _next_json_delimiter(json_str, offset_key + len(f'"{key}":'))
        if offset_key < 0:
            return None
        start = offset_key + len(dl_0)
        while start < len(json_str):
            offset_key_1 = json_str.find(f'{dl_1},', start)
            if offset_key_1 < 0:
                offset_key_1 = json_str.find(f'{dl_1}}}', start)
                if offset_key_1 < 0:
                    break
            if json_str[offset_key_1 - 1] != '\\':
                break
            offset_key_1 = -1
            start += 1
        if offset_key_1 > offset_key + 1:
            value = json_str[offset_key + 1: offset_key_1]
            if dl_0 == '[':
                value = json.loads(f'[{value}]')
            elif dl_0 == '{':
                value = json.loads(f'{{{value}}}')
            return value
        else:
            offset_key_1 = json_str.rfind(f'{dl_1}}}', offset_key)
            if offset_key_1 >= 0:
                value = json_str[offset_key + 1: offset_key_1]
                if dl_0 == '[':
                    value = json.loads(f'[{value}]')
                elif dl_0 == '{':
                    value = json.loads(f'{{{value}}}')
                return value
        return None


def parse_json_keys(json_str, keys):
    json_str = json_str.replace(" }", "}").replace("\n", "").replace("{{", "{")
    try:
        r = {}
        for k in keys:
            v = parse_json_key(json_str, k)
            r.update({k: v})
        return r
    except:
        return None
    
async def acall_f(sem, f, timeout, task_id, **kwargs):
    async with sem:
        output = await asyncio.wait_for(f(**kwargs), timeout=timeout)
        return output, task_id
    
def get_function_parameters(f, arguments_dict):
    parameters = inspect.signature(f).parameters
    parameter_names = [param_name for param_name in parameters]
    return [arguments_dict[x] for x in parameter_names]


async def acall_batch(max_threads, f, timeout, arguments_list):
    sem = asyncio.Semaphore(max_threads)
    tasks = []
    for task_id, arguments in enumerate(arguments_list):

        async def async_function(**arguments):
            parameters = get_function_parameters(f, arguments)
            loop = asyncio.get_event_loop()
            # Run the sync function in a separate thread
            result = await loop.run_in_executor(None, f, *parameters)
            return result

        tasks.append(asyncio.create_task(acall_f(sem, async_function, timeout, task_id, **arguments)))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    results = [r for r in results if isinstance(r, tuple)]
    results = sorted(results, key=lambda x: x[1])
    results = [x[0] for x in results]
    return results


def call_batch(max_threads, f, timeout, arguments_list):
    outputs = asyncio.run(acall_batch(max_threads, f, timeout, arguments_list))
    return outputs

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
    
def get_path_value(m, path, default_value):
    paths = path.split(".")
    value = m
    for p in paths:
        m = value
        if isinstance(m, dict):
            value = m.get(p)
        else:
            return default_value
    return value if value is not None else default_value