import os
import pickle


def combineDocs():

    combined = dict()

    input_path = 'IndexingRetrieval/relevance_docs/tmpDocs/'
    infs = [f for f in os.listdir(input_path) if f.startswith('relevantDocs')]
    infiles = [os.path.join(input_path, f) for f in infs]


    for f in infiles:
        doc_docs = pickle.load(open(f,'rb'))
        combined.update(doc_docs)

    pickle.dump(combined, open('IndexingRetrieval/relevance_docs/relevantDocs', 'wb'))


if __name__ == '__main__':
    combineDocs()


# len 0 : 4319 
# len 1 : 4383
# len 2 : 4455
# len 3 : 4297
# total : 17454


# test result
"""
test = []
for f in infiles:
    d = pickle.load(open(f,'rb'))
    test.append(d)
for i in range(len(test)):
    print(len(test[i]))
"""