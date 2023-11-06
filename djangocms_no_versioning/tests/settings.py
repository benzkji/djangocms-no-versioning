"""Settings that need to be set in order to run the tests."""
import os
import logging


DEBUG = True

logging.getLogger("factory").setLevel(logging.WARN)

SITE_ID = 1
CMS_CONFIRM_VERSION4 = True

# from selenium.webdriver.firefox import webdriver
# from selenium.webdriver.phantomjs import webdriver
# SELENIUM_WEBDRIVER = webdriver

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite",
    }
}

X_FRAME_OPTIONS = "SAMESITE"

LANGUAGE_CODE = "en"
LANGUAGES = (
    (
        "en",
        "English",
    ),
    (
        "de",
        "Deutsch",
    ),
    (
        "fr",
        "Frentsch",
    ),
)

ROOT_URLCONF = "djangocms_no_versioning.tests.urls"

MEDIA_ROOT = os.path.join(APP_ROOT, "tests/test_app_media")
MEDIA_URL = "/media/"
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(APP_ROOT, "../test_app_static")

CMS_PLACEHOLDER_CONF = {
    "translated_placeholder": {
        "language_fallback": False,
    },
    "untranslated_placeholder": {
        "language_fallback": False,
        # 'untranslated': True,  # legacy version
        "untranslated": "en",
    },
    "editmode_fallback_placeholder": {
        "language_fallback": True,
        "editmode_language_fallback": True,
    },
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # 'DIRS': [],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "sekizai.context_processors.sekizai",
                "cms.context_processors.cms_settings",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
                # 'django.template.loaders.eggs.Loader',
            ],
        },
    },
]

CMS_TEMPLATES = (("base.html", "Default"),)

CMS_PERMISSION = True
CMS_CACHE_DURATIONS = {
    "menus": 60,
    "content": 60,
}

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(os.path.join(APP_ROOT, "tests/coverage"))
COVERAGE_MODULE_EXCLUDES = [
    "tests$",
    "settings$",
    "urls$",
    "locale$",
    "migrations",
    "fixtures",
    "admin$",
    "django_extensions",
]

EXTERNAL_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "sekizai",
    "treebeard",
    "cms",
    "menus",
    "djangocms_text_ckeditor",
    "django.contrib.admin",
]

INTERNAL_APPS = [
    "djangocms_no_versioning",
    "djangocms_no_versioning.tests.test_app",
]

INSTALLED_APPS = INTERNAL_APPS + EXTERNAL_APPS
COVERAGE_MODULE_EXCLUDES += EXTERNAL_APPS

SECRET_KEY = "foobarasdvcasdvasXXXxxsvXY"

MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]
