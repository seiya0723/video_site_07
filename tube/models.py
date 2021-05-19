from django.db import models
from django.utils import timezone

import uuid


class Category(models.Model):

    class Meta:
        db_table = "category"

    # TIPS:数値型の主キーではPostgreSQLなど一部のDBでエラーを起こす。それだけでなく予測がされやすく衝突しやすいので、UUID型の主キーに仕立てる。
    id     = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    name   = models.CharField(verbose_name="カテゴリ名", max_length=20)

    def __str__(self):
        return self.name

#実際には動画サイトで多対多を実装する時、良いね悪いねの評価等に使う。タグはハッシュタグとして扱うほうがよい。
class Tag(models.Model):

    class Meta:
        db_table = "tag"

    id     = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    name   = models.CharField(verbose_name="タグ名", max_length=20)

    def __str__(self):
        return self.name


class Video(models.Model):

    class Meta:

        db_table = "video"

    id       = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    title    = models.CharField(verbose_name="タイトル", max_length=50)

    category = models.ForeignKey(Category, verbose_name="カテゴリ", on_delete=models.PROTECT)

    tag      = models.ManyToManyField(Tag, verbose_name="タグ", blank=True)

    description  = models.CharField(verbose_name="動画説明文", max_length=300)
    dt           = models.DateTimeField(verbose_name="投稿日", default=timezone.now)
    edited       = models.BooleanField(default=False)

    movie        = models.FileField(verbose_name="動画",upload_to="tube/movie",blank=True)
    mime         = models.TextField(verbose_name="MIMEタイプ", null=True)
    thumbnail    = models.ImageField(verbose_name="サムネイル", upload_to="tube/thumbnail/", null=True)

    def __str__(self):
        return self.title


class VideoComment(models.Model):

    class Meta:
        db_table = "comment"

    id      = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    content = models.CharField(verbose_name="コメント文", max_length=500)
    target  = models.ForeignKey(Video, verbose_name="コメント先の動画", on_delete=models.CASCADE)
    dt      = models.DateTimeField(verbose_name="投稿日", default=timezone.now)

    def __str__(self):
        return self.content

