import networkx as nx
from networkx.readwrite import json_graph
import pandas


class Network:

    def __init__(self, df, relationships):
        # construct network
        # 3 networks: reply to, retweet from, and mentions
        # 2 datasources with different field: twitter-Tweet & twitter-Stream

        columns = df.columns.values.tolist()

        if relationships == 'reply_to':
            if 'text' in columns and 'user.screen_name' in columns:
                df = df[['text', 'user.screen_name']].dropna()
                # extract tweet starting with @XXX
                df['reply_to'] = df['text'].str.extract('^@([A-Za-z0-9-_]+)',
                                                        expand=True)
                new_df = df[['reply_to', 'user.screen_name', 'text']].dropna()

                self.graph = nx.DiGraph()
                for row in new_df.iterrows():
                    self.graph.add_edge(row[1]['user.screen_name'],
                                        row[1]['reply_to'],
                                        text=row[1]['text'])
            elif '_source.text' in columns and '_source.user.screen_name' in columns:
                df = df[['_source.text', '_source.user.screen_name']].dropna()
                df['reply_to'] = df['_source.text'].str.extract(
                    '^@([A-Za-z0-9-_]+)',
                    expand=True)
                new_df = df[['reply_to', '_source.user.screen_name',
                             '_source.text']].dropna()

                self.graph = nx.DiGraph()
                for row in new_df.iterrows():
                    self.graph.add_edge(row[1]['_source.user.screen_name'],
                                        row[1]['reply_to'],
                                        text=row[1]['_source.text'])
            else:
                raise ValueError(
                    'The File you selected does not have complete '
                    'information to construct a network. You must '
                    'have the full tweet as well as the author information.')

        elif relationships == 'retweet_from':
            if 'text' in columns and 'user.screen_name' in columns:
                df = df[['text', 'user.screen_name']].dropna()
                # extract tweets has RT @XXX
                df['retweet_from'] = df['text'] \
                    .str.extract('RT @([A-Za-z0-9-_]+):', expand=True)
                new_df = df[['retweet_from', 'user.screen_name',
                             'text']].dropna()

                self.graph = nx.DiGraph()
                for row in new_df.iterrows():
                    self.graph.add_edge(row[1]['user.screen_name'],
                                        row[1]['retweet_from'],
                                        text=row[1]['text'])
            elif '_source.text' in columns and '_source.user.screen_name' in columns:
                df = df[['_source.text', '_source.user.screen_name']].dropna()
                df['retweet_from'] = df['_source.text'] \
                    .str.extract('RT @([A-Za-z0-9-_]+):', expand=True)
                new_df = df[['retweet_from',
                             '_source.user.screen_name',
                             '_source.text']].dropna()

                self.graph = nx.DiGraph()
                for row in new_df.iterrows():
                    self.graph.add_edge(row[1]['_source.user.screen_name'],
                                        row[1]['retweet_from'],
                                        text=row[1]['_source.text'])
            else:
                raise ValueError(
                    'The File you selected does not have complete '
                    'information to construct a network. You must '
                    'have the full tweet as well as the author information.')

        elif relationships == 'mentions':
            if 'text' in columns and 'user.screen_name' in columns:
                df = df[['text', 'user.screen_name']].dropna()
                # extract tweets contains any @
                df['mentions'] = df['text'].str.findall('@([A-Za-z0-9-_]+)')
                tmp = []

                def __backend(r):
                    x = r['user.screen_name']
                    y = r['text']
                    zz = r['mentions']
                    for z in zz:
                        tmp.append({'screen_name': x,
                                    'tweet': y,
                                    'mention': z})

                df.apply(__backend, axis=1)
                new_df = pandas.DataFrame(tmp).dropna()

                self.graph = nx.DiGraph()
                for row in new_df.iterrows():
                    self.graph.add_edge(row[1]['screen_name'],
                                        row[1]['mention'],
                                        text=row[1]['tweet'])
            elif '_source.text' in columns and '_source.user.screen_name' in columns:
                df = df[['_source.text', '_source.user.screen_name']].dropna()
                df['mentions'] = df['_source.text'].str.findall(
                    '@([A-Za-z0-9-_]+)')
                tmp = []

                def __backend(r):
                    x = r['_source.user.screen_name']
                    y = r['_source.text']
                    zz = r['mentions']
                    for z in zz:
                        tmp.append({'screen_name': x,
                                    'tweet': y,
                                    'mention': z})

                df.apply(__backend, axis=1)
                new_df = pandas.DataFrame(tmp).dropna()

                self.graph = nx.DiGraph()
                for row in new_df.iterrows():
                    self.graph.add_edge(row[1]['screen_name'],
                                        row[1]['mention'],
                                        text=row[1]['tweet'])
            else:
                raise ValueError(
                    'The File you selected does not have complete '
                    'information to construct a network. You must '
                    'have the full tweet as well as the author information.')

    def prune_network(self):
        d = nx.degree_centrality(self.graph)
        d = sorted(d.items(), key=lambda x: x[1], reverse=True)
        if len(d) >= 500:
            for n in d[500:]:
                self.graph.remove_node(n[0])
        self.graph.remove_nodes_from(nx.isolates(self.graph))

        return self.graph

    def export_json(self):
        d3js_graph = json_graph.node_link_data(self.graph)
        d3js_graph['nodes'] = [{'id': node['id'],
                                'connectivity': self.graph.in_degree()[
                                                    node['id']]
                                                + self.graph.out_degree()[
                                                    node['id']]}
                               for node in d3js_graph['nodes']]

        return d3js_graph

    def export_gephi(self):
        return nx.generate_gml(self.graph)

    def export_pajek(self):
        return nx.generate_pajek(self.graph)

    def assortativity(self):
        result = {}
        result['average_degree_connectivity'] = nx.average_degree_connectivity(
            self.graph)
        result['k_nearest_neighbors'] = nx.k_nearest_neighbors(self.graph)

        # k degree distribution
        k_degree = []
        for k in result['average_degree_connectivity'].keys():
            k_degree.append((k, result['average_degree_connectivity'][k],
                             result['k_nearest_neighbors'][k]))

        k_degree.insert(0, ['degree k', 'average_degree_connectivity',
                            'k_nearest_neighbors'])

        return k_degree

    def node_attributes(self):
        result = {}

        result['degree_centrality'] = nx.degree_centrality(self.graph)
        result['in_degree_centrality'] = nx.in_degree_centrality(self.graph)
        result['out_degree_centrality'] = nx.out_degree_centrality(self.graph)
        result['closeness_centrality'] = nx.closeness_centrality(self.graph)
        result['betweenness_centrality'] = nx.betweenness_centrality(
            self.graph)
        result['load_centrality'] = nx.load_centrality(self.graph)
        result['average_neighbor_degree'] = nx.average_neighbor_degree(
            self.graph)
        result['square_clustering'] = nx.square_clustering(self.graph)
        result['closeness_vitality'] = nx.closeness_vitality(self.graph)

        # nodes attributes
        node_attributes = []
        for node in self.graph.nodes():
            node_attributes.append((node, result['degree_centrality'][node],
                                    result['in_degree_centrality'][node],
                                    result['out_degree_centrality'][node],
                                    result['closeness_centrality'][node],
                                    result['betweenness_centrality'][node],
                                    result['load_centrality'][node],
                                    result['average_neighbor_degree'][node],
                                    result['square_clustering'][node],
                                    result['closeness_vitality'][node]))

        node_attributes.insert(0, ['node',
                                   'degree_centrality',
                                   'in_degree_centrality',
                                   'out_degree_centrality',
                                   'closeness_centrality',
                                   'betweenness_centrality',
                                   'load_centrality',
                                   'average_neighbor_degree',
                                   'square_clustering',
                                   'closeness_vitality'])

        return node_attributes

    def edge_attributes(self):
        result = {}
        result['edge_betweenness_centrality'] = nx.edge_betweenness_centrality(
            self.graph)
        result['edge_load'] = nx.edge_load(self.graph)

        edge_attributes = []
        for edge in self.graph.edges():
            edge_attributes.append((edge,
                                    result['edge_betweenness_centrality'][
                                        edge],
                                    result['edge_load'][edge]))
        edge_attributes.insert(0, ['edge', 'edge_betweenness_centrality',
                                   'edge_load'])

        return edge_attributes

    def strong_components(self):
        strong = nx.strongly_connected_components(self.graph)
        strong_nodes = [['strongly_connected_component']]
        for n in strong:
            strong_nodes.append([list(n)[0]])

        return strong_nodes

    def weak_components(self):
        weak = nx.weakly_connected_components(self.graph)
        weak_nodes = [['weakly_connected_component']]
        for n in weak:
            weak_nodes.append([list(n)[0]])

        return weak_nodes

    def triads(self):
        rslt = {}
        rslt['triadic_census'] = nx.triadic_census(self.graph)

        return rslt
