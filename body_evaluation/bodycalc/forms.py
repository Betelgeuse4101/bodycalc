from django import forms
from .models import BodyComposition


GENDER_CHOICES = [
    ('M', 'Мужчина'),
    ('F', 'Женщина'),
]


class BodyCompositionForm(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'radio-select'}),
        label="Пол*"
    )
    class Meta:
        model = BodyComposition
        fields = '__all__'
        widgets = {
            'gender': forms.RadioSelect,
            'age': forms.NumberInput(attrs={'min': 1, 'max': 120}),
            'height': forms.NumberInput(attrs={'min': 50, 'max': 250, 'step': 0.1}),
            'weight': forms.NumberInput(attrs={'min': 20, 'max': 300, 'step': 0.1}),
        }
        labels = {
            'name': "Имя",
            'gender': "Пол",
            'age': "Возраст (лет)",
            'height': "Рост (см)",
            'weight': "Вес (кг)",

            # Жировые складки
            'skinfold_chest': "Складка на груди (мм)",
            'skinfold_abdominal': "Складка на животе (мм)",
            'skinfold_thigh': "Складка на бедре (мм)",
            'skinfold_triceps': "Складка на трицепсе (мм)",
            'skinfold_subscapular': "Подлопаточная складка (мм)",
            'skinfold_suprailiac': "Надподвздошная складка (мм)",
            'skinfold_midaxillary': "Подмышечная складка (мм)",
            'skinfold_calf': "Складка на голени (мм)",

            # Окружности
            'circumference_arm': "Обхват плеча (см)",
            'circumference_forearm': "Обхват предплечья (см)",
            'circumference_thigh': "Обхват бедра (см)",
            'circumference_calf': "Обхват голени (см)",

            # Диаметры
            'diameter_arm': "Диаметр плеча (см)",
            'diameter_forearm': "Диаметр предплечья (см)",
            'diameter_thigh': "Диаметр бедра (см)",
            'diameter_calf': "Диаметр голени (см)",
        }
        help_texts = {
            'skinfold_chest': "Измеряется по средней подмышечной линии на уровне мечевидного отростка",
            'skinfold_abdominal': "Измеряется вертикально в 2 см справа от пупка",
            'skinfold_thigh': "Измеряется посередине передней поверхности бедра",
            'skinfold_triceps': "Измеряется посередине задней поверхности плеча",
            'skinfold_subscapular': "Измеряется под нижним углом лопатки",
            'skinfold_suprailiac': "Измеряется над гребнем подвздошной кости по средней подмышечной линии",
            'skinfold_midaxillary': "Измеряется на уровне мечевидного отростка по средней подмышечной линии",
            'skinfold_calf': "Измеряется на максимальной выпуклости икроножной мышцы",

            'circumference_arm': "Измеряется при расслабленной мышце, посередине между акромионом и локтевым отростком",
            'circumference_forearm': "Измеряется в наиболее широком месте предплечья",
            'circumference_thigh': "Измеряется непосредственно под ягодичной складкой",
            'circumference_calf': "Измеряется в наиболее широком месте голени",

            'diameter_arm': "Измеряется чуть выше локтевого сустава",
            'diameter_forearm': "Измеряется в запястье",
            'diameter_thigh': "Измеряется ширина коленки",
            'diameter_calf': "Измеряется в лодыжке",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем минимальные значения для всех числовых полей
        for field in self.fields:
            if isinstance(self.fields[field], forms.FloatField):
                self.fields[field].initial = 0  # Установка значения по умолчанию
                self.fields[field].widget.attrs.update({
                    'min': 0.1,  # Минимальное допустимое значение
                    'step': 0.1,
                    'required': 'required'  # Обязательное поле
                })

    def clean(self):
        cleaned_data = super().clean()
        gender = cleaned_data.get('gender')

        if gender == 'F':
            # Для женщин делаем складку на голени необязательной
            if not cleaned_data.get('skinfold_calf'):
                cleaned_data['skinfold_calf'] = 0.0

        # Общая валидация числовых полей
        for field in self.fields:
            if isinstance(self.fields[field], forms.FloatField):
                if cleaned_data.get(field) is None:
                    self.add_error(field, 'Это поле обязательно')

        return cleaned_data
