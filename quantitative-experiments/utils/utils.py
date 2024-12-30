import json
import javalang

def get_parsed_code(code):
    tokens = javalang.tokenizer.tokenize(code)
    try:
        parsed_code = list(tokens)
        return parsed_code
    except TypeError:
        print(code)
        return []

def get_patch_list(file_name, bug_id, parsed=True):
    f = open(f'./patches/{file_name}_{bug_id}.json', 'r')
    patch_data = json.load(f)
    plausible_patches = []
    for patch in patch_data['patches']:
        if patch["correctness"] == 'plausible':
            if parsed: 
                parsed_patch = get_parsed_code(patch["patch"])
                plausible_patches.append({
                    'code': patch["patch"],
                    'parsed_token': parsed_patch,
                })
            else:
                plausible_patches.append({
                    'code': patch["patch"]
                })
    return plausible_patches

def get_buggy_line(buggy_line, parsed=True):
    if parsed:
        parsed_buggy_line = get_parsed_code(buggy_line)
        return {
            'code': buggy_line,
            'parsed_token': parsed_buggy_line
        }
    else:
        return {
            'code': buggy_line
        }

def output_ranked_patch(bug_id, ranked_patch, prompt, format='normal'):
    with open(f'./result/CURE/{bug_id}/{prompt}_rank.java', 'w') as f:
        if format == 'normal':
            for patch in ranked_patch:
                f.write(f"{patch['rk_score']}: {patch['code']}\n")
        elif format == 'CURE':
            for patch in ranked_patch:
                f.write(f"{patch['code']}\n")
        elif format == 's3_kv':
            for key, value in ranked_patch.items():
                f.write(f"{value}: {key}\n")
        