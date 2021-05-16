from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name="Название группы", max_length=200,
        help_text=(
            "В названии группы не "
            "должно содержаться "
            "нецензурной лексики "
            "и словосочетаний, "
            "призывающих к конфликту с другими"
            " группами лиц. "
            "Уместите название в 200 символов"
        )
    )
    slug = models.SlugField(
        verbose_name="URL группы", unique=True,
        help_text="Формируется автоматически"
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text=(
            "Ограничений по символам нет, "
            "в остальном обратите внимание"
            " на указания в формировании названия группы"
        )
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст публикации",
        help_text=(
            "Постарайтесь не использовать "
            "нецензурную лексику,"
            "задевать власть, национальные "
            "меньшинства и "
            "других представителей флоры и фауны"
        )
    )
    pub_date = models.DateTimeField(
        "Дата публикации", auto_now_add=True,
        help_text=(
            "Дата публикации "
            "формируется автоматически"
        ),
        db_index=True
    )
    group = models.ForeignKey(
        Group, related_name="posts",
        on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name="Группа",
        help_text=(
            "Укажите группу из предложенных,"
            " где опубликуется пост"
        )
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts",
        verbose_name="Автор", help_text="Автор - это вы"
    )
    image = models.ImageField(
        upload_to='posts/', verbose_name="Изображение", blank=True, null=True,
        help_text="Можете добавить изображение"
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments",
        verbose_name="Комментированный пост",
        help_text="Можете добавить комментарий"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comments", verbose_name="Автор",
        help_text="Автор комментария - это вы"
    )
    text = models.TextField(
        verbose_name="Комментарий",
        help_text="Здесь вы можете написать все, что думаете"
    )
    created = models.DateTimeField(
        verbose_name="Дата создания комментария", auto_now_add=True,
        help_text="Дата формируется автоматически", db_index=True
    )

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower",
        verbose_name="Подписчик",
        help_text="Этот пользователь подписан на автора"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following",
        verbose_name="Автор", help_text="Ваша подписка"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_following'
            )
        ]
