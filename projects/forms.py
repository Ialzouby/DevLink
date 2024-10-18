from django import forms

class RatingForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],  # Rating from 1 to 5
        label="Rate this project",
        widget=forms.RadioSelect
    )
