#################################
##### Name: Chien-wei Tseng
##### Uniqname: cwtseng
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

CACHE_DICT = {}
CACHE_FILE_NAME = "cache.json"

CACHE_DICT_NEAR = {}
CACHE_FILE_NAME_NEAR= "cache_near.json"

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.

    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zipcode-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')

    Instance Methods
    -------------------
    info :
        return information of this instance attributes
        input: none
        return: string
    '''

    def __init__(self, category='w1', name='w2', address='w3', zipcode='w4', phone='w5'):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    url = 'https://www.nps.gov/index.htm'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    soup_detail = soup.find('ul', class_="dropdown-menu SearchBar-keywordSearch")
    soup_detail2 = soup_detail.find_all('a')
    state_url_dict={}
    for i in soup_detail2:
        state_url_dict[i.text.lower()] =  'https://www.nps.gov' + i.attrs['href']
    return state_url_dict

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    url = site_url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    name = soup.find('div', class_="Hero-titleContainer clearfix").find('a').text
    category = soup.find('div', class_="Hero-designationContainer").find('span', class_="Hero-designation").text
    addr = soup.find('span', itemprop="addressLocality").text
    region = soup.find('span', itemprop="addressRegion").text
    addr = f"{addr}, {region}"
    zipcode = soup.find('span', itemprop="postalCode").text.strip()
    phone = soup.find('span', itemprop="telephone").text.strip()
    site = NationalSite(category, name, addr, zipcode, phone)
    return site

def get_site_instance_with_cache(site_url):
    '''Make an instances from a national site URL with cache check.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    request_key = site_url
    if request_key in CACHE_DICT.keys():
        print("Using cache")
        name = CACHE_DICT[request_key]['name']
        category = CACHE_DICT[request_key]['category']
        addr = CACHE_DICT[request_key]['addr']
        zipcode = CACHE_DICT[request_key]['zipcode']
        phone = CACHE_DICT[request_key]['phone']
        site = NationalSite(category, name, addr, zipcode, phone)
    else:
        print("Fetching")
        url = site_url
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        name = soup.find('div', class_="Hero-titleContainer clearfix").find('a').text
        category = soup.find('div', class_="Hero-designationContainer").find('span', class_="Hero-designation").text
        addr = soup.find('span', itemprop="addressLocality").text
        region = soup.find('span', itemprop="addressRegion").text
        addr = f"{addr}, {region}"
        zipcode = soup.find('span', itemprop="postalCode").text.strip()
        phone = soup.find('span', itemprop="telephone").text.strip()

        CACHE_DICT[request_key] = {}
        CACHE_DICT[request_key]['name'] = name
        CACHE_DICT[request_key]['category'] = category
        CACHE_DICT[request_key]['addr'] = addr
        CACHE_DICT[request_key]['zipcode'] = zipcode
        CACHE_DICT[request_key]['phone'] = phone
        save_cache(CACHE_DICT)
        site = NationalSite(category, name, addr, zipcode, phone)
    return site

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    url = state_url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    soup_detail = soup.find_all('div', class_="col-md-9 col-sm-9 col-xs-12 table-cell list_left")
    base_url = 'https://www.nps.gov'
    Nationalsite_list = []
    for i in soup_detail:
        soup_detail2 = i.find('h3').find('a').attrs['href']
        park_url = base_url + soup_detail2 + 'index.htm'
        Nationalsite = get_site_instance_with_cache(park_url)
        Nationalsite_list.append(Nationalsite)
    return Nationalsite_list

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    base_url = 'http://www.mapquestapi.com/search/v2/radius'
    KEY = secrets.API_KEY
    zipcode = site_object.zipcode
    param_dict = {'key':KEY, 'origin':zipcode, 'maxMatches':10, 'radius':10, 'ambiguities':'ignore','outFormat':'json'}
    response = requests.get(base_url,param_dict)
    result = response.json()
    NearPlace_dict = result
    return NearPlace_dict

