<h1>Multi Model Routing With Multi Armed Bandit</h1>

To install all the dependencies, please run:
<code>pip install -r requirements.txt</code>

On first run, GTFS file have to be combined to create the time-expanded graph. To do this, simply run:
<code>python main.py</code>

From second run on, since the graph created above was saved to pickle format, simply run below to avoid creating the graph again:

<code>python main.py --read_from_pickle</code>

<em>Note: only do this if you expect to use the same graph. If the graph data changed, then you have to create the graph again.</em>
