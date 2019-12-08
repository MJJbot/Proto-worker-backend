from gensim.test.utils import datapath
from gensim.models.fasttext import load_facebook_vectors
import numpy as np
from konlpy.tag import Mecab
mecab = Mecab()


class NLPcore():
    def __init__(self):
        self.cap_path = datapath("/home/ubuntu/seungho/fastText/build/run11_chat_mecab_190824.bin")
        self.model = load_facebook_vectors(self.cap_path)
        self.example = self.model['안녕']
        
        
    def get_sentence_vec(self, A):
        res = mecab.morphs(A)
        vec = np.zeros_like(self.example)
        for morph in res:
            vec += self.model[morph]
        return vec
    
    
    def queryDB(self, query, DB):
        TH = 0.9
        DB_vec_list = list(map(self.get_sentence_vec, DB))

        A = np.array(DB_vec_list)
        B = np.array(self.get_sentence_vec(query)).reshape(-1, 1)
        inner = np.matmul(A, B)

        NA = np.linalg.norm(A, axis=1, keepdims=True)
        NB = np.linalg.norm(B, axis=0, keepdims=True)
        norm = np.matmul(NA, NB)
        sim = inner / norm
        print(query)
        print(DB)
        print(np.amax(sim))
        if np.amax(sim) >= TH:
            return np.argmax(sim)
        else:
            return -1


