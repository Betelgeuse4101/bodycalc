from django.db import models
from django.core.validators import MinValueValidator
import math


class BodyComposition(models.Model):
    GENDER_CHOICES = [('M', 'Мужчина'), ('F', 'Женщина')]

    # Основные данные
    name = models.CharField(max_length=100, verbose_name="Имя")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    height = models.FloatField(validators=[MinValueValidator(50)])
    weight = models.FloatField(validators=[MinValueValidator(20)])

    # Жировые складки (мм)
    skinfold_chest = models.FloatField()
    skinfold_abdominal = models.FloatField()
    skinfold_thigh = models.FloatField()
    skinfold_triceps = models.FloatField()
    skinfold_subscapular = models.FloatField()
    skinfold_suprailiac = models.FloatField()
    skinfold_midaxillary = models.FloatField()
    skinfold_calf = models.FloatField(null=True, blank=True)

    # Окружности (см)
    circumference_arm = models.FloatField()
    circumference_forearm = models.FloatField()
    circumference_thigh = models.FloatField()
    circumference_calf = models.FloatField()

    # Диаметры (см)
    diameter_arm = models.FloatField()
    diameter_forearm = models.FloatField()
    diameter_thigh = models.FloatField()
    diameter_calf = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_body_surface(self):
        """Площадь поверхности тела по Дюбуа"""
        return 0.007184 * (self.height ** 0.725) * (self.weight ** 0.425)

    def calculate_fat(self):
        """Жировой компонент по Матейко"""
        if self.gender == 'M':
            a = (self.skinfold_chest + self.skinfold_abdominal + self.skinfold_thigh +
                 self.skinfold_triceps + self.skinfold_subscapular + self.skinfold_suprailiac +
                 self.skinfold_midaxillary + (self.skinfold_calf or 0)) / 16
        else:
            a = (self.skinfold_chest + self.skinfold_abdominal + self.skinfold_thigh +
                 self.skinfold_triceps + self.skinfold_subscapular + self.skinfold_suprailiac +
                 self.skinfold_midaxillary) / 14

        H_absol = a * self.calculate_body_surface() * 1.3
        return {
            'absolute': round(H_absol, 2),
            'percentage': min(60, max(5, round((H_absol * 100) / self.weight, 2)))
        }

    def calculate_muscle(self):
        """Мышечный компонент по Матейко"""
        circumferences = [
            self.circumference_arm,
            self.circumference_forearm,
            self.circumference_thigh,
            self.circumference_calf
        ]
        skinfolds = [
            self.skinfold_triceps,
            getattr(self, 'skinfold_forearm', self.skinfold_triceps * 0.9),
            self.skinfold_thigh,
            self.skinfold_calf or self.skinfold_thigh * 0.8
        ]

        r = (sum(circumferences) / (2 * math.pi * 4) -
             sum(skinfolds) / (2 * 4 * 10))

        M_absol = (self.height * (r ** 2) * 6.5) / 1000
        return {
            'absolute': round(M_absol, 2),
            'percentage': min(60, max(20, round((M_absol * 100) / self.weight, 2)))
        }

    def calculate_bone(self):
        """Костный компонент по Матейко"""
        diameters = [
            self.diameter_arm,
            self.diameter_forearm,
            self.diameter_thigh,
            self.diameter_calf
        ]
        d_squared = (sum(diameters) / len(diameters)) ** 2
        O_absol = (self.height * d_squared * 1.2) / 1000
        return {
            'absolute': round(O_absol, 2),
            'percentage': round((O_absol * 100) / self.weight, 2)
        }

    def get_results(self):
        results = {
            'fat': self.calculate_fat(),
            'muscle': self.calculate_muscle(),
            'bone': self.calculate_bone()
        }
        total = sum(c['percentage'] for c in results.values())
        results['remaining'] = {
            'absolute': round(self.weight - sum(c['absolute'] for c in results.values()), 2),
            'percentage': round(100 - total, 2)
        }
        return results

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()}, {self.age} лет)"
