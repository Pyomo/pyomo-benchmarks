"""
Make graphs from Pyomo_benchmark_new JSON data
"""
from os import walk
from os.path import join
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

xkcd_colors = {}
with open('rgb.txt', 'r') as colors:
  for line in colors:
    if 'License' in line:
        continue
    name, color = line.split('#')
    name = name.strip()
    color = color.strip()
    xkcd_colors['xkcd:' + name] = '#' + color

colors = ['xkcd:black', 'xkcd:red', 'xkcd:blue', 'xkcd:pink', 'xkcd:electric purple', 
          'xkcd:orange', 'xkcd:teal', 'xkcd:magenta', 'xkcd:grey',
          'xkcd:turquoise', 'xkcd:cyan', 'xkcd:maroon',
          'xkcd:olive', 'xkcd:salmon', 'xkcd:beige', 'xkcd:navy blue', 
          'xkcd:hot pink', 'xkcd:burnt yellow', 'xkcd:blue grey', 
          'xkcd:battleship grey', 'xkcd:yellow', 'xkcd:light purple']

colors_rgb = [xkcd_colors[color] for color in colors]

python = ['python-2.7',
           'python-3.4',
           'python-3.5',  'python-3.6',
           'python-3.7', 'python-3.8',
           'pypy2', 'pypy3']

measure = ['create_instance', 'discretize', 'postprocessing', 'nl',
        'lp', 'bar', 'gams', 'test_time']

# Get the last two months
today = datetime.today()
months = [today.strftime('%Y-%m'), (today + relativedelta(months=-1)).strftime('%Y-%m')]
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
        pFiles[build] = [file for file in pFilesAll \
                         if build == int(file.split('-')[3])]
      
    pData[py] = {}
    for problem in problems:
        pData[py][problem] = {}
        for m in measure:
            pData[py][problem][m] = []

    for build in last50:
        # If the file exists for that build...
        if pFiles[build]:
            file = pFiles[build][0]
            # Capture the data
            with open(file, 'r') as f:
                rundata, timedata = json.load(f)
            # Append the build # and test result to the dictionary for each problem
            for key in timedatakeys:
                i = timedatakeys.index(key)
                for m in measure:
                    if m in timedata[key]:
                        # Insert the data if it exists
                        pData[py][problems[i]][m].append((build, timedata[key][m]))
                    else:
                        # Put a hole if it doesn't
                        pData[py][problems[i]][m].append((build, ''))
        else:
            # Place empty data
            for problem in problems:
                for m in measure:
                    pData[py][problem][m].append((build, ''))

py = 'python-2.7'
xax = list(range(-49, 1))
    
# Create figure
fig = go.Figure()

# Add traces
i = 0
for m in measure:
    i += 1
    yax = [val[1] for val in pData[py][problem][m]]
    
    fig.add_trace(go.Scatter(
        x=xax,
        y=yax,
        name=m,
        text=['{} s'.format(item) for item in yax],
        yaxis='y{}'.format(i),
        line=dict(color = colors_rgb[i]),
    ))
fig.update_traces(
    hoverinfo="name+x+text",
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
    ),
    yaxis1=dict(
        anchor="x",
        autorange=True,
        fixedrange=False,
        domain=[0, 0.125],
        mirror=True,
        range=[0, 0.05],
        showline=True,
        side="left",
        tickfont={"color": colors_rgb[1], 'size': 9},
        tickmode="auto",
        ticks="",
        tickson="boundaries",
        type="linear",
        zeroline=False
    ),
    yaxis2=dict(
        anchor="x",
        autorange=True,
        fixedrange=False,
        domain=[0.125, 0.25],
        mirror=True,
        range=[0, 0.05],
        showline=True,
        side="left",
        tickfont={"color": colors_rgb[2], 'size': 9},
        tickmode="auto",
        ticks="",
        tickson="boundaries",
        type="linear",
        zeroline=False
    ),
    yaxis3=dict(
        anchor="x",
        autorange=True,
        fixedrange=False,
        domain=[0.25, 0.375],
        mirror=True,
        range=[0, 0.05],
        showline=True,
        side="left",
        tickfont={"color": colors_rgb[3], 'size': 9},
        tickmode="auto",
        ticks="",
        tickson="boundaries",
        type="linear",
        zeroline=False
    ),
    yaxis4=dict(
        anchor="x",
        autorange=True,
        fixedrange=False,
        domain=[0.375, 0.5],
        mirror=True,
        range=[0, 0.05],
        showline=True,
        side="left",
        tickfont={"color": colors_rgb[4], 'size': 9},
        tickmode="auto",
        ticks="",
        tickson="boundaries",
        type="linear",
        zeroline=False
    ),
    yaxis5=dict(
        anchor="x",
        autorange=True,
        fixedrange=False,
        domain=[0.5, 0.675],
        mirror=True,
        range=[0, 0.05],
        showline=True,
        side="left",
        tickfont={"color": colors_rgb[5], 'size': 9},
        tickmode="auto",
        ticks="",
        tickson="boundaries",
        type="linear",
        zeroline=False
    ),
    yaxis6=dict(
        anchor="x",
        autorange=True,
        fixedrange=False,
        domain=[0.675, 0.75],
        mirror=True,
        range=[0, 0.05],
        showline=True,
        side="left",
        tickfont={"color": colors_rgb[6], 'size': 9},
        tickmode="auto",
        ticks="",
        tickson="boundaries",
        type="linear",
        zeroline=False
    ),
    yaxis7=dict(
        anchor="x",
        autorange=True,
        fixedrange=False,
        domain=[0.75, 0.875],
        mirror=True,
        range=[0, 0.05],
        showline=True,
        side="left",
        tickfont={"color": colors_rgb[7], 'size': 9},
        tickmode="auto",
        ticks="",
        tickson="boundaries",
        type="linear",
        zeroline=False
    ),
    yaxis8=dict(
        anchor="x",
        autorange=True,
        fixedrange=False,
        domain=[0.875, 1],
        mirror=True,
        range=[0.01, 0.05],
        showline=True,
        side="left",
        tickfont={"color": colors_rgb[8], 'size': 9},
        tickmode="auto",
        ticks="",
        tickson="boundaries",
        type="linear",
        zeroline=False
    )
)

# Update layout
title='Python = {}, Problem = {}'.format(py, problem)
fig.update_layout(
    title=title,
    yaxis={'automargin': True},
    dragmode="zoom",
    hovermode="x",
    legend=dict(traceorder="reversed"),
    height=900,
    template="plotly_white",
    margin=dict(
        t=100,
        b=100
    ),
)

fig.show()
