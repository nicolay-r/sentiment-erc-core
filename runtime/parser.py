# -*- coding: utf-8 -*-
from core.source.tokens import Tokens
from core.processing.lemmatization.base import Stemmer


class TextParser:
    """
    Represents a parser of news sentences.
    Now uses in neural networks for text processing.
    As a result we have a list of terms, where term could be a
        1) Word
        2) Token
    """

    # TODO: Create unique name based on this template.
    _token_placeholder = "tokenplaceholder"

    def __init__(self):
        pass

    @staticmethod
    def parse_to_list(text, save_tokens=False, stemmer=None, debug=False):
        return TextParser._parse_core(text, save_tokens, stemmer, debug)

    @staticmethod
    def parse(text, save_tokens=False, stemmer=None, debug=False):
        terms = TextParser._parse_core(text, save_tokens, stemmer, debug)
        return ParsedText(terms, keep_tokens=save_tokens, is_lemmatized=stemmer is not None)

    @staticmethod
    def _parse_core(text, save_tokens=False, stemmer=None, debug=False):
        """
        Separates sentence into list of terms

        save_tokens: bool
            keep token information in result list of terms.
        stemmer: None or Stemmer
            apply stemmer for lemmatization
        return: list
            list of unicode terms, where each term: word or token
        """
        assert(isinstance(text, unicode))
        assert(isinstance(save_tokens, bool))
        assert(isinstance(stemmer, Stemmer) or stemmer is None)

        # Separate everything via spaces.
        terms = [w.strip(u' ') for w in text.split(' ')]

        # Process with tokens
        processed_terms = TextParser._process_terms(terms, save_tokens)

        if stemmer is not None:

            # Temp replace tokens with placeholder
            tokens = []
            for i, t in enumerate(processed_terms):
                if Tokens.is_token(t):
                    tokens.append(t)
                    processed_terms[i] = TextParser._token_placeholder

            # Pass to lemmatizer, and then check the result.
            processed_terms = stemmer.lemmatize_to_list(u' '.join(processed_terms))

            # Replace placeholder back
            j = 0
            for i, t in enumerate(processed_terms):
                if t == TextParser._token_placeholder and j < len(tokens):
                    processed_terms[i] = tokens[j]
                    j += 1

        if debug:
            TextParser._print(processed_terms)

        return processed_terms

    @staticmethod
    def _process_terms(terms, save_tokens):
        assert(isinstance(terms, list))
        parsed_terms = []
        for term in terms:

            if term is None:
                continue

            # TODO: return list which combines terms and tokens.
            modified_term, tokens = TextParser._split_tokens(term)

            if modified_term is not None:
                parsed_terms.append(modified_term)

            if len(tokens) > 0 and save_tokens:
                parsed_terms.extend(tokens)

        return parsed_terms


    @staticmethod
    def _split_tokens(term):
        """
        Splitting off tokens from terms ending, i.e. for example:
            term: "сказать,-" -> "(term: "сказать", ["COMMA_TOKEN", "DASH_TOKEN"])
        return: (unicode or None, list)
            modified term and list of extracted tokens.
        """

        tokens_before = []
        tokens_after = []

        number = Tokens.try_create_number(term)
        if number is not None:
            return None, [number]

        url = Tokens.try_create_url(term)
        if url is not None:
            return None, [url]

        first_index = 0
        last_index = len(term) - 1

        # TODO: Fix bug of incorrect order of extracted tokens
        # Refactor, this implementation.
        # Support case
        # w0:w1,w2;w3 -> [w0, 'colon', w1, 'comma', w2, 'semicolon', w3]

        while first_index <= last_index:
            token = Tokens.try_create(term[first_index])
            if token is None:
                break
            tokens_before.append(token)
            first_index += 1

        while last_index >= first_index:
            token = Tokens.try_create(term[last_index])
            if token is None:
                break
            tokens_after.append(token)
            last_index -= 1

        # inplace concat.
        tokens_before.extend(tokens_after[::-1])

        modified_term = term[first_index:last_index+1] if last_index >= first_index else None
        return modified_term, tokens_before

    @staticmethod
    def _print(terms):
        for t in terms:
            print '"{}" '.format(t.encode('utf-8')),


class ParsedText:
    """
    Represents a processed text with extra parameters
    that were used during parsing.
    """

    _number_example = u"0"
    _url_example = u"http://sample.url"

    def __init__(self, terms, keep_tokens, is_lemmatized):
        assert(isinstance(terms, list))
        assert(isinstance(keep_tokens, bool))
        assert(isinstance(is_lemmatized, bool))
        self._terms = terms
        self._mask = None
        self.keep_tokens = keep_tokens
        self.is_lemmatized = is_lemmatized

    def subtext(self, begin, end):
        assert(isinstance(begin, int))
        assert(isinstance(end, int))
        return ParsedText(self._terms[begin:end],
                          keep_tokens=self.keep_tokens,
                          is_lemmatized=self.is_lemmatized)

    @property
    def Terms(self):
        for term in self._terms:
            yield term

    def is_tokenized(self):
        return self._mask is None

    def untokenize(self):
        """
        replace tokens in list of terms with related term.
        """
        self._mask = [False] * len(self._terms)
        for i, term in enumerate(self._terms):

            changed = False
            if term == Tokens.NUMBER:
                self._terms[i] = self._number_example
                changed = True
            elif Tokens.is_token(term):
                self._terms[i] = next(Tokens.iter_chars_by_token(term))
                changed = True

            self._mask[i] = changed

    def tokenize(self):
        """
        revert some terms that were tokens into token values.
        """
        if self._mask is None:
            return

        for i, m in enumerate(self._mask):
            if m is False:
                continue

            if self._terms[i] == self._number_example:
                self._terms[i] = Tokens.NUMBER
            elif self._terms[i] == self._url_example:
                self._terms[i] = Tokens.URL
            else:
                self._terms[i] = Tokens.try_create(self._terms[i])

        self._mask = None

    def __len__(self):
        return len(self._terms)

    def __iter__(self):
        for term in self._terms:
            yield term
