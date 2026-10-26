"""List indexed media; download only explicitly selected IDs, retaining originals."""

import argparse
import json
from pathlib import Path
from edu_host import AmbiguousGlassesError, EduClientError, EduSession, WifiSecurity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bt', default='auto', help='Paired device address or auto')
    parser.add_argument('--wifi-config', required=True, type=Path)
    parser.add_argument('--media-id', action='append', type=int, default=[])
    parser.add_argument('--output', default='captures/exports', type=Path)
    args = parser.parse_args()
    if any(media_id <= 0 for media_id in args.media_id):
        parser.error('--media-id must be positive')
    try:
        credentials = json.loads(args.wifi_config.read_text(encoding='utf-8'))
        if not isinstance(credentials, dict):
            raise ValueError('WiFi config must be a JSON object')
        ssid = credentials.get('ssid')
        password = credentials.get('password', '')
        security = credentials.get('security', 'WPA2')
        if not isinstance(ssid, str) or not isinstance(password, str) or not isinstance(security, str):
            raise ValueError('ssid, password and security must be strings')
        try:
            security = WifiSecurity[security.upper()]
        except KeyError:
            raise ValueError('Unknown WiFi security') from None
        with EduSession(bt=args.bt) as glasses:
            print('Media capabilities:', glasses.media_capabilities())
            with glasses.media_import(ssid, password, security) as media:
                items = {item.media_id: item for item in media.list()}
                for item in items.values():
                    print(item.media_id, item.kind, item.file.name, item.file.size)
                missing = set(args.media_id) - items.keys()
                if missing:
                    raise ValueError('Selected IDs are absent from this catalog: %s' % sorted(missing))
                complete = True
                for media_id in dict.fromkeys(args.media_id):
                    result = media.download(items[media_id], args.output)
                    print('Downloaded:', media_id, result.files)
                    print('main_success:', result.main_success, 'complete:', result.complete)
                    print('Errors:', result.errors)
                    complete = complete and result.main_success and result.complete
                return 0 if complete else 1
    except (AmbiguousGlassesError, EduClientError, OSError, ValueError) as error:
        print('Failed:', error)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
