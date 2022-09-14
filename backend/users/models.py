from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole:
    USER = 'user'
    ADMIN = 'admin'

ROLES = (
    (UserRole.USER, UserRole.USER),
    (UserRole.ADMIN, UserRole.ADMIN)
)

class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Email пользователя',
        max_length=254,
        blank=False,
        unique=True
    )
    username = models.CharField(
        verbose_name='Логин пользователя',
        max_length=150,
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False
    )
    role = models.CharField(
        verbose_name='Права доступа',
        max_length=10,
        choices=ROLES,
        default='user'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'],
                name="unique_auth"
            ),
        ]

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self):
        return (
            self.role == UserRole.ADMIN
            or self.is_staff
            or self.is_superuser
        )

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            )
        ]
