'''
    Furk.net player for XBMC
    Copyright (C) 2010 Gpun Yog

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import re

# quircks for old xbmc
try:
    import json
    from urlparse import parse_qs
except:
    # pre-frodo and python 2.4
    import simplejson as json
    from cgi import parse_qs

# Plugin constants
__settings__ = xbmcaddon.Addon(id='plugin.video.furk')
__plugin__ = 'Furk.net'
__author__ = 'Gpun Yog'
__url__ = 'https://www.furk.net/t/xbmc'
__version__ = '1.0.11'
print "[PLUGIN] '%s: version %s' initialized! argv=%s" % (__plugin__, __version__, sys.argv)

API_URL = "https://www.furk.net/api/"

pluginhandle = None
try:
    pluginhandle = int(sys.argv[1])
except:
    pluginhandle = ""


# based on whatthefurk plugin code
class FurkAPI(object):

    def __init__(self, api_key=''):
        self.api_key = api_key

    def metasearch(self, params):
        params['type'] = 'video'
        params['filter'] = 'cached'
        resp = self._call('plugins/metasearch', params)
        if 'files' in resp:
            return resp['files']
        else:
            return None

    def file_get(self, params={}):
        params['type'] = 'video'
        resp = self._call('file/get', params)
        files = resp['files']
        return files

    def login(self, login, pwd):
        resp = self._call('login/login', {"login": login, "pwd": pwd})
        self.api_key = resp['api_key']
        return self.api_key

    def _call(self, cmd, params):
        url = "%s%s" % (API_URL, cmd)
        body = self._fetch(url, params)

        data = json.loads(body)
        if data['status'] != 'ok':
            xbmcgui.Dialog().ok('Error', data['error'])
            return None
        return data

    def _fetch(self, url, params):
        if self.api_key:
            params['api_key'] = self.api_key
        params['pretty'] = 1
        paramsenc = urllib.urlencode(params)
        req = urllib2.Request(url, paramsenc)
        opener = urllib2.build_opener()
        response = opener.open(req)

        body = response.read()
        response.close()
        return body


def add_pseudo_items():
    name = '[SEARCH]'
    url = sys.argv[0] + '?action=search&query='
    listitem = xbmcgui.ListItem(name)
    listitem.setInfo(type='video', infoLabels={'Title': name})
    xbmcplugin.addDirectoryItem(
        handle=pluginhandle,
        url=url,
        listitem=listitem,
        isFolder=True)

    if __settings__.getSetting('recent_queries') != '':
        name = '[SEARCH HISTORY]'
        url = sys.argv[0] + '?action=search_history'
        listitem = xbmcgui.ListItem(name)
        listitem.setInfo(type='video', infoLabels={'Title': name})
        xbmcplugin.addDirectoryItem(
            handle=pluginhandle,
            url=url,
            listitem=listitem,
            isFolder=True)


def runner():
    # check if login and pass has been set
    if __settings__.getSetting('api_key') == '' or (__settings__.getSetting('login') == '' or __settings__.getSetting('password') == ''):
        resp = xbmcgui.Dialog().yesno(
            "No username/password set!",
            "Furk.net requires you to be logged in to view",
            "videos.  Would you like to log-in now?")
        if resp:
            __settings__.openSettings()
        else:
            return

    # get params
    params = parse_qs(sys.argv[2][1:])
    for k in params:
        params[k] = params[k][0]
    xbmc.log("params=%s" % params)

    # show files list by default
    if not params:
        params['action'] = 'root'

    # menu listing
    # just play a file
    if(params['action'] == 'play'):
        xbmc.Player().play(urllib.unquote(params['url']))
        return

    # api obj is needed
    api_key = __settings__.getSetting('api_key')
    if api_key == '':
        api = FurkAPI()
        api_key = api.login(
            login=__settings__.getSetting('login'),
            pwd=__settings__.getSetting('password'))
        __settings__.setSetting('api_key', api_key)
    else:
        api = FurkAPI(api_key)

    # root menu
    if(params['action'] == 'root'):
        files = api.file_get()
        add_pseudo_items()
        if not files:
            return
        for fl in files:
            url = sys.argv[0] + '?action=file&id=' + fl['id']
            listitem = xbmcgui.ListItem(fl['name'])
            if 'ss_urls_tn_all' in fl:
                listitem.setThumbnailImage(fl['ss_urls_tn_all'])
            listitem.setInfo(
                type='video',
                infoLabels={
                    'title': fl['name'],
                    'size': int(
                        fl['size'])})
            xbmcplugin.addDirectoryItem(
                handle=pluginhandle,
                url=url,
                listitem=listitem,
                isFolder=True)

        xbmcplugin.endOfDirectory(pluginhandle)

    elif(params['action'] == 'file'):
        f = api.file_get({'id': params['id'], 't_files': 1})[0]
        t_files = f['t_files']
        for item in t_files:
            if not re.match('^(audio|video)/', item['ct']):
                continue
            url = sys.argv[0] + '?action=play&url=' + item['url_dl']
            name = item['name']
            if 'bitrate' in item:
                name = '%s %skb/s' % (item['name'], item['bitrate'])
            listitem = xbmcgui.ListItem(name)
            if 'url_tn' in item:
                listitem.setThumbnailImage(item['url_tn'])
            listitem.setInfo(
                'video', {
                    'title': name, 'size': int(
                        item['size']), 'duration': item['length']})
            xbmcplugin.addDirectoryItem(
                handle=pluginhandle,
                url=url,
                listitem=listitem,
                isFolder=True)

        xbmcplugin.endOfDirectory(pluginhandle)

    elif(params['action'] == 'search_history'):
        if __settings__.getSetting('recent_queries') == '':
            return

        recent = __settings__.getSetting('recent_queries').split('|')
        if '' in recent:
            recent.remove('')
            total = len(recent) + 1
        for r in recent:
            name = urllib.unquote(r)
            url = sys.argv[0] + '?action=search&q=' + r

            listitem = xbmcgui.ListItem(name)
            listitem.setInfo(type='video', infoLabels={'Title': name})
            xbmcplugin.addDirectoryItem(
                handle=pluginhandle,
                url=url,
                listitem=listitem,
                isFolder=True)
        xbmcplugin.endOfDirectory(pluginhandle)

    elif(params['action'] == 'search'):
        if 'q' not in params:
            params['q'] = ''
        keyboard = xbmc.Keyboard(urllib.unquote(params['q']), 'Search')
        keyboard.doModal()

        if not keyboard.isConfirmed():
            print 'not confirmed'
            return

        params['q'] = keyboard.getText()
        files = api.metasearch({'q': params['q']})
        if not files:
            xbmcgui.Dialog().ok('No results', 'No results')
            return

        # add history
        recent = __settings__.getSetting('recent_queries').split('|')
        recent = [urllib.unquote(r) for r in recent]
        if params['q'] in recent:
            recent.remove(params['q'])
        recent.insert(0, params['q'])
        recent = [urllib.quote(r) for r in recent]
        __settings__.setSetting(id='recent_queries', value='|'.join(recent))

        add_pseudo_items()
        for item in files:
            url = sys.argv[0] + '?action=file&id=' + item['id']
            listitem = xbmcgui.ListItem(item['name'])
            if 'ss_urls_tn_all' in item:
                listitem.setThumbnailImage(item['ss_urls_tn_all'])
            listitem.setInfo(
                type='video',
                infoLabels={
                    'title': item['name'],
                    'size': int(
                        item['size'])})
            xbmcplugin.addDirectoryItem(
                handle=pluginhandle,
                url=url,
                listitem=listitem,
                isFolder=True)

        xbmcplugin.endOfDirectory(pluginhandle)

    elif(params['action'] == 'search_history'):
        recent = __settings__.getSetting('recent_queries').split('|')
        if '' in recent:
            recent.remove('')
            total = len(recent) + 1

        for r in recent:
            name = urllib.unquote(r)
            url = sys.argv[0] + '?action=search&q=' + r

            listitem = xbmcgui.ListItem(name)
            listitem.setInfo(type='video', infoLabels={'Title': name})
            xbmcplugin.addDirectoryItem(
                handle=pluginhandle,
                url=url,
                listitem=listitem,
                isFolder=True)

        xbmcplugin.endOfDirectory(pluginhandle)


if __name__ == "__main__":
    runner()


sys.modules.clear()
