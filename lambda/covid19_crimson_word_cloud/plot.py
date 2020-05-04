import random

import numpy as np
import plotly as py
import plotly.graph_objects as go
from plotly.offline import plot


def word_cloud(words, scores):
    lower, upper = 10, 80
    frequency = [round((((x - min(scores)) / (max(scores) - min(scores))) ** 1.5) * (
            upper - lower) + lower) for x in scores]
    colors = [py.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for
              i in range(len(scores))]

    # set location
    x = list(np.arange(0, len(scores), 0.5))
    y = [i for i in range(len(scores))]
    random.shuffle(x)
    random.shuffle(y)

    data = go.Scatter(
        x=x,
        y=y,
        mode='text',
        text=words,
        hovertext=['{0} {1}'.format(w, s, format(s, '.2%')) for w, s in
                   zip(words, scores)],
        hoverinfo='text',
        textfont={
            'size': frequency,
            'color': colors,
            'family': 'Arial'

        }
    )

    layout = go.Layout(
        {
            'xaxis':
                {
                    'showgrid': False,
                    'showticklabels': False,
                    'zeroline': False,
                },
            'yaxis':
                {
                    'showgrid': False,
                    'showticklabels': False,
                    'zeroline': False,
                },
            'margin':
                {
                    't':10,
                    'b':10,
                    'l':10,
                    'r':10
                }
        })

    fig = go.Figure(data=[data], layout=layout)

    # save the plot
    div = plot(fig, output_type="div", auto_open=False, image_filename="word_cloud_img")

    return div


if __name__ == "__main__":
    words = ['gobierno', 'pandemia', 'salud', 'quarentena', 'más', 'coronavirus', 'cuarentena', 'covid-19', 'caso',
             '#covid19', 'presidente', 'contra', 'casos', 'mil', 'vida', 'bolsonaro', 'saúde', 'casa', 'governo',
             'brasil', 'país', 'virus', 'mortes', 'coronavírus', 'daí', 'mortos', '#coronavirus', '#quédateencasa',
             'mundo', 'están', 'ministerio', 'médicos', 'nacional', 'hoy', 'personas', '😂', 'esto', 'positivo',
             'presos', 'tá', 'vai', 'años', 'dar', 'derechos', 'durante', 'mejor', 'violadores', '#quedateencasa',
             'atenção', 'día', 'covid19', 'cómo', 'importante', 'nessa', '@jairbolsonaro', 'covid', 'crisis', 'días',
             'general', 'situação', 'vírus', 'aborto', 'emergencia', 'femicidas', 'medidas', 'trabajadores', 'vidas',
             '2020', 'claro', 'derecho', 'humanos', 'millones', 'nada', 'nuestros', 'nunca', 'número', 'plan',
             'social', 'trump', 'vez', '🐍', 'abril', 'curva', 'dice', 'dicen', 'forma', 'frente', 'gente', 'hospital',
             'méxico', '@vandson_lima', 'cristão', 'falta', 'fase', 'ley', 'mal', 'medio', 'ministro', 'momento',
             'nuevo', 'parece', 'política', 'pública', 'público', 'sistema', 'artículo', 'china', 'confirmados',
             'corona', 'dando', 'era', 'fazendo', 'gran', 'jamás', 'maior', 'mas', 'menos', 'meses', 'muertes', 'pf',
             'plena', 'programa', 'queria', 'semana', 'siempre', 'través', 'venezuela', 'vista', 'alguém', 'apoyo',
             'chile', 'decreto', 'después', 'favor', 'haber', 'haciendo', 'países', 'pueblo', 'sair', 'san', 'seguir',
             'stf', 'total', 'vc', 'vía', '👇', '#covidー19', '@alfredodelmazo', '@lopezobrador_', 'alexandre', 'aos',
             'atendimento', 'decir', 'economia', 'economía', 'estados', 'familiares', 'funciones', 'governadores',
             'hospitales', 'igual', 'libertad', 'madre', 'moro', 'mucho', 'médico', 'organización', 'otros',
             'pacientes', 'parte', 'pelas', 'persona', 'poco', 'queremos', 'responsabilidad', 'segunda', 'vcs', 'ver',
             '#esfuerzoydisciplina', '#venezuela', 'además', 'agua', 'ayer', 'ayudar', 'combate', 'contagios',
             'dinero', 'estos', 'federal', 'horas', 'isolamento', 'izquierda', 'justo', 'libera', 'liberar', 'mental',
             'milhões', 'mismo', 'moraes', 'mujer', 'nas', 'necesario', 'ninguém', 'oposición', 'paz', 'peor', 'pq',
             'primera', 'problema', 'provincia', 'querer', 'realmente', 'redes', 'salir', 'seja', 'sempre', 'sigue',
             'síntomas', 'todas', 'vídeo', 'à', 'él', '👏', '#covid_19', '@ivanduque', '@nicolasmaduro', 'acaba',
             'amigos', 'argentina', 'campaña', 'compra', 'comprar', 'criminal', 'culpa', 'da', 'dessa', 'deu', 'dijo',
             'dios', 'empresa', 'empresas', 'enfrentar', 'especial', 'fala', 'faço', 'horrível', 'há', 'información',
             'instituciones', 'instituto', 'insumos', 'investigación', 'lucha', 'luego', 'manos', 'menor', 'muertos',
             'nadie', 'ningún', 'nomeação', 'ola', 'papel', 'paulo', 'pedro', 'pelos', 'personal', 'pessoa', 'pide',
             'población', 'protección', 'quanto', 'quiere', 'rio', 'rodríguez', 'salida', 'salió', 'sanitaria', 'sean',
             'sei', 'sendo', 'ta', 'tanto', 'trabajando', 'tres', 'tão', 'unidos', 'urgente', 'última', '😢', 'brote',
             'datos', 'diretor', 'ilegal', 'manhã', 'mano', 'mata', 'miedo', 'noticias', 'positivos', 'único']
    counts = [137, 131, 106, 88, 83, 80, 80, 73, 59, 55, 51, 48, 43, 43, 42, 40, 38, 36, 34, 33, 32, 32, 29, 28, 28,
              28, 27, 27, 26, 25, 25, 25, 25, 23, 22, 21, 20, 20, 20, 20, 20, 19, 19, 19, 19, 19, 19, 18, 18, 18, 17,
              17, 17, 17, 16, 16, 16, 16, 16, 16, 16, 15, 15, 15, 15, 15, 15, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14,
              14, 14, 14, 14, 13, 13, 13, 13, 13, 13, 13, 13, 13, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12,
              12, 12, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 10,
              10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
              9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
              8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 7, 7, 7,
              7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
              7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6,
              6, 6]

    div = word_cloud(words, counts)
    with open("tmp.html", "w") as f:
        f.write(div)
