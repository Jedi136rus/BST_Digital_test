from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Robot
from orders.models import Order
from django.core.mail import send_mail
from R4C.settings import EMAIL_HOST_USER


@receiver(post_save, sender=Robot)
def post_save_robot(created, **kwargs):
    if created:
        serial = kwargs['instance'].serial
        orders = Order.objects.filter(robot_serial__iexact=serial).all()
        # в теории можно отправить только первому (раннему заказчику) т.к. робот один поставили
        # лучше все же всем отправить, и кто первый купит
        for ord in orders:
            email = ord.customer.email
            model = kwargs['instance'].model
            version = kwargs['instance'].version
            message = f"Добрый день!\nНедавно вы интересовались нашим роботом модели {model}, версии {version}.\n" \
                      f"Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами"
            # send_db_mail('welcome', email, use_celery=False)
            send_mail(
                "Поступление роботов!",
                message,
                EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            print(f'отправил {email}')
            # поидее нужно удалить запись, т.к. заказ может быть выполнен
            ord.delete()
