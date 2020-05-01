from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Tworzy i zapisuje w bazie danych użytkownika.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Tworzy i zapisuje w bazie danych użytkownika. Domyślnie nie jest to superużytkownik, ani członek zarządu.
        """
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        if password is None:
            password = self.make_random_password()
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Tworzy superużytkownika.
        :param email:
        :param password:
        :param extra_fields:
        :return:
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self._create_user(email, password, **extra_fields)
