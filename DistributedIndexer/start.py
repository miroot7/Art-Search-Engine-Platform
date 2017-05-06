#!/use/bin/env python3

import subprocess

num_reducers = 4

def indexer():
	# runs three MapReduce programs
    p_invindex = subprocess.Popen(['python3', '-m' 'MapReduceFramework.coordinator', '--mapper_path=DistributedIndexer/mr_apps/invindex_mapper.py', '--reducer_path=DistributedIndexer/mr_apps/invindex_reducer.py', '--input_path=DataFiltering/targets', '--job_path=DistributedIndexer/invindex_jobs', '--num_reducers='+str(num_reducers)])
    p_invindex.wait()


    p_doc = subprocess.Popen(['python3', '-m', 'MapReduceFramework.coordinator', '--mapper_path=DistributedIndexer/mr_apps/docs_mapper.py', '--reducer_path=DistributedIndexer/mr_apps/docs_reducer.py', '--input_path=DataFiltering/targets', '--job_path=DistributedIndexer/docs_jobs', '--num_reducers='+str(num_reducers)])
    p_doc.wait()


    p_idf = subprocess.Popen(['python3', '-m', 'MapReduceFramework.coordinator', '--mapper_path=DistributedIndexer/mr_apps/idf_mapper.py', '--reducer_path=DistributedIndexer/mr_apps/idf_reducer.py', '--input_path=DataFiltering/targets', '--job_path=DistributedIndexer/idf_jobs', '--num_reducers=1'])
    p_idf.wait()


	# python3 -m MapReduceFramework.coordinator --mapper_path=DistributedIndexer/mr_apps/invindex_mapper.py --reducer_path=DistributedIndexer/mr_apps/invindex_reducer.py --input_path=DataFiltering/targets --job_path=DistributedIndexer/invindex_jobs --num_reducers=4

	# python3 -m MapReduceFramework.coordinator --mapper_path=DistributedIndexer/mr_apps/docs_mapper.py --reducer_path=DistributedIndexer/mr_apps/docs_reducer.py --input_path=DataFiltering/targets --job_path=DistributedIndexer/docs_jobs --num_reducers=4

	# python3 -m MapReduceFramework.coordinator --mapper_path=DistributedIndexer/mr_apps/idf_mapper.py --reducer_path=DistributedIndexer/mr_apps/idf_reducer.py --input_path=DataFiltering/targets --job_path=DistributedIndexer/idf_jobs --num_reducers=1


if __name__ == '__main__':
	indexer()
