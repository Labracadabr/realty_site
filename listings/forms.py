from django import forms
from django.utils.translation import gettext_lazy as _


class LeadForm(forms.Form):
    INTERESTS = [
        ("", _("I'm interested in…")),
        ("buy_land", _("Buying land")),
        ("island", _("An island")),
        ("legal", _("Legal & documents")),
        ("construction", _("Construction")),
        ("other", _("Something else")),
    ]

    name = forms.CharField(label=_("Your name"), max_length=120)
    email = forms.EmailField(label=_("Email"), required=False)
    phone = forms.CharField(label=_("Phone / WhatsApp"), max_length=40, required=False)
    telegram = forms.CharField(label=_("Telegram"), max_length=60, required=False)
    interest = forms.ChoiceField(label=_("Interest"), choices=INTERESTS, required=False)
    message = forms.CharField(label=_("Message"), widget=forms.Textarea(attrs={"rows": 4}), required=False, max_length=3000)
    property_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    # Honeypot: humans don't see it, bots fill it in.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    def clean(self):
        data = super().clean()
        if not (data.get("email") or data.get("phone") or data.get("telegram")):
            raise forms.ValidationError(_("Please leave at least one way to contact you."))
        return data
