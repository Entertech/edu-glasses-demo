"""Read device information through the independently installed Looktech Glasses SDK."""

import argparse
from looktech_glasses_sdk import AmbiguousGlassesError, GlassesClientError, GlassesSession


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bt', default='auto', help='Paired device address or auto')
    args = parser.parse_args()
    try:
        with GlassesSession(bt=args.bt) as glasses:
            print('Protocol:', glasses.hello_ack.proto_ver)
            print('Capabilities:', glasses.capabilities)
            print('Device:', glasses.info())
            if glasses.supports('SENSORS'):
                print('Sensors:', glasses.sensors())
    except (AmbiguousGlassesError, GlassesClientError, OSError, ValueError) as error:
        print('Failed:', error)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
