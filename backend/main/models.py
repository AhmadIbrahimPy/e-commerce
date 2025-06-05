import sys, string, random
from formatter import NullWriter
from io import BytesIO
from lib2to3.pgen2.token import NUMBER

from PIL import Image
import pillow_heif

from django.db import models

from django.contrib.auth.models import AbstractUser

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .images_path import *

# Create your models here.

ROLE_CHOICES = [
    (1, 'Superuser Admin'),
    (2, 'Staff Admin'),
    (101, 'User'),
]

class UserAccounts(AbstractUser):
    role = models.PositiveSmallIntegerField(
        default=0,
        choices=ROLE_CHOICES,
        verbose_name="User Role",
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    country = models.ForeignKey(
        "Countries",
        verbose_name="User Country",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='country_user_account'
    )

    mobile = models.ForeignKey(
        "Mobiles",
        verbose_name="User Mobile",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='mobile_user_account'
    )

    email = models.ForeignKey(
        "Emails",
        verbose_name="User Emails",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='email_user_account'
    )

    image = models.ImageField(
        verbose_name="User Image",
        upload_to=user_image_path,
        blank=True,
        null=True,
        max_length=6000,
        help_text="User Image.",
    )

    is_deleted = models.BooleanField(
        verbose_name="User Delete ?",
        default=False,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True,
        blank=True, null=True
    )
    created_by = models.ForeignKey(
        "self",
        verbose_name="Created By",
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='created_user_account'
    )
    updated_at = models.DateTimeField(
        verbose_name="Last Updated At",
        auto_now=True,
        blank=True, null=True
    )
    updated_by = models.ForeignKey(
        "self",
        verbose_name="Updated By",
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='updated_user_account'
    )
    def save(self, *args, **kwargs):
        if self.image:
            try:
                image = Image.open(self.image)
            except:
                heif_file = pillow_heif.open_heif(self.image)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                )

            image = image.convert('RGB')
            output = BytesIO()
            image.save(output, format='JPEG', quality=75)
            output.seek(0)

            self.image = InMemoryUploadedFile(
                output, 'ImageField', self.image.name.split('.')[0] + '.jpg',
                'image/jpeg', sys.getsizeof(output), None
            )

        super().save(*args, **kwargs)

    def __repr__(self):
        """
        Return a detailed string representation of the object for debugging.
        """
        return f"<User account {self.first_name} ID: {self.id} ({self.role})>"

    def __str__(self):
        """
        String representation of the user_account object, including its status and update time.
        """
        status = "Active" if self.is_active else "Inactive"
        last_update = f", updated {self.updated_at.strftime('%Y-%m-%d')}" if self.updated_at else ", just created"
        return f"User account {self.first_name} ID: {self.id} ({self.role}) - {status}{last_update}"

    class Meta:
        """
        Meta class to define custom table name, permissions, and order of records.
        """
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"
        ordering = ['-updated_at', '-created_at']
        get_latest_by = "updated_at"
        permissions = [
            ("can_publish_user_account", "Can publish user account"),
        ]
        unique_together = [('username', 'email', 'phone')]  # Ensures that each network has a unique combination of name and code

