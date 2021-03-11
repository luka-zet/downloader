
from django import forms


def check_provider(url):
    if 'tele' in url or 'plusx' in url:
        pass
    else:
        raise forms.ValidationError('Playlist invalid, or unsupported')


class UrlForm(forms.Form):
    iptv_url = forms.URLField(label="URL of playlist", required=True,
                              validators=[check_provider])
    ignore_archive_days = forms.BooleanField(
        label="Ignore days archive days from playlist", required=False)