def get_nearby_places_with_cache(site_object):
    '''Obtain API data from MapQuest API with cache check.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    base_url = 'http://www.mapquestapi.com/search/v2/radius'
    KEY = secrets.API_KEY
    zipcode = site_object.zipcode
    request_key = zipcode
    if request_key in CACHE_DICT_NEAR.keys():
        print("Using cache")
        NearPlace_dict = CACHE_DICT_NEAR[request_key]
    else:
        print('Fetching')
        param_dict = {'key':KEY, 'origin':zipcode, 'maxMatches':10, 'radius':10, 'ambiguities':'ignore','outFormat':'json'}
        response = requests.get(base_url,param_dict)
        result = response.json()
        CACHE_DICT_NEAR[request_key] = result
        save_cache_near(CACHE_DICT_NEAR)
        NearPlace_dict = result

    return NearPlace_dict

def print_near_places(site_name, NearPlace_dict):
    ''' print places result

    Parameters
    ----------
    site_name: string
        name of the site

    NearPlace_dict: dict
        the site's near places dictionay

    Returns
    -------
    None
    '''
    print("-"*50)
    print(f"Places near {site_name}")
    print("-"*50)
    for i in NearPlace_dict['searchResults']:
        name = 'no name'
        category = 'no category'
        address = 'no address'
        city = 'no city'
        if 'name' in i['fields'].keys():
            if i['fields']['name'] == '':
                name = 'no name'
            else:
                name = i['fields']['name']
        if 'category' in i['fields'].keys():
            if i['fields']['address'] == '':
                category = 'no category'
            else:
                category = i['fields']['category']
        if 'address' in i['fields'].keys():
            if i['fields']['address'] == '':
                address = 'no address'
            else:
                address = i['fields']['address']
        if 'city' in i['fields'].keys():
            if i['fields']['city'] == '':
                city = 'no city'
            else:
                city = i['fields']['city']
        place = f"- {name} ({category}): {address}, {city}"
        print(place)

def print_national_sites(state_name, NationalSite_list):
    ''' print sites result
    Parameters
    ----------
    state_name: string
        name of the state

    NationalSite_list: list
        list of sites in the state

    Returns
    -------
    None
    '''
    print("-"*50)
    print(f"List of national sites in {state_name}")
    print("-"*50)
    j = 1
    for i in NationalSite_list:
        print(f"[{j}] {i.info()}")
        j = j+1

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dump_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILE_NAME, "w")
    fw.write(dump_json_cache)
    fw.close()

def open_cache_near():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILE_NAME_NEAR, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache_near(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dump_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILE_NAME_NEAR, "w")
    fw.write(dump_json_cache)
    fw.close()


if __name__ == "__main__":
    CACHE_DICT= open_cache()
    CACHE_DICT_NEAR = open_cache_near()
    state_url_dict = build_state_url_dict()

    state_name = input('Enter a state name (e.g. Michigan, michigan) or "exit" : ')
    while(state_name != "exit"):
        if state_name.lower() in state_url_dict.keys():
            state_url = state_url_dict[state_name.lower()]
            NationalSite_list = get_sites_for_state(state_url)
            print_national_sites(state_name, NationalSite_list)
            search_num = input('Choose the number for detail search or "exit" or "back": ')
            while(search_num != "exit" and search_num != "back"):
                if search_num.isnumeric():
                    if int(search_num)< len(NationalSite_list):
                        NationalSite_inst = NationalSite_list[int(search_num)-1]
                        NearPlace_dict = get_nearby_places_with_cache(NationalSite_inst)
                        site_name = NationalSite_inst.name
                        print_near_places(site_name, NearPlace_dict)
                    else:
                        print(f"[Error] Invalid input")
                        print()
                        print("-"*50)
                search_num = input('Choose the number for detail search or "exit" or "back": ')
            if (search_num == 'back'):
                state_name = input('Enter a state name (e.g. Michigan, michigan) or "exit" : ')
            if (search_num == 'exit'):
                state_name = 'exit'
        else:
            print(f"[Error] Enter a proper state name")
            print()
            state_name = input('Enter a state name (e.g. Michigan, michigan) or "exit" : ')

