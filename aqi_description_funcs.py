
def aqi_longdescription(value):
    if value <= 50:
        return f"""-Индекс качества воздуха (AQI) = {value} 🟢
-Уровень AQI - "Хороший". ✅
-Качество воздуха является удовлетворительным и не содержит риска для здоровья.

👩‍⚕️Рекомендуемые меры предосторожности: можно продолжать свою деятельность на свежем воздухе в обычном режиме."""

    elif 51 <= value <= 100:
        return f"""-Индекс качества воздуха (AQI) = {value} 🟡
-Уровень AQI - "Приемлемый". 👌
-Некоторые загрязняющие вещества могут незначительно воздействовать на очень немногих гиперчувствительных людей.

👩‍⚕️ Рекомендуемые меры предосторожности: чувствительные люди должны избегать активного отдыха, так как могут возникнуть респираторные симптомы."""

    elif 101 <= value <= 150:
        return f"""-Индекс качества воздуха (AQI) = {value} 🟠
-Уровень AQI - "Нездоровый для чувствительных групп" ⚠️
-Члены чувствительных групп могут испытывать последствия для здоровья. Широкая общественность меньше подвержена влиянию.
        
👩‍⚕️ Рекомендуемые меры предосторожности: общество в целом и чувствительные люди в частности, рискуют испытать раздражение носоглотки и проблемы с дыханием. Ограничьте свое пребывание на улице."""

    elif 151 <= value <= 200:
        return f"""-Индекс качества воздуха (AQI) = {value} 🔴
-Уровень AQI - "Вредный". ❗️
-Некоторые представители населения могут испытывать последствия для здоровья; члены чувствительных групп могут испытывать более серьезные последствия для здоровья.
    
👩‍⚕️ Рекомендуемые меры предосторожности: увеличивается вероятность побочных эффектов и обострение заболеваний сердца и легких в целом, особенно для уязвимых групп людей. Ограничьте свое пребывание на улице."""
    
    elif 201 <= value <= 300:
        return f"""-Индекс качества воздуха (AQI) = {value} 🔴
-Уровень AQI - "Крайне вреден". ❗️❗️
-Риск воздействия на здоровье повышен для всех категорий людей.

👩‍⚕️ Рекомендуемые меры предосторожности: у чувствительных групп людей будет наблюдаться снижение выносливости и активности. Ограничьте свое пребывание на улице, оставайтесь в помещениях."""
    
    elif 301 <= value:
        return f"""-Индекс качества воздуха (AQI) = {value} 🔴
-Уровень AQI - "Опасный!". ❌
-Опасен для здоровья, крайне высокий риск неблагоприятных последствий для здоровья!

👩‍⚕️ Рекомендуемые меры предосторожности: все население рискует испытать сильные раздражения и неблагоприятные последствия для здоровья, которые могут спровоцировать заболевания. Оставайтесь в закрытых помещениях и не выходите на улицу."""


def aqi_shortdescription(value):
    if value <= 50:
        return 'Хорошее ✅'
    elif 51 <= value <= 100:
        return "Приемлемо👌"
    elif 101 <= value <= 150:
        return "Нездоровое⚠️"
    elif 151 <= value <= 200:
        return "Вредное❗️"
    elif 201 <= value <= 300:
        return "Крайне   \n вреднен❗️❗️"
    elif 301 <= value:
        return 'Опасен для\nздоровья!❌'