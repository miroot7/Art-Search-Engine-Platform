#!/use/bin/env python3

import subprocess

num_reducers = 4


def relevant_analysis():
	# runs three MapReduce programs
    p_rel = subprocess.Popen(['python3', '-m' 'MapReduceFramework.coordinator', '--mapper_path=RelevanceAnalysis/mr_apps/relevance_analysis_mapper.py', '--reducer_path=RelevanceAnalysis/mr_apps/relevance_analysis_reducer.py', '--input_path=DataFiltering/targets', '--job_path=RelevanceAnalysis/relevance_jobs', '--num_reducers='+str(num_reducers)])
    p_rel.wait()

    # python3 -m MapReduceFramework.coordinator --mapper_path=RelevanceAnalysis/mr_apps/relevance_analysis_mapper.py --reducer_path=RelevanceAnalysis/mr_apps/relevance_analysis_reducer.py --input_path=DataFiltering/targets --job_path=RelevanceAnalysis/relevance_jobs --num_reducers=60


if __name__ == '__main__':
	relevant_analysis()
