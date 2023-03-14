import requests
from discordwebhook import Discord
from discord_webhook import DiscordWebhook, DiscordEmbed
import traceback
import os
import json
import datetime

def discord_webhook(players):

    api = "" #ur api here
    webhook_url = "" #ur webhook discord url here
    link = 'https://euw1.api.riotgames.com'
    webhook = DiscordWebhook(url=f'{webhook_url}')

    excluded_players = ['notorious pro', 'uncheap', 'bredwiners', 'chris dior']

    for player in players:
        if player not in excluded_players:
            try:
                while True:
                    kill_sum = 0
                    assits_sum = 0
                    deaths_sum = 0
                    count_wins = 0
                    count_losses = 0
                    try:
                        while True:
                            try:
                                response = requests.get(f'{link}/lol/summoner/v4/summoners/by-name/{player}?api_key={api}').json()
                                puuid = response['puuid']
                                user_id = response['id']
                                break
                            except:
                                pass
                        users = []
                        horas = []
                        kdas=[]
                        prob_champion = {}

                        response = requests.get(f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?api_key={api}')
                        matches = response.json()
                        del matches[10:20]
                        for m in matches:
                            r = requests.get(f'https://europe.api.riotgames.com/lol/match/v5/matches/{m}?api_key={api}').json()
                            type_queue = ":monkey: Match"
                            cor = 16744192
                            champ = None
                            count_champ = 0
                            gameEndTimestamp = r['info']['gameEndTimestamp']
                            time = gameEndTimestamp // 1000
                            data = datetime.datetime.fromtimestamp(time)
                            data = data.strftime('%Y-%m-%d %H:%M')
                            for participant in r['info']['participants']:
                                if participant['puuid'] == puuid:
                                    worl = f':green_circle:'
                                    kill_sum += participant["kills"]
                                    deaths_sum += participant["deaths"]
                                    assits_sum += participant["assists"]
                                    if participant['win'] is True:
                                        count_wins += 1
                                    elif participant['win'] is False and r['info']['gameDuration']<480:
                                        worl = f':orange_circle:'
                                        count_losses +=1
                                    elif participant['win'] is False:
                                        worl = f':red_circle:'
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
                                        kda = f'{participant["challenges"]["kda"]:.2f}'
                                    except:
                                        kda = 'not found'

                                    emoji = ':arrow_forward:'

                                    if float(kda)<1.5:
                                            emoji = ':skull:'
                                    elif float(kda)<2:
                                        emoji = ':alien:'
                                    elif float(kda)<3:
                                        emoji = ':vampire:'
                                    elif float(kda)<=4:
                                        emoji = ':fire:'
                                    else:
                                        emoji = ':cold_face:'

                                    a = f'''{type_queue} - **{participant["championName"]}** - {participant["kills"]}/{participant["deaths"]}/{participant["assists"]}
                                    '''
                                    c = f'''{emoji} {kda}
                                    '''
                                    b = f'''{worl} {data}
                                    '''
                                    users.append(a)
                                    horas.append(b)
                                    kdas.append(c)

                                    a = f'''{type_queue} - **{participant["championName"]}** - {participant["kills"]}/{participant["deaths"]}/{participant["assists"]}:fire: kda {kda} - {worl:<}
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
                                r2 = requests.get(f'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{user_id}?api_key={api}').json()
                                tier = r2[0]['tier']
                                rank = r2[0]['rank']
                                lp = f"{r2[0]['leaguePoints']} LP"
                            except:
                                tier = 'Unranked'
                                rank = ''
                                lp = '0 LP'
                            try:
                                r3 = requests.get(f'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{user_id}?api_key={api}').json()
                                wins = r3[0]['wins']
                                losses = r3[0]['losses']
                            except:
                                wins = 0
                                losses = 0
                            
                            if (wins==0) and (losses==0):
                                winrate = 'W/L not found'
                            else:
                                winrate = f'{wins/(wins+losses)*100:.2f}'

                        embed = DiscordEmbed(title=f'{tier} {rank}', description=f"""**k/d/a average** {kill_sum/len(matches):.1f}/{deaths_sum/len(matches):.1f}/{assits_sum/len(matches):.1f}
                        **kda average** {((kill_sum/len(matches))+assits_sum/len(matches))/(deaths_sum/len(matches)):.2f}""", color=cor)
                        embed.add_embed_field(name=f'__SCORES LAST 10 GAMES | {count_wins}W/{count_losses}L__ ', value=f"""{''.join([l for l in users])}""")
                        embed.add_embed_field(name=f'__KDA__', value=f'{"".join(k for k in kdas)}')
                        embed.add_embed_field(name=f'__HOURS__', value=f"""{''.join(h for h in horas)}""")
                        embed.set_author(name=f'{player}', url='https://u.gg/', icon_url='https://www.nicepng.com/png/full/10-102337_free-icons-png-peach-png.png')
                        embed.set_footer(text=f"({champ}) - Most Played Champion | {tier} {rank} {lp} | {wins}W {losses}L | {winrate}% WR", icon_url=f"https://opgg-static.akamaized.net/meta/images/lol/champion/{champ}.png")
                        webhook.add_embed(embed)
                        response = webhook.execute()
                        break
                    except Exception as erro:
                        embed = DiscordEmbed(title='__ERROR__', description=f'{traceback.print_exception()}', color=16385285)
                        webhook.add_embed(embed)
                        response = webhook.execute()
            except:
                embed = DiscordEmbed(title=f'__ERROR__', description=f"Dont have the minimum of 10 games played this season", color=15919616)
                embed.set_author(name=f'{player}', url='https://u.gg/', icon_url='https://www.nicepng.com/png/full/10-102337_free-icons-png-peach-png.png')
                embed.set_footer(text=f"(error)", icon_url=f"https://www.pngmart.com/files/7/Danger-Sign-Transparent-Background.png")
                webhook.add_embed(embed)
                response = webhook.execute()
