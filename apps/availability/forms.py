from django import forms


WEEKDAYS = [
    (0, "Seg"),
    (1, "Ter"),
    (2, "Qua"),
    (3, "Qui"),
    (4, "Sex"),
    (5, "Sáb"),
    (6, "Dom"),
]


class GenerateRecurringSlotsForm(forms.Form):
    # opção A: por mês/ano
    month = forms.IntegerField(label="Mês (1-12)", required=False, min_value=1, max_value=12)
    year = forms.IntegerField(label="Ano", required=False, min_value=2000, max_value=2100)

    # opção B: por intervalo
    start_date = forms.DateField(label="Data início", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(label="Data fim", required=False, widget=forms.DateInput(attrs={"type": "date"}))

    weekdays = forms.MultipleChoiceField(
        label="Dias da semana",
        choices=WEEKDAYS,
        widget=forms.CheckboxSelectMultiple,
    )

    # janela 1
    start_time = forms.TimeField(label="Início", widget=forms.TimeInput(attrs={"type": "time"}))
    end_time = forms.TimeField(label="Fim", widget=forms.TimeInput(attrs={"type": "time"}))

    # janela 2 (opcional)
    start_time_2 = forms.TimeField(label="Início 2", required=False, widget=forms.TimeInput(attrs={"type": "time"}))
    end_time_2 = forms.TimeField(label="Fim 2", required=False, widget=forms.TimeInput(attrs={"type": "time"}))

    slot_minutes = forms.IntegerField(label="Duração (min)", min_value=5, initial=60)
    break_minutes = forms.IntegerField(label="Intervalo (min)", min_value=0, initial=0)

    def clean(self):
        cleaned = super().clean()

        month, year = cleaned.get("month"), cleaned.get("year")
        start_date, end_date = cleaned.get("start_date"), cleaned.get("end_date")

        # precisa OU (month+year) OU (start_date+end_date)
        using_month = bool(month and year)
        using_range = bool(start_date and end_date)

        if using_month and using_range:
            raise forms.ValidationError("Use mês/ano OU intervalo de datas (não ambos).")

        if not using_month and not using_range:
            raise forms.ValidationError("Informe mês/ano OU intervalo de datas.")

        st, et = cleaned.get("start_time"), cleaned.get("end_time")
        if st and et and et <= st:
            raise forms.ValidationError("Na janela 1: Fim deve ser maior que Início.")

        st2, et2 = cleaned.get("start_time_2"), cleaned.get("end_time_2")
        if (st2 and not et2) or (et2 and not st2):
            raise forms.ValidationError("Na janela 2: preencha Início 2 e Fim 2 (ou deixe ambos vazios).")
        if st2 and et2 and et2 <= st2:
            raise forms.ValidationError("Na janela 2: Fim 2 deve ser maior que Início 2.")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("Data fim deve ser maior ou igual à data início.")

        return cleaned


class DayOffForm(forms.Form):
    date = forms.DateField(label="Data", widget=forms.DateInput(attrs={"type": "date"}))
    reason = forms.CharField(label="Motivo", required=False, max_length=200)