#Art Search Engine Platform

##Prerequisites
### python3.5+
###python libraries
* See `requirement.txt` attached.

##Usage
* First, from the `DataFiltering` folder, you should be able to run `python -m DataFiltering.DataFiltering` and 
`python -m DataFiltering.collocation` to preprocess the downloaded dataset from MoMA and Wikipedia.

* Next, from the `root directory` of the repo, start the workers by run `python -m MapReduceFramework.workers`
to start the map reduce framework. 

* Then from the same repo, you should be able to run 
`python -m DistributedIndexer.start` 
to acquire inverted index job outputs, IDF job output and document store jobs outputs.

* Then use the command `python -m RelevanceAnalysis.relevant_analysis_start`
to start the relevance analysis MapReduce program and write out the relevant document outputs. 

* After all MapReduce jobs completed, turn off the workers of MapReduce Framework.

* Again from the same repo, you should run the following command 
`python -m TFIDFPreCalculation.DataCombination` to combine the original data sets to one.
and  then `python -m TFIDFPreCalculation.TFIDF_PreCalculation` for pre-calculating Inverted Index, IDF, TF-IDF calculation to avoid calculation during search engine data retrieval to accelerate the data retrieval time after the search engine started running to improve the search engine performance.

* Then execute `python -m RelevanceAnalysis.relevant_extraction` to build the doc-list(docs) results. 
Then, open `url: localhost:port/search?idx_job=x for x in range(4)` and replace port to the port number print on terminal 

* Finally, from the same repo again, run `python -m start_777` to start the search engine. By open url: `url: localhost:port`, replaced by the port number demonstrated on terminal, you can access the search engine and start searching.

##Note
* If you failed to run the command lines above, you may replace all the `python` in the command lines with `python3`
* If you come across "ImportError", you may not fully meet the prerequisites, please install the necessary python
libraries as indicated in `Prerequisites`

##Author
* [Jiaxuan Lu](jl5006@nyu.edu)(jl5006@nyu.edu) 
* [Nan Liu](nl1554@nyu.edu)(nl1554@nyu.edu)
* [Oukan Fan](of394@nyu.edu)(of394@nyu.edu)


