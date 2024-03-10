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
        service.unpublish()
        return {'result': f'{product.title} was not published because it has bad words'}


@shared_task(bind=True, default_retry_delay=30, max_retries=5)
def create_product_upload_report(self, tasks_file_name: str, upload_id: str):
    from shop.models import ProductUpload
    from shop.services.service import CsvOutputLogService, UploadLogger
    upload = ProductUpload.objects.get(id=upload_id)
    logger = UploadLogger(task_results_filename=tasks_file_name, upload=upload)
    try:
        logger.read_dataclasses_from_file()
        result = logger.start_work()
        output_logs = CsvOutputLogService(file_path=f'backend/tasks_data/{upload.file_name}.csv', report_result=result)
        output_logs.export_csv()
    except Exception as e:
        logging.warning(f'Task did not started because of {e}')
        self.retry(exc=e)
