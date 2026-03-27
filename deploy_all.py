#!/usr/bin/env python3
"""Deploy all 12 coming-soon pages to Vercel."""

import sys
import json
import time
import requests

sys.path.insert(0, '/root/clawd/scripts')
from google_auth import _get_secret_from_infisical

VERCEL_TOKEN = _get_secret_from_infisical('VERCEL_API_TOKEN')

PRODUCTS = [
    'nexdo',
    'toolshelf',
    'ghl-experts',
    'fractional-cfo',
    'invoiq',
    'petcarepro',
    'menucost',
    'hoststack',
    'poolpro',
    'sundayengine',
    'careloop',
    'llm-seo-audit',
]

BASE_DIR = '/root/clawd/projects/portfolio/coming-soon'

def deploy(slug):
    html_path = f'{BASE_DIR}/{slug}/index.html'
    with open(html_path, 'r') as f:
        html_content = f.read()

    # Vercel project name must be lowercase alphanumeric + hyphens, max 52 chars
    project_name = f'ph-{slug}'

    headers = {
        'Authorization': f'Bearer {VERCEL_TOKEN}',
        'Content-Type': 'application/json'
    }

    payload = {
        'name': project_name,
        'files': [
            {
                'file': 'index.html',
                'data': html_content,
                'encoding': 'utf-8'
            }
        ],
        'projectSettings': {
            'framework': None
        },
        'target': 'production'
    }

    resp = requests.post(
        'https://api.vercel.com/v13/deployments',
        headers=headers,
        json=payload,
        timeout=60
    )

    data = resp.json()
    return data

results = {}
failures = []

for slug in PRODUCTS:
    print(f'Deploying {slug}...', flush=True)
    try:
        result = deploy(slug)
        if 'url' in result:
            url = f"https://{result['url']}"
            results[slug] = url
            print(f'  ✓ {slug}: {url}', flush=True)
        elif 'error' in result:
            err = result['error']
            failures.append({'slug': slug, 'error': err})
            print(f'  ✗ {slug}: ERROR - {err}', flush=True)
        else:
            # Sometimes the URL is in a different field
            print(f'  ? {slug}: response = {json.dumps(result)[:300]}', flush=True)
            results[slug] = result
        # Brief pause between deploys
        time.sleep(2)
    except Exception as e:
        failures.append({'slug': slug, 'error': str(e)})
        print(f'  ✗ {slug}: EXCEPTION - {e}', flush=True)

print('\n=== DEPLOYMENT SUMMARY ===')
print(f'Successful: {len(results)}')
print(f'Failed: {len(failures)}')
print('\nURLs:')
for slug, url in results.items():
    if isinstance(url, str):
        print(f'  {slug}: {url}')
    else:
        print(f'  {slug}: {json.dumps(url)[:200]}')

if failures:
    print('\nFailures:')
    for f in failures:
        print(f'  {f["slug"]}: {f["error"]}')

# Save results
with open(f'{BASE_DIR}/deployment_results.json', 'w') as f:
    json.dump({'results': results, 'failures': failures}, f, indent=2, default=str)

print('\nResults saved to deployment_results.json')
