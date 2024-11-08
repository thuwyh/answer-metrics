import json

from openai_api import gpt4_prompt, gpt4_prompt_async
import time
import traceback
import logging

from utils import call_batch, cutoff_normalize, flush_file, null_or_empty, parse_json_keys

workspace = {"log_f": None, "search_gpt_steps_f": None, "partial_articles_f": None, "article_f": None,
             "entity_events_f": None,
             "unconfirmed_entity_events_f": None,
             "urls_f": None}

def output(log_f, s):
    if log_f is None:
        return
    log_f.write(f"{s}\n")
    flush_file(log_f)


def prompt_format(prompt, prompt_var, cutoff, normalize):
    for k in prompt_var:
        v = prompt_var[k]
        if v is not None and isinstance(v, str):
            prompt_var[k] = cutoff_normalize(v, cutoff, normalize)
            print(f"prompt {k} length={len(prompt_var[k].split(' '))}\t", end='')
    prompt = str.format(prompt, **prompt_var)
    print()
    return prompt


def call_gpt(config, prompt_var, prompt=None):
    '''prompt_var: list --> more than one input
       prompt: list --> more than one GPT calls in the the workflow'''
    if isinstance(prompt_var, list):
        r = []
        for one in prompt_var:
            r.append(call_gpt(config, one, prompt))
        return r
    if prompt is None:
        prompt = config['prompt']
    if prompt is None:
        return None
    if not isinstance(prompt, list):
        if isinstance(prompt, tuple):
            keys = prompt[1]  # means to parse the result as json using keys as json keys
            prompt = prompt[0]
        else:
            keys = None
        assert isinstance(prompt, str)
        try:
            prompt = prompt_format(prompt, prompt_var, config['cutoff'], config['normalize_newline'])
        except Exception as e:
            traceback.print_exc()
            return None
        output(workspace['log_f'], "**********input***********************************************")
        output(workspace['log_f'], prompt)
        messages = [{"role": "system", "content": config['system']}]
        messages.append({"role": "user", "content": prompt})
        start_time = time.time()
        r = gpt4_prompt(messages, config.get('k', 3),
                        max_tokens=config.get('max_tokens', 512),
                        temperature=config.get('temperature', 1.0),
                        timeout=config.get('timeout'), stream=False,
                        model=config['model'],
                        skip_cache=config.get('skip_cache', False),
                        try_num=config.get('try_num', 10),
                        backoff_to_16k=config.get('backoff_to_16k', False),
                        print_out=config.get('print_out_prompt', False),
                        api_key=config.get('api_key', ['nb-sma8A92Ztx1USYMSImdEfLKeWGplo9DLdfEtGkVxARD6ROfc02JF-4zNWcgs32LeCCc']),
                        api_base=config.get('api_base', ["http://cooper.k8s.nb-prod.com/v1"]),
                        gpt_log_f=config.get('gpt_log_f'))
        if r is None:
            logging.warning(f"gpt run failed! The messages is as follows:\n {messages}\n")
            return None
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"GPT execution_time={execution_time}")
        output(workspace['log_f'], "\noutput\n")
        output(workspace['log_f'], f"{str(r)}\n")
        if keys is not None:
            r_jsonl = []
            for r_one in r:
                if r_one is None:
                    r_jsonl.append(None)
                else:
                    r_one = r_one.strip()
                    json_offset = r_one.find('```json')
                    if json_offset >= 0:
                        r_one = r_one[json_offset:]
                        if r_one.endswith('```'):
                            r_one = r_one[len('```json'): (-1) * len('```')].strip()
                        else:
                            r_one = r_one[len('```json'): ].strip()
                    r_jsonl.append(parse_json_keys(r_one, keys))
            return r_jsonl
        return r
    else:
        r_list = []
        prompt_list = prompt
        for i, prompt in enumerate(prompt_list):
            r = call_gpt(config, prompt_var, prompt)
            if r is None or len(r) == 0:
                r_list.append(None)
            else:
                r_list.append(r)
                if isinstance(r[0], dict):
                    for k, v in r[0].items():
                        if v is not None:
                            assert k not in prompt_var
                            prompt_var.update({k: v})
        return r_list


