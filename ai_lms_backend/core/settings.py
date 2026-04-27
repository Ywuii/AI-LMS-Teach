import os
from pathlib import Path

# 设置项目根目录的绝对路径，Django利用这个路径来定位各种文件的位置
BASE_DIR = Path(__file__).resolve().parent.parent


# 安全配置
# 加密会话、密码的密钥
SECRET_KEY = "django-insecure--_2)6x*5cyc5*^t*$#^1j7b&%r4cl=2^-fj-6*=r4s)pdy($hc"
# 调式模式
DEBUG = True
# 允许访问的域名
ALLOWED_HOSTS = []


# Application definition
# 启用的Django应用列表，自己新注册的应用要在这里注册
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    "chat",
    "authentication",
    "experts",
    "django_apscheduler",
    "system",
    "course"
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
CORS_ALLOWED_ORIGINS = ["http://localhost:8848"]
CORS_ALLOW_CREDENTIALS = True

# URL和模板配置
# 指定Django项目的主URL配置文件的路径
ROOT_URLCONF = "core.urls"
# 定义Django如何查找和渲染HTML
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# 指定WSGI应用的入口
WSGI_APPLICATION = "core.wsgi.application"

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ai_ims',     # 数据库名
        'USER': 'root',          # 数据库用户名
        'PASSWORD': '79113865Xie',      # 数据库密码
        'HOST': 'localhost',             # 数据库主机地址
        'PORT': '3306',                  # 数据库端口
        'OPTIONS': {
            'charset': 'utf8mb4',        # 支持 emoji
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 环境变量配置
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "79113865Xie")

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'api': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Django REST Framework 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# 时区设置
TIME_ZONE = 'Asia/Shanghai'  # 根据你的时区设置
USE_TZ = True

# APScheduler 配置（可选）
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"