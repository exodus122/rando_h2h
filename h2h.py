import math
import isodate
import json
import requests
import datetime as dt

h2h_dict = {}
only_last_6_months = False # update the date below
exclude_forfeits = False
rsl = False

races_to_ignore = [
	"/ootr/foolish-hitman-6686", "/ootr/fancy-joker-0845", "/ootr/superb-sonic-2858", "/ootr/good-charizard-5956", "/ootr/snug-stanley-8914", 
    "/ootr/silly-booyah-8918", "/ootr/shiny-starfox-5460", "/ootr/tasty-glitterworld-8886", "/ootr/sunken-bobomb-4482", "/ootr/grumpy-frankerz-4171", 
    "/ootr/perfect-shadow-2224", "/ootr/outrageous-rikku-8568", "/ootr/lucky-celeste-1554", "/ootr/crafty-roy-7935", "/ootr/dynamic-ramuh-6935", 
    "/ootr/vanilla-cutscene-3816", "/ootr/neutral-terry-8758", "/ootr/secret-boo-3063", "/ootr/neutral-wiggler-2655", "/ootr/brainy-rosalina-0001", 
    "/ootr/dizzy-pichu-8455", "/ootr/mecha-pichu-8730", "/ootr/virtual-bobomb-2478", "/ootr/mecha-waluigi-8484", "/ootr/frantic-palutena-0122", 
    "/ootr/vanilla-squirtle-0008", "/ootr/dazzling-spyro-0662", "/ootr/hungry-ness-0776", "/ootr/cute-magikarp-2640", "/ootr/eager-pipboy-0271", 
    "/ootr/clever-crash-3803", "/ootr/good-tatl-8571", "/ootr/travelling-jynx-3630", "/ootr/silly-fran-3719", "/ootr/funky-squirtle-8170", 
    "/ootr/dapper-ken-3879", "/ootr/brainy-zip-5110", "/ootr/clumsy-doge-5536", "/ootr/wild-luma-5585", "/ootr/prudent-robotnik-4582", 
    "/ootr/salty-shulk-4701", "/ootr/epic-booyah-8904", "/ootr/gnarly-koopa-2338", "/ootr/saucy-resetti-6596", "/ootr/sleepy-star-4192", 
    "/ootr/agreeable-knuckles-8852", "/ootr/clumsy-charizard-9323", "/ootr/outrageous-ken-5788", "/ootr/gnarly-stardrop-8626", 
    "/ootr/zany-meowth-7965", "/ootr/grumpy-snake-6968", "/ootr/elegant-subpixel-6193", "/ootr/brainy-cid-1324", "/ootr/clumsy-epona-8295", 
    "/ootr/silly-pacman-2546", "/ootr/agreeable-impa-6188", "/ootr/dapper-mido-2509", "/ootr/hyper-pierre-4015", "/ootr/bonus-shiro-4790", 
    "/ootr/dynamic-wolfos-7643", "/ootr/dynamax-saburo-5036"
]

def readjson(url, text_only=False, tries=5):

    for i in range(tries):
        response = requests.get(url)
        status = response.status_code

        if status == 200:
            if text_only:
                return response.text
            else:
                return response.json()
        if status == 404:
            return

def validate_race(race): # make sure it is a standard race, and not a teams race. also ignore certain races. also ignore unrecorded races
    if race['goal']['name'] != "Standard Ruleset" and race['goal']['name'] != "Standard Tournament Season 4" and not rsl:
        return False
    if race['goal']['name'] != "Random settings league" and "Random settings league" not in race['goal']['name'] and rsl:
        return False
    
    if "coop" in race['info'].lower() or "co-op" in race['info'].lower() or "multiworld" in race['info'].lower():
        return False
    
    if race['url'] in races_to_ignore:
        return False

    if race['recorded'] == False:
        return False
    
    for entrant in race['entrants']:
        if entrant['team']:
            return False

    return True

def add_race_to_dict(race):
    
    for entrant in race['entrants']:
    
        if entrant['user']['name'] not in h2h_dict:
            h2h_dict[entrant['user']['name']] = {}
            
        if not entrant['place']:
            if race['entrants_count'] != 2 and exclude_forfeits:
                continue
            entrant['place'] = 9999
    
        for entrant2 in race['entrants']:
        
            if entrant['user']['name'] != entrant2['user']['name'] and entrant['place'] != entrant2['place']:
                
                if not entrant2['place']:
                    if race['entrants_count'] != 2 and exclude_forfeits:
                        continue
                    entrant2['place'] = 9999
                
                if entrant2['user']['name'] not in h2h_dict[entrant['user']['name']]:
                    h2h_dict[entrant['user']['name']][entrant2['user']['name']] = [0,0]
            
                if entrant['place'] < entrant2['place']:
                    h2h_dict[entrant['user']['name']][entrant2['user']['name']][0] += 1
                elif entrant['place'] > entrant2['place']:
                    h2h_dict[entrant['user']['name']][entrant2['user']['name']][1] += 1
    
def check_lower(pair):
    key,value = pair
    return (key.lower(),value)


# main routine
page = 1
num_pages = math.inf
done = False
while page <= num_pages:
    json = readjson(f'https://racetime.gg/ootr/races/data?show_entrants=true&page={page}')
    for race in json['races']:
        if not validate_race(race):
            continue
            
        theDate = race['ended_at']
        if theDate:
            theDate = isodate.parse_date(theDate)
        else:
            theDate = dt.date(1970, 1, 1)

        if only_last_6_months and theDate < dt.datetime(day=3,month=5,year=2021).date():
            done = True
            break
        
        add_race_to_dict(race)
        
    if done:
        break
    
    print('completed page '+str(page))
    page += 1
    
    num_pages = json['num_pages'] # json['num_pages']


filename = 'ootr_h2h_'
if only_last_6_months:
    filename += 'past6months_'
else:
    filename += 'alltime_'
    
if rsl:
    filename += 'rsl'
else:
    filename += 'standard'


with open(filename+'.txt', 'w') as f:
    f.writelines("player1\tplayer2\twins\tlosses\n")
    for key, value in sorted(h2h_dict.items(), key=check_lower):
        for key2, value2 in sorted(value.items(), key=check_lower):
            f.writelines(key+'\t'+key2+"\t"+str(value2[0])+"\t"+str(value2[1])+'\n')
