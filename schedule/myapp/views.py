from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.serializers import json, serialize
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Amats
from .models import Pakalpojums
from .models import Darbinieki
from .forms import MemberForm, ChangeStatusForm
from .forms import ServiceEditForm
from django.contrib import messages
from .forms import MemberEditForm
from django.views.generic.detail import DetailView
from .forms import ServiceForm
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, AmatsForm, UserLoginForm, SaveInfoForm, DarbAprakstsForm
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime, date
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.mail import send_mail
import json
from django.core.serializers import serialize
from .models import Amats, Darbinieki, Pakalpojums


def employee_base(request):
    all_darbinieki = Darbinieki.objects.all()
    return render(request, "employee_base.html", {'all': all_darbinieki})


def service_base(request, status=None):
    if status == 'drizuma':
        all_service = Pakalpojums.objects.filter(datums__gt=date.today(), status__isnull=True)
    elif status == 'nokaveti':
        all_service = Pakalpojums.objects.filter(datums__lte=date.today(), status__isnull=True)
    elif status == 'pabeigti':
        all_service = Pakalpojums.objects.exclude(status__isnull=True)
    else:
        all_service = Pakalpojums.objects.all()

    context = {'all': all_service, 'status': status}
    return render(request, "service_base.html", context)


def service_employee(request, status=None):
    user = request.user
    darb_ID = request.session.get('darb_ID')
    # Получаем все услуги для текущего пользователя (darb_ID)
    employee_all_service = Pakalpojums.objects.filter(darb_ID=darb_ID)

    if status == 'uzsaktie':
        employee_all_service = employee_all_service.filter(status=0)
    elif status == 'drizuma':
        employee_all_service = employee_all_service.filter(datums__gt=date.today(), status=None)
    elif status == 'nokaveti':
        employee_all_service = employee_all_service.filter(datums__lte=date.today(), status=None)
    elif status == 'pabeigti':
        employee_all_service = employee_all_service.filter(status=1)
    elif status == 'atsauksmes':
        employee_all_service = employee_all_service.filter(status=1, darb_kval__gt=0)
    context = {'employee_services': employee_all_service, 'status': status}
    return render(request, "service_employee.html", context)


def user_service(request):
    pakalpojums = Pakalpojums.objects.first()  # или используйте логику для выбора нужного объекта
    form = SaveInfoForm(request.POST or None, instance=pakalpojums)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # дополнительные действия после сохранения формы
            return redirect('user_service')

    return render(request, "user_service.html", {'pakalpojums': pakalpojums, 'form': form})


def prof_base(request):
    all_amats = Amats.objects.all()
    form = AmatsForm()

    if request.method == 'POST':
        form = AmatsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('prof_base')

    return render(request, 'prof_base.html', {'all': all_amats, 'form': form})


def prof_edit(request, pk):
    amats = get_object_or_404(Amats, amata_ID=pk)

    if request.method == 'POST':
        form = AmatsForm(request.POST, instance=amats)
        if form.is_valid():
            form.save()
            # Redirect to prof_base or any other appropriate URL
            return redirect('prof_base')
    else:
        form = AmatsForm(instance=amats)

    return render(request, 'prof_edit.html', {'form': form, 'amats': amats})


def employee(request):
    if request.method == "POST":
        form = MemberForm(request.POST or None)
        if form.is_valid():
            form.save()
        else:
            vards = request.POST['vards']
            uzvards = request.POST['uzvards']
            personas_kods = request.POST['personas_kods']
            # amats = request.POST['amats']
            talrunis = request.POST['talrunis']
            dz_datums = request.POST['dz_datums']
            uzsak_datums = request.POST['uzsak_datums']
            prasmes = request.POST['prasmes']
            login = request.POST['login']
            parole = request.POST['parole']

            messages.success(request, (" Parbaudiet pierakstītas vērtības!"))
            return render(request, "employee.html", {
                'vards': vards,
                'uzvards': uzvards,
                'personas_kods': personas_kods,
                # 'amats': amats,
                'talrunis': talrunis,
                'dz_datums': dz_datums,
                'uzsak_datums': uzsak_datums,
                'prasmes': prasmes,
                'login': login,
                'parole': parole,
            })

        messages.success(request, ('Jauns darbinieks tiek saglabats!'))
        return redirect('employee_base')
    else:
        form = MemberEditForm()  # Замените на свою форму

    nos = Amats.objects.all()
    return render(request, "employee.html", context={
        'form': form,
        'nos': nos,
    })


