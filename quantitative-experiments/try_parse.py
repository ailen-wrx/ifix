import csv
import os
import xmltodict
from collections import OrderedDict, Counter
import textwrap

from utils import STACK_TRACES, LINE_NUM

BUG_COLOR = '#F5B7B1'
COLOR_LIST = [
    '#A9CCE3',
    '#AED6F1',
    '#A3E4D7',
    '#A2D9CE',
    '#A9DFBF'
]

IPR_RESULT_LOCATION = "/Users/ruixinwang/.ipr/Math_30/iproutput"

metadata = {}

DUMMY_VALUE = {
    'serialized': False,
    'type': '\\',
    'val': ''
}

def value_to_string(value):
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
                'val': str(value[key])
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
            'val': str(value)
        }


for fname in os.listdir(IPR_RESULT_LOCATION):
    patch_idx, srcfile, line_number = os.path.splitext(fname)[0].split("#")
    patch_idx = int(patch_idx)
    stack_trace_idx = '#'.join([srcfile, line_number])
    if stack_trace_idx not in metadata:
        metadata[stack_trace_idx] = {}
    num_pass = 0
    content = open(os.path.join(IPR_RESULT_LOCATION, fname), "r").read().replace('\r', '')
    with open(os.path.join(IPR_RESULT_LOCATION, fname), "w") as g:
        g.write(content)
    with open(os.path.join(IPR_RESULT_LOCATION, fname), 'r') as f:
        for row in csv.reader(f):
            if row == ['A round starts:']:
                num_pass += 1
                if num_pass > 1: break
            else:
                lineno, status, name, value = row
                if status == "method" or status == "infix" or \
                        (status == "defined") or \
                        (status == "used"):
                    name = f'{name}@@#{lineno}'
                    name = f'##{name}' if (status == "method" or status == "infix") else name
                    if name not in metadata[stack_trace_idx]:
                        metadata[stack_trace_idx][name] = {}
                    metadata[stack_trace_idx][name][patch_idx] = value

                pass

metadata['__num_rows__'] = 0
for stack_trace_idx in metadata:
    if stack_trace_idx == '__num_rows__': continue
    for name in metadata[stack_trace_idx]:
        metadata[stack_trace_idx][name] = dict(OrderedDict(sorted(metadata[stack_trace_idx][name].items())))
        if len(metadata[stack_trace_idx][name]) > metadata['__num_rows__']:
            metadata['__num_rows__'] = len(metadata[stack_trace_idx][name])

tables = []

for i, stack_trace in enumerate(STACK_TRACES):
    idx = '#'.join([os.path.split(stack_trace['file'])[-1], str(stack_trace['line'])])

    table = {
        'title': stack_trace['id'],
        'lines': [],
        'collapse': 0 if i == 0 else 1,
        'variables': []
    }

    for patch_idx in range(metadata['__num_rows__']):
        table['lines'].append(f'buggy #{LINE_NUM}' if patch_idx == 0 else f'patch #{LINE_NUM + patch_idx}')

    tables.append(table)

    for name in metadata[idx]:
        variable = {
            'name': name.split("@@#")[0],
            'lineno': name.split("@@#")[1],
            'identical': 0,
            'values': []
        }

        value = DUMMY_VALUE

        value_list = [value_to_string(metadata[idx][name][ii]) for ii in metadata[idx][name]]
        raw_value_list = [x["type"] for x in value_list]
        counter = Counter(raw_value_list)
        for counter_idx, counter_key in enumerate(counter):
            counter[counter_key] = COLOR_LIST[counter_idx % len(COLOR_LIST)]
        if raw_value_list[0] not in raw_value_list[1:]:
            variable['identical'] = 1

        for patch_idx in range(metadata['__num_rows__']):
            if patch_idx in metadata[idx][name]:
                value = value_to_string(metadata[idx][name][patch_idx])
            variable['values'].append({
                'val': value["type"],
                'color': BUG_COLOR if patch_idx == 0 else counter[value["type"]] if value["type"] in counter else '#FFFFFF',
                'is_serialized': value["serialized"],
                'serialized_val': value["val"],
            })
            value = DUMMY_VALUE
        table['variables'].append(variable)


pass
