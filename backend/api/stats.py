import json
from queue import Empty

from flask import Blueprint, jsonify, Response, stream_with_context
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from database import execute
from realtime import publish_dashboard_update, subscribe, unsubscribe

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/summary', methods=['GET'])
def summary():
    """Return dashboard summary statistics scoped to the current tenant."""
    verify_jwt_in_request(optional=True)
    tenant_id = get_jwt().get('tenant_id')

    if tenant_id:
        scans = execute('SELECT COUNT(*) as cnt FROM malware_scans WHERE tenant_id = %s', (tenant_id,), fetchone=True)
        vuln_reports = execute('SELECT COUNT(*) as cnt FROM vuln_reports WHERE tenant_id = %s', (tenant_id,), fetchone=True)
        job_scam_checks = execute('SELECT COUNT(*) as cnt FROM job_scam_checks WHERE tenant_id = %s', (tenant_id,), fetchone=True)
        malware = execute(
            'SELECT COUNT(*) as cnt FROM malware_scans WHERE tenant_id = %s AND status = %s',
            (tenant_id, 'MALICIOUS'),
            fetchone=True,
        )
        fraud_detected = execute(
            'SELECT COUNT(*) as cnt FROM malware_scans WHERE tenant_id = %s AND fraud_detected = TRUE',
            (tenant_id,),
            fetchone=True,
        )
    else:
        scans = execute('SELECT COUNT(*) as cnt FROM malware_scans', fetchone=True)
        vuln_reports = execute('SELECT COUNT(*) as cnt FROM vuln_reports', fetchone=True)
        job_scam_checks = execute('SELECT COUNT(*) as cnt FROM job_scam_checks', fetchone=True)
        malware = execute(
            'SELECT COUNT(*) as cnt FROM malware_scans WHERE status = %s',
            ('MALICIOUS',),
            fetchone=True,
        )
        fraud_detected = execute(
            'SELECT COUNT(*) as cnt FROM malware_scans WHERE fraud_detected = TRUE',
            fetchone=True,
        )

    total_activity = 0
    if scans and 'cnt' in scans:
        total_activity += scans['cnt']
    if vuln_reports and 'cnt' in vuln_reports:
        total_activity += vuln_reports['cnt']
    if job_scam_checks and 'cnt' in job_scam_checks:
        total_activity += job_scam_checks['cnt']

    return jsonify({
        'total_scans': total_activity,
        'total_activity': total_activity,
        'malware_detected': malware['cnt'] if malware and 'cnt' in malware else 0,
        'vulnerability_reports': vuln_reports['cnt'] if vuln_reports and 'cnt' in vuln_reports else 0,
        'job_scam_checks': job_scam_checks['cnt'] if job_scam_checks and 'cnt' in job_scam_checks else 0,
        'fraud_detected': fraud_detected['cnt'] if fraud_detected and 'cnt' in fraud_detected else 0,
    })


@stats_bp.route('/stream', methods=['GET'])
def stream():
    """Stream dashboard update signals as server-sent events."""

    def event_stream():
        queue = subscribe()
        try:
            yield 'event: ready\ndata: {"status":"connected"}\n\n'
            while True:
                try:
                    message = queue.get(timeout=25)
                    yield f'event: stats-updated\ndata: {json.dumps(message)}\n\n'
                except Empty:
                    yield ': keep-alive\n\n'
        finally:
            unsubscribe(queue)

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'text/event-stream',
        'X-Accel-Buffering': 'no',
    }
    return Response(stream_with_context(event_stream()), headers=headers)
