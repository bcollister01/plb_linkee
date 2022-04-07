# For Google Knowledge Graph API
import requests
import urllib
import json
import os
import pandas as pd
from pattern.text.en import singularize, pluralize
from requests_html import HTML
from requests_html import HTMLSession


# Next few functions sourced from https://practicaldatascience.co.uk/data-science/how-to-access-the-google-knowledge-graph-search-api

def get_source(url):
    """Returns the source code for the provided URL.

    Parameters
      ----------
    url (string): URL of the page to scrape.

    Returns
    -------
    response (object): HTTP response object from requests_html.
    """

    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)


def get_knowledge_graph(api_key, query):
    """Return a Google Knowledge Graph for a given query.

    Parameters
    ----------
    api_key (string): Google Knowledge Graph API key.
    query (string): Term to search for.

    Returns
    -------
    response (object): Knowledge Graph response object in JSON format.
    """

    endpoint = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'query': query,
        'limit': 10,
        'indent': True,
        'key': api_key,
    }

    url = endpoint + '?' + urllib.parse.urlencode(params)
    response = get_source(url)

    return json.loads(response.text)


def get_knowledge_graph_df(input):
    """
    Uses Google's knowledge graph to generate Pandas DataFrame of entities
    deemed most similar to input searched. DataFrame includes categorization
    of entity, title, short description and URL (usually to Wikipedia).
    You will need to have set up an API key in Google Cloud Console to get this
    to work (it's free to do and you can do 100k requests a day I believe.)
    https://console.cloud.google.com/apis
    Parameters
    ----------
    input (string): Final Linkee answer

    Returns
    -------
    knowledge_graph_df (Pandas DataFrame): info on Knowledge Graph results
    """
    threshold = 0.2
    api_key = os.environ['GOOGLE_LINKEE_KEY']
    knowledge_graph_json = get_knowledge_graph(api_key, input)
    knowledge_graph_df = pd.json_normalize(knowledge_graph_json, record_path='itemListElement')
    return knowledge_graph_df
    # Only using scores if knowledge graph actually returns something
    if len(knowledge_graph_df) > 0:
        max_score = max(knowledge_graph_df['resultScore'])
        knowledge_graph_df = knowledge_graph_df.loc[knowledge_graph_df['resultScore'] > threshold * max_score]
        index_match = knowledge_graph_df.index[knowledge_graph_df['result.name'] == input]
        if len(index_match) == 1:
            n = index_match[0]
            knowledge_graph_df = pd.concat([knowledge_graph_df.iloc[[n], :], knowledge_graph_df.drop(n, axis=0)],
                                           axis=0)
            knowledge_graph_df.reset_index(inplace=True, drop=True)
    return knowledge_graph_df


def classify_input(knowledge_graph_df):
    """Classify the input word/phrase as a certain category
    to improve search results. Acts as failsafe if initial search
    of input fails.

    Parameters
    ----------
    knowledge_graph_df: Return of get_knowledge_graph_df

    Returns
    -------
    category (string): Category of input

    """
    if "SportsTeam" in knowledge_graph_df['result.@type'][0]:
        entity_tags = knowledge_graph_df['result.@type'][1]
    else:
        entity_tags = knowledge_graph_df['result.@type'][0]

    if ("Movie" in entity_tags) or ("MovieSeries" in entity_tags):
        category = "Movie"
    elif ("TVEpisode" in entity_tags) or ("TVSeries" in entity_tags):
        category = "TV"
    elif ("VideoGame" in entity_tags) or ("VideoGameSeries" in entity_tags):
        category = "VideoGame"
    elif ("Book" in entity_tags) or ("BookSeries" in entity_tags):
        category = "Book"
    elif "Person" in entity_tags:
        category = "Person"
    elif ("MusicAlbum" in entity_tags) or ("MusicGroup" in entity_tags) or ("MusicRecording" in entity_tags):
        category = "Music"
    elif ("Place" in entity_tags) or ("AdministrativeArea" in entity_tags):
        category = "Place"
    else:
        category = "Thing"

    return (category)


def tailored_search(category, input):
    """Change the search to get better keywords for input, based on its category

    Parameters
    ----------
    category (string): Category of input
    input (string): Final Linkee answer

    Returns
    -------
    search_input (string): Search term to use to find keywords

    """
    if category == "Movie" or category == "TV" or category == "Book":
        search_input = input + " " + category + " information"
    elif category == "Place":
        search_input = input + " location"
    else:
        search_input = input
    return (search_input)


def collect_urls(knowledge_graph_df):
    """Collect the urls from the knowledge graph to give more options to scrape
    from.

    Parameters
    ----------
    knowledge_graph_df: Return of get_knowledge_graph_df

    Returns
    -------
    list of urls (string): urls found

    """
    if 'result.detailedDescription.url' in knowledge_graph_df.columns:
        knowledge_graph_df = knowledge_graph_df[knowledge_graph_df['result.detailedDescription.url'].notna()]
        urlList = knowledge_graph_df['result.detailedDescription.url'].tolist()
    else:
        urlList = []
    return urlList
