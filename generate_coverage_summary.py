import json
import xml.etree.ElementTree as ET
import os
import sys
from datetime import datetime, timezone

SERVICES = ['auth', 'busqueda', 'common', 'hoteles', 'inventario',
            'notificaciones', 'pagos', 'reservas', 'usuarios']

THRESHOLD = 50

def parse_coverage_xml(path):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        line_rate = float(root.attrib.get('line-rate', 0))
        branch_rate = float(root.attrib.get('branch-rate', 0))
        lines_valid = int(root.attrib.get('lines-valid', 0))
        lines_covered = int(root.attrib.get('lines-covered', 0))
        branches_valid = int(root.attrib.get('branches-valid', 0))
        branches_covered = int(root.attrib.get('branches-covered', 0))

        # Per-file breakdown
        files = []
        for pkg in root.iter('package'):
            for cls in pkg.iter('class'):
                filename = cls.attrib.get('filename', '')
                file_line_rate = float(cls.attrib.get('line-rate', 0))
                file_lines = sum(1 for _ in cls.iter('line'))
                files.append({
                    'name': os.path.basename(filename),
                    'path': filename,
                    'coverage': round(file_line_rate * 100, 1),
                    'lines': file_lines
                })

        return {
            'line_coverage': round(line_rate * 100, 1),
            'branch_coverage': round(branch_rate * 100, 1),
            'lines_covered': lines_covered,
            'lines_valid': lines_valid,
            'branches_covered': branches_covered,
            'branches_valid': branches_valid,
            'passes_threshold': line_rate * 100 >= THRESHOLD,
            'files': sorted(files, key=lambda f: f['coverage'])
        }
    except Exception as e:
        return None

def main():
    coverage_dir = sys.argv[1] if len(sys.argv) > 1 else './coverage-reports'
    summary = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'threshold': THRESHOLD,
        'services': {}
    }

    for service in SERVICES:
        xml_path = os.path.join(coverage_dir, service, 'coverage.xml')
        if os.path.exists(xml_path):
            data = parse_coverage_xml(xml_path)
            if data:
                summary['services'][service] = data
                status = 'PASS' if data['passes_threshold'] else 'FAIL'
                print(f"  {status}  {service:<20} {data['line_coverage']:>5.1f}%  ({data['lines_covered']}/{data['lines_valid']} lines)")
            else:
                print(f"  SKIP  {service:<20} could not parse XML")
        else:
            print(f"  MISS  {service:<20} no coverage.xml found at {xml_path}")

    # Overall stats
    services_data = list(summary['services'].values())
    if services_data:
        total_lines = sum(s['lines_valid'] for s in services_data)
        total_covered = sum(s['lines_covered'] for s in services_data)
        overall = round(total_covered / total_lines * 100, 1) if total_lines > 0 else 0
        summary['overall'] = {
            'line_coverage': overall,
            'lines_covered': total_covered,
            'lines_valid': total_lines,
            'passes_threshold': overall >= THRESHOLD,
            'services_passing': sum(1 for s in services_data if s['passes_threshold']),
            'services_total': len(services_data)
        }
        print(f"\n  Overall: {overall}% ({total_covered}/{total_lines} lines)")
        print(f"  Services passing: {summary['overall']['services_passing']}/{len(services_data)}")

    out_path = 'coverage-summary.json'
    with open(out_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nWritten: {out_path}")

if __name__ == '__main__':
    main()