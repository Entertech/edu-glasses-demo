"""Observe device events without mapping native buttons to duplicate commands."""

import argparse
import math
from edu_host import AmbiguousGlassesError, EduClientError, EduSession


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bt', default='auto', help='Paired device address or auto')
    parser.add_argument('--seconds', type=float, default=30)
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds <= 0:
        parser.error('--seconds must be finite and positive')
    try:
        with EduSession(bt=args.bt) as glasses:
            glasses.add_event_listener(print)
            if glasses.supports('DEVICE_CAPTURE_STATE'):
                print('Capture state:', glasses.get_capture_state())
            glasses.wait(args.seconds)
    except KeyboardInterrupt:
        return 0
    except (AmbiguousGlassesError, EduClientError, OSError, ValueError) as error:
        print('Failed:', error)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
