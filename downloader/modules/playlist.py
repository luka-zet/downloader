import re
import sys
import requests
from django.core.exceptions import ValidationError


class Playlist:
    def __init__(self, playlist_url):
        self.playlist_url = playlist_url

    def get_playlist(self) -> object:
        # check provider and playlist type
        if 'tele' in self.playlist_url:
            if 'hls' in self.playlist_url:
                provider = "tele-hls"
            else:
                provider = "tele-mpeg"
        elif 'plus' in self.playlist_url:
            provider = 'plusx'
        else:
            raise ValidationError('Playlist invalid, or unsupported')

        # download and read playlist
        r = requests.get(self.playlist_url)
        list_from_file = r.text
        lines = list_from_file.splitlines()

        cleared_playlist = ''
        for line in lines:
            if line.startswith('#EXTINF'):
                cleared_playlist += line + ',-sep-'
            elif line.startswith('http'):
                cleared_playlist += line + '\n'

        # more clear and splitting playlist
        temp_playlist = []
        for line in cleared_playlist.splitlines():
            # Split url from settings
            temp_channel_setting = line.split('-sep-')
            # Get settings
            temp_channel_string = temp_channel_setting[0]
            # Remove unused channel name
            temp_channel_string = temp_channel_string.split(',')
            temp_channel_setting[0] = temp_channel_string[0]
            temp_playlist.append(temp_channel_setting)

        clear_playlist = []
        for i in range(len(temp_playlist)):
            temp = temp_playlist[i][0]
            url_of_channel = temp_playlist[i][1]

            m = re.search('group-title="(.+?)"', temp)
            if m:
                group = m.group(1)
            else:
                group = None

            m = re.search('tvg-id="(.+?)"', temp)
            if m:
                tvg_id = m.group(1)
            else:
                tvg_id = None

            m = re.search('tvg-name="(.+?)"', temp)
            if m:
                tvg_name = m.group(1)
            else:
                tvg_id = None

            m = re.search('catchup-days="(.+?)"', temp)
            if m:
                catchup_days = m.group(1)
            else:
                m = re.search('timeshift="(.+?)"', temp)
                if m:
                    catchup_days = m.group(1)
                else:
                    catchup_days = None

            if provider == 'tele-hls' or provider == 'tele-mpeg':
                m = re.search('catchup-source="(.+?)"', temp)
                if m:
                    catchup_source = m.group(1)
                else:
                    catchup_source = None
            else:
                catchup_source = url_of_channel

            m = re.search('tvg-logo="(.+?)"', temp)
            if m:
                logo = m.group(1)
            else:
                logo = None

            temp = {"group": group, "tvg_id": tvg_id, "tvg_name": tvg_name, "catchup_days": catchup_days,
                    "catchup_source": catchup_source, "url": url_of_channel, "logo": logo}
            clear_playlist.append(temp)
        return clear_playlist, provider

    @staticmethod
    def get_url_of_program(playlist_type, url, start, duration, format='mp4'):
        if playlist_type == 'tele-hls':
            req = requests.get(f'{url}?utc={start}', allow_redirects=False)
            link = req.headers['location']
            link = link.split('index.m3u8')
            link = [link[0], link[1].split('&startTime=')]
            link = f'{link[0]}index-{start}-{duration}.{format}{link[1][0]}'
            return link

        elif playlist_type == 'tele-mpeg':
            req = requests.get(f'{url}?utc={start}', allow_redirects=False)
            link = req.headers['location']
            link = link.split('timeshift_abs')
            link = [link[0], link[1].split('.ts')]
            link = f'{link[0]}index-{start}-{duration}.{format}{link[1][1]}'
            return link

        elif playlist_type == 'plusx':
            link = url.split('mono.m3u8')
            link = f'{link[0]}archive-{start}-{duration}.ts{link[1]}'
            return link

        else:
            print('Not supported iptv provider')
            sys.exit(1)

    def get_channel_settings(self, channel):
        clear_iptv_playlist = self.get_playlist()[0]
        for kanal in clear_iptv_playlist:
            if kanal.get('tvg_name') is not None:
                name = kanal.get('tvg_name')
            name = kanal.get('tvg_id')
            if kanal.get('catchup_source') is not None:
                while name == channel:
                    if kanal.get('catchup_source').startswith('http'):
                        selected_channel_url = kanal.get('catchup_source')
                    else:
                        selected_channel_url = kanal.get('url')
                    if kanal.get('logo'):
                        selected_channel_logo_url = kanal.get('logo')
                    selected_channel_archive_days = int(kanal.get('catchup_days'))
                    break
                try:
                    selected_channel_url
                except NameError:
                    pass
                else:
                    break
        return selected_channel_url, selected_channel_archive_days, selected_channel_logo_url
