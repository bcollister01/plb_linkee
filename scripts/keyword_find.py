# from knowledge_graph import get_knowledge_graph_df, classify_input, collect_urls, tailored_search
from clean_text import CleanUpText
import knowledge_graph
# different knowledge
# knowledge_graph.get_knowledge_graph_df()


# Import packages
from pattern.text.en import singularize, pluralize
import wikipedia
import re
import yake
import nltk #For some reason, had to uninstall and reinstall
import numpy as np
import pandas as pd



Clean_text = CleanUpText()

def get_wiki_links(urlList):
    """Extract the URLs linking to Wikipedia from a list of URLs"""
    url_wiki = [urlList[i] for i in range(len(urlList)) if urlList[i].find("wiki") != -1]
    # if len(url_wiki) == 0:
    #   print('No Urls')
    # if url_wiki:
    return (url_wiki)


def get_wiki_text(url_wiki, keep_words=10000):
    """
    Takes a list of urls and scrapes from Wikipedia links
    if present.
    Parameters
    ----------
    urlList (list) : a list of wikipedia urls
    keep_words (integer): the number of words to keep (approx up to paragraph)

    Returns
    -------
    text_comb (string): the text extracted from the paragraphs until word limit
                          reached
    """
    text_comb = ''
    total_words = 0
    key_url_terms = []
    if len(url_wiki) > 1:
        url_terms = [url.split('/wiki/')[1] for url in url_wiki[1:]]
        # limiting to 3 max by the fact the url should be limited like that anyway
        for s in url_terms:
            s = s.replace("_", " ")
            key_term = s.translate(str.maketrans('', '', string.punctuation))
            key_term = " ".join(key_term.split())
            key_url_terms.append(key_term)
    for url in url_wiki:
        wiki_term = url.split('/wiki/')[1]
        print(f"Looking at wiki page for: {wiki_term}")
        try:
            text_wiki = (wikipedia.page(wiki_term, auto_suggest=False)).content
        except KeyError:  # fullurl errors can be caused by unicode or other symbols
            text_wiki = (wikipedia.page(wiki_term, auto_suggest=True)).content
        # This will drop headers surrounded by ==
        text_wiki = re.sub(r'==.*?==+', '', text_wiki)
        paras = text_wiki.split('\n\n')
        word_count = len(paras[0].split())  # number of words in 1st paragraph
        remaining_words = keep_words - total_words
        j = 0
        text = paras[0]
        while word_count < remaining_words and j < len(paras) - 1:
            j += 1
            para_text = paras[j]
            word_count = word_count + len(para_text.split())
            text = text + ' ' + para_text
        # Drop new line /n clutter
        text = text.replace('\n', ' ')
        text = re.sub("\s\s+", " ", text)
        text_comb = text_comb + text  # change if want more than one
        total_words = total_words + word_count
        if total_words >= keep_words:
            break  # break out of for loop when we have enough words

    return text_comb, key_url_terms


def wiki_autosuggest(input, keep_words=10000, suggest=False):
    """
    Gets text from Wikipedia using whichever page is found and cleans up the text

    Parameters
    ----------
    input (string): original input word
    keep_words (integer): number of words to keep
    suggest (Boolean): suggest = True means use wikipedia autosuggest function,
                       False takes the input as is to find the page

    Returns
    -------
    text (string): text that has been cleaned up

    """
    # Get text from single wikipedia page
    try:
        text_wiki = (wikipedia.page(input, auto_suggest=suggest)).content
    except Exception as err:
        print(err.args)
        raise ValueError(f'No urls found for {input}')
        # if no exception raised clean up text
    # This will drop headers surrounded by ==
    text_wiki = re.sub(r'==.*?==+', '', text_wiki)
    paras = text_wiki.split('\n\n')
    word_count = len(paras[0].split())  # number of words in 1st paragraph
    j = 0
    text = paras[0]
    while word_count < keep_words and j < len(paras) - 1:
        j += 1
        para_text = paras[j]
        word_count = word_count + len(para_text.split())
        text = text + ' ' + para_text
    # Drop new line /n clutter
    text = text.replace('\n', ' ')
    text = re.sub("\s\s+", " ", text)
    return text


