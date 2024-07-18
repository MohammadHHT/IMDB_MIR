from collections import Counter

import numpy as np


class Scorer:
    def __init__(self, index, number_of_documents):
        """
        Initializes the Scorer.

        Parameters
        ----------
        index : dict
            The index to score the documents with.
        number_of_documents : int
            The number of documents in the index.
        """

        self.index = index
        self.idf = {}
        self.N = number_of_documents

    def get_list_of_documents(self, query):
        """
        Returns a list of documents that contain at least one of the terms in the query.

        Parameters
        ----------
        query: List[str]
            The query to be scored

        Returns
        -------
        list
            A list of documents that contain at least one of the terms in the query.

        Note
        ---------
            The current approach is not optimal but we use it due to the indexing structure of the dict we're using.
            If we had pairs of (document_id, tf) sorted by document_id, we could improve this.
                We could initialize a list of pointers, each pointing to the first element of each list.
                Then, we could iterate through the lists in parallel.

        """
        list_of_documents = []
        for term in query:
            if term in self.index.keys():
                list_of_documents.extend(self.index[term].keys())
        return list(set(list_of_documents))

    def get_idf(self, term):
        """
        Returns the inverse document frequency of a term.

        Parameters
        ----------
        term : str
            The term to get the inverse document frequency for.

        Returns
        -------
        float
            The inverse document frequency of the term.

        Note
        -------
            It was better to store dfs in a separate dict in preprocessing.
        """
        #* done?
        idf = self.idf.get(term, None)
        if idf is None:
                self.idf[term] = np.log(self.N / len(self.index[term].keys()))
                return self.idf[term]
        return idf

    def get_query_tfs(self, query):
        """
        Returns the term frequencies of the terms in the query.

        Parameters
        ----------
        query : List[str]
            The query to get the term frequencies for.

        Returns
        -------
        dict
            A dictionary of the term frequencies of the terms in the query.
        """

        #* DONE
        return dict(Counter(query))

    def compute_scores_with_vector_space_model(self, query, method):
        """
        compute scores with vector space model

        Parameters
        ----------
        query: List[str]
            The query to be scored
        method : str ((n|l)(n|t)(n|c).(n|l)(n|t)(n|c))
            The method to use for searching.

        Returns
        -------
        dict
            A dictionary of the document IDs and their scores.
        """

        #* DONE
        query_tfs = self.get_query_tfs(query)
        scores = {}

        docs = self.get_list_of_documents(query)
        doc_method, query_method = method.split('.')

        for doc_id in docs:
            score = self.get_vector_space_model_score(query, query_tfs, doc_id, doc_method, query_method)
            scores[doc_id] = score

        return scores

    def get_vector_space_model_score(
        self, query, query_tfs, document_id, document_method, query_method
    ):
        """
        Returns the Vector Space Model score of a document for a query.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        query_tfs : dict
            The term frequencies of the terms in the query.
        document_id : str
            The document to calculate the score for.
        document_method : str (n|l)(n|t)(n|c)
            The method to use for the document.
        query_method : str (n|l)(n|t)(n|c)
            The method to use for the query.

        Returns
        -------
        float
            The Vector Space Model score of the document for the query.
        """

        #* DONE

        score = 0

        for term in query:
            if doc_dict := self.index.get(term, None):
                tf = doc_dict.get(document_id, 0)
                query_tf = query_tfs.get(term, 0)

                    
                if document_method[0] == 'l':
                    tf = 1 + np.log(tf) if tf < 0 else 0

                if document_method[1] == 't':
                    idf = self.get_idf(term)
                elif document_method[1] == 'n':
                    idf = 1

                if query_method[0] == 'l':
                    query_tf = 1 + np.log(query_tf)  if query_tf < 0 else 0
                
                if query_method[1] == 't':
                    query_idf = self.get_idf(term)
                elif query_method[1] == 'n':
                    query_idf = 1

                w_doc, w_query = tf*idf, query_tf*query_idf
                score += w_doc * w_query

        return score

    def compute_cosine_norm(self, ):
        return 


    def compute_socres_with_okapi_bm25(
        self, query, average_document_field_length, document_lengths
    ):
        """
        compute scores with okapi bm25

        Parameters
        ----------
        query: List[str]
            The query to be scored
        average_document_field_length : float
            The average length of the documents in the index.
        document_lengths : dict
            A dictionary of the document lengths. The keys are the document IDs, and the values are
            the document's length in that field.

        Returns
        -------
        dict
            A dictionary of the document IDs and their scores.
        """

        #* DONE
        scores = {}
        documents = self.get_list_of_documents(query)

        for document_id in documents:
            score = self.get_okapi_bm25_score(query, document_id, average_document_field_length, document_lengths)
            scores[document_id] = score

        return scores

    def get_okapi_bm25_score(
        self, query, document_id, average_document_field_length, document_lengths
    ):
        """
        Returns the Okapi BM25 score of a document for a query.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        document_id : str
            The document to calculate the score for.
        average_document_field_length : float
            The average length of the documents in the index.
        document_lengths : dict
            A dictionary of the document lengths. The keys are the document IDs, and the values are
            the document's length in that field.

        Returns
        -------
        float
            The Okapi BM25 score of the document for the query.
        """

        #* DONE
        k1 = 1.5
        b = 0.75
        score = 0

        doc_len = document_lengths.get(document_id, 0)

        for term in query:
            if term in self.index:
                tf = self.index[term].get(document_id, 0)
                idf = self.get_idf(term)
                term_score = idf * ((tf * (k1 + 1)) /
                                    (tf + k1 * (1 - b + b * (doc_len /
                                                                average_document_field_length)
                                                )
                                    ))
                score += term_score

        return score

    def compute_scores_with_unigram_model(
        self, query, smoothing_method, document_lengths=None, alpha=0.5, lamda=0.5
    ):
        """
        Calculates the scores for each document based on the unigram model.

        Parameters
        ----------
        query : str
            The query to search for.
        smoothing_method : str (bayes | naive | mixture)
            The method used for smoothing the probabilities in the unigram model.
        document_lengths : dict
            A dictionary of the document lengths. The keys are the document IDs, and the values are
            the document's length in that field.
        alpha : float, optional
            The parameter used in bayesian smoothing method. Defaults to 0.5.
        lamda : float, optional
            The parameter used in some smoothing methods to balance between the document
            probability and the collection probability. Defaults to 0.5.

        Returns
        -------
        float
            A dictionary of the document IDs and their scores.
        """

        #* DONE
        scors = {}
        documents = self.get_list_of_documents(query)

        for document_id in documents:
            score = self.compute_score_with_unigram_model(query,
                                                          document_id,
                                                          smoothing_method,
                                                          document_lengths,
                                                          alpha,
                                                          lamda)
            scors[document_id] = score

        return scors

    def compute_score_with_unigram_model(
        self, query, document_id, smoothing_method, document_lengths, alpha, lamda
    ):
        """
        Calculates the scores for each document based on the unigram model.

        Parameters
        ----------
        query : str
            The query to search for.
        document_id : str
            The document to calculate the score for.
        smoothing_method : str (bayes | naive | mixture)
            The method used for smoothing the probabilities in the unigram model.
        document_lengths : dict
            A dictionary of the document lengths. The keys are the document IDs, and the values are
            the document's length in that field.
        alpha : float, optional
            The parameter used in bayesian smoothing method. Defaults to 0.5.
        lamda : float, optional
            The parameter used in some smoothing methods to balance between the document
            probability and the collection probability. Defaults to 0.5.

        Returns
        -------
        float
            The Unigram score of the document for the query.
        """

        #* DONE
        score = 0
        doc_len = document_lengths.get(document_id, 0)
        model_size = sum(document_lengths.values())

        for term in query:
            tf = self.index.get(term, {}).get(document_id, 0)
            model_tf = sum([self.index.get(term, {}).get(doc, 0) for doc in document_lengths.keys()])

            if smoothing_method == 'bayes':
                tf = (tf + alpha) / (doc_len + alpha * len(self.index))
            elif smoothing_method == 'naive':
                tf = tf / doc_len
            elif smoothing_method == 'mixture':
                tf = lamda * (tf / doc_len) + (1 - lamda) * (model_tf / model_size)

            score += np.log(tf) if tf > 0 else 0

        return score
