import requests
from discordwebhook import Discord
from traceback import print_exc
from dotenv import load_dotenv
import os

load_dotenv()


def discord_webhook(players):

    api_key = os.getenv("api")
    webhook_url = os.getenv("webhook_url")
    link = 'https://euw1.api.riotgames.com'

    excluded_players = ['notorious pro', 'uncheap', 'bredwiners', 'chris dior']

    for player in players:
        if player not in excluded_players:
            kill_sum = 0
            assits_sum = 0
            deaths_sum = 0
            count_wins = 0
            count_losses = 0
            try:
                while True:
                    try:
                        response = requests.get(f'{link}/lol/summoner/v4/summoners/by-name/{player}?api_key={api_key}').json()
                        puuid = response['puuid']
                        user_id = response['id']
                        break
                    except:
                        pass
                users = []
                prob_champion = {}

                response = requests.get(f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?api_key={api_key}')
                matches = response.json()
                del matches[10:20]
                for m in matches:
                    r = requests.get(f'https://europe.api.riotgames.com/lol/match/v5/matches/{m}?api_key={api_key}').json()
                    type_queue = ":monkey: Match"
                    cor = 14712638
                    champ = None
                    count_champ = 0
                    for participant in r['info']['participants']:
                        if participant['puuid'] == puuid:
                            worl = "Win"
                            kill_sum += participant["kills"]
                            deaths_sum += participant["deaths"]
                            assits_sum += participant["assists"]
                            if participant['win'] is True:
                                count_wins += 1
                            elif participant['win'] is False and r['info']['gameDuration']<480:
                                worl = "Remake"
                                count_losses +=1
                            elif participant['win'] is False:
                                worl = "Losse"
                                count_losses +=1

                            if r['info']['queueId']==420:
                                type_queue = ':star: Solo/Duo Ranked Match'
                            if r['info']['queueId']==430:
                                type_queue = ':shark: Blind Pick Match'
                            if r['info']['queueId']==400:
                                type_queue = ':shark: Draft Pick Match'
                            if r['info']['queueId']==440:
                                type_queue = ':star: Flex Ranked Match'

                            try:
                                kda = participant["challenges"]["kda"]
                            except:
                                kda = 'not found'

                            if type(kda) is float:
                                kda = f'{kda:.2f}'

                            a = f'''{type_queue} - **{participant["championName"]}** - {participant["kills"]}/{participant["deaths"]}/{participant["assists"]}:fire: kda {kda} - **{worl}**
                            '''
                            users.append(a)
                                
                            current_champion = participant['championName']

                            if current_champion in prob_champion:
                                prob_champion[current_champion] += 1
                            else:
                                prob_champion[current_champion] = 1

                            break
                    
                    if count_wins >=5:
                        cor = 65323

                    for k,v in prob_champion.items():
                        if v>count_champ:
                            champ = k
                            count_champ = v

                    try:
                        r2 = requests.get(f'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{user_id}?api_key={api_key}').json()
                        tier = r2[0]['tier']
                        rank = r2[0]['rank']
                    except:
                        tier = 'rank'
                        rank = 'not found'
                    try:
                        r3 = requests.get(f'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{user_id}?api_key={api_key}').json()
                        wins = r3[0]['wins']
                        losses = r3[0]['losses']
                    except:
                        wins = 0
                        losses = 0
                    
                    if wins==0 and losses==0:
                        winrate = 'W/L not found'
                    else:
                        winrate = wins/(wins+losses)*100

                    if type(winrate) is float:
                        winrate = f'{winrate:.2f}'

                webhook = Discord(url=f'{webhook_url}')
                webhook.post(embeds=[{
                "title": f"{player}",
                "fields": [{
                    "name": f"__SCORES LAST 10 GAMES | {count_wins}W/{count_losses}L__ ",
                    "value": f"""‎
                    {''.join([l for l in users])}""",
                    "inline": True
                }],
                "color": cor,
                "description": f"""**k/d/a average** {kill_sum/len(matches):.1f}/{deaths_sum/len(matches):.1f}/{assits_sum/len(matches):.1f}
                **kda average** {((kill_sum/len(matches))+assits_sum/len(matches))/(deaths_sum/len(matches)):.2f}""",
                "footer": {
                    "text": f"({champ}) - Most Played Champion | {tier} {rank} | {wins}W {losses}L | {winrate}% WR",
                    "icon_url": f"https://opgg-static.akamaized.net/meta/images/lol/champion/{champ}.png"
                }}])
            except Exception as erro:
                webhook = Discord(url=f'{webhook_url}')
                webhook.post(embeds=[{
                "title": f"{player}",
                "fields": [{    
                    "name": f"__ERROR__ ",
                    "value": f"""SOMETHING WENT WRONG ({erro})
                    {print_exc()}""",
                    "inline": True
                }],
                "color": 15919616,
                "footer": {
                    "text": f"(error)",
                    "icon_url": f"https://www.pngmart.com/files/7/Danger-Sign-Transparent-Background.png"
                }}])