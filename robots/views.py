from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

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
                # проверим создание экземпляра на наличие дублей
                if Robot.objects.filter(model=data['model'], version=data['version']).exists():
                    return JsonResponse({'response': f"{data['model']}-{data['version']} is already exist",
                                         'result': 'error'}, status=404)
                else:
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
        return JsonResponse({'msg': 'ok'}, status=200)


