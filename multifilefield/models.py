from django.db import models
from django.conf import settings

from datetime import datetime


MULTIFILEFIELD_ROOT = getattr(settings, 'MULTIFILEFIELD_ROOT', settings.MEDIA_ROOT)


def get_path(basename):
    return MULTIFILEFIELD_ROOT + '/%s' % basename


def upload_to(instance, name):
    # This should be able to handle a foreignkey property specified in meta.
    #
    # ie: if specified, path would be root/foreignkey.id/basename

    return get_path(name)


class UploadedFile(models.Model):
    upload = models.FileField(upload_to=upload_to, max_length=400)
    created_at = models.DateTimeField('created', null=True, blank=True, default=datetime.now)
    updated_at = models.DateTimeField('updated', null=True, blank=True)

    class Meta:
        verbose_name = 'Uploaded File'
        verbose_name_plural = 'Uploaded Files'


    def __unicode__(self):
        return '%s' % self.basename


    @property
    def basename(self):
        return self.upload.url.split('/')[-1]


    def save(self, *args, **kwargs):
        self.updated_at = datetime.today()
        if not self.id:
            self.created_at = datetime.today()

        return super(UploadedFile, self).save(*args, **kwargs)


    def get_absolute_url(self):
        return get_path(self.basename)
