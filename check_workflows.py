import urllib.request, json

url = 'https://api.github.com/repos/RicharZhaoyj/tool-link-cn/actions/runs?per_page=5'
headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'LinkCN-Bot'}
req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    runs = data.get('workflow_runs', [])
    if not runs:
        print('No workflow runs found')
    else:
        for run in runs:
            rid = run['id']
            name = run['name']
            status = run['status']
            conclusion = run.get('conclusion', 'N/A')
            created = run['created_at']
            print('{} | {} | {} | {} | {}'.format(rid, name, status, conclusion, created))
        print('Total: {} runs'.format(len(runs)))
except Exception as e:
    print('Error: {}'.format(e))