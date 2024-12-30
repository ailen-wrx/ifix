import falcon
import csv
import os
import xmltodict
from collections import OrderedDict, Counter
import difflib
from pathlib import Path

from utils import get_oracle

DUMMY_VALUE = {
    'serialized': False,
    'type': '\\',
    'val': ''
}


def utf_16_encode(string):
    surrogate_set = ''.join(c for c in string if c > '\uFFFF')
    if len(surrogate_set) > 0:
        new_value = ""
        for word in string:
            if word in surrogate_set:
                x = word.encode('utf-16-le')
                xx = [chr(int.from_bytes(y, 'little')) for y in (x[0:2], x[2:4])]
                new_value += str(xx).strip('[]').replace(' ', '').replace("'", '').replace(",", '').upper().replace('U',
                                                                                                                    'u')
            else:
                new_value += word
        return new_value
    else:
        return string


def value_to_string(value):
    value = utf_16_encode(value)
    orig_value = value
    try:
        value = xmltodict.parse(value)
    except Exception:
        value = value
    if type(value) is dict:
        key = list(value.keys())[0]
        if type(value[key]) is dict or type(value[key]) is list:
            return {
                'serialized': True,
                'type': key,
                'val': str(orig_value)
            }
        else:
            if key == 'double' and value[key] != "NaN":
                return {
                    'serialized': False,
                    'type': str(float(value[key])),
                    'val': ''
                }
            return {
                'serialized': False,
                'type': str(value[key]),
                'val': ''
            }
    else:
        return {
            'serialized': True,
            'type': str(value).split('\n')[0].strip("<>").split('.')[-1],
            'val': str(orig_value)
        }


def compare_names(new, olds):
    for old in olds:
        iter_n = new.split("@@@")[-1]
        iter_o = old.split("@@@")[-1]
        if iter_n != iter_o:
            continue
        lineno_n = new.split("@@@")[0].split("@@#")[-1]
        lineno_o = old.split("@@@")[0].split("@@#")[-1]
        if lineno_n != lineno_o:
            continue
        name_n = new.split("@@@")[0].split("@@#")[0]
        name_o = old.split("@@@")[0].split("@@#")[0]
        diff_cnt = 0
        len = 0
        for i, diff in enumerate(difflib.ndiff(name_n, name_o)):
            len += 1
            if diff[0] != ' ': diff_cnt += 1
        if (diff_cnt / len) < 0.3:
            str = ""
            diff_flg = False
            for i, diff in enumerate(difflib.ndiff(name_n, name_o)):
                if diff[0] == ' ':
                    str += diff[-1]
                    diff_flg = False
                elif diff_flg == False:
                    str += '*'
                    diff_flg = True
            return old, f'{str}@@#{lineno_n}@@@{iter_n}', f'{name_o}@@#{lineno_o}', f'{str}@@#{lineno_n}', int(iter_n)
    return None


