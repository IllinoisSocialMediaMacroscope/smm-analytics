from plotly.graph_objs import *
from plotly.offline import plot
# import networkx as nx


def plot_pie_chart(labels, values, title):
    """
    plot pie chart
    :param labels: list of label, shape must match parameter values
    :param values: list of values, shape must match parameter labels
    :param title: title to show
    :return: html code in a div
    """
    trace = Pie(labels=labels, values=values, textinfo='label+percent')
    layout = Layout(
        title=title,
        font=dict(family='Arial', size=12),
        margin=dict(
            l=70,
            r=70,
            t=70,
            b=70,
        )
    )
    fig = Figure(data=[trace], layout=layout)
    div = plot(fig, output_type='div', image='png', auto_open=False,
                    image_filename='plot_img')

    return div


# def plot_network(graph, layout, relationships, title):
#     """
#     plot network graph
#     :param graph: networkx graph
#     :param layout: network layout
#     :param relationships: reply, retweet, mention or anything else
#     :param title: title to show
#     :return: html code in a div
#     """
#
#     if layout == 'spring':
#         pos = nx.spring_layout(graph)
#     elif layout == 'circular':
#         pos = nx.circular_layout(graph)
#     elif layout == 'fruchterman':
#         pos = nx.fruchterman_reingold_layout(graph)
#     elif layout == 'random':
#         pos = nx.random_layout(graph)
#     elif layout == 'shell':
#         pos = nx.shell_layout(graph)
#     elif layout == 'spectral':
#         pos = nx.spectral_layout(graph)
#     edge_attri = nx.get_edge_attributes(graph, 'text')
#     edge_trace = Scatter(x=[], y=[], text=[],
#                          line=Line(width=1, color='#b5b5b5'),
#                          hoverinfo='text',
#                          mode='lines',
#                          hoveron='points')
#     for edge in graph.edges():
#         x0, y0 = pos[edge[0]]
#         x1, y1 = pos[edge[1]]
#         edge_trace['x'] += [x0, x1, None]
#         edge_trace['y'] += [y0, y1, None]
#         edge_trace['text'].append(edge_attri[edge])
#
#     node_trace = Scatter(x=[], y=[], text=[], mode='markers',
#                          hoverinfo='text', hoveron='points+fills',
#                          marker=Marker(showscale=True,
#                                        colorscale='Portland',
#                                        reversescale=False,
#                                        color=[],
#                                        size=10,
#                                        colorbar=dict(thickness=15,
#                                                      title='node in-degree plus out-degree',
#                                                      xanchor='left',
#                                                      titleside='right'),
#                                        line=dict(width=2)))
#     for node in graph.nodes():
#         x, y = pos[node]
#         node_trace['x'].append(x)
#         node_trace['y'].append(y)
#
#     # set label
#     for node in graph.nodes():
#         node_trace['marker']['color'].append(graph.in_degree()[node] + graph.out_degree()[node])
#         if relationships == 'reply_to':
#             node_trace['text'].append("@" + node + " is replied by "
#                                   + str(graph.in_degree()[node])
#                                   + " user(s), and replies to "
#                                   + str(graph.out_degree()[node]) + " user(s)")
#
#         elif relationships == 'retweet_from':
#             node_trace['text'].append("@" + node + " is retweeted by "
#                                       + str(graph.in_degree()[node])
#                                       + " user(s) and retweets from "
#                                       + str(graph.out_degree()[node])
#                                       + " user(s)")
#
#         elif relationships == 'mentions':
#             node_trace['text'].append("@" + node + " is mentioned by "
#                                       + str(graph.in_degree()[node])
#                                       + " user(s) and mentions "
#                                       + str(graph.out_degree()[node])
#                                       + " user(s)")
#
#     fig = Figure(data=Data([edge_trace, node_trace]),
#                  layout=Layout(
#                      title=title,
#                      titlefont=dict(size=16), showlegend=False,
#                      hovermode='closest', margin=dict(b=20, l=5, r=5, t=40),
#                      xaxis=XAxis(showgrid=False, zeroline=False,
#                                  showticklabels=False),
#                      yaxis=YAxis(showgrid=False, zeroline=False,
#                                  showticklabels=False)
#                  ))
#
#     div = plot(fig, output_type='div', image='png', auto_open=False,
#                image_filename='plot_img')
#
#     return div


def plot_bar_chart(index, counts, title):
    """
    plot bar chart
    :param index: x - axis, usually the index
    :param counts: y - axis, usually counts
    :param title:
    :return:
    """

    trace = Bar(x=index, y=counts,
                marker=dict(color='rgba(200,75,73,1.0)',
                            line=dict(color='rgba(111,11,9,1.0)',width=2)))
    layout = Layout(
        title=title,
        font=dict(family='Arial', size=12),
        yaxis=dict(
            showgrid=True,
            showline=True,
            showticklabels=True,
            linecolor='rgba(102, 102, 102, 0.8)',
            linewidth=2,
            # 10 fold cross validation
            range=[0, 1]
        ),
        margin=dict(
            l=70,
            r=70,
            t=70,
            b=70,
        )
    )

    fig = Figure(data=[trace], layout=layout)
    div = plot(fig, output_type='div', image='png', auto_open=False, image_filename='plot_img')

    return div
