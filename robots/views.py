from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd
import datetime
from io import BytesIO

from .models import Robot
from .forms import RobotForm


@method_decorator(csrf_exempt, name='dispatch')
class RobotsApi(View):

    def post(self, request):
        data = json.loads(request.body.decode())
        # переведем все строковые значения в верхний регистр
        for key in data:
            if type(data[key]) == str:
                data[key] = data[key].upper()
        new_obj = RobotForm(data)
        # провалидируем входные данные
        if new_obj.is_valid():
            # если поле serial не передалось составим его из model и version
            if not data.get("serial", None):
                data['serial'] = f"{data['model']}-{data['version']}"
            new_robot = Robot.objects.create(**data)
            new_robot.save()
            return JsonResponse({'response': data,
                                 'result': 'ok'}, status=200)
        else:
            # соберем ошибки в переданных полях
            response = {}
            for k in new_obj.errors:
                response[k] = new_obj.errors[k][0]
            return JsonResponse({'response': response, 'result': 'error'}, status=404)


def excel_report(request):
    date_end = datetime.date.today() - datetime.timedelta(weeks=1)

    queryset = Robot.objects.exclude(created__lt=date_end).all()
    # проверим есть ли вообще записи за этот период
    if len(queryset) == 0:
        return JsonResponse({'response': {'message': 'empty robots list'}, 'result': 'error'}, status=404)
    robots_df = pd.DataFrame(list(queryset.values('model', 'version')))
    robots_df['Количество за неделю'] = 1   # создадим поле что бы потом использовать сумму для подсчета кол-ва
    robots_df = robots_df.groupby(['model', 'version'], as_index=False).aggregate({'Количество за неделю': 'sum'})\
        .rename(columns={'model': 'Модель', 'version': 'Версия'})

    with BytesIO() as b:
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        # найдем модели по которым будем формировать страницы
        models = list(robots_df['Модель'].drop_duplicates())
        for model in models:
            list_df = robots_df.loc[robots_df['Модель'] == model]
            list_df.to_excel(writer, sheet_name=model)
        writer.close()

        # Set up the Http response.
        filename = f'robot_report(since {date_end} till {datetime.date.today()}).xlsx'
        response = HttpResponse(
            b.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
