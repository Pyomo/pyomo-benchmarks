"""
Make graphs from Pyomo_benchmark_new JSON data
"""
from os import walk
from os.path import join
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

colors = ['#acc2d9', '#ff0789', '#966ebd', '#ad900d', '#009337',
          '#850e04', '#3e82fc', '#fe420f', '#fe828c', '#85a3b2',
          '#f0833a', '#b1d27b', '#ff796c', '#c79fef', '#e50000',
          '#15b01a', '#653700', '#75bbfd', '#c20078', '#929591',
          '#f97306', '#380282', '#ceb301', '#580f41', '#dbb40c',
          '#4b006e', '#a9f971', '#610023', '#516572', '#040273',
          '#a83c09', '#0b4008', '#ed0dd9', '#d648d7', '#98eff9',
          '#87ae73', '#b04e0f', '#fc5a50', '#020035', '#c0737a',
          '#5e819d', '#80013f', '#76cd26', '#045c5a', '#a2a415',
          '#af884a', '#769958', '#cb0162', '#12e193', '#980002',
          '#030aa7', '#e17701', '#01a049', '#fcb001', '#ce5dae',
          '#ac9362', '#49759c', '#be6400', '#e03fd8', '#826d8c']

python = ['python-2.7',
          'python-3.4',
          'python-3.5',  'python-3.6',
          'python-3.7', 'python-3.8',
          'pypy2', 'pypy3']

measure = ['create_instance', 'discretize', 'postprocessing', 'nl',
           'lp', 'bar', 'gams', 'test_time']

# Get the last two months
today = datetime.today()
months = [today.strftime('%Y-%m'),
          (today + relativedelta(months=-1)).strftime('%Y-%m')]
# Assume the existence of the data-archive
# under the name "data-archive"
dataFiles = []
for month in months:
    for (dirpath, dirnames, filenames) in walk('./data-archive/pr_archive/{}/'.format(month)):
        dataFiles += [join(dirpath, file) for file in filenames]

dataFiles.sort()
currBuild = int(dataFiles[-1].split('-')[3])
last50 = list(range(currBuild-49, currBuild+1))

# Initialize empty data dictionary
pData = {}
#TODO: This might need to be altered.
# I'm making the assumption that the most recent data file is a good
# reference set for what problems should exist for *ALL* other files.
# If new problems are added/changed, I'm not sure how this would cause issues
with open(dataFiles[-1], 'r') as f:
    rundata, timedata = json.load(f)
# JSON version of the problem name
timedatakeys = [key for key in timedata.keys()]
# Human-readable version of the problem name
problems = [key.split('.')[-1] for key in timedata.keys()]

for py in python:
    pFilesAll = [file for file in dataFiles if py in file]
    pFiles = {}
    for build in last50:
        pFiles[build] = [file for file in pFilesAll
                         if build == int(file.split('-')[3])]

    pData[py] = {}
    for problem in problems:
        pData[py][problem] = {}
        for m in measure:
            pData[py][problem][m] = []

    date = {}
    sha = {}
    for build in last50:
        # If the file exists for that build...
        if pFiles[build]:
            file = pFiles[build][0]
            # Capture the data
            with open(file, 'r') as f:
                rundata, timedata = json.load(f)
            # Append the build
            # and test result to the dictionary for each problem
            date = datetime.utcfromtimestamp(rundata['time']).strftime('%Y-%m-%d')
            sha = rundata['sha'][0:8]
            for key in timedatakeys:
                i = timedatakeys.index(key)
                for m in measure:
                    if m in timedata[key]:
                        # Insert the data if it exists
                        pData[py][problems[i]][m].append((build, date, sha, timedata[key][m]))
                    else:
                        # Put a hole if it doesn't
                        pData[py][problems[i]][m].append((build, '', '', ''))
        else:
            # Place empty data
            for problem in problems:
                for m in measure:
                    pData[py][problem][m].append((build, '', '', ''))


py = 'python-2.7'
problem = 'test_stochpdegas_automatic'
xax = list(range(-49, 1))

# Create figure
fig = go.Figure()

# Add traces
i = 0
for m in measure:
    yax = [val[-1] for val in pData[py][problem][m]]
    if list(filter(None, yax)) == []:
        continue
    i += 1
    dates = [val[1] for val in pData[py][problem][m]]
    shas = [val[2] for val in pData[py][problem][m]]
    txt = []
    for j in list(range(len(dates))):
        txt.append(dates[j] + ', ' + shas[j])

    fig.add_trace(go.Scatter(
        x=xax,
        y=yax,
        name=m,
        text=txt,
        yaxis='y{}'.format(i),
        line=dict(color=colors[i-1]),
    ))

fig.update_traces(
    hoverinfo="text+x",
    line={"width": 0.5},
    marker={"size": 8},
    mode="lines+markers",
    showlegend=True
)

# Update axes
fig.update_layout(
    xaxis=dict(
        autorange=True,
        range=[-49, 0],
        rangeslider=dict(
            autorange=True,
            range=[-49, 1]
        ),
        type="linear"
    )
)

"""
Plotly is a restrictive here. It requires a manual
hard-coding of number of yaxes. I am hardcoding 20
different plots, but dynamically assigning the domains.
If the extra plots are not needed,
they will simply not show.
"""

d = 1/i
j = 0
while j < 20:
    if d*j >= 1:
        domain = [1, 1]
    else:
        domain = [d*j, d*(j+1)]
    globals()['yaxis{}'.format(j+1)]=dict(
        anchor="x",
        autorange=True,
        fixedrange=False,
        domain=domain,
        mirror=True,
        showline=True,
        side="left",
        tickfont={"color": colors[j], 'size': 9},
        tickmode="auto",
        ticks="",
        tickson="boundaries",
        type="linear",
        zeroline=False
    ),
    j += 1


fig.update_layout(
    yaxis1=yaxis1[0],
    yaxis2=yaxis2[0],
    yaxis3=yaxis3[0],
    yaxis4=yaxis4[0],
    yaxis5=yaxis5[0],
    yaxis6=yaxis6[0],
    yaxis7=yaxis7[0],
    yaxis8=yaxis8[0],
    yaxis9=yaxis9[0],
    yaxis10=yaxis10[0],
    yaxis11=yaxis11[0],
    yaxis12=yaxis12[0],
    yaxis13=yaxis13[0],
    yaxis14=yaxis14[0],
    yaxis15=yaxis15[0],
    yaxis16=yaxis16[0],
    yaxis17=yaxis17[0],
    yaxis18=yaxis18[0],
    yaxis19=yaxis19[0],
    yaxis20=yaxis20[0]
)



# Update layout
title = 'Python = {}, Problem = {}'.format(py, problem)
h = 150*i
fig.update_layout(
    title=title,
    yaxis={'automargin': False},
    dragmode="zoom",
    hovermode="x",
    legend=dict(traceorder="reversed", yanchor="top", y=0.99, xanchor="left"),
    height=h,
    template="plotly_white",
    margin=dict(
        t=50,
        b=50
    ),
)

fig.show()

# fig.write_html('nameoffile')
