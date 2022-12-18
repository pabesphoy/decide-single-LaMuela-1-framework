from django.shortcuts import render
from voting.models import Voting, QuestionOption, Question, Auth
from base import mods
from django.http import HttpResponse
import matplotlib.pyplot as plt
from itertools import cycle
import numpy as np
from decide_statistics import tests
import logging
from django.conf import settings
import datetime

logging.getLogger('matplotlib.font_manager').disabled = True

graph_image_directory = 'decide_statistics/static/decide_statistics/graph.png'

def index(request):
    votings = Voting.objects.filter(end_date__isnull = False).filter(postproc__isnull = False)
    votings_with_votes = []
    for voting in votings:
        number_of_votes = 0
        for postproc in voting.postproc:
            number_of_votes += int(postproc['votes'])
        if number_of_votes > 0:
            votings_with_votes.append(voting)

    
    modelmap = {"votings":votings_with_votes}
    voting = request.GET.get("voting")
    graph_type = request.GET.get("graph_type")
    if voting is None:
        voting = 0
    if graph_type is None:
        graph_type = ''
    if voting == 0 or voting == '0' or graph_type == '':
        return render(request, "decide_statistics/index.html", modelmap)
    elif Voting.objects.filter(id__exact = voting).count() == 0:
        return HttpResponse("Esta votación no existe")
    elif Voting.objects.get(id__exact = voting) not in votings_with_votes:
        return HttpResponse("Esta votación no ha terminado o no tiene votos")
    else:
        return showVoting(request, voting, graph_type, modelmap)
    

def showVoting(request, voting_id, graph_type, modelmap):
    if graph_type == 'bar':
        show_bar(voting_id)
    elif graph_type == 'pie':
        show_pie(voting_id) 
    elif graph_type == 'horizontal_bar':
        show_horizontal_bar(voting_id) 
    elif graph_type == 'dots':
        show_dots(voting_id) 
    elif graph_type == 'line':
        show_plot(voting_id) 
    else:
        return HttpResponse("Tipo de gráfico no válido")

    return render(request, "decide_statistics/showVoting.html", modelmap)


def show_bar(voting_id):
    fig, ax = plt.subplots()
    voting, options_str, counts, bar_colors = get_voting_showing_parameters(voting_id)

    
    ax.bar(options_str, counts, label=options_str, color=bar_colors)
    ax.set_title(voting.question.desc)
    ax.legend(title='Opciones')
    plt.savefig(graph_image_directory)

def show_pie(voting_id):
    fig, ax = plt.subplots()
    voting, options_str, counts, bar_colors = get_voting_showing_parameters(voting_id)
    y = np.array(counts)

    plt.pie(y, labels = options_str)
    plt.legend(title = voting.question.desc)
    plt.savefig(graph_image_directory)

def show_horizontal_bar(voting_id):
    fig, ax = plt.subplots()
    voting, options_str, counts, bar_colors = get_voting_showing_parameters(voting_id)

    y_pos = np.arange(len(options_str))

    ax.barh(y_pos, counts, align='center', color = bar_colors)
    ax.set_yticks(y_pos, labels=options_str)
    ax.invert_yaxis()
    ax.set_xlabel('Options')
    ax.set_title(voting.question.desc)

    plt.savefig(graph_image_directory)

def show_dots(voting_id):
    fig, ax = plt.subplots()
    voting, options_str, counts, bar_colors = get_voting_showing_parameters(voting_id)

    ax.scatter(options_str, counts, color=bar_colors)
    plt.legend(title = voting.question.desc)
    plt.savefig(graph_image_directory)

def show_plot(voting_id):
    fig, ax = plt.subplots()
    voting, options_str, counts, bar_colors = get_voting_showing_parameters(voting_id)
    ax.plot(options_str, counts)
    plt.legend(title = voting.question.desc)
    plt.savefig(graph_image_directory)

def get_voting_showing_parameters(voting_id):
    voting = Voting.objects.get(id__exact = voting_id)
    options = QuestionOption.objects.filter(question = voting.question)
    options_str = []
    bar_colors = []
    counts = []
    for v in voting.postproc:
        options_str.append(v['option'])
        counts.append(v['votes'])

    color_cycler = cycle(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])
    for i in range(0, len(counts)):
        bar_colors.append(next(color_cycler))

    return voting, options_str, counts, bar_colors

