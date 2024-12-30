from patch import PatchRanking, IPR
import json

FILE_NAME = 'MannWhitneyUTest.java'
BUG_ID = 'Math_30'
BUGGY_LINE = "final int n1n2prod = n1 * n2;"

def output_cluster(cluster_data):
    output_data = {}
    for key, value in cluster_data.items():
        tmp = []
        for patch in value:
            tmp.append({
                'code': patch['code'],
                'test_case': patch['test_case']
            })
        output_data[key] = tmp
    with open(f'./cluster_{BUG_ID}_{FILE_NAME}.json', 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f'INFO: Clustered patches of {FILE_NAME} have been dumped into ./cluster_{BUG_ID}_{FILE_NAME}.json')


# # 首先我们展示下PatchRanking这个类怎么用
# pr_1 = PatchRanking(FILE_NAME, BUG_ID, BUGGY_LINE, None)

# ranked_patch = pr_1.get_ranked_patch()
# cluster_data = pr_1.get_cluster_data()

# output_cluster(cluster_data)

# # 注意，这个ranked patch是要最后展示的，但是它是一个数组，每个元素是字典，字典有一个key叫cluster，value是cluster的id，还有一个key叫code，value是patch的代码
# for patch in ranked_patch:
#     print(f"{patch['cluster']}: {patch['code']}")



# 接下来我们展示一下实际中多stage怎么用
# 先初始化一个IPR类
ipr = IPR(FILE_NAME, BUG_ID, BUGGY_LINE)

# 现在我们有一个默认的stage，id是1（也就是咱俩说过的第0层）
print(ipr.patch_data.keys())

# 访问这个stage的数据
ranked_patch = ipr.patch_data[ipr.stage_id].get_ranked_patch()   # 这是要展示的
cluster_data = ipr.patch_data[ipr.stage_id].get_cluster_data()   # 这是存个底

print('cluster dist: ', ipr.cluster_dist)
for patch in ranked_patch:
    print(f"{patch['cluster']}: {patch['code']}")
# print(cluster_data['cluster_3'])

# 假设前端传回来了说要explore一下cluster_3
cluster_id = 'cluster_1'
# 首先get一下当前的stage id
cur_stage = ipr.get_stage_id()
# 然后生成下一步的stage id
next_stage = cur_stage + '_' + cluster_id.split('_')[-1]
# 然后加入这个stage
ipr.set_patch_data(next_stage, cluster_data[cluster_id])
ipr.set_stage_id(next_stage)


# ok, 你得到了全新的ipr
print(ipr.patch_data.keys())
ranked_patch_new = ipr.patch_data[ipr.stage_id].get_ranked_patch()   # 这是要展示的
cluster_data_new = ipr.patch_data[ipr.stage_id].get_cluster_data()   # 这是存个底

# output_cluster(cluster_data_new)
print('cluster dist: ', ipr.cluster_dist)
for patch in ranked_patch_new:
    print(f"{patch['cluster']}: {patch['code']}")




