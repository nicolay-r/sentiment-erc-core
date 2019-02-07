# re-core 0.19.1
![](https://img.shields.io/badge/Python-2.7-brightgreen.svg)

This project is a core library for
[RuSentRel](https://github.com/nicolay-r/RuSentRel) dataset processing and sentiment relation extraction task between mentioned named entities in text.
This library provides API for synonyms, news, opinions, entities files reading.

## Source

### Embeddings

Represents a wrapper over [Word2Vec](https://radimrehurek.com/gensim/models/word2vec.html) model api of [gensim](https://radimrehurek.com/gensim/) library.
This core provides an additional wrappers for:
* News collection from [rusvectores](http://rusvectores.org/ru/models/), which has specific pos prefixes for words of vocabulary;
* Wrapper for additional punctuation signs (tokens) in text, i.e. `":", ";", ".", "!"` etc.

## Processing

### Lemmatization

1. Yandex Mystem wrapper

### Named entities recognition (NER)

Provides wrappers for:
1. DeepPavlov [[repo](https://github.com/deepmipt/ner)]
2. [Texterra](https://texterra.ispras.ru/)

### Syntax parser

Provides wrappers for:
1. INemo SyntaxNet [[repo](https://github.com/IINemo/syntaxnet_wrapper)]
2. Texterra syntax parser [[Texterra](https://texterra.ispras.ru/)]

## Installation

Using [virtualenv](https://www.pythoncentral.io/how-to-install-virtualenv-python/).
Create virtual environment, suppose `my_env`, and activate it as follows:
```
virtualenv my_env
source my_env/bin/activate
```

Then install dependencies as follows:
```
pip install -r dependencies.txt
```
