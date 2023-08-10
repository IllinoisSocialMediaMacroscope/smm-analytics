import plot
from network_analysis import Network


def algorithm(df, params):
    """
    wrapper function to put each individual algorithm inside
    :param df: dataframe that contains all the input dataset
    :param params: algorithm specific parameters
    :return: a dictionary of { outputname: output content in memory }
    """

    output = {}

    # algorithm specific code
    # construct network analysis
    NW = Network(df, params['relations'])
    output['d3js'] = NW.export_json()
    output['gephi'] = NW.export_gephi()
    output['pajek'] = NW.export_pajek()
    output['assortativity'] = NW.assortativity()
    output['node_attributes'] = NW.node_attributes()
    output['edge_attributes'] = NW.edge_attributes()
    output['strong_components'] = NW.strong_components()
    output['weak_components'] = NW.weak_components()
    output['triads'] = NW.triads()

    # plot network
    pruned_network = NW.prune_network()
    output['div'] = plot.plot_network(pruned_network, params['layout'],
                                      params['relations'],
                                      title=params['relations']
                                            + ' Network graph of 500 nodes with highest degree centrality')

    return output