async def call_gpt_async(config, prompt_var, prompt=None):
    '''prompt_var: list --> more than one input
       prompt: list --> more than one GPT calls in the the workflow'''
    if isinstance(prompt_var, list):
        r = []
        for one in prompt_var:
            r.append(await call_gpt_async(config, one, prompt))
        return r
    if prompt is None:
        prompt = config['prompt']
    if prompt is None:
        return None
    if not isinstance(prompt, list):
        if isinstance(prompt, tuple):
            keys = prompt[1]  # means to parse the result as json using keys as json keys
            prompt = prompt[0]
        else:
            keys = None
        assert isinstance(prompt, str)
        try:
            prompt = prompt_format(prompt, prompt_var, config['cutoff'], config['normalize_newline'])
        except Exception as e:
            traceback.print_exc()
            return None
        output(workspace['log_f'], "**********input***********************************************")
        output(workspace['log_f'], prompt)
        messages = [{"role": "system", "content": config['system']}]
        messages.append({"role": "user", "content": prompt})
        start_time = time.time()
        r = await gpt4_prompt_async(messages, config.get('k', 3),
                        max_tokens=config.get('max_tokens', 512),
                        temperature=config.get('temperature', 1.0),
                        timeout=config.get('timeout'), stream=False,
                        is_json=config.get("is_json", False),
                        model=config['model'],
                        try_num=config.get('try_num', 10),
                        backoff_to_16k=config.get('backoff_to_16k', False),
                        print_out=config.get('print_out_prompt', False),
                        api_key=config.get('api_key', ['nb-sma8A92Ztx1USYMSImdEfLKeWGplo9DLdfEtGkVxARD6ROfc02JF-4zNWcgs32LeCCc']),
                        api_base=config.get('api_base', ["http://cooper.k8s.nb-prod.com/v1"]),
                        gpt_log_f=config.get('gpt_log_f'))
        if r is None:
            logging.warning(f"gpt run failed! The messages is as follows:\n {messages}\n")
            return None
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"GPT execution_time={execution_time}")
        output(workspace['log_f'], "\noutput\n")
        output(workspace['log_f'], f"{str(r)}\n")
        if keys is not None:
            r_jsonl = []
            for r_one in r:
                if r_one is None:
                    r_jsonl.append(None)
                else:
                    r_one = r_one.strip()
                    json_offset = r_one.find('```json')
                    if json_offset >= 0:
                        r_one = r_one[json_offset:]
                        if r_one.endswith('```'):
                            r_one = r_one[len('```json'): (-1) * len('```')].strip()
                        else:
                            r_one = r_one[len('```json'): ].strip()
                    r_jsonl.append(parse_json_keys(r_one, keys))
            return r_jsonl
        return r
    else:
        r_list = []
        prompt_list = prompt
        for i, prompt in enumerate(prompt_list):
            r = await call_gpt_async(config, prompt_var, prompt)
            if r is None or len(r) == 0:
                r_list.append(None)
            else:
                r_list.append(r)
                if isinstance(r[0], dict):
                    for k, v in r[0].items():
                        if v is not None:
                            assert k not in prompt_var
                            prompt_var.update({k: v})
        return r_list


class GPT:

    def __init__(self, config):
        self.config = config
        self.preprocessor = config['preprocessor']
        self.postprocessor = config['postprocessor']
        assert self.postprocessor is not None

    def run(self, intermediate_results, skip_cache):
        config = self.config.copy()
        config.update({'skip_cache': skip_cache})
        if self.preprocessor is not None:
            prompt_vars = self.preprocessor(config, **intermediate_results)
            if prompt_vars is None:
                return None
        else:
            prompt_vars = None
        if prompt_vars is None:
            gpt_output = None
        else:
            gpt_output = call_gpt(config, prompt_vars)
        input = {} if prompt_vars is None \
            else {"prompt_vars": prompt_vars} if isinstance(prompt_vars, list) \
            else prompt_vars
        input.update({'gpt_output': gpt_output})
        [input.update({k: v}) for k, v in intermediate_results.items()]
        return self.postprocessor(config, **input)

    async def run_async(self, intermediate_results):
        if self.preprocessor is not None:
            prompt_vars = self.preprocessor(self.config, **intermediate_results)
            if prompt_vars is None:
                return None
        else:
            prompt_vars = None
        if prompt_vars is None:
            gpt_output = None
        else:
            gpt_output = await call_gpt_async(self.config, prompt_vars)
        input = {} if prompt_vars is None \
            else {"prompt_vars": prompt_vars} if isinstance(prompt_vars, list) \
            else prompt_vars
        input.update({'gpt_output': gpt_output})
        [input.update({k: v}) for k, v in intermediate_results.items()]
        return self.postprocessor(self.config, **input)


class GPTList:

    def __init__(self, config_list):
        self.gpt_list = GPTList.create_gpt_list(config_list)

    @staticmethod
    def create_gpt_list(config_list):
        l = []
        for c in config_list:
            if c is None:
                return None
            l.append(GPT(c))
        return l

    def run(self, intermediate_results, intermediate_results_to_keep=None, skip_cache=False):
        if null_or_empty(self.gpt_list):
            return None
        output = None
        output_1 = {}
        for gpt in self.gpt_list:
            if gpt is None:
                return None
            output = gpt.run(intermediate_results, skip_cache)
            if output is None:
                logging.warning(f"gpt run failed!")
                return None
            print(f'gpt answer:\n {json.dumps(output, indent=4)}\n')
            for k, v in output.items():
                intermediate_results.update({k: v})
                if intermediate_results_to_keep is not None:
                    if k in intermediate_results_to_keep:
                        output_1.update({k: v})
        if len(output_1) > 0:
            for k, v in output_1.items():
                if k not in output:
                    output.update({k: v})
        return output


    async def run_async(self, intermediate_results, intermediate_results_to_keep=None):
        output = None
        output_1 = {}
        for gpt in self.gpt_list:
            output = await gpt.run_async(intermediate_results)
            if output is None:
                logging.warning(f"gpt run failed!")
                return None
            for k, v in output.items():
                intermediate_results.update({k: v})
                if intermediate_results_to_keep is not None:
                    if k in intermediate_results_to_keep:
                        output_1.update({k: v})
        if len(output_1) > 0:
            for k, v in output_1.items():
                if k not in output:
                    output.update({k: v})
        return output


    def batch_run(self, intermediate_results_list, intermediate_results_to_keep_list=None):
        if null_or_empty(intermediate_results_to_keep_list):
            intermediate_results_to_keep_list = [None for _ in intermediate_results_list]
        arguments_list = [{'intermediate_results': x, 'intermediate_results_to_keep': y}
                          for x, y in zip(intermediate_results_list, intermediate_results_to_keep_list)]
        results = call_batch(60, self.run, 3600, arguments_list)
        return results
