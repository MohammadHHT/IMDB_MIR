import hashlib
import itertools
import random
from collections import defaultdict

import numpy as np

class MinHashLSH:
    def __init__(self, documents, num_hashes):
        """
        Initialize the MinHashLSH

        Parameters
        ----------
        documents : list of str
            The input documents for similarity analysis.
        num_hashes : int
            Number of hashes for mini-hashing.
        """
        self.documents = documents
        self.num_hashes = num_hashes

    def shingle_document(self, document, k=2):
        """
        Convert a document into a set of shingles.

        Parameters
        ----------
        document : str
            The input document.
        k : int
            The size of each shingle.

        Returns
        ----------
        set
            A set of shingles.
        """
        shingles = {document[i:i+k] for i in range(len(document) - k + 1)}
        return shingles

    def build_characteristic_matrix(self):
        """
        Build the characteristic matrix representing the presence of shingles in documents.

        Returns
        ----------
        numpy.ndarray
            The binary characteristic matrix.
        """
        #* DONE
        shingles = np.array([self.shingle_document(doc) for doc in self.documents])
        shingles_sum = np.unique(shingles.flatten())
        matrix = np.zeros(shape=(shingles_sum.shape[0], len(self.documents)))
        for i, shingle in enumerate(shingles_sum):
            matrix[i,:] = np.isin(shingle, shingles)
        return matrix

    def min_hash_signature(self):
        """
        Perform Min-Hashing to generate hash signatures for documents.

        Returns
        ----------
        numpy.ndarray
            The Min-Hash signatures matrix.
        """
        #* DONE

        c_matrix = self.build_characteristic_matrix()
        sig_matrix = np.full((self.num_hashes, len(self.documents)), np.inf)
        for row in range(sig_matrix.shape[0]):
            perm = np.random.permutation(c_matrix.shape[0])
            for col in range(sig_matrix.shape[1]):
                ones = np.where(c_matrix[:,col])
                sig_matrix[row, col] = np.min(np.intersect1d(perm, ones))

        return sig_matrix

    def lsh_buckets(self, signature, bands=10, rows_per_band=10):
        """
        Group documents into Locality-Sensitive Hashing (LSH) buckets based on Min-Hash signatures.

        Parameters
        ----------
        signature : numpy.ndarray
            Min-Hash signatures for documents.
        bands : int
            Number of bands for LSH.
        rows_per_band : int
            Number of rows per band.

        Returns
        ----------
        dict
            A dictionary mapping bucket IDs to lists of document indices.
        """
        #* DONE
        if bands * rows_per_band != self.num_hashes:
            raise ValueError("number of hashes must be equal to number of bands times rows_per_band")
        
        buckets = defaultdict(list)

        for doc in range(signature.shape[1]):
            for band in range(bands):
                i = band * rows_per_band
                band_signature = signature[i:i + rows_per_band, doc]
                bucket_id = hashlib.md5(','.join(band_signature).encode('utf8')).hexdigest()
                buckets[bucket_id].append(doc)

        return buckets       

    def perform_lsh(self):
        """
        Perform the entire Locality-Sensitive Hashing (LSH) process.

        Returns
        ----------
        dict
            A dictionary mapping bucket IDs to lists of document indices.
        """
        #* DONE
        signature = self.min_hash_signature()
        bands = 10
        rows_per_band = self.num_hashes // bands
        return self.lsh_buckets(signature, bands, rows_per_band)

    def jaccard_score(self, first_set, second_set):
        """
        Calculate jaccard score for two sets.

        Parameters
        ----------
        first_set : set
            Set of first shingled document.
        second_set : set
            Set of second shingled document.

        Returns
        ----------
        float
            Jaccard score.
        """
        #* DONE
        intersection = len(first_set.intersection(second_set))
        union = len(first_set.union(second_set))

        return intersection / union if union else 0.0

    def jaccard_similarity_test(self, buckets, all_documents):
        """
        Test your near duplicate detection code based on jaccard similarity.

        Parameters
        ----------
        buckets : dict
            A dictionary mapping bucket IDs to lists of document indices.
        all_documents : list
            The input documents for similarity analysis.
        """
        correct_near_duplicates = 0
        all_near_duplicates = 0

        for bucket_id in buckets.keys():
            docs_in_this_bucket = buckets[bucket_id]
            unique_doc_ids = set(docs_in_this_bucket)
            if len(unique_doc_ids) > 1:
                combinations = list(itertools.combinations(unique_doc_ids, 2))
                for comb in combinations:
                    all_near_duplicates += 1

                    first_doc_id = comb[0]
                    second_doc_id = comb[1]

                    first_shingled_doc = self.shingle_document(all_documents[first_doc_id], 2)
                    second_shingled_doc = self.shingle_document(all_documents[second_doc_id], 2)

                    near_duplicated_jaccard_score = self.jaccard_score(first_shingled_doc, second_shingled_doc)
                    current_score = 0

                    for _ in range(5):
                        random_doc_id = first_doc_id
                        while random_doc_id == first_doc_id or random_doc_id == second_doc_id:
                            random_doc_id = random.randint(0, len(all_documents) - 1)
                        random_shingled_doc = self.shingle_document(all_documents[random_doc_id], 2)

                        random_jaccard_score = self.jaccard_score(first_shingled_doc, random_shingled_doc)

                        if near_duplicated_jaccard_score > random_jaccard_score:
                            current_score += 1

                    if current_score == 5:
                        correct_near_duplicates += 1

        # a good score is around 0.8
        print("your final score in near duplicate detection:", correct_near_duplicates / all_near_duplicates)
