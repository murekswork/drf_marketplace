import logging
import os

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

task_logger = logging.getLogger(name='CELERY TASKS LOGGER')


@shared_task(bind=True, default_retry_delay=10, max_retries=3)
def check_badwords_article(self, article_id):
    from articles.models import Article
    from articles.services.validation.service import ArticleBadwordsValidationService
    try:
        article = Article.objects.get(id=article_id)
        service = ArticleBadwordsValidationService(article)
        result = service.validate()
        if result is True:
            service.publish()
            task_logger.info('Article published')
        else:
            task_logger.info('Article with bad words was not published!')
    except Exception as e:
        task_logger.error(f'Article check task was not completed! {e}', exc_info=True)


@shared_task(bind=True, default_retry_delay=10, max_retries=5)
def check_badwords_product(self, product_id):
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
        self.retry(exc=e)
    else:
        return {'result': 'Product was not published'}


@shared_task(bind=True, default_retry_delay=30, max_retries=5)
def create_product_upload_report(self, tasks_file_name: str, upload_id: str):
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
        task_logger.critical(f'{self.__name__} was not completed! {e}', exc_info=True)
        # if _retry_count < 5:
        self.retry(exc=e)


@shared_task(bind=True, default_retry_delay=30, max_retries=5)
def upload_products_task(self, file, shop_id):
    from shop.models import Shop
    from shop.services.product_upload_services.product_upload import ProductCSVUploader
    try:
        shop = Shop.objects.get(id=shop_id)
        upload_service = ProductCSVUploader(source=file, shop=shop)
        upload_service.upload()
        upload_service.save_tasks()
        return upload_service.get_tasks_filename()
    except Exception as e:
        task_logger.critical(f'{self.__name__} was not completed! {e}', exc_info=True)
        self.retry(exc=e)
