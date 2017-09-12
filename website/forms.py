from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from root.models import Profile, Post, Comment


class UserRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter email'}))
    birthday = forms.DateField(required=False, widget=forms.DateInput(format='%d/%m/%Y',
                                                      attrs={'placeholder': 'DD/MM/YYYY'}),
                               input_formats=('%d/%m/%Y',))
    country = forms.CharField(required=False, max_length=100,
                              widget=forms.TextInput(attrs={'placeholder': 'Enter country'}))
    city = forms.CharField(required=False, max_length=100,
                           widget=forms.TextInput(attrs={'placeholder': 'Enter city'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput(attrs={'placeholder': 'Repeat Password'}))

    class Meta:
        model = get_user_model()
        fields = ['email', 'password1', 'password2', 'birthday', 'country', 'city']

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    def clean_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if str(password1) == str(password2):
            print(password1)
            print(password2)
            raise ValidationError("Passwords are not identical!")
        if len(password1) < 6:
            raise ValidationError("Password must have 6 or more chars!")
        if len(password1) == len([i for i in password1 if i.isdigit()]):
            raise ValidationError("Password can not consist only of digits!")
        return password1

    def clean(self):
        return self.cleaned_data

    def save(self):
        data = self.cleaned_data
        user = get_user_model().objects.create(email=data['email'])
        user.set_password(data['password1'])
        user.save()
        user_profile = Profile.objects.get(user=user)
        user_profile.birthday = data['birthday']
        user_profile.country = data['country']
        user_profile.city = data['city']
        user_profile.save()


class UserLoginForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))

    class Meta:
        model = get_user_model()
        fields = ['email', 'password']

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            return email
        else:
            raise ValidationError("Email can't be empty")

    def clean_password(self):
        password = self.cleaned_data.get('password', None)
        if len(password) < 6:
            raise ValidationError("Password must have 6 or more chars!")
        return password

    def clean(self):
        return self.cleaned_data


class VerifyEmailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VerifyEmailForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    code = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter verification code'},))

    class Meta:
        model = get_user_model()
        fields = ['code']

    def clean(self):
        return self.cleaned_data


class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    search = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Search'},))

    def clean(self):
        return self.cleaned_data


class PostCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostCreateForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Post
        exclude = ('owner',)
        fields = ['title', 'image', 'text']

    def clean(self):
        return self.cleaned_data


class CommentCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentCreateForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    text = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter comment'}, ))

    class Meta:
        model = Comment
        exclude = ('owner', 'post')
        fields = ['text', ]

    def clean(self):
        return self.cleaned_data