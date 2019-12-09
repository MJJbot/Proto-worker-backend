import tensorflow_hub as hub
import numpy as np
import tensorflow_text
from typing import List


class USE():
    def __init__(self):
        # loading from local
        self.embed = hub.load('/home/ubuntu/seungho/Mujinjang/USE/weights/multilingual_large_2')

        # loading from tf-hub
        # self.embed = hub.load('https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/2')

    def __call__(self, sentence_list):
        if not (isinstance(sentence_list, list) or isinstance(sentence_list, str)):
            raise ValueError
        elif isinstance(sentence_list, str):
            sentence_list = np.asarray([sentence_list])
        return self.embed(sentence_list)['outputs']

    def similarity_matrix(self, database, query):
        """
        :param database: list or str of key
        :param query: list or str of query
        :return: similarity matrix of key row and query column
        """
        if isinstance(database, str):
            database = np.asarray([database])
        elif not (isinstance(database, str) or isinstance(database, list)):
            raise ValueError

        if isinstance(query, str):
            query = np.asarray([query])
        elif not (isinstance(query, str) or isinstance(query, list)):
            raise ValueError

        database_embedding = self.embed(database)['outputs']
        query_embedding = self.embed(query)['outputs']
        similarity_list = np.inner(database_embedding, query_embedding)

        return similarity_list


    def calculate_similarity(self, key, query):
        """
        :param key: str of key
        :param query: str of query
        :return: similairty scalar (np.float32)
        """
        if isinstance(key, str):
            key = np.asarray([key])
        elif not isinstance(key, str):
            raise ValueError

        if isinstance(query, str):
            query = np.asarray([query])
        elif not isinstance(query, str):
            raise ValueError

        key_embedding = self.embed(key)['outputs'][0]
        query_embedding = self.embed(query)['outputs'][0]
        similarity = np.inner(key_embedding, query_embedding)

        return similarity

    def query_db(self, database: List[str], query: str, threshold: float=0.85):
        """
        :param database: list of str of database
        :param query: str to query
        :param threshold: float
        """
        sim = self.similarity_matrix(database, query).squeeze()
        max_value = np.amax(sim)
        if max_value >= threshold:
            max_idx = np.argmax(sim)
            print(f'{query} == {database[max_idx]}')
            print(f'similarity: {max_value}')
            return max_idx
        else:
            print('no similar sentence')
            return -1


if __name__ == '__main__':
    encoder = USE()
    korean_sentence_list = ['님 나이가?', '오늘 방송 일정 뭐임?', '고양이 키움?']
    query = '몇살이에요?'

    sim_matrix = encoder.similarity_matrix(korean_sentence_list, query)
    sim = encoder.calculate_similarity(query, query)
    print(sim_matrix.shape, sim_matrix)
    print(sim)
