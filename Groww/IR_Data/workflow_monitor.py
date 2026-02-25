#!/usr/bin/env python3
"""
GitHub Actions Workflow Monitor
Monitors the Groww IR Data fetch workflow and sends notifications on failure
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = 'Rachitjainca/groww-ir-data'
WORKFLOW_NAME = 'Fetch Groww IR Data'
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK')

# GitHub API
GITHUB_API = 'https://api.github.com'

def get_workflow_runs(limit=10):
    """Get recent workflow runs from GitHub"""
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    url = f'{GITHUB_API}/repos/{GITHUB_REPO}/actions/workflows/@main'
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error fetching workflow: {response.status_code}")
        return None
    
    workflow_id = response.json()['workflows'][0]['id']
    
    # Get runs
    runs_url = f'{GITHUB_API}/repos/{GITHUB_REPO}/actions/workflows/{workflow_id}/runs'
    params = {'per_page': limit, 'status': 'all'}
    
    runs_response = requests.get(runs_url, headers=headers, params=params)
    return runs_response.json()['workflow_runs']

def send_discord_notification(title, description, color, details):
    """Send notification to Discord webhook"""
    if not DISCORD_WEBHOOK:
        return False
    
    payload = {
        "content": f"🔔 {title}",
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "fields": [
                {"name": k, "value": str(v)[:1024], "inline": True}
                for k, v in details.items()
            ],
            "timestamp": datetime.utcnow().isoformat()
        }]
    }
    
    response = requests.post(DISCORD_WEBHOOK, json=payload)
    return response.status_code == 204

def send_slack_notification(title, description, color, details):
    """Send notification to Slack webhook"""
    if not SLACK_WEBHOOK:
        return False
    
    # Convert color to emoji
    emoji = "❌" if color == 15158332 else "✅" if color == 3066993 else "⚠️"
    
    # Build fields for Slack
    fields = []
    for k, v in details.items():
        fields.append({
            "type": "mrkdwn",
            "text": f"*{k}:*\n{str(v)[:500]}"
        })
    
    payload = {
        "text": f"{emoji} {title}",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{emoji} {title}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": description}
            },
            {
                "type": "section",
                "fields": fields
            }
        ]
    }
    
    response = requests.post(SLACK_WEBHOOK, json=payload)
    return response.status_code == 200

def check_workflow_health():
    """Check if workflow is running correctly"""
    print("=" * 60)
    print("Groww IR Data - Workflow Monitor")
    print("=" * 60)
    
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN not set in .env")
        return False
    
    # Get recent runs
    runs = get_workflow_runs(limit=20)
    
    if not runs:
        print("❌ Could not fetch workflow runs")
        return False
    
    print(f"\n📊 Recent workflow runs ({len(runs)} shown):\n")
    
    # Analyze runs
    failed_runs = []
    success_runs = []
    
    for run in runs:
        status = run['status']
        conclusion = run['conclusion']
        created_at = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
        
        icon = "✅" if conclusion == 'success' else "❌" if conclusion == 'failure' else "⏳"
        print(f"{icon} [{created_at.strftime('%Y-%m-%d %H:%M:%S')}] {conclusion.upper() if conclusion else status}")
        
        if conclusion == 'failure':
            failed_runs.append(run)
        elif conclusion == 'success':
            success_runs.append(run)
    
    # Check for continuous failures
    recent_runs = runs[:10]
    recent_failures = [r for r in recent_runs if r['conclusion'] == 'failure']
    
    print(f"\n📈 Stats (last 10 runs):")
    print(f"  ✅ Successful: {len([r for r in recent_runs if r['conclusion'] == 'success'])}")
    print(f"  ❌ Failed: {len(recent_failures)}")
    print(f"  ⏳ In Progress: {len([r for r in recent_runs if r['status'] != 'completed'])}")
    
    # Check run frequency
    if len(recent_runs) >= 2:
        latest_run = recent_runs[0]
        second_run = recent_runs[1]
        
        latest_time = datetime.fromisoformat(latest_run['created_at'].replace('Z', '+00:00'))
        second_time = datetime.fromisoformat(second_run['created_at'].replace('Z', '+00:00'))
        
        time_diff = (latest_time - second_time).total_seconds() / 60
        print(f"  ⏱️  Time between recent runs: {time_diff:.1f} minutes")
        
        if time_diff > 2:
            print(f"  ⚠️  Expected 1 minute interval, got {time_diff:.1f} minutes")
    
    # Send alert if there are recent failures
    if len(recent_failures) >= 3:
        print(f"\n❌ ALERT: {len(recent_failures)} recent failures detected!")
        
        failure_times = []
        for run in recent_failures[:3]:
            run_time = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
            failure_times.append(run_time.strftime('%H:%M:%S'))
        
        details = {
            "Failures": str(len(recent_failures)),
            "Repository": GITHUB_REPO,
            "Last Failures": ", ".join(failure_times),
            "Action": f"[View Logs](https://github.com/{GITHUB_REPO}/actions)"
        }
        
        send_discord_notification(
            title="⚠️ Workflow Failure Alert",
            description=f"{len(recent_failures)} recent workflow failures detected",
            color=15158332,  # Red
            details=details
        )
        
        send_slack_notification(
            title="⚠️ Workflow Failure Alert",
            description=f"{len(recent_failures)} recent workflow failures detected",
            color=15158332,  # Red
            details=details
        )
        
        return False
    
    elif len(recent_runs) > 0 and recent_runs[0]['conclusion'] == 'failure':
        print(f"\n⚠️  WARNING: Latest run failed")
        
        latest_run = recent_runs[0]
        run_time = datetime.fromisoformat(latest_run['created_at'].replace('Z', '+00:00'))
        
        details = {
            "Status": "FAILED",
            "Run ID": str(latest_run['id']),
            "Time": run_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            "Repository": GITHUB_REPO,
            "Action": f"[View Logs](https://github.com/{GITHUB_REPO}/actions/runs/{latest_run['id']})"
        }
        
        send_discord_notification(
            title="Groww IR Data Fetch Failed",
            description="Latest workflow run failed",
            color=15158332,  # Red
            details=details
        )
        
        send_slack_notification(
            title="Groww IR Data Fetch Failed",
            description="Latest workflow run failed",
            color=15158332,  # Red
            details=details
        )
        
        return False
    
    else:
        print(f"\n✅ Workflow running normally")
        return True
    
    print("\n" + "=" * 60)

def setup_env_template():
    """Create .env.example for monitoring setup"""
    template = """# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token

# Discord Webhook (optional)
# Get from: https://discord.com/developers/applications
DISCORD_WEBHOOK=https://discordapp.com/api/webhooks/YOUR_WEBHOOK_URL

# Slack Webhook (optional)
# Get from: https://api.slack.com/messaging/webhooks
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
"""
    
    env_example = os.path.join(os.path.dirname(__file__), '.env.monitor.example')
    if not os.path.exists(env_example):
        with open(env_example, 'w') as f:
            f.write(template)
        print(f"\n📝 Created {env_example}")
        print("   Copy to .env and fill in your credentials to enable monitoring")

if __name__ == '__main__':
    try:
        setup_env_template()
        health_ok = check_workflow_health()
        exit(0 if health_ok else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
