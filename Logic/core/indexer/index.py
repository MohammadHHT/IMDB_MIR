import time
import os
import json
import copy
from collections import defaultdict

from .indexes_enum import Indexes, Index_types

class Index:
    def __init__(self, preprocessed_documents: list):
        """
        Create a class for indexing.
        """

        self.preprocessed_documents = preprocessed_documents

        self.index = {
            Indexes.DOCUMENTS.value: self.index_documents(),
            Indexes.STARS.value: self.index_stars(),
            Indexes.GENRES.value: self.index_genres(),
            Indexes.SUMMARIES.value: self.index_summaries(),
        }

    def index_documents(self):
        """
        Index the documents based on the document ID. In other words, create a dictionary
        where the key is the document ID and the value is the document.

        Returns
        ----------
        dict
            The index of the documents based on the document ID.
        """

        #* DONE
        index = {doc['id']:doc for doc in self.preprocessed_documents}
        return index

    def index_stars(self):
        """
        Index the documents based on the stars.

        Returns
        ----------
        dict
            The index of the documents based on the stars. You should also store each terms' tf in each document.
            So the index type is: {term: {document_id: tf}}
        """

        #* DONE
        index = defaultdict(dict)
        for doc in self.preprocessed_documents:
            if stars := doc.get('stars', None):
                for star in stars:
                    for term in star.split():
                        if doc['id'] in index[term]:
                            index[term][doc['id']] += 1
                        else:
                            index[term][doc['id']] = 1
        return index


    def index_genres(self):
        """
        Index the documents based on the genres.

        Returns
        ----------
        dict
            The index of the documents based on the genres. You should also store each terms' tf in each document.
            So the index type is: {term: {document_id: tf}}
        """

        #* DONE
        index = defaultdict(dict)
        for doc in self.preprocessed_documents:
            if genres := doc.get('genres', None):
                for genre in genres:
                    if doc['id'] in index[genre]:
                        index[genre][doc['id']] += 1
                    else:
                        index[genre][doc['id']] = 1
        return index

    def index_summaries(self):
        """
        Index the documents based on the summaries (not first_page_summary).

        Returns
        ----------
        dict
            The index of the documents based on the summaries. You should also store each terms' tf in each document.
            So the index type is: {term: {document_id: tf}}
        """

        #* DONE
        index = defaultdict(dict)
        for doc in self.preprocessed_documents:
            if summaries := doc.get('summaries', None):
                for summary in summaries:
                    for term in summary.split():
                        if doc['id'] in index[term]:
                            index[term][doc['id']] += 1
                        else:
                            index[term][doc['id']] = 1
        return index


    def get_posting_list(self, word: str, index_type: str):
        """
        get posting_list of a word

        Parameters
        ----------
        word: str
            word we want to check
        index_type: str
            type of index we want to check (documents, stars, genres, summaries)

        Return
        ----------
        list
            posting list of the word (you should return the list of document IDs that contain the word and ignore the tf)
        """

        try:
            #* DONE
            return list(self.index[index_type][word].keys())
        except:
            return []

    def add_document_to_index(self, document: dict):
        """
        Add a document to all the indexes

        Parameters
        ----------
        document : dict
            Document to add to all the indexes
        """

        #* DONE
        self.preprocessed_documents.append(document)

        for key, idx in self.index.items():
            if key == Indexes.DOCUMENTS.value:
                idx[document['id']] = document
            else:
                if document[key]:
                    for item in document[key]:
                        for term in item.split():
                            if document['id'] in idx[term]:
                                idx[term][document['id']] += 1
                            else:
                                idx[term][document['id']] = 1    


    def remove_document_from_index(self, document_id: str):
        """
        Remove a document from all the indexes

        Parameters
        ----------
        document_id : str
            ID of the document to remove from all the indexes
        """

        #* DONE
        document = self.index[Indexes.DOCUMENTS.value].pop(document_id, None)

        if document:
            for key, idx in self.index.items():
                if key != Indexes.DOCUMENTS.value:
                    if document[key]:
                        for item in document[key]:
                            for term in item.split():
                                del idx[term][document['id']]
                                if not idx[term]:
                                    del idx[term]

    def delete_dummy_keys(self, index_before_add, index, key):
        if len(index_before_add[index][key]) == 0:
            del index_before_add[index][key]

    def check_if_key_exists(self, index_before_add, index, key):
        if not index_before_add[index].__contains__(key):
            index_before_add[index].setdefault(key, {})


    def check_add_remove_is_correct(self):
        """
        Check if the add and remove is correct
        """

        dummy_document = {
            'id': '100',
            'stars': ['tim', 'henry'],
            'genres': ['drama', 'crime'],
            'summaries': ['good']
        }

        index_before_add = copy.deepcopy(self.index)
        self.add_document_to_index(dummy_document)
        index_after_add = copy.deepcopy(self.index)

        if index_after_add[Indexes.DOCUMENTS.value]['100'] != dummy_document:
            print('Add is incorrect, document')
            return


        self.check_if_key_exists(index_before_add, Indexes.STARS.value, 'tim')

        if (set(index_after_add[Indexes.STARS.value]['tim']).difference(set(index_before_add[Indexes.STARS.value]['tim']))
                != {dummy_document['id']}):
            print('Add is incorrect, tim')
            return

        self.check_if_key_exists(index_before_add, Indexes.STARS.value, 'henry')

        if (set(index_after_add[Indexes.STARS.value]['henry']).difference(set(index_before_add[Indexes.STARS.value]['henry']))
                != {dummy_document['id']}):
            print('Add is incorrect, henry')
            return

        self.check_if_key_exists(index_before_add, Indexes.GENRES.value, 'drama')

        if (set(index_after_add[Indexes.GENRES.value]['drama']).difference(set(index_before_add[Indexes.GENRES.value]['drama']))
                != {dummy_document['id']}):
            print('Add is incorrect, drama')
            return

        self.check_if_key_exists(index_before_add, Indexes.GENRES.value, 'crime')

        if (set(index_after_add[Indexes.GENRES.value]['crime']).difference(set(index_before_add[Indexes.GENRES.value]['crime']))
                != {dummy_document['id']}):
            print('Add is incorrect, crime')
            return

        self.check_if_key_exists(index_before_add, Indexes.SUMMARIES.value, 'good')

        if (set(index_after_add[Indexes.SUMMARIES.value]['good']).difference(set(index_before_add[Indexes.SUMMARIES.value]['good']))
                != {dummy_document['id']}):
            print('Add is incorrect, good')
            return

        # Change the index_before_remove to its initial form if needed

        self.delete_dummy_keys(index_before_add, Indexes.STARS.value, 'tim')
        self.delete_dummy_keys(index_before_add, Indexes.STARS.value, 'henry')
        self.delete_dummy_keys(index_before_add, Indexes.GENRES.value, 'drama')
        self.delete_dummy_keys(index_before_add, Indexes.GENRES.value, 'crime')
        self.delete_dummy_keys(index_before_add, Indexes.SUMMARIES.value, 'good')

        print('Add is correct')

        self.remove_document_from_index('100')
        index_after_remove = copy.deepcopy(self.index)

        if index_after_remove == index_before_add:
            print('Remove is correct')
        else:
            print('Remove is incorrect')

    def store_index(self, path: str, index_name: str = None):
        """
        Stores the index in a file (such as a JSON file)

        Parameters
        ----------
        path : str
            Path to store the file
        index_name: str
            name of index we want to store (documents, stars, genres, summaries)
        """

        if not os.path.exists(path):
            os.makedirs(path)

        if index_name not in self.index:
            raise ValueError('Invalid index name')

        #* DONE
        with open(os.path.join(path, f"{index_name}.json"), 'w') as f:
            json.dump(self.index[index_name], f)

    def load_index(self, path: str):
        """
        Loads the index from a file (such as a JSON file)

        Parameters
        ----------
        path : str
            Path to load the file
        """

        #* DONE
        for index_name in self.index.keys():
            try:
                with open(os.path.join(path, f"{index_name}.json"), 'r') as f:
                    self.index[index_name] = json.load(f)
            except:
                print(f"Not found {index_name}.json in given path")

    def check_if_index_loaded_correctly(self, index_type: str, loaded_index: dict):
        """
        Check if the index is loaded correctly

        Parameters
        ----------
        index_type : str
            Type of index to check (documents, stars, genres, summaries)
        loaded_index : dict
            The loaded index

        Returns
        ----------
        bool
            True if index is loaded correctly, False otherwise
        """

        return self.index[index_type] == loaded_index

    def check_if_indexing_is_good(self, index_type: str, check_word: str = 'good'):
        """
        Checks if the indexing is good. Do not change this function. You can use this
        function to check if your indexing is correct.

        Parameters
        ----------
        index_type : str
            Type of index to check (documents, stars, genres, summaries)
        check_word : str
            The word to check in the index

        Returns
        ----------
        bool
            True if indexing is good, False otherwise
        """

        # brute force to check check_word in the summaries
        start = time.time()
        docs = []
        doc_key = index_type if index_type != 'documents' else 'id'
        
        for document in self.preprocessed_documents:
            if doc_key not in document or document[doc_key] is None:
                continue

            for field in document[doc_key]:
                if check_word in field:
                    docs.append(document['id'])
                    break

            # if we have found 3 documents with the word, we can break
            if len(docs) == 3:
                break

        end = time.time()
        brute_force_time = end - start

        # check by getting the posting list of the word
        start = time.time()
        # TODO: based on your implementation, you may need to change the following line
        posting_list = self.get_posting_list(check_word, index_type)

        end = time.time()
        implemented_time = end - start

        print('Brute force time: ', brute_force_time)
        print('Implemented time: ', implemented_time)

        if set(docs).issubset(set(posting_list)):
            print('Indexing is correct')

            if implemented_time < brute_force_time:
                print('Indexing is good')
                return True
            else:
                print('Indexing is bad')
                return False
        else:
            print('Indexing is wrong')
            return False

# TODO: Run the class with needed parameters, then run check methods and finally report the results of check methods

if __name__ == '__main__':
    with open('data/IMDB_preped.json', 'r') as f:
        docs = json.load(f)

    index = Index(docs)
    path = "data/index/"
    for index_type in Indexes:
        index.store_index(path, index_type.value)

    index.check_add_remove_is_correct()
    index.load_index(path)

    for index_type in index.index:
        loaded_index = index.index[index_type]
        print(f"{index_type} index loaded correctly? ", index.check_if_index_loaded_correctly(index_type, loaded_index))

    print("documents")
    index.check_if_indexing_is_good("documents", 'tt4430212')
    print("stars")
    index.check_if_indexing_is_good("stars", 'Dean')
    print("genres")
    index.check_if_indexing_is_good("genres", 'Musical')
    print("summaries")
    index.check_if_indexing_is_good("summaries", 'Action')
  
    