class Countries(models.Model):
    # Country name (Egypt, Saudi Arabia)
    name = models.CharField(
        verbose_name="Country Name",
        default="",
        max_length=25,
        null=False,
        blank=True,
        db_index=True,
        help_text="Country name (Egypt, Saudi Arabia).",
    )

    # Country code (EG, SA)
    code = models.CharField(
        verbose_name="Country Code",
        default="",
        max_length=5,
        null=False,
        blank=True,
        unique=True,
        help_text="Country code (EG, SA).",
    )

    # Phone prefix (+20, +966)
    phone_prefix = models.CharField(
        verbose_name="Phone Prefix",
        default="",
        max_length=5,
        null=False,
        blank=True,
        unique=True,
        help_text="Phone prefix (+20, +966).",
    )

    # Expected phone number length
    number_length = models.IntegerField(
        verbose_name="Phone Number Length",
        default=1,
        null=False,
        blank=True,
        help_text="Expected phone number length.",
    )

    # Currency code (EGP, SAR)
    currency = models.CharField(
        verbose_name="Currency Code",
        default="",
        max_length=4,
        null=False,
        blank=True,
        unique=True,
        help_text="Currency code (EGP, SAR).",
    )

    # Geographical latitude
    latitude = models.FloatField(
        verbose_name="Latitude",
        default=0.0,
        null=False,
        blank=True,
        help_text="Geographical latitude.",
    )

    # Geographical longitude
    longitude = models.FloatField(
        verbose_name="Longitude",
        default=0.0,
        null=False,
        blank=True,
        help_text="Geographical longitude.",
    )

    # Timezone string (Africa/Cairo)
    timezone = models.CharField(
        verbose_name="Timezone",
        default="",
        max_length=20,
        null=False,
        blank=True,
        help_text="Timezone string (Africa/Cairo).",
    )

    # Image for the country (flag or similar)
    image = models.ImageField(
        verbose_name="Country Image",
        upload_to=country_image_path,
        blank=True,
        null=True,
        max_length=6000,
        help_text="Country Image.",
    )

    # Active status
    is_active = models.BooleanField(
        verbose_name="Is Active?",
        help_text="When 'Is Active?' is selected, it means it is activated.",
        default=False,
        null=True,
        blank=True
    )

    # Timestamps and user tracking
    created_at = models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True,
        blank=True, null=True
    )
    created_by = models.ForeignKey(
        UserAccounts,
        verbose_name="Created By",
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='created_countries'
    )
    updated_at = models.DateTimeField(
        verbose_name="Last Updated At",
        auto_now=True,
        blank=True, null=True
    )
    updated_by = models.ForeignKey(
        UserAccounts,
        verbose_name="Updated By",
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='updated_countries'
    )

    def clean(self):
        """
        Custom validation for the Countries model.
        This method is automatically called if full_clean() is used.
        """
        errors = {}

        object_id = 0
        if self.id:
            object_id = self.id
        filter_all_objects = Countries.objects.filter(~models.Q(id=object_id))

        if not self.name:
            errors['name'] = _("Country name is required.")
        else:
            if filter_all_objects.filter(name__iexact=self.name.lower()):
                errors['name'] = _(f"Name '{self.name}' already exists.")

        if not self.code or len(self.code) > 5:
            errors['code'] = _("Country code must be 5 characters or less.")
        else:
            if filter_all_objects.filter(code__iexact=self.code.lower()):
                errors['code'] = _(f"Code '{self.code}' already exists.")

        if not self.phone_prefix.startswith("+"):
            errors['phone_prefix'] = _("Phone prefix must start with '+'.")
        else:
            if filter_all_objects.filter(phone_prefix__iexact=self.phone_prefix.lower()):
                errors['phone_prefix'] = _(f"Phone Prefix '{self.phone_prefix}' already exists.")

        if not (3 <= self.number_length <= 15):
            errors['number_length'] = _("Phone number length must be between 3 and 15.")

        if self.latitude < -90 or self.latitude > 90:
            errors['latitude'] = _("Latitude must be between -90 and 90.")

        if self.longitude < -180 or self.longitude > 180:
            errors['longitude'] = _("Longitude must be between -180 and 180.")

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Automatically converts uploaded image (if any) to JPG format and compresses it.
        Also supports HEIF/HEIC formats (from iPhone).
        """
        self.full_clean()
        if self.image:
            try:
                image = Image.open(self.image)
            except Exception:
                heif_file = pillow_heif.open_heif(self.image)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                )

            image = image.convert('RGB')
            output = BytesIO()
            image.save(output, format='JPEG', quality=75)
            output.seek(0)

            self.image = InMemoryUploadedFile(
                output, 'ImageField', self.image.name.split('.')[0] + '.jpg',
                'image/jpeg', sys.getsizeof(output), None
            )

        super().save(*args, **kwargs)

    def __repr__(self):
        return f"<Country {self.name} ID: {self.id} ({self.code})>"

    def __str__(self):
        """
        String representation of the country object.
        """
        status = "Active" if self.is_active else "Inactive"
        last_update = f", updated {self.updated_at.strftime('%Y-%m-%d')}" if self.updated_at else ", just created"
        return f"Country {self.name} ID: {self.id} ({self.code}) - {status}{last_update}"

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['-updated_at', '-created_at']
        db_table = "countries"
        get_latest_by = "updated_at"
        default_related_name = "countries"
        permissions = [
            ("can_publish_country", "Can publish country"),
        ]
        unique_together = [('name', 'code')]

class Networks(models.Model):
    # ForeignKey relation to the Countries model
    country = models.ForeignKey(
        Countries,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text='The country where the network is.',
    )

    # Name of the network
    name = models.CharField(
        verbose_name="Network Name",
        default="",
        max_length=25,
        null=False,
        blank=True,
        db_index=True,
        help_text='Network name such as (Vodafone, Etisalat, etc.).',
    )

    # network code
    code = models.CharField(
        verbose_name="Network Code",
        default="",
        max_length=5,
        null=False,
        blank=True,
        help_text='Prefix used in mobile numbers (e.g., 010, 011, etc.)',
    )

    # Active status
    is_active = models.BooleanField(
        verbose_name="Is Active?",
        help_text="When 'Is Active?' is selected, it means it is activated.",
        default=False,
        null=True,
        blank=True
    )

    # Timestamps and user tracking
    created_at = models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True,
        blank=True, null=True
    )
    created_by = models.ForeignKey(
        UserAccounts,
        verbose_name="Created By",
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='created_networks'
    )
    updated_at = models.DateTimeField(
        verbose_name="Last Updated At",
        auto_now=True,
        blank=True, null=True
    )
    updated_by = models.ForeignKey(
        UserAccounts,
        verbose_name="Updated By",
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='updated_networks'
    )

    def clean(self):
        """
        Custom validation for the Networks model.
        This method is automatically called if full_clean() is used.
        """
        errors = {}

        object_id = 0
        if self.id:
            object_id = self.id
        filter_all_objects = Networks.objects.filter(~models.Q(id=object_id))

        if not self.country:
            errors['name'] = _("Country select is required.")
        else:
            filter_all_objects = filter_all_objects.filter(~models.Q(country__id=self.country.id))
        if not self.name:
            errors['name'] = _("Network name is required.")
        else:
            if filter_all_objects.filter(name__iexact=self.name.lower()):
                errors['name'] = _(f"Name '{self.name}' already exists.")

        if not self.code or len(self.code) > 5:
            errors['code'] = _("Network code must be 5 characters or less.")
        else:
            try:
                int(self.code)
                code_is_integer = True
            except:
                code_is_integer = False
            if code_is_integer is False:
                errors['code'] = _("The network code cannot contain letters and symbols.")
            else:
                if filter_all_objects.filter(code__iexact=self.code.lower()):
                    errors['code'] = _(f"Name '{self.code}' already exists.")

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Override the save method to ensure the model data is validated before saving.
        """
        self.full_clean()  # Custom validation check before saving
        super().save(*args, **kwargs)

    def __repr__(self):
        """
        Return a detailed string representation of the object for debugging.
        """
        return f"<Network {self.name} ID: {self.id} ({self.code})>"

    def __str__(self):
        """
        String representation of the network object, including its status and update time.
        """
        status = "Active" if self.is_active else "Inactive"
        last_update = f", updated {self.updated_at.strftime('%Y-%m-%d')}" if self.updated_at else ", just created"
        return f"Network {self.name} ID: {self.id} ({self.code}) - {status}{last_update}"

    class Meta:
        """
        Meta class to define custom table name, permissions, and order of records.
        """
        verbose_name = "Network"
        verbose_name_plural = "Networks"
        ordering = ['-updated_at', '-created_at']
        db_table = "networks"  # Ensure the table name is networks
        get_latest_by = "updated_at"
        default_related_name = "networks"

        permissions = [
            ("can_publish_network", "Can publish network"),  # Custom permission for publishing networks
        ]

        unique_together = [('name', 'code')]  # Ensures that each network has a unique combination of name and code

