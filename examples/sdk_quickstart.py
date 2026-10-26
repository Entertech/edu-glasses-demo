"""Read device information through the independently installed EDU SDK."""

import argparse
from edu_host import AmbiguousGlassesError, EduClientError, EduSession


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bt', default='auto', help='Paired device address or auto')
    args = parser.parse_args()
    try:
        with EduSession(bt=args.bt) as glasses:
            print('Protocol:', glasses.hello_ack.proto_ver)
            print('Capabilities:', glasses.capabilities)
            print('Device:', glasses.info())
            if glasses.supports('SENSORS'):
                print('Sensors:', glasses.sensors())
    except (AmbiguousGlassesError, EduClientError, OSError, ValueError) as error:
        print('Failed:', error)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
