from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.serializers import json, serialize
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Amats
from .models import Pakalpojums
from .models import Darbinieki
from .models import *
from .forms import MemberForm, ChangeStatusForm, IzbraukumsForm
from .forms import ServiceEditForm
from django.contrib import messages
from .forms import MemberEditForm
from django.views.generic.detail import DetailView
from .forms import ServiceForm
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, AmatsForm, UserLoginForm, SaveInfoForm, DarbAprakstsForm
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime, date, timedelta
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.mail import send_mail
import json
from django.core.serializers import serialize
from django.utils.crypto import get_random_string
from .models import Amats, Darbinieki, Pakalpojums
import random

from django.utils import timezone


def employee_base(request):
    if not request.session.get('darb_ID'):
        return redirect('login')
    all_darbinieki = Darbinieki.objects.filter(menedzeris=False).distinct()
    return render(request, "employee_base.html", {'all': all_darbinieki})


def service_base(request, status='visi'):
    if not request.session.get('darb_ID'):
        return redirect('login')
    server_time = timezone.now()
    local_time = server_time - timedelta(hours=2)
    if status == 'visi':
        all_service = Pakalpojums.objects.exclude(status=1)
    elif status == 'drizuma':
        all_service = Pakalpojums.objects.filter(datums__gt=date.today(), status__isnull=True)
    elif status == 'procesa':
        all_service = Pakalpojums.objects.filter(status=0)
    elif status == 'nokaveti':
        all_service = Pakalpojums.objects.filter(datums__lte=local_time)
        all_service = all_service.exclude(datums=local_time.date(), laiks__lt=local_time.time())
        all_service = all_service.filter(status__isnull=True)
    elif status == 'pabeigti':
        all_service = Pakalpojums.objects.filter(status=1)
    else:
        all_service = Pakalpojums.objects.all()

    search_query = request.GET.get('search_query')
    if search_query:
        all_service = all_service.filter(r_numurs__icontains=search_query)

    context = {'all': all_service, 'status': status}
    return render(request, "service_base.html", context)


def service_employee(request, status='visi'):
    if not request.session.get('darb_ID'):
        return redirect('login')
    user = request.user
    darb_ID = request.session.get('darb_ID')

    employee_all_service = Pakalpojums.objects.filter(darb_ID=darb_ID)
    if status == 'visi':
        employee_all_service = employee_all_service.exclude(status=1)
    elif status == 'uzsaktie':
        employee_all_service = employee_all_service.filter(status=0)
    elif status == 'drizuma':
        employee_all_service = employee_all_service.filter(status__isnull=True, datums__gt=date.today())
    elif status == 'nokaveti':
        employee_all_service = employee_all_service.filter(datums__lte=date.today(), status=None)
    elif status == 'pabeigti':
        employee_all_service = employee_all_service.filter(status=1)
    search_query = request.GET.get('search_query')
    if search_query:
        employee_all_service = employee_all_service.filter(r_numurs__icontains=search_query)

    context = {'employee_services': employee_all_service, 'status': status}
    return render(request, "service_employee.html", context)


def user_service(request):
    if not request.session.get('darb_ID'):
        return redirect('login')
    pakalpojums = Pakalpojums.objects.first()  # или используйте логику для выбора нужного объекта
    form = SaveInfoForm(request.POST or None, instance=pakalpojums)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # дополнительные действия после сохранения формы
            return redirect('user_service')

    return render(request, "user_service.html", {'pakalpojums': pakalpojums, 'form': form})


def prof_base(request):
    if not request.session.get('darb_ID'):
        return redirect('login')
    all_amats = Amats.objects.all()
    form = AmatsForm()

    if request.method == 'POST':
        form = AmatsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('prof_base')

    return render(request, 'prof_base.html', {'all': all_amats, 'form': form})


