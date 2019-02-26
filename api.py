# -*- coding: utf-8 -*-

from google.cloud import datastore

client = datastore.Client()


def get_group_numbers():
    query = client.query(kind='Group')
    results = list(query.fetch())
    return [results[i].key.name for i in range(len(results))]


def get_group(id):
    return client.get(client.key("Group", str(id)))["people"]


def get_number_members_tuple():
    query = client.query(kind='Group')
    results = list(query.fetch())
    return [(results[i].key.name, results[i]['people']) for i in range(len(results))]

# for i in groups:
#     task = datastore.Entity(client.key('Group', str(i)))
#     task.update({'people': groups[i]})
#     client.put(task)
