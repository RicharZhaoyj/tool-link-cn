import urllib.request, json, base64

# GitHub API with basic auth using stored token
# Check workflow runs
url = 'https://api.github.com/repos/RicharZhaoyj/tool-link-cn/actions/runs?per_page=5'
req = urllib.request.Request(url)
req.add_header('Accept', 'application/vnd.github+json')
req.add_header('User-Agent', 'LinkCN-Bot')
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    runs = data.get('workflow_runs', [])
    if not runs:
        print('No workflow runs found')
    else:
        for run in runs:
            print('ID: {}'.format(run['id']))
            print('  Name: {}'.format(run['name']))
            print('  Status: {}'.format(run['status']))
            print('  Conclusion: {}'.format(run.get('conclusion', 'N/A')))
            print('  Created: {}'.format(run['created_at']))
            print('  Updated: {}'.format(run['updated_at']))
            print('')
        print('Total runs shown: {}'.format(len(runs)))
except urllib.error.HTTPError as e:
    print('HTTP Error {}: {}'.format(e.code, e.reason))
    if e.code == 403:
        print('Rate limited or unauthenticated')
except Exception as e:
    print('Error: {}'.format(e))