def prof_edit(request, pk):
    if not request.session.get('darb_ID'):
        return redirect('login')
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
    if not request.session.get('darb_ID'):
        return redirect('login')
    if request.method == "POST":
        form = MemberForm(request.POST or None)
        if form.is_valid():
            tehnika = request.POST.get('tehnika', False)  # Default value False if not checked
            montesana = request.POST.get('montesana', False)
            programm = request.POST.get('programm', False)
            vaditajs = request.POST.get('vaditajs', False)
            tehmont = request.POST.get('tehmont', False)
            vards = form.cleaned_data['vards']
            uzvards = form.cleaned_data['uzvards']
            talrunis = form.cleaned_data['talrunis']
            login = (vards[:len(vards) // 2] + uzvards[:len(uzvards) // 2] + talrunis[:len(talrunis) // 4]).lower()
            parole = get_random_string(length=random.randint(8, 15))

            form.instance.login = login
            form.instance.parole = parole

            epasts = form.cleaned_data['epasts']
            send_mail('Print%Serviss reģistrācija',
                      'Jūsu konts veiksmīgi izvediots! Jūsu Login: ' + login + ' Parole :' + parole,
                      'hi@demomailtrap.com',
                      [epasts])

            form.save()
        else:
            vards = request.POST['vards']
            uzvards = request.POST['uzvards']
            epasts = request.POST['epasts']
            talrunis = request.POST['talrunis']
            dz_datums = request.POST['dz_datums']
            uzsak_datums = request.POST['uzsak_datums']
            tehnika = request.POST['tehnika']

            messages.success(request, (" Parbaudiet pierakstītas vērtības!"))
            return render(request, "employee.html", {
                'vards': vards,
                'uzvards': uzvards,
                'epasts': epasts,
                'talrunis': talrunis,
                'dz_datums': dz_datums,
                'uzsak_datums': uzsak_datums,
                'tehnika': tehnika,

            })

        messages.success(request, ('Jauns darbinieks tiek saglabats!'))
        return redirect('employee_base')
    else:
        form = MemberForm()

    return render(request, "employee.html", context={
        'form': form,

    })


def service(request):
    if not request.session.get('darb_ID'):
        return redirect('login')
    darbinieki = Darbinieki.objects.filter(menedzeris=False)
    pak_tipi = PakTip.objects.all()
    selected_paktip_id = request.POST.get('paktip_ID')

    vards_displayed = False
    if request.method == "POST":
        form = ServiceForm(request.POST or None)

        if form.is_valid():
            form.instance.pan_datums = date.today()
            form.save()
            messages.success(request, ('Jauns pakalpojums tiek saglabāts!'))
            return redirect('service_base')
        else:
            nosaukums = request.POST['nosaukums']
            klients = request.POST['klients']
            k_talrunis = request.POST['k_talrunis']
            k_epasts = request.POST['k_epasts']
            datums = request.POST['datums']
            laiks = request.POST['laiks']
            vieta = request.POST['vieta']
            sit_aprakts = request.POST['sit_aprakts']
            darb_ID = request.POST['darb_ID']
            pak_tipi = request.POST['pak_tipi']
            serija_nr = request.POST['serija_nr']
            komplektacija = request.POST['komplektacija']

            messages.success(request, (" Parbaudiet pierakstītas vērtības!"))
            return render(request, "service.html", {
                'form': form,
                'darbinieki': darbinieki,
                'pak_tipi': pak_tipi,
                'nosaukums': nosaukums,
                'klients': klients,
                'k_talrunis': k_talrunis,
                'k_epasts': k_epasts,
                'datums': datums,
                'laiks': laiks,
                'vieta': vieta,
                'sit_aprakts': sit_aprakts,
                'darb_ID': darb_ID,

                'serija_nr': serija_nr,
                'komplektacija': komplektacija,

            })

    else:
        form = ServiceForm()

    return render(request, "service.html", {'form': form, 'darbinieki': darbinieki, 'paktip': pak_tipi})


def izbraukums(request):
    if not request.session.get('darb_ID'):
        return redirect('login')

    if request.method == "POST":
        form = IzbraukumsForm(request.POST or None)
        if form.is_valid():
            # Сохраняем данные только при валидной форме
            instance = form.save(commit=False)
            instance.status = True  # Устанавливаем значение статуса
            instance.datums = datetime.now()  # Устанавливаем значение даты
            instance.save()
            messages.success(request, 'Jauns pakalpojums tiek saglabāts!')
            return redirect('service_employee')
        else:
            auto = request.POST['auto']
            nobraukums = request.POST['nobraukums']
            p_laiks = request.POST['p_laiks']
            darb_apraksts = request.POST['darb_apraksts']

            messages.success(request, (" Parbaudiet pierakstītas vērtības!"))
            return render(request, "service_employee_detail.html", {
                'form': form,
                'auto': auto,
                'nobraukums': nobraukums,
                'p_laiks': p_laiks,
                'darb_apraksts': darb_apraksts,

            })

    else:
        form = IzbraukumsForm()

    return render(request, "service_employee.html", {'form': form})


def get_darbinieki(request):
    if not request.session.get('darb_ID'):
        return redirect('login')
    selected_paktip_id = int(request.GET.get('selected_paktip_id'))

    if selected_paktip_id == 1:
        darbinieki = Darbinieki.objects.filter(tehnika=True)
    elif selected_paktip_id == 2:
        darbinieki = Darbinieki.objects.filter(montesana=True)
    elif selected_paktip_id == 3:
        darbinieki = Darbinieki.objects.filter(programm=True)
    elif selected_paktip_id == 4:
        darbinieki = Darbinieki.objects.filter(vaditajs=True)
    elif selected_paktip_id == 5:
        darbinieki = Darbinieki.objects.filter(tehmont=True)
    else:
        # Default to an empty queryset if no specific paktip is selected
        darbinieki = Darbinieki.objects.none()

        # Serialize darbinieki queryset to JSON
    darbinieki_list = list(darbinieki.values('darb_ID', 'vards', 'uzvards'))
    return JsonResponse({'darbinieki': darbinieki_list})


class EmployeeDetailView(DetailView):
    model = Darbinieki
    template_name = 'employee_detail.html'
    context_object_name = 'employee'


class ServiceDetailView(DetailView):
    model = Pakalpojums
    template_name = 'service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['darbinieki'] = Darbinieki.objects.all
        darbinieks = self.object.darb_ID
        context['paktip'] = PakTip.objects.all()
        paktip = self.object.paktip_ID

        context['selected_darbinieks'] = darbinieks
        context['selected_paktip'] = paktip
        return context


def employee_delete(request, pk):
    if not request.session.get('darb_ID'):
        return redirect('login')
    employee = get_object_or_404(Darbinieki, darb_ID=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, ('Darbinieks tiek dzēsts!'))
        return redirect('employee_base')
    return render(request, 'employee_delete.html', {'employee': employee})


def service_delete(request, pk):
    if not request.session.get('darb_ID'):
        return redirect('login')
    service = get_object_or_404(Pakalpojums, pak_ID=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('service_base')
    return render(request, 'service_delete.html', {'service': service})


def prof_delete(request, pk):
    if not request.session.get('darb_ID'):
        return redirect('login')
    prof = get_object_or_404(Amats, amata_ID=pk)
    if request.method == 'POST':
        prof.delete()
        return redirect('prof_base')
    return render(request, 'prof_delete.html', {'prof': prof})


def save_employee(request, pk):
    if not request.session.get('darb_ID'):
        return redirect('login')
    employee = get_object_or_404(Darbinieki, darb_ID=pk)
    if request.method == 'POST':
        form = MemberEditForm(request.POST, instance=employee)
        if form.is_valid():
            tehnika = request.POST.get('tehnika', False)  # Default value False if not checked
            montesana = request.POST.get('montesana', False)
            programm = request.POST.get('programm', False)
            vaditajs = request.POST.get('vaditajs', False)
            tehmont = request.POST.get('tehmont', False)
            form.save()
            messages.success(request, 'Darbinieks veiksmīgi saglabāts!')
            return redirect('employee_base')
        else:
            messages.error(request, 'Radās kļūda saglabājot darbinieku. Pārbaudiet ievadītos datus.')

            return render(request, 'employee_detail.html',
                          {'form': form, 'employee': employee, 'errors': form.errors})
    else:
        form = MemberEditForm(instance=employee)

    return render(request, 'employee_base.html',
                  {'form': form, 'employee': employee, 'errors': form.errors})


def save_service(request, pk):
    if not request.session.get('darb_ID'):
        return redirect('login')
    darbinieki = Darbinieki.objects.all()
    paktip = PakTip.objects.all()
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
                          {'form': form, 'service': service, 'errors': form.errors, 'darbinieki': darbinieki,
                           'paktip': paktip})
    else:
        form = ServiceEditForm(instance=service)

    return render(request, 'service_detail.html',
                  {'form': form, 'service': service, 'darbinieki': darbinieki, 'paktip': paktip})


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
                        context = {'employee_services': employee_services, 'status': 'visi'}
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
    if not request.session.get('darb_ID'):
        return redirect('login')
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
    if not request.session.get('darb_ID'):
        return redirect('login')
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
    if not request.session.get('darb_ID'):
        return redirect('login')
    pakalpojums = get_object_or_404(Pakalpojums, pak_ID=pk)
    return render(request, 'print_service.html', {'pakalpojums': pakalpojums})


def drive_print(request, pk):
    if not request.session.get('darb_ID'):
        return redirect('login')
    pakalpojums = get_object_or_404(Pakalpojums, pak_ID=pk)
    return render(request, 'drive_print.html', {'pakalpojums': pakalpojums})


def service_employee_detail(request, pk):
    if not request.session.get('darb_ID'):
        return redirect('login')
    pakalpojums = get_object_or_404(Pakalpojums, pak_ID=pk)
    return render(request, 'service_employee_detail.html', {'pakalpojums': pakalpojums})


def simple_mail(request):
    if not request.session.get('darb_ID'):
        return redirect('login')
    send_mail('Thats your subject1',
              'Thats your message body1',
              'hi@demomailtrap.com',
              ['oskars@gmail.com'])
    return HttpResponse('Message sent!')


def save_darb_apraksts(request, pk):
    if not request.session.get('darb_ID'):
        return redirect('login')

    pakalpojums = Pakalpojums.objects.get(pk=pk)

    if request.method == 'POST':
        form = DarbAprakstsForm(request.POST, instance=pakalpojums)
        if form.is_valid():
            darb_apraksts_value = form.cleaned_data['darb_apraksts']
            if not darb_apraksts_value.strip():
                return JsonResponse({'error': 'Lūdzu, ievadiet tekstu pirms pievienošanas.'}, status=400)

            # Сохраняем darb_apraksts и текущую дату в PakInfo
            pak_info = PakInfo.objects.create(pak_ID=pakalpojums, darb_apraksts=darb_apraksts_value,
                                              datums=date.today())

            # Возвращаем JSON-ответ об успешном сохранении
            return JsonResponse({'success': True})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'error': errors}, status=400)

    return render(request, 'service_employee_detail.html', {'form': form})


