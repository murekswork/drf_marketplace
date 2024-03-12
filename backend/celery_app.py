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
app.conf.update(
    CELERY_WORKER_CONCURRENCY=4
)
app.autodiscover_tasks()


@shared_task()
def check_badwords_article(article_id):
    from articles.models import Article
    from articles.services.validation.service import (
        ArticleEntityBadWordsValidationService,
    )
    time.sleep(5)
    article = Article.objects.get(id=article_id)
    service = ArticleEntityBadWordsValidationService(article)
    result = service.validate()
    if result is True:
        service.publish()
        print('Article published')
    else:
        print('Bad article was not published!')


@shared_task(bind=True, default_retry_delay=10, max_retries=5)
def check_badwords_product(self, product_id, _retry_count=0):
    from products.models import Product
    from products.services.validation.product_validation import (
        ProductEntityBadWordsValidateService,
    )
    try:
        product = Product.objects.get(id=product_id)
        service = ProductEntityBadWordsValidateService(product)
        result = service.validate()
        if result is True:
            service.publish()
            return {'result': f'{product.title} was published'}
        else:
            service.unpublish()
            return {'result': f'{product.title} was not published because it has bad words'}
    except Exception as e:
        logging.warning(f'Task did not started because of {e}')
        if _retry_count < 5:
            self.retry(exc=e, kwargs={'_retry_count': _retry_count + 1})
        else:
            return {'result': 'Product was not published'}


@shared_task(bind=True, default_retry_delay=30, max_retries=5)
def create_product_upload_report(self, tasks_file_name: str, upload_id: str, _retry_count=0):
    from shop.models import ProductUpload
    from shop.services.product_upload_services.upload_log_exporter_service import (
        CsvUploadResultExporter,
    )
    from shop.services.product_upload_services.upload_log_maker_service import (
        UploadLogMaker,
    )
    try:
        upload = ProductUpload.objects.get(id=upload_id)
        logger = UploadLogMaker(task_results_filename=tasks_file_name, upload=upload)
        result = logger.create_report()
        output_logs = CsvUploadResultExporter(
            output_source=f'backend/tasks_data/{upload.file_name}.csv', input_report_result=result)
        output_logs.export()
    except Exception as e:
        logging.warning(f'Task did not started because of {e}')
        if _retry_count < 5:
            self.retry(exc=e, kwargs={
                'retry_count': _retry_count + 1})
        else:
            logging.critical(f'Could not create product upload report BECAUSE OF {e}')


@shared_task(bind=True, default_retry_delay=30, max_retries=5)
def upload_products_task(self, file, shop_id):
    from shop.models import Shop
    from shop.services.product_upload_services.product_upload import ProductCSVUploader
    shop = Shop.objects.get(id=shop_id)
    upload_service = ProductCSVUploader(source=file, shop=shop)
    upload_service.upload()
    upload_service.save_tasks()
    return upload_service.get_tasks_filename()
