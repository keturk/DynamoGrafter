# MIT License
#
# Copyright (c) 2023 Kamil Ercan Turkarslan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from graphviz import Digraph


def generate_html_label(table_name, primary_key, attributes, gs_indexes):
    label_parts = [
        '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">''',
        '''<TR><TD>{}</TD></TR>'''.format(table_name)
    ]

    for attribute, attr_type in attributes:
        attribute_string = f"{attribute} ({attr_type})"
        if attribute == primary_key:
            attribute_string += " (PK)"
        if attribute in gs_indexes:
            attribute_string += " (GSI)"
        label_parts.append('''<TR><TD>{}</TD></TR>'''.format(attribute_string))

    label_parts.append('''</TABLE>>''')
    return ''.join(label_parts)


def generate_graph_from_yaml(yaml_data):
    dot = Digraph(comment='DynamoDB Tables Diagram')
    table_pks = {}
    indexes_dict = {}

    for table_key, table_value in yaml_data.get('Resources', {}).items():
        if table_value.get('Type') != 'AWS::DynamoDB::Table':
            continue

        properties = table_value.get('Properties')
        if not properties:
            continue

        key_schema = properties.get('KeySchema')
        if not key_schema:
            continue

        primary_key = next((item['AttributeName'] for item in key_schema if item['KeyType'] == 'HASH'), None)
        if not primary_key:
            continue

        table_name = properties.get('TableName')
        table_pks[table_name] = primary_key

        gs_indexes = properties.get('GlobalSecondaryIndexes', [])
        ls_indexes = properties.get('LocalSecondaryIndexes', [])

        gsis = [next(item['AttributeName'] for item in gsi['KeySchema'] if item['KeyType'] == 'HASH') for gsi in
                gs_indexes]
        lsis = [next(item['AttributeName'] for item in lsi['KeySchema'] if item['KeyType'] == 'RANGE') for lsi in
                ls_indexes]

        indexes = gsis + lsis
        if indexes:
            indexes_dict[table_name] = indexes

    for table_key, table_value in yaml_data.get('Resources', {}).items():
        if table_value.get('Type') != 'AWS::DynamoDB::Table':
            continue

        table_name = table_value['Properties'].get('TableName')
        attributes = [(attr['AttributeName'], attr['AttributeType']) for attr in
                      table_value['Properties'].get('AttributeDefinitions', [])]
        gs_indexes = table_value['Properties'].get('GlobalSecondaryIndexes', [])
        ls_indexes = table_value['Properties'].get('LocalSecondaryIndexes', [])

        primary_key = table_pks.get(table_name)
        label = generate_html_label(table_name, primary_key, attributes, gs_indexes + ls_indexes)
        dot.node(table_name, label)

    for table, indexes in indexes_dict.items():
        for idx in indexes:
            if idx in table_pks.values():
                related_tables = [t for t, pk in table_pks.items() if pk == idx and t != table]
                for related_table in related_tables:
                    dot.edge(related_table, table, color="blue")

    return dot
