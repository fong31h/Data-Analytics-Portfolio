import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re

base_url = 'https://play.limitlesstcg.com'

def create_1_df(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html,'html.parser')
    rows = soup.select('tr')
    deck, deck_links, count, share, score, win = [], [], [], [], [], []
    for row in rows:
        one_row = row.select('td')
        for index, data in enumerate(one_row):
            if index == 2:
                deck.append(data.text)
                deck_links.append(data.a['href'])
            if index == 3:
                count.append(data.text)
            if index == 4:
                share.append(data.text)
            if index == 5:
                score.append(data.text)
            if index == 6:
                win.append(data.text)
    df = pd.DataFrame({'Deck':deck,
                  'Count':count,
                  'Share':share,
                  'Score':score,
                  'Win_Percentage':win,
                    'Deck_links':deck_links})
    return df

def cook_soup(url):
    base_url = 'https://play.limitlesstcg.com'
    r = requests.get(base_url + url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def cook_soups(link_list):
    soups = []
    for link in link_list:
        soup = cook_soup(link)
        soups.append(soup)
    return soups

def create_2_df(soup):
    rows = soup.select('tr')
    player, date, tournament, tournament_url, place, score, lst_url = [], [], [], [], [], [], []
    deck = [soup.select('div[class="name"]')[0].text for i in range(len(rows)-1)]
    
    for row in rows:
        one_row = row.select('td')
        for index, data in enumerate(one_row):
            if index == 0:
                player.append(data.text)
            if index == 1:
                tournament.append(data.text)
                tournament_url.append(data.a['href'])
            if index == 2:
                date.append(data.a['data-time'])
            if index == 3:
                place.append(data.text)
            if index == 4:
                score.append(data.text)
            if index == 5:
                try:
                    lst_url.append(data.a['href'])
                except TypeError:
                    lst_url.append('Decklist not available')
                
    df = pd.DataFrame({'Deck':deck,
                        'Player':player,
                        'Date':date,
                        'Tournament':tournament,
                        'Place':place,
                        'Score':score,
                        'Decklist_url':lst_url,
                          'Tournament_url':tournament_url})
    regex = re.compile(r"(\d{0,4})[a-z]{2} of (\d{0,4})")
    placement, player_total = [], []
    for row in df['Place']:
        try:
            placement.append(int(re.search(regex, row)[1]))
        except TypeError:
            placement.append(None)
        try:
            player_total.append(int(re.search(regex, row)[2]))
        except TypeError:
            player_total.append(None)
    df['Placement'] = placement
    df['Player_Total'] = player_total
    df.drop('Place',axis=1,inplace=True)
    df['Date'] = [datetime.date.fromtimestamp(int(date)/1000) for date in df['Date']]
    #strftime("%B %d, %Y")
    df = df[['Deck', 'Player', 'Date', 'Tournament', 'Placement', 'Player_Total', 'Score', 'Decklist_url', 'Tournament_url']]
    return df

def create_2_dfs(soups):
    df_list = []
    for soup in soups:
        df = create_2_df(soup)
        df.dropna(inplace=True)
        df_list.append(df)
    df = pd.concat(df_list).reset_index(drop=True)
    return df

def scrape_decklist(url):
    request = requests.get(url)
    html = request.text
    soup = BeautifulSoup(html, 'html.parser')
    number, card, version = [], [], []
    regex = re.compile(r"([12]) ([\w'é\-\.]*(?: [\wé\-\.]*)?(?: [\wé\-\.]*)?) ?(\([\w-]*\))?")
    for a in soup.select('a[target="_blank"]'):
        match = re.search(regex, a.text)
        if match is not None:
            number.append(match[1])
            card.append(match[2].strip())
            if match[3] is None:
                version.append('NA')
            else:
                version.append(match[3])
    df = pd.DataFrame({'Amount':number,
                'Card':card,
                'Version':version})
    return df

def add_decklist_column(link_list, df):
    n, length = 0, len(link_list)
    keys, decklists = [], []
    for index, link in enumerate(df['Decklist_url']):
        keys.append(index)
        if link != 'Decklist not available':
            decklist = scrape_decklist(base_url + link)
            decklists.append(decklist)
        else:
            decklists.append('No decklist')
        n += 1
        if n % 50 == 0:
            print(f"{(n / length)*100} %")
    df['Decklists'] = decklists
    return df

def convert_to_json(series):
    new_series = []
    for lst in series:
        if type(lst) != str:
            lst = lst.to_json()
            new_series.append(lst)
        else:
            new_series.append(lst)
    return new_series

def get_bools(column, pokemon_string):
    bools = []
    for decklist in column:
        if decklist.find(pokemon_string) != -1:
            bools.append(True)
        else:
            bools.append(False)
    return bools

def create_finishes_df(df):
    new = pd.DataFrame({'Finishes':['Top 64',
                    'Top 16',
                    'Top 8',
                    'Top 4',
                    '2nd Place',
                    'Tournament Wins'],
                        'Count':[len(df),len(df[df['Placement'] <= 16]),
                                   len(df[df['Placement'] <= 8]),
                                       len(df[df['Placement'] <= 4]),
                                           len(df[df['Placement'] <= 2]),
                                               len(df[df['Placement'] <= 1])]})
        
        
        # data=[len(df),len(df[df['Placement'] <= 16]),
        #                            len(df[df['Placement'] <= 8]),
        #                                len(df[df['Placement'] <= 4]),
        #                                    len(df[df['Placement'] <= 2]),
        #                                        len(df[df['Placement'] <= 1])],
        #      index=['Top 64 Finishes',
        #             'Top 16 Finishes',
        #             'Top 8 Finishes',
        #             'Top 4 Finishes',
        #             '2nd Place Finishes',
        #             'Tournament Wins'])
    return new

def filter_top_finishes(df, pokemon):
    df1 = df[df['Decklists'].str.contains(pokemon)]
    df2 = df1[(df1['Player_Total'] >= 200) & (df1['Placement'] <= 64)].sort_values(['Placement','Player_Total'], ascending=[True, False])
    return df2

def make_score(df):
    df1 = create_finishes_df(df)
    score = df1['Count'][1] * 3
    score += df1['Count'][2] * 6
    score += df1['Count'][3] * 10
    score += df1['Count'][4] * 15
    score += df1['Count'][5] * 25
    score += df1['Count'][0]
    return score

def normalize_score(scores_df):
    for i in range(len(scores)):
        if scores['Expansion'][i] == 'Genetic Apex':
            scores['Score'][i] = float(scores['Score'][i] * .55)
        elif scores['Expansion'][i] == 'Mythical Island':
            scores['Score'][i] = float(scores['Score'][i] * .6)
        elif scores['Expansion'][i] == 'Space-Time Smackdown':
            scores['Score'][i] = float(scores['Score'][i] * .65)
        elif scores['Expansion'][i] == 'Triumphant Light':
            scores['Score'][i] = float(scores['Score'][i] * .7)
        elif scores['Expansion'][i] == 'Shining Revelry':
            scores['Score'][i] = float(scores['Score'][i] * .75)
        elif scores['Expansion'][i] == 'Celestial Guardians':
            scores['Score'][i] = float(scores['Score'][i] * .8)
        elif scores['Expansion'][i] == 'Extradimensional Crisis':
            scores['Score'][i] = float(scores['Score'][i] * .85)
        elif scores['Expansion'][i] == 'Eevee Grove':
            scores['Score'][i] = float(scores['Score'][i] * .9)
        elif scores['Expansion'][i] == 'Wisdom of Sea and Sky':
            scores['Score'][i] = float(scores['Score'][i] * .95)
        elif scores['Expansion'][i] == 'Secluded Springs':
            scores['Score'][i] = float(scores['Score'][i] * 1)
    maxs = max(scores_df['Score'])
    mins = min(scores_df['Score'])
    for score in scores_df['Score']:
        norm = (score / ((maxs - mins))) * 100
        normalized.append(norm)
    normalized = [round(norm,2) for norm in normalized]
    return normalized

def power_ranking_table(df, ex_list):
    scores = []
    expansions = []
    normalized = []
    for name in ex_list:
        exp = df[df['Decklists'].str.contains(name)].sort_values('Date').iloc[0]['Expansion']
        expansions.append(exp)
    for name in ex_list:
        df_ = filter_top_finishes(df, name)
        score = make_score(df_)
        scores.append(score)
    ex_list[ex_list.index('A1-36')] = 'Charizard ex: A1'
    ex_list[ex_list.index('A2b-10')] = 'Charizard ex: A2b'
    ex_list[ex_list.index('A1-96')] = 'Pikachu ex: A1'
    ex_list[ex_list.index('A2b-22')] = 'Pikachu ex: A2b'
    scores = pd.DataFrame({'Pokémon':ex_list,
                           'Score':scores,
                          'Expansion':expansions})
    # for i in range(len(scores)):
    #     if scores['Expansion'][i] == 'Genetic Apex':
    #         scores['Score'][i] = float(scores['Score'][i] * .55)
    #     elif scores['Expansion'][i] == 'Mythical Island':
    #         scores['Score'][i] = float(scores['Score'][i] * .6)
    #     elif scores['Expansion'][i] == 'Space-Time Smackdown':
    #         scores['Score'][i] = float(scores['Score'][i] * .65)
    #     elif scores['Expansion'][i] == 'Triumphant Light':
    #         scores['Score'][i] = float(scores['Score'][i] * .7)
    #     elif scores['Expansion'][i] == 'Shining Revelry':
    #         scores['Score'][i] = float(scores['Score'][i] * .75)
    #     elif scores['Expansion'][i] == 'Celestial Guardians':
    #         scores['Score'][i] = float(scores['Score'][i] * .8)
    #     elif scores['Expansion'][i] == 'Extradimensional Crisis':
    #         scores['Score'][i] = float(scores['Score'][i] * .85)
    #     elif scores['Expansion'][i] == 'Eevee Grove':
    #         scores['Score'][i] = float(scores['Score'][i] * .9)
    #     elif scores['Expansion'][i] == 'Wisdom of Sea and Sky':
    #         scores['Score'][i] = float(scores['Score'][i] * .95)
    #     elif scores['Expansion'][i] == 'Secluded Springs':
    #         scores['Score'][i] = float(scores['Score'][i] * 1)
    # maxs = max(scores['Score'])
    # mins = min(scores['Score'])
    # for score in scores['Score']:
    #     norm = (score / ((maxs - mins))) * 100
    #     normalized.append(norm)
    # normalized = [round(norm,2) for norm in normalized]
    normalized = get_normalized(scores)
    scores['Score'] = normalized
    scores = scores.sort_values('Score',ascending=False).reset_index(drop=True)
    return scores

def filter_nonex_frame(df, cardid):
    indices = []
    for i in range(len(df['Decklists'])):
        f = df['Decklists'][i].find(f'({cardid})')
        if f != -1:
            indices.append(i)
    return df.iloc[indices]

def easy_decklist_filter(df, cardid):
    regex = re.compile(r'A[1234][ab]?-\d{1,3}')
    if re.match(regex, cardid):
        df = filter_nonex_frame(df, cardid)
    else:
        df = df[df['Decklists'].str.contains(cardid)]
    return df.reset_index(drop=True)

def get_partners(df, pokemon):
    regex = re.compile(r"([\w\-']+ ?(?:ex)?) ?([\w-]+ ?(?:ex)?)?")
    partners = []
    filtered = df[df['Deck'].str.contains(pokemon)]
    for deck in filtered['Deck']:
        matches = re.match(regex, deck)
        for i in (1,2):
            if matches[i] != pokemon:
                if matches[i] is not None:
                    partners.append(matches[i].strip())
                else:
                    partners.append(f"Solo {pokemon}")
    partners = pd.Series(partners).value_counts().head(5)
    partners = pd.DataFrame(partners).reset_index().rename(columns={'index':'Partner','count':'Count'})
    return partners