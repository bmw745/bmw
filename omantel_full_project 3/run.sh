#!/bin/bash

# إيقاف أي عمليات gunicorn موجودة
pkill -9 gunicorn 2>/dev/null || true

# بدء الخادم مع ملف التكوين
echo "بدء تشغيل خادم Gunicorn..."
exec gunicorn -c gunicorn_config.py app:app
