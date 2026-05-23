import urllib.request, json

# Fetch latest run logs
run_id = '26320812244'
url = 'https://api.github.com/repos/RicharZhaoyj/tool-link-cn/actions/runs/{}/jobs'.format(run_id)
req = urllib.request.Request(url)
req.add_header('Accept', 'application/vnd.github+json')
req.add_header('User-Agent', 'LinkCN-Bot')
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    for job in data.get('jobs', []):
        print('Job: {}'.format(job['name']))
        print('  Status: {}'.format(job['status']))
        print('  Conclusion: {}'.format(job.get('conclusion', 'N/A')))
        for step in job.get('steps', []):
            print('  Step: {} | {} | {}'.format(step['name'], step['status'], step.get('conclusion', 'N/A')))
except Exception as e:
    print('Error: {}'.format(e))