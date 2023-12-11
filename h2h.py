import math
import isodate
import json
import requests
import datetime as dt

import unicodedata
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

h2h_dict = {}
winner_list = []
use_date_range = True # update the date below
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

s6_top64 = [
    "WTHH", "Marco", "Exodus", "Aosuna", "Scarlet", "SeYsEy", "juwk", "MrMario7788", "Cola", "Flouche", "Sora", "Goomba", "Sponge", "YUSoEpic", "wordsforswords", "Icola", "Yoyocarina", "FantaTanked", "Cfalcon", "rockchalk", "Kydams", "iceninetm", "idunno", "JustSam", "mrmartin", "gsk8", "Riley", "Oneshot013", "BrotinderDose", "Engel", "RyuuKane", "DubuDeccer", "Rafa", "WoodenBarrel", "Drooness", "Xavi", "Kirox", "Synii", "Jaybone25", "Gavaroni", "CheckRaise", "Alaszun", "EarlWeird", "soli", "Machie", "z3ph1r", "Titou", "Koari", "Volc-41", "Luiferns", "favio94", "MasterAleks", "Challensois_", "docheaps", "tanjo3", "Wafo", "TheAranaut", "MorceauLion64", "Xuross", "Gogeta", "Braaks", "Chuckles501", "Fer", "xenoh"
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
        
    #only get league seeds
    '''if "league" not in race['info'].lower():
        return False'''
    
    #only get s6 test seeds
    '''if "s6" not in race['info'].lower():
        return False'''
    
    #only get Weekly seeds
    '''if "eu weekly" not in race['info'].lower() and "weekly eu" not in race['info'].lower() and "na weekly" not in race['info'].lower() and "weekly na" not in race['info'].lower() and "na standard" not in race['info'].lower() and "eu standard" not in race['info'].lower() and "standard na" not in race['info'].lower() and "standard eu" not in race['info'].lower():
        return False'''
    
    if "coop" in race['info'].lower() or "co-op" in race['info'].lower() or "multiworld" in race['info'].lower() or "mixed" in race['info'].lower():
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
        entrant['user']['name'] = strip_accents(entrant['user']['name'])
        
        if entrant['user']['name'] not in s6_top64:
            continue
        
        if entrant['user']['name'] not in h2h_dict:
            h2h_dict[entrant['user']['name']] = {}
            
        if not entrant['place']:
            if race['entrants_count'] != 2 and exclude_forfeits:
                continue
            entrant['place'] = 9999
    
        for entrant2 in race['entrants']:
            entrant2['user']['name'] = strip_accents(entrant2['user']['name'])
            
            if entrant2['user']['name'] not in s6_top64:
                continue
        
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
                    
        '''
        # weekly winners
        if(entrant['place_ordinal'] == "1st"):
            print(entrant['user']['name'])
            region = ""
            if("na " in race['info'].lower() or " na" in race['info'].lower()):
                region = "NA"
            if("eu " in race['info'].lower() or " eu" in race['info'].lower()):
                region = "EU"
        
            time = str(entrant['finish_time'])
            finish_hours = time[time.index('T')+1:time.index('H')]
            finish_minutes = time[time.index('H')+1:time.index('M')]
            finish_seconds = time[time.index('M')+1:time.index('.')]
            finish_time = finish_hours + ":" + finish_minutes + ":" + finish_seconds
        
            winner_list.append([race['started_at'][:race['started_at'].index('T')], region, str(race['entrants_count']), entrant['user']['name'], finish_time])
        '''
    
def check_lower(pair):
    key,value = pair
    return (key.lower(),value)


# main routine
page = 1
num_pages = 1000
done = False
while page <= num_pages:
    json = readjson('https://racetime.gg/ootr/races/data?show_entrants=true&page='+str(page))
    for race in json['races']:
        
        #print(race)
            
        theDate = race['ended_at']
        if theDate:
            theDate = isodate.parse_date(theDate)
        else:
            theDate = dt.date(1970, 1, 1)

        if use_date_range and theDate < dt.datetime(day=1,month=2,year=2022).date():
            done = True
            break
            
        if not validate_race(race):
            continue
        
        add_race_to_dict(race)
        
    if done:
        break
    
    print('completed page '+str(page))
    page += 1
    
    #num_pages = json['num_pages'] # json['num_pages']


filename = 'ootr_h2h_'
if use_date_range:
    filename += 'daterange_'
else:
    filename += 'alltime_'
    
if rsl:
    filename += 'rsl'
else:
    filename += 'standard'
    
if exclude_forfeits:
    filename += '_no_forfeits'


with open(filename+'.txt', 'w') as f:
    f.writelines("player1\tplayer2\twins\tlosses\n")
    for key, value in sorted(h2h_dict.items(), key=check_lower):
        for key2, value2 in sorted(value.items(), key=check_lower):
            #print(key+'\t'+key2+"\t"+str(value2[0])+"\t"+str(value2[1])+'\n')
            f.writelines(key+'\t'+key2+"\t"+str(value2[0])+"\t"+str(value2[1])+'\n')


'''with open('weeklywinners.txt', 'w') as f:
    f.writelines("date\tregion\tentrants\twinner\ttime\n")
    for x in winner_list:
        f.writelines(x[0]+'\t'+x[1]+"\t"+x[2]+"\t"+x[3]+"\t"+x[4]+'\n')'''
