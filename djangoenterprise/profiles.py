from django.db import models
from django.conf import settings
from django.utils import timezone

PROFILE_TYPE_BOT = 0
PROFILE_TYPE_USER = 1
PROFILE_TYPE_PEOPLE = 2 # without account
PROFILE_TYPE_DEPARTAMENT = 3
PROFILE_TYPE_ORG = 4
PROFILE_TYPE_RESOURCE = 5

PROFILE_TYPE_LIST = ( PROFILE_TYPE_BOT, PROFILE_TYPE_USER, PROFILE_TYPE_PEOPLE, PROFILE_TYPE_DEPARTAMENT, PROFILE_TYPE_ORG, PROFILE_TYPE_RESOURCE )

PROFILE_TYPE_CHOICES_EDITOR = (
  ( PROFILE_TYPE_PEOPLE, 'People' ),
  ( PROFILE_TYPE_DEPARTAMENT, 'Departament' ),
  ( PROFILE_TYPE_ORG, 'Organization' ),
  ( PROFILE_TYPE_RESOURCE, 'Resource' ),
)

PROFILE_TYPE_CHOICES = (
  ( PROFILE_TYPE_BOT, 'Bot' ),
  ( PROFILE_TYPE_USER, 'User' ),
) + PROFILE_TYPE_CHOICES_EDITOR

PROFILE_TYPE_FOR_TASK = ( PROFILE_TYPE_PEOPLE, PROFILE_TYPE_DEPARTAMENT, PROFILE_TYPE_ORG, PROFILE_TYPE_RESOURCE )

class BaseProfile(models.Model):
    profile_type = models.PositiveSmallIntegerField( blank=False, null=False, default = PROFILE_TYPE_USER )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True, related_name="profile")
    name = models.CharField(max_length=75, blank=True)
    avatar = models.ImageField(blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.CharField(max_length=250, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.profile_type in PROFILE_TYPE_LIST: # check for profile type
            self.modified_at = timezone.now()
            return super(BaseProfile, self).save(*args, **kwargs)
        else:
            raise Exception("Cannot save - wrong profile type!")

    def __str__(self):
        return self.display_name

    def get_absolute_url(self):
        return reverse_lazy('profiles_detail', kwargs={ 'pk': self.id} )

    @property
    def has_account(self):
        return ( self.profile_type in ( PROFILE_TYPE_USER, PROFILE_TYPE_BOT ) )

    @property
    def display_name(self):
        s = ''
        if self.name:
            s = self.name
        else:
            if self.user:
                s = self.user.username
        return s + " (" + PROFILE_TYPE_CHOICES[self.profile_type][1] + ")"

    def sub_profiles(self):
        return Profile_Affiliation.objects.filter(main_profile=self )

    def main_profiles(self):
        return Profile_Affiliation.objects.filter(sub_profile=self )

    def list_of_avail_for_affiliate(self):
        return Profile.objects.all().exclude( id = self.id ).exclude( sub_profile__main_profile_id = self.id )

    def description_html(self):
        return self.description
