from .index_reader import Index_reader
from .indexes_enum import Indexes, Index_types
import json

class Metadata_index:
    def __init__(self, path='data/index/'):
        """
        Initializes the Metadata_index.

        Parameters
        ----------
        path : str
            The path to the indexes.
        """
        
        #* DONE
        # self.documents = self.read_documents(path)
        self.documents = Index_reader(path, index_name=Indexes.DOCUMENTS).index
        self.metadata_index = self.create_metadata_index()
        self.store_metadata_index(path)

    def read_documents(self, path):
        """
        Reads the documents.
        
        """

        #* DONE
        document_path = path + Indexes.DOCUMENTS.value + '.json'
        with open(document_path, 'r') as file:
            documents = json.load(file)
        return documents

    def create_metadata_index(self):    
        """
        Creates the metadata index.
        """
        metadata_index = {}
        metadata_index['averge_document_length'] = {
            'stars': self.get_average_document_field_length('stars'),
            'genres': self.get_average_document_field_length('genres'),
            'summaries': self.get_average_document_field_length('summaries')
        }
        metadata_index['document_count'] = len(self.documents)

        return metadata_index
    
    def get_average_document_field_length(self, where):
        """
        Returns the sum of the field lengths of all documents in the index.

        Parameters
        ----------
        where : str
            The field to get the document lengths for.
        """

        #TODO
        length = 0
        for doc_id in self.documents.keys():
            doc = self.documents.get(doc_id, {})
            val = doc.get(where, None)
            if val:
                length += len(val)
        return length / len(self.documents)

    def store_metadata_index(self, path):
        """
        Stores the metadata index to a file.

        Parameters
        ----------
        path : str
            The path to the directory where the indexes are stored.
        """
        path =  path + Indexes.DOCUMENTS.value + '_' + Index_types.METADATA.value + '.json'
        with open(path, 'w') as file:
            json.dump(self.metadata_index, file, indent=4)


    
if __name__ == "__main__":
    meta_index = Metadata_index()