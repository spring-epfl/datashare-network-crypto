# %%
from IPython import get_ipython

# %%
get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# %%
import copy
import json
import math
import statistics
import numpy as np
import matplotlib.pyplot as plt


# %%
plt.rc('text', usetex=True)
plt.rc('font', family='serif', size=18)
plt.rc('figure', figsize=(5.5,5))
plt.rc('text.latex', preamble=r'\usepackage{mathptmx}')


# %%
with open('../benchmarks/benchmark-mspsi-2019051218051557677155.json') as content:
    data = json.load(content)


# %%
def compute_stats(data):
    fields = ['publish', 'query', 'reply', 'cardinality']
    params = ['n_document_published', 'n_kwd_per_doc', 'n_kwd_per_query']
    measures = ['time', 'length']
    output = {}
    
    for field in fields:
        entries = []

        for entry_in in data[field]:
            entry = {}
            for param in params:
                entry[param] = entry_in[param]
            for measure in measures:
                values = entry_in[measure + 's']
                if len(values) > 0:
                    mean = statistics.mean(values)
                    sem = statistics.stdev(values) / math.sqrt(len(values))
                    entry[measure] = {'mean':mean, 'sem':sem}
            entries.append(entry)
        output[field] = entries
        
    return output


def filter_entries(entries, variable, value):
    output = []
    for entry in entries:
        if entry[variable] == value:
            output.append(entry)
    return output


def get_plot_data(entries, variable, measure, const_term=0):
    means = []
    sems = []
    xvalues = []
    
    entries_s = sorted(entries, key=lambda x: x[variable])
    
    for entry in entries_s:
        xvalues.append(entry[variable])
        means.append(entry[measure]['mean'] + const_term)
        sems.append(entry[measure]['sem'])
    return (xvalues, means, sems)


# %%
def get_data_by_measure(field, measure, const_term=0):
    return get_plot_data(filter_entries(filter_entries(stats[field], 'n_kwd_per_doc', 100), 'n_kwd_per_query', 10), 'n_document_published', measure, const_term)
def get_data_by_measure_publish(field, measure, const_term=0):
    return get_plot_data(filter_entries(stats[field], 'n_kwd_per_doc', 100), 'n_document_published', measure, const_term)


# %%
stats = compute_stats(data)

data_publish_time = get_data_by_measure_publish('publish', 'time')
data_publish_length = get_data_by_measure_publish('publish', 'length')

# Query contains 360 bytes for signature, we estimate and include 1 ms for obtaining, 1 ms for signing
data_query_time = get_data_by_measure('query', 'time', 0.002)
data_query_length = get_data_by_measure('query', 'length', 360)

# Reply contains 16 extra bytes to identify the querier, we estimate and include 1 ms for signature verification
data_reply_time = get_data_by_measure('reply', 'time', 0.001)
data_reply_length = get_data_by_measure('reply', 'length', 16)

data_card_time = get_data_by_measure('cardinality', 'time')


# %%
fig, ax = plt.subplots()

#plt.title('Querying a single journalist')

x, y, yerr = data_query_time
ax.errorbar(x, y, yerr=yerr, label="Query", color='blue', fmt='o-')
x, y, yerr = data_reply_time
ax.errorbar(x, y, yerr=yerr, label="Reply", color='red', fmt='v-')
x, y, yerr = data_card_time
ax.errorbar(x, y, yerr=yerr, label="Process reply", color='green', fmt='^-')

ax.set_yscale('log')
ax.set_ylabel('Time (s)')
ax.legend(loc=(0.02, 0.57))

ax2 = ax.twinx()

x, y, yerr = data_query_length
ax2.errorbar(x, y, yerr=yerr, label="Query size", color='orange', fmt='s:')
x, y, yerr = data_reply_length
ax2.errorbar(x, y, yerr=yerr, label="Reply size", color='black', fmt='p:')

ax2.set_ylim(bottom=0, top=700)
ax2.set_ylabel('Data size (bytes)')
ax2.legend(loc=(0.52, 0.29), labelspacing=0.25)

plt.xscale('log')
ax.set_xlabel('\# Documents')

plt.savefig("single-journalist.pdf", bbox_inches='tight', pad_inches=0.01)
plt.show()


# %%
selector = lambda x: x["n_kwd_per_doc"] == 100 and x["n_document_published"] == 1000
def get_time_measurement(field):
    return statistics.mean(list(filter(selector, data[field]))[0]["times"])
def get_size_measurement(field):
    return statistics.mean(list(filter(selector, data[field]))[0]["lengths"])

# Query contains 360 bytes for signature, we estimate and include 1 ms for obtaining, 1 ms for signing
query_time = get_time_measurement("query") + 0.002
query_size = get_size_measurement("query") + 360

# Reply contains 16 extra bytes to identify the querier
response_size = get_size_measurement("reply") + 16

process_time = get_time_measurement("cardinality")


# %%
fig, ax = plt.subplots()

#plt.title('Querying all journalists')

x = np.logspace(1, 4, num = 12)

y_query_time = query_time * np.ones(x.shape)
ax.errorbar(x, y_query_time, label="Query", color='blue', fmt='o-')
y_process_time = process_time * x
ax.errorbar(x, y_process_time, label="Process replies", color='green', fmt='^-')

ax.set_yscale('log')
ax.set_ylabel('Time (s)')
ax.legend(loc=2)

ax2 = ax.twinx()

y_query_size = query_size * np.ones(x.shape)
ax2.errorbar(x, y_query_size, label="Query size", color='orange', fmt='s:')

y_responses_size = response_size * x
ax2.errorbar(x, y_responses_size, label="Replies size (sum)", color='black', fmt='p:')

ax2.set_yscale('log')
ax2.set_ylabel('Data size (bytes)')
ax2.set_ylim((10e1, 10e7))
ax2.legend(loc=(0.34,0.17))

plt.xscale('log')
ax.set_xlabel('\# Journalists')

plt.savefig("all-journalist.pdf", bbox_inches='tight', pad_inches=0.01)
plt.show()


# %%
# we estimate and include 1 ms for signature verification
response_time = get_time_measurement("reply") + 0.001

# Reply contains 16 extra bytes to identify the querier
response_size = get_size_measurement("reply") + 16


# %%
fig, ax = plt.subplots()

#plt.title('Answering all queries')

x = np.logspace(1, 4, num = 12)

y_reply_time = response_time * x
ax.errorbar(x, y_reply_time, label="Replies to queries", color='red', fmt='v-')

ax.set_yscale('log')
ax.set_ylabel('Time (s)')
ax.legend(loc=2)

ax2 = ax.twinx()

y_query_size = query_size * x
ax2.errorbar(x, y_query_size, label="Queries incoming", color='orange', fmt='s:')
y_response_size = response_size * x
ax2.errorbar(x, y_response_size, label="Replies outgoing", color='black', fmt='p:')

ax2.set_yscale('log')
ax2.set_ylabel('Data size (bytes)')
ax2.legend(loc=4)
ax2.set_ylim((10e2, 10e7))

plt.xscale('log')
ax.set_xlabel('\# Queries / day')

plt.savefig("all-queries.pdf", bbox_inches='tight', pad_inches=0.01)
plt.show()




