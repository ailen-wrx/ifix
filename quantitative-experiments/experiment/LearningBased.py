import torch
import javalang 
from transformers import RobertaTokenizer, RobertaForMaskedLM
import json, copy
from utils.utils import *

def get_context(bug_id, file_name, line_no, tokenizer, model):
    bug_f = open(f'./context/{bug_id}/{file_name}', 'r')
    file_content = bug_f.readlines()

    ret = []
    mask_token = "<mask>"
    pre_code = file_content[:line_no - 1]
    fault_line = file_content[line_no - 1].strip()
    post_code = file_content[line_no:]

    line_size = 100 
    while (1):
        pre_code_input = "</s> " + " ".join([x.strip() for x in pre_code[-line_size:]])
        post_code_input = " ".join([x.strip() for x in post_code[0:line_size]]).replace("\n", "").strip()
        if tokenizer(pre_code_input + fault_line + post_code_input, return_tensors='pt')['input_ids'].size()[1] < 490:
            break
        line_size -= 1
    return pre_code_input, post_code_input

def bert_rerank(model, tokenizer, patch, context):
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    parsed_patch = list(javalang.tokenizer.tokenize(patch))
    new_prob = 0
    for index, p in enumerate(parsed_patch):
        length = len(p.value)
        mask_patch = patch[:p.position.column-1] + '<mask>' + patch[length + p.position.column-1:]
        cur_input = tokenizer(context[0] + mask_patch + context[1], return_tensors='pt').to(device)
        # input_ids = cur_input["input_ids"]
        # attention_mask = cur_input['attention_mask']
        outputs = model(**cur_input)
        mask_token_index = (cur_input.input_ids == tokenizer.mask_token_id)[0].nonzero(as_tuple=True)[0]
        
        prob = outputs['logits'][0, mask_token_index, :].softmax(dim=1)[0].max()
        new_prob += float(prob)
        

    return new_prob


def LearningBased_ranking_result(file_name, bug_id, line_no, model, tokenizer):
    plausible_patches = get_patch_list(file_name, bug_id)
    pre_code_input, post_code_input = get_context(bug_id, file_name, line_no, tokenizer, model)
    tmp_patch = copy.deepcopy(plausible_patches)
    for patch in tmp_patch:
        patch['rk_score'] = bert_rerank(model, tokenizer, patch['code'], [pre_code_input, post_code_input])
    tmp_patch.sort(key=lambda x: x['rk_score'], reverse=True)
    output_ranked_patch(bug_id, tmp_patch, 'LearningBased')
    return tmp_patch

def LearningBased_test():
    print(torch.cuda.is_available())
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    model = RobertaForMaskedLM.from_pretrained("microsoft/codebert-base-mlm").to(device)
    tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base-mlm")
    with open('./data/bug_info.json', 'r') as f:
        bug_info = json.load(f)
        for bi in bug_info:
            LearningBased_ranking_result(bi['FILE_NAME'], bi['BUG_ID'], bi['LINE_NUMBER'], model, tokenizer)
            print(f'{bi["BUG_ID"]} finished!')