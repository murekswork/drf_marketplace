import logging
import os
import time

from celery import Celery, shared_task

from cfehome.settings import CELERY_BROKER_URL

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfehome.settings')

app = Celery('service')
app.config_from_object('django.conf:settings')
app.conf.broker_url = CELERY_BROKER_URL
app.conf.result_backend = CELERY_BROKER_URL
app.autodiscover_tasks()


@shared_task()
def check_badwords_article(article_id):
    from articles.models import Article
    from articles.services.service import ArticleBadWordsValidator
    time.sleep(5)
    article = Article.objects.get(id=article_id)
    service = ArticleBadWordsValidator(article)
    result = service.validate_bad_words()
    if result is True:
        service.publish()
        print('Article published')
    else:
        print('Bad article was not published!')


@shared_task()
def check_badwords_product(product_id):
    from products.models import Product
    from products.services.service import ProductBadWordsValidateService
    product = Product.objects.get(id=product_id)
    service = ProductBadWordsValidateService(product)
    result = service.validate_bad_words()
    if result is True:
        service.publish()
        return {'result': f'{product.title} was published'}
    else:
        return {'result': f'{product.title} was not published because it has bad words'}


@shared_task(bind=True, default_retry_delay=30 * 60, max_retries=5)
def get_upload_logs(self, tasks: list, upload_id: str):
    from shop.services.service import UploadLogger
    from shop.models import ProductUpload
    upload = ProductUpload.objects.get(id=upload_id)
    logger = UploadLogger(task_results=tasks, upload=upload)
    try:
        result = logger.start_work()
        with open(f'backend/tasks_data/{upload.file_name}.txt', 'w+') as f:
            f.write(str(result))

    except Exception as e:
        logging.warning(f'Task did not started because of {e}')
        self.retry(exc=e)
