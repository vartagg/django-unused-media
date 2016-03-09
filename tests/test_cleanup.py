from preggy import expect
from django.db import models

from django_unused_media.cleanup import _get_file_fields, _get_all_media, get_used_media, get_unused_media, _remove_media, remove_unused_media
from .base import BaseTestCase
from .models import FileFieldsModel, CustomFileldsModel
from .utils import create_file, create_image, create_file_and_write, exists_media_path


class UtilsTestCase(BaseTestCase):
    def setUp(self):
        super(UtilsTestCase, self).setUp()

        self.model1 = FileFieldsModel(
            file_field=create_file('file1.txt'),
            image_field=create_image('image1.jpg'),
            char_field='test1'
        )
        self.model1.save()

        self.model2 = FileFieldsModel(
            file_field=create_file('file2.txt'),
            image_field=create_image('image2.jpg'),
            char_field='test2'
        )
        self.model2.save()

        self.model3 = CustomFileldsModel(
            custom_field=create_file('file3.txt'),
            char_field='test3'
        )
        self.model3.save()

        self.model4 = CustomFileldsModel(
            char_field='test4'
        )
        self.model4.save()

    def test_get_file_fields(self):
        file_fields = _get_file_fields()
        expect(file_fields).to_be_instance_of(list).to_length(3)

        for f in file_fields:
            expect(f).to_be_instance_of(models.FileField)

        file_fields_names = [f.name for f in file_fields]

        expect(file_fields_names).to_include('file_field').to_include('image_field').to_include('custom_field')
        expect(file_fields_names).Not.to_include('char_field')

    def test_get_used_media(self):
        expect(get_used_media())\
            .to_be_instance_of(list).to_length(5)\
            .to_include(self.model1.file_field.name)\
            .to_include(self.model1.image_field.name)\
            .to_include(self.model2.file_field.name)\
            .to_include(self.model2.image_field.name)\
            .to_include(self.model3.custom_field.name)

    def test_get_all_media(self):
        expect(_get_all_media())\
            .to_be_instance_of(list).to_length(5)\
            .to_include(self.model1.file_field.name)\
            .to_include(self.model1.image_field.name)\
            .to_include(self.model2.file_field.name)\
            .to_include(self.model2.image_field.name)\
            .to_include(self.model3.custom_field.name)

    def test_get_all_media_with_additional(self):
        create_file_and_write('file.txt')
        expect(_get_all_media())\
            .to_be_instance_of(list).to_length(6)\
            .to_include(self.model1.file_field.name)\
            .to_include(self.model1.image_field.name)\
            .to_include(self.model2.file_field.name)\
            .to_include(self.model2.image_field.name)\
            .to_include(self.model3.custom_field.name)\
            .to_include('file.txt')

    def test_get_unused_media_empty(self):
        expect(get_unused_media()).to_be_empty()

    def test_get_unused_media(self):
        create_file_and_write('notused.txt')
        used_media = get_unused_media()
        expect(used_media).to_be_instance_of(list).to_length(1)
        expect(used_media[0]).to_match(r'^.*notused.txt')

    def test_get_unused_media_subfolder(self):
        create_file_and_write('subfolder/notused.txt')
        used_media = get_unused_media()
        expect(used_media).to_be_instance_of(list).to_length(1)
        expect(used_media[0]).to_match(r'^.*subfolder/notused.txt$')

    def test_remove_media(self):
        expect(exists_media_path('file.txt')).to_be_false()
        create_file_and_write('file.txt')
        expect(exists_media_path('file.txt')).to_be_true()
        _remove_media(['file.txt'])
        expect(exists_media_path('file.txt')).to_be_false()

    def test_remove_unused_media(self):
        expect(get_unused_media()).to_be_empty()
        create_file_and_write('notused.txt')
        expect(get_unused_media()).Not.to_be_empty()
        remove_unused_media()
        expect(get_unused_media()).to_be_empty()