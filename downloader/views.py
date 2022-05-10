from django.shortcuts import render, redirect
from django.contrib import messages
from .modules.playlist import Playlist
from .modules.epg import EPG
from .modules import utils
from .forms import UrlForm
import requests
import os.path


def home(request):
    try:
        del request.session['iptv_url']
        del request.session['iptv_provider']
        del request.session['channels']
        del request.session['channels_names']
        del request.session['selected_channel_name']
        del request.session['ignore_archive_days']

    except KeyError:
        pass
    return render(request, 'downloader/base.html', {'url_form': UrlForm})


def get_channels(request):
    if request.method == "POST":
        form = UrlForm(request.POST)

        if form.is_valid():
            epg_url = 'https://epg.ovh/pl/plar.xml'
            playlist_url = form.cleaned_data['iptv_url']
            request.session['ignore_archive_days'] = form.cleaned_data['ignore_archive_days']
            request.session['iptv_url'] = playlist_url
            iptv_playlist = Playlist(playlist_url)
            iptv_playlist_items = iptv_playlist.get_playlist()
            clear_iptv_playlist = iptv_playlist_items[0]
            iptv_provider = iptv_playlist_items[1]
            request.session['iptv_provider'] = iptv_provider
            channels = []
            channels_names = []
            for i in range(len(clear_iptv_playlist)):
                if clear_iptv_playlist[i].get('catchup_days'):
                    print(clear_iptv_playlist[i])
                    channel = (clear_iptv_playlist[i])
                    channels.append(channel)
                    channels_names_once = (channel.get('tvg_id'), channel.get('tvg_name'))
                    channels_names.append(channels_names_once)
            request.session['channels'] = channels
            request.session['channels_names'] = channels_names

            messages.success(request, f'Valid playlist for {iptv_provider}')
            request.session.modified = True

            if not os.path.isfile('downloader/static/epg/epg.xml') or \
                    utils.is_file_older_than_x_hours('downloader/static/epg/epg.xml', 6):
                file_stream = requests.get(epg_url, stream=True)
                with open('downloader/static/epg/epg.xml', 'wb') as local_file:
                    for data in file_stream:
                        local_file.write(data)

            return render(request, 'downloader/channels.html', {'url_form': form,
                                                                'channels': channels_names,
                                                                'iptv_list': clear_iptv_playlist})
        else:
            messages.warning(request, 'The form is invalid.')
            return redirect('downloader-home')
    else:
        form = UrlForm
        return render(request, 'downloader/channels.html', {'url_form': form, 'channels': None})


def get_epg(request):
    if request.method == "POST":
        if 'selected_channel_name' not in request.session:
            request.session['selected_channel_name'] = request.POST['channels']
        iptv_playlist = Playlist(request.session['iptv_url'])
        epg_xml = EPG('downloader/static/epg/epg.xml')
        selected_channel_name_in_epg = epg_xml.find_channel_name(request.POST['channels'])
        if selected_channel_name_in_epg is None:
            messages.warning(request, f"Cannot find channel {request.POST['channels']}, select proper name")
            all_channels_in_epg = list(epg_xml.get_channels())
            proper_channels_names = utils.find_proper_channel(request.POST['channels'], all_channels_in_epg)
            proper_channels_list = []
            for item in proper_channels_names:
                channel_pair = (request.session['selected_channel_name'], item)
                proper_channels_list.append(channel_pair)
            iptv_playlist_items = iptv_playlist.get_playlist()
            clear_iptv_playlist = iptv_playlist_items[0]
            return render(request, 'downloader/channels.html', {'channels': proper_channels_list,
                                                                'iptv_list': clear_iptv_playlist})

        else:
            channel_settings = iptv_playlist.get_channel_settings(request.session['selected_channel_name'])
            archive_url = channel_settings[0]
            days = channel_settings[1]
            if request.session['ignore_archive_days']:
                days = None

            logo_url = channel_settings[2]
            epg_for_selected_channel = epg_xml.get_epg_for_channel(selected_channel_name_in_epg, days)        
            for x in range(len(epg_for_selected_channel)):
                epg_for_selected_channel[x]['archiveurl'] = archive_url

            channels_names = request.session['channels_names']
            selected_channel_name = request.session['selected_channel_name']
            del request.session['selected_channel_name']
            return render(request, 'downloader/channels.html', {'epg_for_selected_channel': epg_for_selected_channel,
                                                                'channels': channels_names,
                                                                'selected_channel_name': selected_channel_name,
                                                                'logo_url': logo_url})
    else:
        return redirect('downloader-home')


def download(request):
    if request.method == "POST":
        iptv_playlist = Playlist(request.session['iptv_url'])
        archive_url = request.POST['archive_url']
        start = request.POST['start']
        duration = request.POST['duration']
        format = request.POST['format']
        title = request.POST['title']
        print(request.POST['title'])
        url = iptv_playlist.get_url_of_program(request.session['iptv_provider'], archive_url, start, duration, format)
        return render(request, 'downloader/download.html', {'url': url, 'title': title})

