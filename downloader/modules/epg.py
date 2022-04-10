import xml.etree.ElementTree as ET
import time
import datetime
import pytz
from . import utils


class EPG:
    def __init__(self, epg_xml):
        self.epg = epg_xml
        self.time_format = "%Y%m%d%H%M%S %z"
        self.tz = 'Europe/Warsaw'

    def get_channels(self):
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.parse(self.epg, parser=parser)
        channel_list = {}
        for channel in tree.iter('channel'):
            display_name = []
            name = channel.get('id')
            for dn in channel.iter('display-name'):
                display_name.append(dn.text)
            channel_list.update({name: display_name})
        return channel_list

    def find_channel_name(self, channel_name):
        channels = self.get_channels()
        for channel in channels.items():
            for ch in channel[1]:
                if ch == channel_name:
                    return channel[0]

    # generate xml with epg for specific  channel
    def find_epg_for_channel(self, channel):
        try:
            channel_search_string = "./programme/[@channel='" + channel + "']"
        except TypeError:
            return []
        tree = ET.parse(self.epg)
        return tree.findall(channel_search_string)

    # generate list of dictionaries with epg
    def get_epg_for_channel(self, channel, days):
        if days is None:
            days = 30
        now_epoch = time.time()
        current_time = datetime.datetime.now()
        catchup_ago = current_time - datetime.timedelta(days=days)
        catchup_ago_epoch = int(catchup_ago.timestamp())

        # get xml with epg for specific channel
        epg_from_xml = self.find_epg_for_channel(channel)
        epg = []

        for program in epg_from_xml:
            start = program.get('start')
            #start = datetime.datetime.strptime(start,self.time_format)
            #start = start.astimezone(pytz.timezone(self.tz)).strftime(self.time_format)
            start = utils.convert_date_tz(start,self.time_format,self.tz)
            stop = program.get('stop')
            #stop = datetime.datetime.strptime(stop,self.time_format)
            #stop = stop.astimezone(pytz.timezone(self.tz)).strftime(self.time_format)
            stop = utils.convert_date_tz(stop,self.time_format,self.tz)
            start_epoch = utils.convert_to_epoch(start, self.time_format)
            stop_epoch = utils.convert_to_epoch(stop, self.time_format)
            if start_epoch > catchup_ago_epoch:
                episode = None
                desc = None
                duration = stop_epoch - start_epoch
                for title in program.iter('title'):
                    title = title.text
                    for episode_num in program.iter('episode-num'):
                        if episode_num.text:
                            episode = episode_num.text
                    for desc in program.iter('desc'):
                        if desc.text:
                            desc = desc.text
                startday = datetime.datetime.strptime(
                    start, self.time_format).strftime('%d-%m-%Y')
                starthour = datetime.datetime.strptime(
                    start, self.time_format).strftime('%H:%M')
                start = datetime.datetime.strptime(
                    start, self.time_format).strftime('%d-%m-%Y %H:%M')
                epg.append([{'startday': startday, 'starthour': starthour, 'title': title, 'episodenum': episode,
                             'startepoch': start_epoch, 'duration': duration, 'description': desc}])
                if stop_epoch >= now_epoch:
                    epg.pop
                    break

        new_epg = []
        for x in range(len(epg)):
            once = epg[x][0]
            new_epg.append(once)

        return new_epg
