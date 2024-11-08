

from utils import get_path_value


def default_preprocessor(config, **kwargs):
    return kwargs


def get_add_gpt_output_as_dict(keys):

    def add_gpt_output_as_dict(config, gpt_output, **kwargs):
        if gpt_output is None or len(gpt_output) == 0 or not isinstance(gpt_output[0], dict):
            return None
        outputs = {}
        for k in keys:
            outputs.update({k: kwargs.get(k)})
        for k, v in gpt_output[0].items():
            if isinstance(v, str):
                v = v.replace("\n\n", "\n")
            outputs.update({k: v})
        return outputs

    return add_gpt_output_as_dict


def get_add_gpt_output_as_dict_all(keys):

    def add_gpt_output_as_dict(config, gpt_output, **kwargs):
        if gpt_output is None or len(gpt_output) == 0 or not isinstance(gpt_output[0], dict):
            return None

        for i in range(len(gpt_output)):
            outputs = {}
            for k in keys:
                outputs.update({k: kwargs.get(k)})
            flag = 1
            for k, v in gpt_output[i].items():
                if not v:
                    flag = 0
                    break
                if isinstance(v, str):
                    v = v.replace("\n\n", "\n")
                outputs.update({k: v})
            if flag:
                return outputs
        return None

    return add_gpt_output_as_dict


def get_add_gpt_output_as_dict_debug(keys):

    def add_gpt_output_as_dict(config, gpt_output, **kwargs):
        if gpt_output is None or len(gpt_output) == 0 or not isinstance(gpt_output[0], dict):
            return None
        print(gpt_output)

        for i in range(len(gpt_output)):
            outputs = {}
            for k in keys:
                outputs.update({k: kwargs.get(k)})
            flag = 1
            for k, v in gpt_output[i].items():
                if not v:
                    flag = 0
                    break
                if isinstance(v, str):
                    v = v.replace("\n\n", "\n")
                outputs.update({k: v})
            if flag:
                return outputs
        return None

    return add_gpt_output_as_dict


def get_check_gpt_outputs(check_key_values, output_keys):

    def check_gpt_outputs(config, gpt_output, **kwargs):
        if gpt_output is None or len(gpt_output) == 0 or not isinstance(gpt_output[0], dict):
            return None
        for k, v in check_key_values.items():
            v_1 = gpt_output[0].get(k)
            if v_1 is None or v_1.lower() != v.lower():
                return None
        outputs = {}
        for k in output_keys:
            outputs.update({k: kwargs.get(k)})
        for k, v in gpt_output[0].items():
            if k in check_key_values:
                continue
            if isinstance(v, str):
                v = v.replace("\n\n", "\n")
            outputs.update({k: v})
        return outputs

    return check_gpt_outputs


def get_set_gpt_output_vcr(field_mapping):

    def set_gpt_output_vcr(config, gpt_output, **kwargs):
        if gpt_output is None or len(gpt_output) == 0 or not isinstance(gpt_output[0], dict):
            return None
        outputs = {}
        [outputs.update({k: v}) for k, v in gpt_output[0].items()]
        value_field = field_mapping.get('value', 'value')
        value = get_path_value(gpt_output[0], value_field, None)
        if value is None:
            return None
        outputs.update({"__value__": value_field})
        confidence_field = field_mapping.get('confidence', 'confidence')
        confidence = get_path_value(gpt_output[0], confidence_field, 1.0)
        outputs.update({"confidence": confidence})
        rational_field = field_mapping.get('rational', 'rational')
        rational = get_path_value(gpt_output[0], rational_field, '')
        outputs.update({rational_field: rational})
        return outputs

    return set_gpt_output_vcr


def get_add_gpt_outputs_as_dict(keys):

    def add_gpt_outputs_as_dict(config, gpt_output, **kwargs):
        if gpt_output is None or len(gpt_output) == 0 or not any(isinstance(x, dict) for x in gpt_output):
            return None
        outputs_list = []
        for i in range(0, len(gpt_output)):
            if not isinstance(gpt_output[i], dict):
                outputs_list.append(None)
                continue
            outputs = {}
            for k in keys:
                outputs.update({k: kwargs.get(k)})
            for k, v in gpt_output[i].items():
                if isinstance(v, str):
                    v = v.replace("\n\n", "\n")
                outputs.update({k: v})
            outputs_list.append(outputs)
        return outputs_list

    return add_gpt_outputs_as_dict