class Mobiles(models.Model):
    user = models.ForeignKey(
        UserAccounts,
        verbose_name="User Related",
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='user_mobile'
    )
    network = models.ForeignKey(
        Networks,
        verbose_name="Network Related",
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name="network_mobile"
    )
    number = models.IntegerField(
        default=0,
        verbose_name="Mobile Number",
        blank=True, null=True
    )
    is_verified = models.BooleanField(default=False)
    is_main = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True
    )
    created_by = models.ForeignKey(
        UserAccounts,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_mobile'
    )

    updated_at = models.DateTimeField(
        verbose_name="Last Updated At",
        auto_now=True
    )
    updated_by = models.ForeignKey(
        UserAccounts,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_mobile'
    )

class Emails(models.Model):
    user = models.ForeignKey(
        UserAccounts,
        verbose_name="User Related",
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='user_email'
    )
    network = models.ForeignKey(
        Networks,
        verbose_name="Network Related",
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name="network_email"
    )
    email = models.CharField(
        max_length=255,
        blank=True, null=True
    )
    is_verified = models.BooleanField(default=False)
    is_main = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True
    )
    created_by = models.ForeignKey(
        UserAccounts,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_mobile'
    )

    updated_at = models.DateTimeField(
        verbose_name="Last Updated At",
        auto_now=True
    )
    updated_by = models.ForeignKey(
        UserAccounts,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_mobile'
    )

