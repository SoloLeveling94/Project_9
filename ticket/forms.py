from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import CharField, ModelForm, RadioSelect

from .models import UserFollows, Review, Ticket


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image', ]
        labels = {'title': 'Titre',
                  'description': 'Description',
                  'image': 'Image',
                  }


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body', ]
        labels = {'headline': 'Titre',
                  'rating': 'Note',
                  'body': 'Commentaire',
                  }
        widgets = {'rating': RadioSelect(choices=[(0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                                         attrs={"class": "list-unstyled d-flex flex-row justify-content-around"})}


class FollowForm(ModelForm):
    followed_user = CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        """ Grants access to the request object """
        self.request = kwargs.pop('request')
        super(FollowForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserFollows
        fields = ["followed_user"]

    def clean_followed_user(self):
        cleaned_data = super(FollowForm, self).clean()
        followed_user = self.cleaned_data["followed_user"].lower()
        if not User.objects.filter(username=followed_user).exists():
            raise ValidationError("L'utilisateur demandé n'existe pas !!!")
        if followed_user == self.request.user.username:
            raise ValidationError("Vous ne pouvez pas vous rajouter !!!")
        find_user = User.objects.filter(username=followed_user)
        if UserFollows.objects.filter(user=self.request.user, followed_user__in=find_user):
            raise ValidationError("Vous avez déjà ajouté l'utilisateur !!!")

        cleaned_data["followed_user"] = User.objects.get(username=followed_user)
        return cleaned_data["followed_user"]
