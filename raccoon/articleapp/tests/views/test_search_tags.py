from articleapp.models import Tag
from django.test import Client, TestCase
from django.urls import reverse_lazy


class SearchTagsViewTests(TestCase):
    def setUp(self):
        self.url_path = reverse_lazy("search_tags")

    def test_タグ検索(self):
        tags = [Tag(name=f"tag_{i}_タグ{i}") for i in range(20)]
        tags = Tag.objects.bulk_create(tags)
        tags = [{"id": tag.id, "name": tag.name} for tag in tags]

        c = Client()
        # クエリパラメータ無し
        response = c.get(self.url_path)
        self.assertListEqual(response.json()["tags"], tags)
        # キーワード空文字
        response = c.get(self.url_path, {"keyword": ""})
        self.assertListEqual(response.json()["tags"], tags)
        # 完全一致
        response = c.get(self.url_path, {"keyword": "tag_1_タグ1"})
        self.assertListEqual(response.json()["tags"], [tags[1]])
        # 大文字小文字を区別しない
        response = c.get(self.url_path, {"keyword": "TAG_1_タグ1"})
        self.assertListEqual(response.json()["tags"], [tags[1]])
        # 部分一致
        response = c.get(self.url_path, {"keyword": "ag_1"})
        self.assertListEqual(response.json()["tags"], [tags[1]] + tags[10:20])
