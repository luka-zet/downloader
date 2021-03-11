
from django import forms


def check_provider(url):
    if 'tele' in url or 'plusx' in url:
        pass
    else:
        raise forms.ValidationError('Playlist invalid, or unsupported')


class UrlForm(forms.Form):
    iptv_url = forms.URLField(label="URL of playlist", required=True,
                              max_length=500,
                              validators=[check_provider],
                              help_text="Paste tele or plusx m3u",
                              widget=forms.TextInput(attrs={'size':75, 'max_length':500}))
    ignore_archive_days = forms.BooleanField(
        label="Ignore days archive days from playlist", required=False)
