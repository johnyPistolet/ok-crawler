import pickle
import re

import requests
from bs4 import BeautifulSoup

from utils import Constants
from utils import Utils

s = requests.Session()

print('\n\n---RESTORE COOKIES---\n\n')

try:
    pickle_file = open('cookies.txt', 'rb')
    session_cookie = pickle.load(pickle_file)
    cookie_jar = requests.utils.cookiejar_from_dict(session_cookie)
    s.cookies.update(cookie_jar)
except IOError:
    session_cookie = ''
except EOFError:
    session_cookie = ''
except ImportError:
    session_cookie = ''
except TypeError:
    session_cookie = ''
except ValueError:
    session_cookie = ''

print("session cookie = " + str(session_cookie))

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/53.0.2785.143 Safari/537.36',
    'Host': 'www.ok.ru',
    'Connection': 'keep-alive',
}

url = 'https://ok.ru/'
r = s.get(url, headers=headers, timeout=5, cookies=session_cookie)

soup = BeautifulSoup(r.text, 'html.parser')
anonym_content = soup.find_all('div', id='anonymPageContent')
print('\nanonym_content size = {}'.format(len(anonym_content)))

if len(anonym_content) > 0:
    # AUTHORIZATION

    print('\n\n---NEED AUTHORIZATION---\n\n')

    login = '380999583285'
    password = '6Pb755ERzoWD2gd7'

    payload = {
        'st.email': login,
        'st.password': password,
        'st.posted': 'set',
        'st.st.screenSize': '1440+x+900',
        'st.st.browserSize': '802',
        'st.st.flashVer': '32.0.0',
        'st.iscode': 'false',
        'st.originalaction': 'https://ok.ru/dk?cmd=AnonymLogin&st.cmd=anonymLogin'
    }

    url = '''https://ok.ru/https'''
    r = s.post(url, data=payload, cookies=session_cookie, headers=headers, timeout=5)

    if r.status_code == 200:
        print('\n\n---LOGIN SUCCESSFULLY---\n\n')

        soup = BeautifulSoup(r.text, 'html.parser')
        toolbar = soup.find_all('div', attrs={"class": "toolbar"})
        toolbar_len = len(toolbar)
        print('toolbar size = {}'.format(toolbar_len))

        avatar = soup.find_all('img', attrs={"id": "viewImageLinkId"})
        avatar_len = len(avatar)
        print('avatar size = {}\n'.format(avatar_len))

        assert toolbar_len > 0 & avatar_len > 0, "Authorization failed"

        session_cookie = requests.utils.dict_from_cookiejar(s.cookies)
        print("session_cookie_dict = " + str(session_cookie))

        with open('cookies.txt', 'wb') as outfile:
            pickle.dump(session_cookie, outfile)

        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/53.0.2785.143 Safari/537.36',
            'Host': 'www.ok.ru',
            'Connection': 'keep-alive',
        }
else:
    toolbar = soup.find_all('div', attrs={"class": "toolbar"})
    print('\n')
    toolbar_len = len(toolbar)
    print('toolbar size = {}'.format(toolbar_len))

    avatar = soup.find_all('img', attrs={"id": "viewImageLinkId"})
    avatar_len = len(avatar)
    print('avatar size = {}\n'.format(avatar_len))

    assert toolbar_len > 0 and avatar_len > 0, "Authorization failed"

print('\n\n---SEARCH FIRST GROUPS PAGE---\n\n')

for search_query in Constants.DEMO_KEY_WORDS:
    url = '''https://ok.ru/search?st.mode=Groups&st.grmode=Groups&st.posted=set&st.query=
        {}'''.format(search_query)
    r = s.get(url, headers=headers, cookies=session_cookie, timeout=5)

    assert r.status_code == 200, "UNABLE TO GET FIRST GROUPS PAGE"

    print('\n\n---PARSE gwt.requested---\n\n')

    gwt_requested = 0
    soup = BeautifulSoup(r.text, 'html.parser')
    gwt_hash_element = soup.findAll('script', type='text/javascript', text=re.compile('.*,gwtHash:.*'))[0]
    splits = re.split(",", str(gwt_hash_element))
    for split in splits:
        if split.__contains__('gwtHash'):
            basic_splits = re.split(":", str(split))
            gwt_split = basic_splits[1]
            gwt_requested = re.sub('''"''', '''''', gwt_split)
            print('GWT HASH VALUE = {}\n\n'.format(gwt_requested))

    group_elements = soup.findAll('div', attrs={"class": "gs_result_i_w gs_result_group-card"})
    print('Groups count = {}\n'.format(len(group_elements)))
    for group_element in group_elements:
        # parse group data
        group_data = Utils.parse_group_tag(group_element, s, headers=headers)
        print('GROUP DATA = {}'.format(group_data))

    print('\n\n---SEARCH OTHER GROUPS PAGE---\n')

    page = 49
    while page <= 50:

        print('\n---SEARCH GROUPS PAGE #{}---'.format(page))

        path = '/search?cmd=PortalSearchResults&st.cmd=searchResult' \
               '&st.mode=Groups&st.query={}&st.grmode=Groups' \
               '&st.page={}&fetch=false&st.loaderid=PortalSearchResultsLoader' \
               '&st.posted=set&gwt.requested={}&'.format(search_query, page, gwt_requested)

        url = 'https://ok.ru' + path

        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/53.0.2785.143 Safari/537.36',
            'Host': 'www.ok.ru',
        }

        r = s.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            group_elements = soup.findAll('div', attrs={"class": "gs_result_i_w gs_result_group-card"})
            print('Groups count {}\n'.format(len(group_elements)))

            for group_element in group_elements:
                # parse group data
                group_data = Utils.parse_group_tag(group_element, s, headers=headers)
                print('GROUP DATA = {}'.format(group_data))

        page += 1
