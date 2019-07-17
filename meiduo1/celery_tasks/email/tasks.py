
from django.core.mail import send_mail
from meiduo1 import settings
from celery_tasks.main import app
from apps.users.utils import generate_verify_email_url

@app.task(bind=True,name='send_verify_email', retry_backoff=3)
def send_active_email(self,email,user_id):
    subject = '美多商场激活邮件'
    message = '成功'
    from_email = settings.EMAIL_FROM
    recipient_list = [email]
    verify_url = generate_verify_email_url(user_id)
    html_message =  '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email,verify_url,verify_url)
    try:
        result = send_mail(subject, message, from_email, recipient_list,html_message=html_message)
    except Exception as e:
        raise self.retry(exc=e,max_retries=3)
    if result != 0:
        raise self.retry(exc=Exception("发送异常"),max_retries=3)
