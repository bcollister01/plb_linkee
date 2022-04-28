from pattern.text.en import singularize, pluralize
import re


class CleanUpText():
    """Class that contains all clean up text functions"""

    @staticmethod
    def ending_pluralize(noun):
        """Return most appropriate plural of the input word."""
        if re.search('[sxz]$', noun):
            return re.sub('$', 'es', noun)
        elif re.search('[^aeioudgkprt]h$', noun):
            return re.sub('$', 'es', noun)
        elif re.search('y$', noun):
            return re.sub('y$', 'ies', noun)
        else:
            return noun

    def add_s_pluralize(self, noun):
        """Naively add s to end of input word to create plural"""
        return noun + 's'

    def tidy_input(self, input_text):
        """Take input word and tidy it up to create a list of options.

        We have a few different pluralize functions just to account for any
        misspellings online/words created when punctuation removed.
        """

        input_words = input_text.split()

        # Add singular forms of plurals and plural forms of singles
        singles = [singularize(plural) for plural in input_words]
        plurals1 = [pluralize(single) for single in singles]
        plurals2 = [self.ending_pluralize(single) for single in singles]
        plurals3 = [self.add_s_pluralize(single) for single in singles]
        input_words = input_words + singles + plurals1 + plurals2 + plurals3

        input_words = input_words + [word.lower() for word in input_words]
        # If you want capitalized words as well
        input_words = input_words + [word[0].upper() + word[1:] for word in input_text.split()]
        input_words = input_words + [word.upper() for word in input_words]

        input_words = list(set(input_words))

        return input_words

    # Cleanup function to clean up the fact at the end
    @staticmethod
    def cleanup_fact(s):
        """ Cleans up string by removing certain characters """
        strip_refs = re.compile("\.?\[\d+\]?")
        s = strip_refs.sub("", s).strip()

        # Pretty ugly
        if s[-1] == ".":
            s = s[0:-1]

        return s
