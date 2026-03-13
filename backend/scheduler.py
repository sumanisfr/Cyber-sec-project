"""Scheduled scan jobs (APScheduler)."""

import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from scanner.vuln_scan import run_scan
from notifications import alert

LOG = logging.getLogger(__name__)


def _load_targets():
    """Load scheduled scan targets from env.

    Expected format: COMMA-separated URLs.
    """
    raw = os.getenv('SCHEDULED_SCAN_TARGETS', '')
    return [u.strip() for u in raw.split(',') if u.strip()]


def _job_scan_target(url: str):
    LOG.info('Running scheduled scan for %s', url)
    report = run_scan(url)
    # if critical issues found, send alert
    critical = [v for v in report.get('details', []) if v.get('level') == 'Critical']
    if critical:
        alert(
            subject=f'CyberShield Alert: Critical issues found on {url}',
            body=f"Critical issues found during scheduled scan for {url}:\n\n" +
            "\n".join([f"{v['name']}: {v['description']}" for v in critical])
        )


def start_scheduler(app):
    scheduler = BackgroundScheduler()
    targets = _load_targets()
    interval = int(os.getenv('SCHEDULED_SCAN_INTERVAL_MINUTES', '60'))

    for t in targets:
        scheduler.add_job(_job_scan_target, 'interval', minutes=interval, args=[t], id=f'scan_{t}')
        LOG.info('Scheduled scan for %s every %s minutes', t, interval)

    scheduler.start()
    app.logger.info('Scheduler started with %d targets', len(targets))
    return scheduler
