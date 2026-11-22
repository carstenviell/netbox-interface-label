from django.test import TestCase


class TranslationTests(TestCase):
    def test_compiled_catalog_is_current(self):
        """django.mo is shipped (target systems usually lack gettext) - it must contain every translated msgid."""
        import gettext
        import os
        import re
        base = os.path.join(os.path.dirname(__file__), "locale", "de", "LC_MESSAGES")
        po = open(os.path.join(base, "django.po"), encoding="utf-8").read()
        with open(os.path.join(base, "django.mo"), "rb") as f:
            catalog = gettext.GNUTranslations(f)._catalog
        missing = [m for m in re.findall(r"^msgid \"(.+)\"\nmsgstr \"(?!\")", po, re.M)
                   if m.replace(chr(92) + chr(34), chr(34)) not in catalog]
        self.assertEqual(missing, [], "django.mo is outdated - run makemessages/msgfmt (see CLAUDE.md)")
        self.assertEqual(re.findall(r'^#, .*fuzzy.*\n(?:#\|.*\n)*msgid "(.*)"', po, re.M), [], "fuzzy (guessed) translations - fix them")


class DisconnectPrefixMigrationTests(TestCase):
    def test_only_unchanged_default_is_switched(self):
        import importlib
        from django.apps import apps as django_apps
        from .models import LabelFormatSettings
        mig = importlib.import_module('netbox_interface_label.migrations.0003_disconnect_prefix_old')
        self.assertEqual(LabelFormatSettings._meta.get_field('disconnect_prefix').default, 'OLD_')
        LabelFormatSettings.objects.all().delete()
        s = LabelFormatSettings.objects.create(disconnect_prefix='GETRENNT_')
        mig.switch_default(django_apps, None)
        s.refresh_from_db()
        self.assertEqual(s.disconnect_prefix, 'OLD_')
        s.disconnect_prefix = 'CUSTOM_'
        s.save()
        mig.switch_default(django_apps, None)
        s.refresh_from_db()
        self.assertEqual(s.disconnect_prefix, 'CUSTOM_')  # own prefix is kept
