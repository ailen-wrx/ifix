import numpy as np

def same_token(token1, token2):
    if token1.value == token2.value and type(token1) == type(token2):
        return True
    return False

def levenshtein_distance(patch1, patch2):
    # Implement calculating levenshtein distanse by dynamic planning
    # todo: the costs of add and delete are both 1
    # todo: but here we set the cost of substitute as 2
    # NOTE: Now we use the cost of substitute as 1 (2023-02-22)
    len_patch1 = len(patch1) + 1
    len_patch2 = len(patch2) + 1

    matrix = [0 for n in range(len_patch1 * len_patch2)]

    # first row
    for i in range(len_patch1):
        matrix[i] = i
    # first column
    for j in range(0, len(matrix), len_patch1):
        if j % len_patch1 == 0:
            matrix[j] = j // len_patch1

    for i in range(1, len_patch1):
        for j in range(1, len_patch2):
            if same_token(patch1[i - 1], patch2[j - 1]):
                cost = 0
            else:
                # the cost of substitute
                cost = 1
            matrix[j * len_patch1 + i] = min(
                matrix[(j - 1) * len_patch1 + i] + 1,
                matrix[j * len_patch1 + (i - 1)] + 1,
                matrix[(j - 1) * len_patch1 + (i - 1)] + cost
            )
    return matrix[-1]

def levenshtein_ratio(len1, len2, leven_dist):
    return ((len1 + len2) - leven_dist) / (len1 + len2)

def similarity(patches):
    patch_num = len(patches)
    
    leven_dist = []
    pdist = np.zeros((patch_num * (patch_num - 1) // 2), dtype=np.int8)
    k = 0

    for i in range(patch_num - 1):
        for j in range(i + 1, patch_num):
            levensh = levenshtein_distance(patches[i], patches[j])
            # print(patches[i])
            leven_dist.append({
                'len1': len(patches[i]),
                'len2': len(patches[j]),
                'leven': levensh
            })
            # pdist[k] = levenshtein_ratio(len(patches[i].parse_token), len(patches[j].parse_token), levensh)
            pdist[k] = levensh
            k += 1

    return pdist, leven_dist