def find_text(input_text, keep_words=10000, cleanup=True, multi_links=True):
    """
    Finds text related to input that can be used for keyword extraction.
    The text is found in the following order, using wikipedia directly without
    autosuggest (as autosuggest can sometimes have a weird error, e.g Belfast),
    wikipedia using autosuggest, then tries using knowledge graph to find wiki links
    This function attempts to clean up the relevant text if cleanup is set to True.

    Parameters
    ----------

    input_text (string): input word (final answer in Linkee)
    keep_words (integer): the number of words (+to end of paragraph) to keep in text.
    multi_links (Boolean): flag for using more than one wiki page
    text (string): the block of text extracted from wiki

    Returns
    -------

    key_url_terms (list): the page names of any pages used to add to keywords
    """
    key_url_terms = []
    try:
        text = wiki_autosuggest(input_text, keep_words=keep_words, suggest=False)
    except Exception as ex:
        print(f"failed with {ex}")
        try:
            text = wiki_autosuggest(input_text, keep_words=keep_words, suggest=True)
        except Exception as e:
            print(f"failed with {e}")
            knowledge_graph_df = get_knowledge_graph_df(input_text)
            if len(knowledge_graph_df) == 0:
                print("No valid keyword")
                # print("nothing found using knowledge graph, trying wiki")
                return "No valid keyword", []
                # keyword vs
            else:
                # Try to get wiki pages from knowledge graph
                urlList = collect_urls(knowledge_graph_df)
                url_wiki = get_wiki_links(urlList)
                if len(url_wiki) >= 1:
                    keep = min(len(url_wiki), 3)
                    url_wiki = url_wiki[0:keep]
                    if multi_links == False:
                        url_wiki = url_wiki[0:1]
                        text, key_url_terms = get_wiki_text(url_wiki, keep_words)
                else:
                    # Use the knowledge graph categories to find wikipedia url
                    print(" No wiki urls: 1st pass")
                    category = classify_input(knowledge_graph_df)
                    search_input = tailored_search(category, input_text)
                    print(f"Searching for urls with input {search_input}")
                    urlList = collect_urls(get_knowledge_graph_df(search_input))
                    url_wiki = get_wiki_links(urlList)
                    if len(url_wiki) >= 1:
                        keep = min(len(url_wiki), 3)
                        url_wiki = url_wiki[0:keep]
                        if multi_links == False:
                            url_wiki = url_wiki[0:1]
                        text, key_url_terms = get_wiki_text(url_wiki, keep_words)
                    else:
                        print("no wiki pages found")
                        return "No valid keyword", []


    # Text Cleaning
    text = re.sub(r"\'", '', text)  # Get rid of \'
    text = re.sub(r"\\xa0...", '', text)  # Get rid of \\xa0...
    text = re.sub(r"\\n", ' ', text)  # Get rid of \\n
    text = re.sub(r"\\u200e", ' ', text)  # Get rid of \\u200e
    text = re.sub(r"U S ", "US ", text)
    text = re.sub(r"logo", '', text)
    text = re.sub(r"[Vv]iew \d+ more rows", '', text)  # Get rid of [Vv]iew \d+ more rows
    text = re.sub(r"\d+ hours ago", '', text)
    # Remove things like "2009.Power" - no space after full stop
    rx = r"\.(?=[A-Za-z])"
    text = re.sub(rx, ". ", text)
    if cleanup == True:
        text = re.sub(r"[\"\'\“\”\[\]\)\(\•\▽\❖\†]+", '', text)
        text = re.sub(r"[-·—,.;:@#?!$+-]+", ' ', text)

    text = ' '.join(text.split())  # Single spacing

    return text, key_url_terms