class InstrumentResource:
    def __init__(self, service):
        self.service = service

    def on_post(self, req, resp):
        media = req.get_media()
        print(media)
        session_id = media['session_id']

        IPR_RESULT_LOCATION = f'{Path.home()}/.ipr/{session_id}/iproutput'
        bug_oracle = get_oracle(session_id)

        metadata = {}

        for fname in os.listdir(IPR_RESULT_LOCATION):
            patch_idx, srcfile, line_number = os.path.splitext(fname)[0].split("#")
            patch_idx = int(patch_idx)
            stack_trace_idx = '#'.join([srcfile, line_number])
            if stack_trace_idx not in metadata:
                metadata[stack_trace_idx] = {}
            num_pass = 0
            iter_dict = {}
            declared_names = []
            content = open(os.path.join(IPR_RESULT_LOCATION, fname), "r").read().replace('\r', '')
            with open(os.path.join(IPR_RESULT_LOCATION, fname), "w") as g:
                g.write(content)
            with open(os.path.join(IPR_RESULT_LOCATION, fname), 'r') as f:
                for row in csv.reader(f):
                    if row == ['<entry>']:
                        num_pass += 1
                        if num_pass > 1: break
                    else:
                        lineno, status, name, value = row
                        if status == "method" or status == "infix" or status == "defined" or status == "used":
                            if status == "used" and name in declared_names:
                                continue
                            declared_names.append(name)

                            name = f'{name}@@#{lineno}'
                            name = f'##{name}' if (status == "method" or status == "infix") else name

                            if name not in iter_dict:
                                iter_dict[name] = 1

                            name_iter = f'{name}@@@{iter_dict[name]}'

                            if name_iter in metadata[stack_trace_idx]:
                                metadata[stack_trace_idx][name_iter][patch_idx] = value
                            else:
                                sim = compare_names(name_iter, metadata[stack_trace_idx])
                                if sim is not None and status == "method":
                                    old_name_iter, new_name_iter, old_name, new_name, iter_n = sim
                                    old_pos = list(metadata[stack_trace_idx].keys()).index(old_name_iter)
                                    items = list(metadata[stack_trace_idx].items())
                                    items.insert(old_pos, (new_name_iter, metadata[stack_trace_idx][old_name_iter]))
                                    metadata[stack_trace_idx] = dict(items)
                                    metadata[stack_trace_idx][new_name_iter] = metadata[stack_trace_idx][old_name_iter]
                                    if old_name_iter != new_name_iter: del metadata[stack_trace_idx][old_name_iter]
                                    iter_dict[name] += 1
                                    iter_dict[new_name] = iter_n
                                    name = new_name
                                    metadata[stack_trace_idx][new_name_iter][patch_idx] = value
                                else:
                                    metadata[stack_trace_idx][name_iter] = {}
                                    metadata[stack_trace_idx][name_iter][patch_idx] = value

                            if status != "used" and status != "infix":
                                iter_dict[name] += 1

                        pass

        metadata['__num_rows__'] = 0
        for stack_trace_idx in metadata:
            if stack_trace_idx == '__num_rows__': continue
            for name in metadata[stack_trace_idx]:
                metadata[stack_trace_idx][name] = dict(OrderedDict(sorted(metadata[stack_trace_idx][name].items())))
                if len(metadata[stack_trace_idx][name]) > metadata['__num_rows__']:
                    metadata['__num_rows__'] = len(metadata[stack_trace_idx][name])

        tables = []

        bhvr_dict = {}
        STACK_TRACES = bug_oracle["STACK_TRACES"]
        for i, stack_trace in enumerate(STACK_TRACES):
            idx = '#'.join([os.path.split(stack_trace['file'])[-1], str(stack_trace['line'])])

            table = {
                'title': stack_trace['id'],
                'lines': [],
                'collapse': 0 if i == 0 else 1,
                'variables': []
            }

            LINE_NUM = bug_oracle["LINE_NUM"]
            for patch_idx in range(metadata['__num_rows__']):
                table['lines'].append(f'buggy #{LINE_NUM}' if patch_idx == 0 else f'patch #{LINE_NUM + patch_idx}')

            tables.append(table)

            for name in metadata[idx]:
                is_buggy_line = False
                lineno = int(name.split("@@#")[1].split("@@@")[0])
                iterno = int(name.split("@@#")[1].split("@@@")[1])
                if lineno > int(idx.split("#")[1]):
                    lineno += metadata['__num_rows__'] - 1
                if lineno == int(idx.split("#")[1]):
                    lineno += min(list(metadata[idx][name].keys()))
                    is_buggy_line = True
                variable = {
                    'name': name.split("@@#")[0],
                    'identical': 0,
                    'values': [],
                    'position': {
                        'url': stack_trace["file"],
                        'line': lineno,
                        'iter': iterno
                    },
                    'is_serialized': 0,
                    'expand': 0,
                    'buggy_line': is_buggy_line
                }

                value = DUMMY_VALUE

                value_list = [value_to_string(metadata[idx][name][ii]) if ii in metadata[idx][name] else DUMMY_VALUE for
                              ii in range(metadata['__num_rows__'])]
                raw_value_list = [x["type"] for x in value_list]
                counter = Counter(raw_value_list)
                if name.split("@@@")[0] not in bhvr_dict:
                    bhvr_dict[name.split("@@@")[0]] = counter.__len__()
                else:
                    if bhvr_dict[name.split("@@@")[0]] == counter.__len__():
                        continue
                    else:
                        bhvr_dict[name.split("@@@")[0]] = counter.__len__()
                for counter_idx, counter_key in enumerate(counter):
                    counter[counter_key] = counter_idx % 5 + 1
                # if raw_value_list[0] not in raw_value_list[1:]:
                if counter.__len__() > 1:
                    variable['identical'] = 1

                for patch_idx in range(metadata['__num_rows__']):
                    if patch_idx in metadata[idx][name]:
                        value = value_to_string(metadata[idx][name][patch_idx])
                    if len(variable['values']) > 0 and ((value["type"] in counter
                                                         and str(counter[value["type"]]) == variable['values'][-1][
                                                             'color'])
                                                        or variable['identical'] == 0):
                        variable['values'][-1]['merged_columns'] += 1
                    else:
                        variable['values'].append({
                            'val': value["type"],
                            'color': '0' if (patch_idx == 0 and value["type"] in counter) else
                            str(counter[value["type"]]) if value["type"] in counter else '#FFFFFF',
                            'expand_lines': 0,
                            'serialized_val': value["val"],
                            'merged_columns': 1
                        })
                    if value["serialized"]:
                        variable["is_serialized"] = 1
                    value = DUMMY_VALUE
                table['variables'].append(variable)

            table['variables'] = sorted(table['variables'], key=lambda x: x['position']['line'])

        resp.media = {
            'stage': 'instrument',
            'result': tables
        }

        print(resp.media)
        resp.status = falcon.HTTP_200
