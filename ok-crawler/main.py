import distutils.util
import os
import pickle
import random
import re
import time

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
print(("session cookie = " + str(session_cookie)))
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/53.0.2785.143 Safari/537.36',
    # 'Host': 'www.ok.ru',
    'Connection': 'keep-alive',
}
url = 'https://ok.ru/'
r = s.get(url, headers=headers, timeout=5, cookies=session_cookie)
soup = BeautifulSoup(r.text, 'html.parser')
anonym_content = soup.find_all('div', id='anonymPageContent')
if len(anonym_content) > 0:
    # AUTHORIZATION
    print('\n\n---NEED AUTHORIZATION---\n\n')
    login = '380999583285'
    password = '6Pb755ERzoWD2gd7'
    # login = 'stepan_stepanovvv'
    # password = 'xKgdvs5zFcjyGyRX'
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
        # AUTHORIZATION - SUCCESSFULLY
        print('\n\n---LOGIN SUCCESSFULLY---\n\n')
        soup = BeautifulSoup(r.text, 'html.parser')
        toolbar = soup.find_all('div', attrs={"class": "toolbar"})
        toolbar_len = len(toolbar)
        avatar = soup.find_all('img', attrs={"id": "viewImageLinkId"})
        avatar_len = len(avatar)
        if avatar_len > 0 and toolbar_len > 0:
            session_cookie = requests.utils.dict_from_cookiejar(s.cookies)
            print(("session_cookie_dict = " + str(session_cookie)))
            with open(Constants.OK_SESSION_COOKIES_FILE_NAME, 'wb') as outfile:
                pickle.dump(session_cookie, outfile)
            headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/53.0.2785.143 Safari/537.36',
                # 'Host': 'www.ok.ru',
                'Connection': 'keep-alive',
            }
        else:
            # clear previously saved cookies
            if os.path.exists(Constants.OK_SESSION_COOKIES_FILE_NAME):
                os.remove(Constants.OK_SESSION_COOKIES_FILE_NAME)
                assert 1, "Authorization failed. Cookies removed.\nPLEASE TRY AGAIN!!!!!!"
            assert 1, "Authorization failed.\nCHECK ok.ru CREDENTIALS!!!!!!"
    else:
        assert 1, "Authorization failed.\nCHECK ok.ru CREDENTIALS AND CONNECTION AND TRY AGAIN!!!!!!"
else:
    # Previous session restored from cookies
    toolbar = soup.find_all('div', attrs={"class": "toolbar"})
    toolbar_len = len(toolbar)
    avatar = soup.find_all('img', attrs={"id": "viewImageLinkId"})
    avatar_len = len(avatar)
    if toolbar_len <= 0 or avatar_len <= 0:
        # clear previously saved cookies
        if os.path.exists(Constants.OK_SESSION_COOKIES_FILE_NAME):
            os.remove(Constants.OK_SESSION_COOKIES_FILE_NAME)
        assert 1, "WTF!!! --- Authorization failed. Cookies removed. --- WTF!!!\n" \
                  "WTF!!! --- PLEASE TRY AGAIN!!!!!! --- WTF!!!"

gwt_requested = None
keywords = Constants.KEY_WORDS
random.shuffle(keywords)
for search_query in Constants.KEY_WORDS:
    print('\n\n----------------\n------ query = "{}" ------\n----------------\n\n'.format(search_query))
    request = 'https://www.advertising-orange.com/?action=wasOkKeywordExecutedLastDays'
    res = requests.get(request, params={'keyword': search_query, 'daysAgo': 3})
    print('wasOkKeywordExecutedLastDays ---------- response = {}\n'.format(res.text))
    if not distutils.util.strtobool(res.text):
        # check daily groups count
        request = 'https://www.advertising-orange.com/?action=getOkDailyGroupsCount'
        res = requests.get(request)
        print('getOkDailyGroupsCount ---------- response = "{}"\n'.format(res.text))
        ok_groups_daily_count = int(res.text)
        print('OK GROUPS DAILY COUNT ---------- {}\n'.format(ok_groups_daily_count))
        if ok_groups_daily_count > 15000:
            quit(15000)

        if gwt_requested is None:
            # parse gwt_requested
            url = '''https://ok.ru/search?st.mode=Groups&st.grmode=Groups&st.posted=set&st.query=
                {}'''.format(search_query)
            r = s.get(url, headers=headers, timeout=5)
            if r.status_code != 200:
                print('\nSTATUS CODE != 200  ===  {}'.format(r.status_code))
            else:
                gwt_requested = 0
                soup = BeautifulSoup(r.text, 'html.parser')
                gwt_hash_element = soup.findAll('script', type='text/javascript', text=re.compile('.*,gwtHash:.*'))[0]
                splits = re.split(",", str(gwt_hash_element))
                for split in splits:
                    if split.__contains__('gwtHash'):
                        basic_splits = re.split(":", str(split))
                        gwt_split = basic_splits[1]
                        gwt_requested = re.sub('''"''', '''''', gwt_split)

        page = 50
        ok_group_max_users_count = 0
        while page > 1 and ok_group_max_users_count < Constants.OK_GROUP_MAX_USERS_COUNT:
            time.sleep(random.randint(3, 14))
            print(('\n---------   SEARCH GROUPS  --  PAGE - {}  --  KEY - {}  --------'.format(page, search_query)))
            path = '/search?cmd=PortalSearchResults&st.cmd=searchResult' \
                   '&st.mode=Groups&st.query={}&st.grmode=Groups' \
                   '&st.page={}&fetch=false&st.loaderid=PortalSearchResultsLoader' \
                   '&st.posted=set&gwt.requested={}&'.format(search_query, page, gwt_requested)
            url = 'https://ok.ru' + path
            headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/53.0.2785.143 Safari/537.36',
                # 'Host': 'www.ok.ru',
                'Connection': 'keep-alive',
            }
            r = s.get(url, headers=headers, timeout=5)
            if r.status_code != 200:
                print('\nSTATUS CODE != 200  ===  {}'.format(r.status_code))
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                group_elements = soup.findAll('div', attrs={"class": "gs_result_i_w gs_result_group-card"})
                max_page_users_count = Utils.parse_group_elements(group_elements=group_elements, s=s, headers=headers)
                if max_page_users_count is None:
                    ok_group_max_users_count = 1000000
                else:
                    ok_group_max_users_count = max(
                        ok_group_max_users_count,
                        max_page_users_count
                    )
                print('max users count = {}'.format(ok_group_max_users_count))
            page -= 1

        if ok_group_max_users_count is not None and ok_group_max_users_count < Constants.OK_GROUP_MAX_USERS_COUNT:
            print('\n---------   SEARCH GROUPS PAGE - 1  --  KEY - {}  --------'.format(search_query))
            url = '''https://ok.ru/search?st.mode=Groups&st.grmode=Groups&st.posted=set&st.query=
                {}'''.format(search_query)
            r = s.get(url, headers=headers, cookies=session_cookie, timeout=5)
            if r.status_code != 200:
                print('\nSTATUS CODE != 200  ===  {}'.format(r.status_code))
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                group_elements = soup.findAll('div', attrs={"class": "gs_result_i_w gs_result_group-card"})
                Utils.parse_group_elements(group_elements=group_elements, s=s, headers=headers)

        # setOkGroupLastDate
        request = 'https://www.advertising-orange.com/?action=setOkGroupLastDate'
        res = requests.post(request, data={'keyword': search_query})
        print('setOkGroupLastDate ---------- response = {}\n'.format(res.text))
