# Linkee Main script
import pandas as pd
from question_gen import generate_card
from os.path import exists

practice_list = ['Tom Hanks', 'Harry Potter', 'California', 'Willem Dafoe', 'Allstate', 'Las Vegas', 'Emmerdale',
                 'The Simpsons']
additional_list = ['Spiderman', 'NCIS (TV series)', 'Criminal Minds', 'Charmed', 'Top Gear', 'Julia Roberts']

    # ['iphone', 'Arsenal', 'Belfast', 'Easter', 'Christmas', 'Cadbury', 'Green Goblin', 'Emmerdale']



# make this a command line entry instead and to load from existing df, make a copy and add to
def build_list():
    import requests
    from bs4 import BeautifulSoup

    # url = 'http://www.google.com/search?q=famous hurricanes'
    # page = requests.get(url)
    # soup = BeautifulSoup(page.text, "html.parser")
    # # print(soup.find('cite').text)
    # print(soup.find('cite').text)

    # Carry out a google search

    text = "famous actors"
    url = 'https://google.com/search?q=' + text
    # Fetch the URL data using requests.get(url),
    # store it in a variable, request_result.
    request_result = requests.get(url, timeout=3)

    # Creating soup from the fetched request
    soupwords = BeautifulSoup(request_result.content,
                              "lxml")  # "html.parser")
    # print(soup)
    print(soup.text[0:11])
    # taking top webpage doesn't seem to work even when html issues is fixed


def add_card(input_list):
    # a list of names that want to generate card for
    # Check with some saved db is aleady there
    # easiest is prob read df, check if exists and then add if doesn't
    # df = pd.DataFrame(columns=('Final Answer', 'Answers', 'Questions'))

    file_exists = exists("Linkee_records.csv")
    if file_exists:
        df = pd.read_csv("Linkee_records.csv")
    else:
        df = pd.DataFrame(
            columns=('Final Answer', 'Answer1', 'Question1', 'Answer2', 'Question2', 'Answer3', 'Question3',
                     'Answer4', 'Question4', 'Review'))

    for final_answer in input_list:
        table_list = df['Final Answer'].tolist()
        if final_answer in table_list:
            continue
        # should check if already in table before searching for it.
        l = len(df)
        answers, questions = generate_card(final_answer)
        if answers != 'not_enough_answers':
            df.loc[l] = [final_answer, answers[0], questions[0], answers[1], questions[1], answers[2], questions[2],
                         answers[3], questions[3], "U"]
    df.to_csv("Linkee_records.csv", index=False)
    print("file saved")

    return  # no output


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # answers, questions = generate_card("Tom Hanks")
    # print(answers, questions)
    add_card(additional_list) # + additional_list + city_list)
    print('question')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
# from question_gen import generate_card
# import pandas as pd
# answers, questions = generate_card("Miley Cyrus")
# combined_list = zip(answers, questions)
# df = pd.DataFrame(list(combined_list), columns = ['answers','questions'])
# pd.options.display.max_colwidth = 300
