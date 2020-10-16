<h1>Multi Model Routing With Multi Armed Bandit</h1>

To install all dependencies, please run: <br>
<code>pip install -r requirements.txt</code>

On the first run, GTFS data have to be combined to create the time-expanded graph. To do this, simply run:<br>
<code>python main.py</code>

From second run on, since the graph created above was saved to pickle format, simply run below to avoid creating the graph again:<br>

<code>python main.py --read_from_pickle</code>

<em>Note: only do this if you expect to use the same graph. If the graph data changed, then you have to create the graph again.</em><br>

<strong>Change search query data </strong><br>
Search queries can be changed in file <code>config.py</code>.<br>
Look for a variable named <code>search_request_list</code>. This variable is a python list which can contain multiple search requests at the same time, which enable testing wth multiple instances. Of course you are free to test one at a time. Each element in the list represents a search request. The format is as follow: <br>
<code>[earliest_departure_time, departure_lat, departure_lon, arrival_lat, arrival_lon, search_requestname, sampling_method, number_of_sampling_iterations]</code>

Other problem related parameter (e.g. walking speed, prices, maximum walking distance) can also be changed in <code>config.py</code>. <br>

<strong>Output</strong>

Output are exported to folder <code>/outputpicture</code><br>
A detailed soltuion info is also available in the file <code>solinfo.csv</code>
