from gensim.models.word2vec import Word2Vec
from ..env import stemmer


class Embedding(object):
    """
    Represents default wrapper over W2V API.
    """

    def __init__(self, w2v_model):
        assert(isinstance(w2v_model, Word2Vec))
        self.w2v_model = w2v_model

    @property
    def vector_size(self):
        return self.w2v_model.vector_size

    @property
    def vocab(self):
        return self.w2v_model.wv.vocab

    def get_vector_by_index(self, index):
        assert(type(index) == int)
        return self.w2v_model.syn0[index]

    def get_word_by_index(self, index):
        assert(type(index) == int)
        return self.w2v_model.wv.index2word[index]

    def find_index_by_word(self, word):
        assert(type(word) == unicode)
        return self.w2v_model.wv.index2word.index(word)

    @staticmethod
    def from_word2vec_filepath(filepath, is_binary):
        w2v_model = Word2Vec.load_word2vec_format(filepath, binary=is_binary)
        return Embedding(w2v_model)

    def similarity(self, word_1, word_2):
        assert(type(word_1) == unicode)
        assert(type(word_2) == unicode)
        # TODO: Implement similarity.
        pass

    def __contains__(self, item):
        assert(type(item) == unicode)
        return item in self.w2v_model

    def __getitem__(self, item):
        assert(type(item) == unicode)
        return self.w2v_model[item]


class RusvectoresEmbedding(Embedding):

    def __init__(self, w2v_model):
        assert(isinstance(w2v_model, Word2Vec))
        super(RusvectoresEmbedding, self).__init__(w2v_model)

    @staticmethod
    def from_word2vec_filepath(filepath, is_binary):
        w2v_model = Word2Vec.load_word2vec_format(filepath, binary=is_binary)
        return RusvectoresEmbedding(w2v_model)

    def __contains__(self, term):
        assert(type(term) == unicode)

        item = self._lemmatize_term_to_rusvectores(term)
        if item is None:
            return False
        return super(RusvectoresEmbedding, self).__contains__(item)

    def __getitem__(self, term):
        assert(type(term) == unicode)

        item = self._lemmatize_term_to_rusvectores(term)
        if item is None:
            return False
        return super(RusvectoresEmbedding, self).__getitem__(item)

    def find_index_by_word(self, word):
        assert(type(word) == unicode)

        item = self._lemmatize_term_to_rusvectores(word)
        if item is None:
            return False
        return super(RusvectoresEmbedding, self).find_index_by_word(item)

    @staticmethod
    def _lemmatize_term_to_rusvectores(term):
        """ combine lemmatized 'text' with POS tag (part of speech). """
        assert(type(term) == unicode)

        term = stemmer.lemmatize_to_str(term)
        pos = stemmer.get_term_pos(term)
        if pos is stemmer.pos_unknown:
            return None
        return '_'.join([term, pos])
