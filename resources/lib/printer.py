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

import sys, re, time
import xbmc, xbmcgui, xbmcplugin
import urllib

__settings__ = sys.modules[ "__main__" ].__settings__

try:
	pluginhandle = int( sys.argv[ 1 ] )
	xbmc.log('got handle=%s' % pluginhandle)	
except:
	pluginhandle = ""

def _addSearchItem():
	name = '[SEARCH]'
	url = sys.argv[0] + '?action=search&query='
	listitem = xbmcgui.ListItem(name)
	listitem.setInfo(type='video', infoLabels={'Title': name})
	xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=listitem, isFolder=True)

def printRecentQueries():
	# search
	_addSearchItem();

	recent = __settings__.getSetting('recent_queries').split('|')
	if '' in recent:
		recent.remove('')
	total = len(recent) + 1

	for r in recent:
		name = urllib.unquote(r)
		url = sys.argv[0] + '?action=search&query=' + r

		listitem = xbmcgui.ListItem(name, thumbnailImage='http://www.furk.net/img/logo.png')
		listitem.setInfo(type='video', infoLabels={'Title': name})
		xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=listitem, isFolder=True)

	xbmcplugin.endOfDirectory(pluginhandle)
	

def printDirs(dirs):
	xbmc.log('handle=%s' % pluginhandle)	
	
	_addSearchItem();

	for d in dirs:
		id = d.getElementsByTagName('id').item(0).firstChild.data
		name = d.getElementsByTagName('name').item(0).firstChild.data
		date = d.getElementsByTagName('date').item(0).firstChild.data
		thumb = d.getElementsByTagName('thumb').item(0).firstChild.data

		url = sys.argv[0] + '?action=files&did=' + id

		listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
		listitem.setInfo(type='video', infoLabels={'Date': date, 'Title': name})
		xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=listitem, isFolder=True)

	xbmcplugin.endOfDirectory(pluginhandle)


def printFiles(files):
	xbmc.log('handle=%s' % pluginhandle)
	xbmcplugin.setContent(pluginhandle, 'videos')
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
	
	total = len(files)
	for f in files:
		id = f.getElementsByTagName('id').item(0).firstChild.data
		name = f.getElementsByTagName('name').item(0).firstChild.data
		play_url = f.getElementsByTagName('url').item(0).firstChild.data

		url = sys.argv[0] + '?action=play&url=' + urllib.quote(play_url)
		
		listitem = xbmcgui.ListItem(name)
		listitem.setInfo(type='video', infoLabels={'Title': name})
		xbmcplugin.addDirectoryItem(pluginhandle, url, listitem, isFolder=False, totalItems=total)

	xbmcplugin.endOfDirectory(pluginhandle)



def playFile(play_url):
	xbmc.Player().play(urllib.unquote(play_url))