def save_completed(request, pk):
    if not request.session.get('darb_ID'):
        return redirect('login')

    pakalpojums = Pakalpojums.objects.get(pk=pk)

    if request.method == 'POST':
        # Просто устанавливаем статус на 1 без сохранения текста
        pakalpojums.status = 1
        pakalpojums.save()

        # Создаем запись в PakInfo только с текущей датой
        pak_info = PakInfo.objects.create(pak_ID=pakalpojums, datums=date.today())

        return JsonResponse({'success': True})

    # Возвращаем ошибку, если запрос не POST
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def change_status(request):
    if not request.session.get('darb_ID'):
        return redirect('login')
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
    if not request.session.get('darb_ID'):
        return redirect('login')
    if request.method == 'POST':
        darb_ID = request.session.get('darb_ID')
        if darb_ID:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_new_password = request.POST.get('confirm_new_password')

            user = Darbinieki.objects.get(darb_ID=darb_ID)

            if check_password(old_password, user.parole):
                if new_password != confirm_new_password:
                    messages.success(request, 'Paroles nesakrīt')
                else:
                    user.parole = new_password
                    user.save()
                    messages.success(request, 'Parole veiksmīgi mainīta')

            else:
                messages.success(request, 'Nepareiza vecā parole')
        else:
            messages.success(request, 'Lietotājs nav atrasts')
    else:
        messages.success(request, 'Netiek atbalstīta šāda pieprasījuma metode')

    return redirect(request.META.get('HTTP_REFERER', 'default_url'))
