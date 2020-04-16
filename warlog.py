import os
import requests
import datetime

api_host = os.environ.get("API_HOST")
api_token = os.environ.get("API_TOKEN")
proxies = {
    "http": os.environ.get('PROXY_URL', ''),
    "https": os.environ.get('PROXY_URL', ''),
}

all_collection_battles_bonus = 500
final_battle_win = 3500
final_extra_battle_win = 1500
final_battle_skipped = -2000
collection_battle_skipped = -500
collection_battle_max = [
    3 * 990,  # Champion
    3 * 935,  # Master
    3 * 880,  # Challenger
]


def get(clan_tag):
    war_created_dates = []
    clan = send_api_request("/clans/%23{clan_tag}/members".format(clan_tag=clan_tag))
    warlog = send_api_request("/clans/%23{clan_tag}/warlog".format(clan_tag=clan_tag))
    current_war = send_api_request("/clans/%23{clan_tag}/currentwar".format(clan_tag=clan_tag))
    players = {}
    for player in clan['items']:
        players[player['tag']] = {
            'tag': player['tag'],
            'name': player['name'],
            'role': player['role'],
            'lastSeen': to_date(player['lastSeen']).isoformat(),
            'expLevel': player['expLevel'],
            'score': 0,
            'wars': {},
        }
    for war in warlog['items']:
        if war['createdDate'] not in war_created_dates:
            war_created_dates.append(war['createdDate'])
        for participant in war['participants']:
            if participant['tag'] in players:
                war_for_participant = get_war_for_participant(participant, war['createdDate'])
                players[participant['tag']]['wars'][war['createdDate']] = war_for_participant
                players[participant['tag']]['score'] += war_for_participant['score']
    sorted_players = [players[tag] for tag in sorted(players.keys(), key=lambda k: players[k]['score'], reverse=True) if len(players[tag]['wars']) > 0]
    for i, player in enumerate(sorted_players):
        for war_date in war_created_dates:
            if war_date not in player['wars']:
                player['wars'][war_date] = {
                    'createdDate': war_date,
                }
        sorted_players[i]['wars'] = {key: player['wars'][key] for key in sorted(player['wars'].keys(), reverse=True)}
    return {
        'now': datetime.datetime.utcnow().isoformat(),
        'lastWarEndDate': to_date(war_created_dates[0]).isoformat(),
        'ttl': calculate_ttl(current_war).seconds,
        'warlog': sorted_players,
    }


def send_api_request(path):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {api_token}'.format(api_token=api_token),
    }
    response = requests.request("GET", api_host + path, headers=headers, proxies=proxies)
    if response.status_code != 200:
        raise Exception(str(response.json()))

    return response.json()


def get_war_for_participant(participant, war_created_date):
    war = {
        'createdDate': war_created_date,
    }
    if is_cards_earned_max(participant['cardsEarned']):
        war['maxCollectionPointsReached'] = True
    else:
        war['maxCollectionPointsReached'] = False
    war['won'] = participant['wins']
    war['lost'] = participant['battlesPlayed'] - participant['wins']
    war['collectionDayBattlesPlayed'] = participant['collectionDayBattlesPlayed']
    war['score'] = calculate_score(participant)
    return war


def calculate_score(participant):
    score = 0
    if is_cards_earned_max(participant['cardsEarned']):
        score += all_collection_battles_bonus
    if participant['battlesPlayed'] > 0:
        if participant['wins'] == 1:
            score += final_battle_win
        if participant['wins'] == 2:
            score += final_battle_win + final_extra_battle_win
    else:
        score += final_battle_skipped
    score += collection_battle_skipped * (3 - participant['collectionDayBattlesPlayed'])
    return score


def is_cards_earned_max(cards_earned):
    return cards_earned in collection_battle_max


def calculate_ttl(current_war):
    utc_now = datetime.datetime.utcnow()
    if 'warEndTime' in current_war:
        return to_date(current_war['warEndTime']) - utc_now
    if 'collectionEndTime' in current_war:
        return to_date(current_war['collectionEndTime']) + datetime.timedelta(hours=24) - utc_now
    # Default TTL
    return datetime.timedelta(days=2)


def to_date(str_date):
    return datetime.datetime.strptime(str_date, '%Y%m%dT%H%M%S.%fZ')
