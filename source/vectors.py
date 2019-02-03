# -*- coding: utf-8 -*-

import io
import operator

import numpy as np

from core.evaluation.labels import Label, NeutralLabel
from core.source.opinion import Opinion


class OpinionVectorCollection:

    def __init__(self, vectors=None):
        self.vectors = {} if vectors is None else vectors

    def add_vector(self, vector):
        assert(isinstance(vector, OpinionVector))
        key = self.__create_key(vector)

        if key in self.vectors:
            print "Vector collection already has a key {}. Ignored".format(
                key.encode('utf-8'))
            return

        self.vectors[key] = vector

    def has_vector(self, vector):
        assert(isinstance(vector, OpinionVector))
        key = self.__create_key(vector)
        return key in self.vectors

    def has_opinion(self, opinion):
        assert(isinstance(opinion, Opinion))
        key = self._create_key(opinion)
        return key in self.vectors

    def find_by_opinion(self, opinion):
        assert(isinstance(opinion, Opinion))
        key = self._create_key(opinion)
        for key, vector in self.vectors.iteritems():
            if (key == self._create_key(opinion)):
                return vector
        return None

    @staticmethod
    def ___create_key(opinion_value_left, opinion_value_right):
        return u"{}_{}".format(opinion_value_left, opinion_value_right)

    @staticmethod
    def __create_key(vector):
        return u"{}_{}".format(vector.value_left, vector.value_right)

    @staticmethod
    def _create_key(opinion):
        return u"{}_{}".format(opinion.value_left, opinion.value_right)

    @classmethod
    def from_file(cls, filepath):
        """ Read the vectors from *.vectors.txt file
        """
        vectors = {}
        with io.open(filepath, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                args = line.split(',')

                opinion_value_left = args[0].strip()
                opinion_value_right = args[1].strip()
                label = Label.from_str(args[len(args) - 1].strip())
                vector = np.array([float(args[i]) for i in range(2, len(args)-1)])

                key = cls.___create_key(opinion_value_left, opinion_value_right)

                vectors[key] = OpinionVector(opinion_value_left, opinion_value_right, vector, label)

        return cls(vectors)

    def get_by_popularity(self, limit=10):
        most_popular = sorted(
            self.vectors.items(),
            key=operator.itemgetter(1).popularity)
        return most_popular[:limit]

    def save(self, filepath):
        """ Save the vectors from *.vectors.txt file
        """
        with open(filepath, 'w') as output:
            for vector in self.vectors.itervalues():
                output.write("{}\n".format(vector.to_unicode().encode('utf-8')))

    def __iter__(self):
        for v in self.vectors.itervalues():
            yield v


class OpinionVector:
    """ Vector of Relation between two values of entities.
    """

    def __init__(self,
                 opinion_value_left,
                 opinion_value_right,
                 vector,
                 label=NeutralLabel,
                 popularity=0):

        assert(isinstance(opinion_value_left, unicode))
        assert(isinstance(opinion_value_right, unicode))
        assert(isinstance(vector, np.ndarray))
        assert(isinstance(label, Label))
        assert(isinstance(popularity, int))
        self.value_left = opinion_value_left
        self.value_right = opinion_value_right
        self.vector = vector
        self.label = label              # sentiment label or 0 in case of neutral
        self.popularity = popularity    # might be used to show an amount of Relations originally

    def set_label(self, label):
        assert(isinstance(label, Label))
        self.label = label

    def to_unicode(self):
        vector_str = ",".join(["%.6f" % v for v in self.vector])
        return u"{}, {}, {}, {}".format(
            self.value_left, self.value_right, vector_str, self.label.to_str())
