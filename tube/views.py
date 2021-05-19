from rest_framework import status,views,response
from django.shortcuts import render, redirect

from django.views import View
from django.db.models import Q

from django.http.response import JsonResponse
from django.template.loader import render_to_string

from django.core.paginator import Paginator

from django.conf import settings


#TIPS:ログイン状態かチェックする。ビュークラスに継承元として指定する(多重継承なので順番に注意)。未ログインであればログインページへリダイレクト。
from django.contrib.auth.mixins import LoginRequiredMixin


from .models import Video,Category,Tag,VideoComment
from .forms import VideoForm, VideoEditForm,VideoCommentForm
from .serializer import VideoSerializer,VideoCommentSerializer

#python-magicで受け取ったファイルのMIMEをチェックする。
#MIMEについては https://developer.mozilla.org/ja/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types を参照。

import magic
ALLOWED_MIME   = ["video/mp4", "image/vnd.adobe.photoshop", "application/postscript", "image/jpeg", "image/png"]

# アップロードの上限
LIMIT_SIZE     = 200 * 1000 * 1000

SEARCH_AMOUNT_PAGE  = 20

#トップページ
class IndexView(View):

    def get(self, request, *args, **kwargs):

        videos = Video.objects.all().order_by("-dt")

        paginator  = Paginator(videos,7)

        if "page" in request.GET:
            videos    = paginator.get_page(request.GET["page"])
        else:
            videos    = paginator.get_page(1)

        context = {"videos": videos,}

        return render(request, "tube/index.html", context)

index = IndexView.as_view()

#アップロードページ
class UploadView(LoginRequiredMixin,View):

    def get(self,request, *args, **kwargs):

        categories = Category.objects.all()
        context = {"categories": categories}

        return render(request, "tube/upload.html", context)


    def post(self, request, *args, **kwargs):

        # TIPS:request.POSTだけでなく、request.FILESも引数に入れる。
        formset = VideoForm(request.POST, request.FILES)

        fileflag = False

        if "movie" in request.FILES:
            mime_type = magic.from_buffer(request.FILES["movie"].read(1024), mime=True)

            if request.FILES["movie"].size >= LIMIT_SIZE:
                mb = str(LIMIT_SIZE / 1000000)

                json = {"error": True,
                        "message": "The maximum file size is " + mb + "MB"}

                return JsonResponse(json)

            if mime_type not in ALLOWED_MIME:
                mime = str(ALLOWED_MIME)
                json = {"error": True,
                        "message": "The file you can post is " + mime + "."}

                return JsonResponse(json)

            if mime_type in ALLOWED_MIME:
                fileflag = True

        else:
            fileflag = True

        # ↑アップロードされたファイルが許可されているMIMEである、もしくはアップロードされていない場合。リクエストの保存を許可する。

        if formset.is_valid():
            print("バリデーションOK")

            if fileflag:
                formset.save()
            else:
                print("このファイルは許可されていません。")

        else:
            print("バリデーションエラー")

        return redirect("tube:index")


upload = UploadView.as_view()


#検索結果表示ページ
class SearchView(View):

    def get(self, request, *args, **kwargs):

        query = Q()
        page = 1

        if "word" in request.GET:

            word_list = request.GET["word"].replace("　", " ").split(" ")
            for w in word_list:
                query &= Q(Q(title__icontains=w) | Q(description__icontains=w))

        if "page" in request.GET:
            page = request.GET["page"]

        videos = Video.objects.filter(query).order_by("-dt")
        amount = len(videos)

        videos_paginator = Paginator(videos, SEARCH_AMOUNT_PAGE)
        videos = videos_paginator.get_page(page)

        context = {"videos": videos,
                   "amount": amount}
        return render(request, "tube/search.html", context)


search = SearchView.as_view()


#動画個別ページ
class SingleView(View):

    def get(self,request, video_pk, *args, **kwargs):

        video = Video.objects.filter(id=video_pk).first()

        comments = VideoComment.objects.filter(target=video_pk).order_by("-dt")

        paginator = Paginator(comments, 5)

        if "page" in request.GET:
            comments = paginator.get_page(request.GET["page"])
        else:
            comments = paginator.get_page(1)

        context = {"video": video,
                   "comments": comments,
                   }

        return render(request, "tube/single.html", context)


    def post(self, request, video_pk, *args, **kwargs):


        copied   = request.POST.copy()

        copied["target"]  = video_pk

        form  = VideoCommentForm(copied)

        if form.is_valid():
            print("コメントバリデーションOK")
            form.save()

        else:
            print("コメントバリデーションNG")

        return redirect("tube:single", video_pk=video_pk)

single = SingleView.as_view()


class DeleteView(LoginRequiredMixin,View):

    def get(self, request, video_pk, *args, **kwargs):

        video   = Video.objects.filter(id=video_pk).first()
        context = { "video":video }

        return render(request, "tube/delete.html", context )


    def post(self, request, video_pk, *args, **kwargs):

        print("削除")

        # .first()で一番上のレコードを1つ取る。
        video    = Video.objects.filter(id=video_pk).first()
        video.delete()

        # TIPS:すでにurls.pyにてpkが数値型であることがわかっているので、バリデーションをする必要はない。

        return redirect("tube:index")

delete = DeleteView.as_view()


class UpdateView(LoginRequiredMixin,View):

    def get(self, request, video_pk, *args, **kwargs):

        video   = Video.objects.filter(id=video_pk).first()
        context = { "video":video }

        return render(request, "tube/update.html", context )

    def post(self, request, video_pk, *args, **kwargs):

        # まず、編集対象のレコード特定
        instance    = Video.objects.filter(id=video_pk).first()

        # 第2引数にinstanceを指定することで、対象の編集ができる。
        formset     = VideoEditForm(request.POST, instance=instance)

        if formset.is_valid():
            print("バリデーションOK")
            formset.save()
            Video.objects.filter(id=video_pk).update(edited=True)

        else:
            print("バリデーションNG")

        return redirect("tube:index")


update  = UpdateView.as_view()