def keyword_extract(text, ngram_size):
    """Extract keywords/phrases of ngram_size using YAKE"""
    # Initialise extractor
    kw_extractor = yake.KeywordExtractor()
    language = "en"
    max_ngram_size = ngram_size
    deduplication_threshold = 0.3
    numOfKeywords = 100
    custom_kw_extractor = yake.KeywordExtractor(lan=language,
                                                n=max_ngram_size,
                                                dedupLim=deduplication_threshold,
                                                top=numOfKeywords, features=None)

    # Run extractor on text and get out words/phrases
    yake_output = custom_kw_extractor.extract_keywords(text)
    words, scores = zip(*yake_output)
    words = list(words)
    scores = list(scores)
    words = [re.sub(r"[,.;@#?!$]+", ' ', i) for i in words]
    return (words, scores)


def answer_keyword_compare(keywords_list, input_words):
    """Remove candidate keywords that contain input words"""

    keywords_list = [x for x in keywords_list if not any(i in input_words for i in x.split())]
    return keywords_list


def remove_non_noun_full_keywords(keywords_list):
    """
    Only retain keywords/keyphrases that are proper nouns.
    """
    pos = nltk.pos_tag(keywords_list)
    new_keyword_list = []
    for ii in np.arange(0, len(pos), 1):
        if pos[ii][1] == 'NNP':
            new_keyword_list.append(pos[ii][0])
        if pos[ii][1] == 'NNPS':
            new_keyword_list.append(pos[ii][0])
    return new_keyword_list


def select_keywords(words2):
    """
    Selects the keywords/phrases to use for question generation. Ensures that
    keyword phrases do not overlap each other.
    """
    words3 = []
    words3.append(words2[0])
    del words2[0]
    for i in range(len(words2)):
        # If at any point, we only have 4 candidate keywords left, use them all
        if len(words2) + len(words3) <= 4:
            words3 = words3 + words2
            break
        test_words = words2[0].lower().split()
        singles = [singularize(plural) for plural in test_words]
        plurals1 = [pluralize(single) for single in singles]
        plurals2 = [Clean_text.ending_pluralize(single) for single in singles]
        plurals3 = [Clean_text.add_s_pluralize(single) for single in singles]
        test_words = list(set(test_words + singles + plurals1 + plurals2 + plurals3))
        previous_words = words3.copy()
        previous_words = [word for phrase in previous_words for word in phrase.split()]
        previous_words = [x.lower() for x in previous_words]
        if len(test_words) + len(previous_words) == len(list(set(test_words + previous_words))):
            words3.append(words2[0])
        del words2[0]
    return (words3)


def linkee_keywords(input_text):
    """
    Main pipeline function which takes input and generates list of keywords using
    wikipedia scraping and NLP.

    Parameters
    ---------
    input (string): the input word which is the final Linkee answer

    Returns
    -------
    final_keywords (list): the list of possible keywords
    """
    answer_list = Clean_text.tidy_input(input_text)

    # Keyword extraction
    text, key_url_terms = find_text(input_text)

    # Potentially here combine 1-gram, 2-gram, 3-gram results
    words_df = pd.DataFrame()
    words = (keyword_extract(text, 2))[0]  # + (keyword_extract(text, 1))[0] + (keyword_extract(text, 3))[0]
    scores = (keyword_extract(text, 2))[1]  # + (keyword_extract(text, 1))[1] + (keyword_extract(text, 3))[1]
    words_df['words'] = words
    words_df['scores'] = scores
    words_df.sort_values(by=['scores'], ascending=False)
    words_df = words_df[:100]

    # Adding wikipedia page names to the words found at the top
    words = key_url_terms + words

    # Cleaning up returned keywords
    words2 = answer_keyword_compare(words, answer_list)

    words2 = remove_non_noun_full_keywords(words2)

    final_keywords = select_keywords(words2)

    return (final_keywords)




