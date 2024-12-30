from experiment.CURE import *
from experiment.S3 import *
from experiment.LearningBased import *
from experiment.SIMPLE_RANK import *
from experiment.RewardRepair import *
from experiment.KNOD import *
from MCR_test import *
import argparse

def main(test):
    if test == 'CURE':
        CURE_test()
    elif test == 'S3':
        S3_test()
    elif test == 'LearningBased':
        LearningBased_test()
    elif test == 'SIMPLE_RANK':
        SIMPLERANK_test()
    elif test == 'RewardRepair':
        RewardRepair_test()
    elif test == 'KNOD':
        KNOD_test()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run experiments for RQ4 and RQ5.')
    parser.add_argument('--rq4', action='store_true', help='Run experiments for RQ4')
    parser.add_argument('--rq5', action='store_true', help='Run experiments for RQ5')
    args = parser.parse_args()

    print("Running iFix patch clustering and sampling on CURE patches.")
    MCR_test()

    if args.rq4:
        print("Evaluating for RQ4: Compared with other patching ranking methods, how effective is the patch clustering and sampling algorithm in terms of the final rank of the correct patch?")
        print("Baseline: original ranking of CURE")
        main('CURE')
        print("Baseline: static patch ranking (S3)")
        main('S3')
        print("Baseline: learning-based patch ranking (Alpharepair)")
        main('LearningBased')
        print("Baseline: similarity-based ranking (ablation study)")
        main('SIMPLE_RANK')

    if args.rq5:
        print("Evaluating for RQ5: How sensitive is the patch clustering and sampling algorithm to the underlying APR techniques?")
        print("Tool: RewardRepair")
        main('RewardRepair')
        print("Tool: KNOD")
        main('KNOD')