from django.shortcuts import render, redirect
from .forms import BodyCompositionForm
from .models import BodyComposition


def evaluation_form(request):
    if request.method == 'POST':
        form = BodyCompositionForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            if evaluation.gender == 'F':
                evaluation.skinfold_calf = None  # Явное указание NULL для женщин
            evaluation.save()
            return redirect('bodycalc:results', pk=evaluation.pk)
    else:
        form = BodyCompositionForm()

    return render(request, 'bodycalc/evaluation_form.html', {
        'form': form,
        'submit_disabled': True  # Первоначально кнопка disabled
    })


def results(request, pk):
    evaluation = BodyComposition.objects.get(pk=pk)
    results = evaluation.get_results()
    bmi = round(evaluation.weight / ((evaluation.height / 100) ** 2), 2)

    context = {
        'evaluation': evaluation,
        'results': results,
        'bmi': bmi
    }
    return render(request, 'bodycalc/results.html', context)