def service(request):
    darbinieki = Darbinieki.objects.filter(menedzeris=False)

    if request.method == "POST":
        form = ServiceForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, ('Jauns pakalpojums tiek saglabāts!'))
            return redirect('service_base')
        else:
            messages.success(request, (" Parbaudiet pierakstītas vērtības!"))
            return render(request, "service.html", {'form': form, 'darbinieki': darbinieki})
    else:
        form = ServiceForm()

    return render(request, "service.html", {'form': form, 'darbinieki': darbinieki})


class EmployeeDetailView(DetailView):
    model = Darbinieki
    template_name = 'employee_detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получение реального amata только для неменеджеров
        context['real_amats'] = Amats.objects.filter(darbinieki__menedzeris=False).distinct()

        return context


class ServiceDetailView(DetailView):
    model = Pakalpojums
    template_name = 'service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['darbinieki'] = Darbinieki.objects.filter(menedzeris=False)

        # Получение объекта darbinieks, который связан с pakalpojums
        darbinieks = self.object.darb_ID

        # Передача объекта darbinieks в контекст
        context['selected_darbinieks'] = darbinieks
        return context


def employee_delete(request, pk):
    employee = get_object_or_404(Darbinieki, darb_ID=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_base')
    return render(request, 'employee_delete.html', {'employee': employee})


def service_delete(request, pk):
    service = get_object_or_404(Pakalpojums, pak_ID=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('service_base')
    return render(request, 'service_delete.html', {'service': service})


def prof_delete(request, pk):
    prof = get_object_or_404(Amats, amata_ID=pk)
    if request.method == 'POST':
        prof.delete()
        return redirect('prof_base')
    return render(request, 'prof_delete.html', {'prof': prof})


def save_employee(request, pk):
    nos = Amats.objects.all()
    employee = get_object_or_404(Darbinieki, darb_ID=pk)

    if request.method == 'POST':
        form = MemberEditForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Darbinieks veiksmīgi saglabāts!')
            return redirect('employee_base')
        else:
            messages.error(request, 'Radās kļūda saglabājot darbinieku. Pārbaudiet ievadītos datus.')

            # Вывод значений полей в командной строке
            for field, value in form.cleaned_data.items():
                print(f'{field}: {value}')

            return render(request, 'employee_detail.html',
                          {'form': form, 'employee': employee, 'errors': form.errors, 'nos': nos})
    else:
        form = MemberEditForm(instance=employee)

    # Вывод значений полей в командной строке
    for field, value in form.cleaned_data.items():
        print(f'{field}: {value}')

    return render(request, 'employee_detail.html',
                  {'form': form, 'employee': employee, 'nos': nos, 'errors': form.errors})


def save_service(request, pk):
    darbinieki = Darbinieki.objects.all()
    service = get_object_or_404(Pakalpojums, pak_ID=pk)
    if request.method == 'POST':
        form = ServiceEditForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pakalpojums veiksmīgi saglabāts!')
            return redirect('service_base')
        else:
            messages.error(request, 'Radās kļūda saglabājot pakalpojumu. Pārbaudiet ievadītos datus.')
            return render(request, 'service_detail.html',
                          {'form': form, 'service': service, 'errors': form.errors, 'darbinieki': darbinieki})
    else:
        form = ServiceEditForm(instance=service)

    return render(request, 'service_detail.html', {'form': form, 'service': service, 'darbinieki': darbinieki})


from django.contrib.sessions.models import Session


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            parole = form.cleaned_data['parole']

            user = Darbinieki.objects.filter(login=login).first()
            if user and check_password(parole, user.parole):
                try:
                    request.session['darb_ID'] = user.darb_ID
                    request.session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    request.session['menedzeris'] = user.menedzeris
                    request.session['login_status'] = True
                    request.session['login_vards'] = user.vards
                    request.session['login_uzvards'] = user.uzvards

                    if user.menedzeris:
                        return redirect('service_base')
                    else:

                        employee_services = Pakalpojums.objects.filter(darb_ID=user.darb_ID)
                        # Передайте employee_services в контекст
                        context = {'employee_services': employee_services, 'status': None}
                        return render(request, "service_employee.html", context)
                except Exception as e:
                    return JsonResponse({'error': f'Error setting session data: {str(e)}'})
            else:
                messages.error(request, 'Nepareizs login vai parole')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout(request):
    response = HttpResponseRedirect(reverse('login'))
    request.session.flush()
    return response


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            r_numurs = form.cleaned_data['r_numurs']
            k_parole = form.cleaned_data['k_parole']

            try:
                pakalpojums = Pakalpojums.objects.get(r_numurs=r_numurs, k_parole=k_parole)
                if pakalpojums:
                    context = {'pakalpojums': pakalpojums}
                    return render(request, 'user_service.html', context)
                else:
                    messages.error(request, 'Nepareizs r_numurs vai k_parole')
            except Pakalpojums.DoesNotExist:
                messages.error(request, 'Pakalpojums ar norādīto r_numurs un k_parole nav atrasts')
    else:
        form = UserLoginForm()

    return render(request, 'user_login.html', {'form': form})


def home(request):
    current_employee = request.user.employee
    return render(request, 'home.html', {'current_employee': current_employee})


def infosave(request, pk):
    pakalpojums = get_object_or_404(Pakalpojums, pak_ID=pk)
    form = SaveInfoForm(request.POST, instance=pakalpojums)

    if form.is_valid():
        pakalpojums_instance = form.save(commit=False)

        try:
            pakalpojums_instance.save()
            messages.success(request, 'Paldies par atsūtītajiem datiem un atsauksmēm!')
            return redirect('user_login')
        except Exception as e:
            print(f"Error saving pakalpojums_instance: {e}")
            messages.error(request, 'Kļūda saglabājot informāciju')
    else:
        messages.error(request, 'Kļūda validācijā')

    return render(request, 'user_service.html', {'form': form, 'pakalpojums': pakalpojums})


def print_service(request, pk):
    pakalpojums = get_object_or_404(Pakalpojums, pak_ID=pk)
    return render(request, 'print_service.html', {'pakalpojums': pakalpojums})


def service_employee_detail(request, pk):
    pakalpojums = get_object_or_404(Pakalpojums, pak_ID=pk)
    return render(request, 'service_employee_detail.html', {'pakalpojums': pakalpojums})


def simple_mail(request):
    send_mail('Thats your subject',
              'Thats your message body',
              'hi@demomailtrap.com',
              ['oskars.loguncovs@gmail.com'])
    return HttpResponse('Message sent!')


from django.http import JsonResponse


def start_service(request):
    if request.method == 'POST':
        pakalpojums_id = request.POST.get('pakalpojums_id')
        pakalpojums = get_object_or_404(Pakalpojums, pk=pakalpojums_id)

        # Изменяем статус на 0
        pakalpojums.status = 0
        pakalpojums.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


def save_darb_apraksts(request, pk):
    pakalpojums = Pakalpojums.objects.get(pk=pk)

    if request.method == 'POST':
        form = DarbAprakstsForm(request.POST, instance=pakalpojums)
        if form.is_valid():
            darb_apraksts_value = form.cleaned_data['darb_apraksts']

            # Если значение darb_apraksts равно '0', присвоим ему пустую строку
            pakalpojums.darb_apraksts = '' if darb_apraksts_value == '0' else darb_apraksts_value
            pakalpojums.status = 1
            pakalpojums.save()
            return redirect('service_employee')
    else:
        form = DarbAprakstsForm(instance=pakalpojums)

    return render(request, 'service_employee_detail.html', {'form': form})


@csrf_exempt
def change_status(request):
    if request.method == 'POST':
        form = ChangeStatusForm(request.POST)
        if form.is_valid():
            pak_ID = form.cleaned_data['pak_ID']
            pakalpojums = Pakalpojums.objects.get(pk=pak_ID)
            pakalpojums.status = 0  # Или любое другое значение, которое вам нужно
            pakalpojums.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Invalid form data'})
    else:
        return JsonResponse({'error': 'Invalid request method'})


User = get_user_model()


def change_password(request):
    if request.method == 'POST':
        darb_ID = request.session.get('darb_ID')
        if darb_ID:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_new_password = request.POST.get('confirm_new_password')

            user = Darbinieki.objects.get(darb_ID=darb_ID)

            if check_password(old_password, user.parole):
                if new_password != confirm_new_password:
                    return JsonResponse({'success': False, 'message': 'Новые пароли не совпадают'})
                else:
                    # Зашифровываем новый пароль
                    hashed_new_password = make_password(new_password)

                    # Обновляем пароль пользователя
                    user.parole = hashed_new_password
                    user.save()
                    return JsonResponse({'success': True, 'message': 'Пароль успешно изменен'})
            else:
                return JsonResponse({'success': False, 'message': 'Старый пароль неверен'})
        else:
            return JsonResponse({'success': False, 'message': 'Пользователь не найден'})
    else:
        return render(request, 'change_password.html')
