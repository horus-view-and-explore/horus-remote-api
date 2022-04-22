import sys
from pprint import pprint
from time import sleep
from os.path import basename

from horus_remote_api.client import Client
from horus_remote_api.connection_socketio import SocketIOConnection


def main():
    try:
        url = sys.argv[1]
    except IndexError:
        program = basename(sys.argv[0])
        print(f"usage: {program} <url>", file=sys.stderr)
        print(f"    example: {program} http://192.168.5.135:3105", file=sys.stderr)
        sys.exit(1)

    running = True

    def event_callback(event):
        nonlocal running
        print(f"New Event[{event.Type}]: {event}")
        running = False

    conn = SocketIOConnection(url, event_callback)

    with Client(conn) as client:
        print(client.ping())

        result = client.get_running_state()
        print(result.GetRunningStateResponse.State)

        # pprint(client.rpc_get_cababilties())
        # pprint(client.list_pipeline_components())

        # Pass and handle a timeout.
        try:
            pprint(client.get_license_state(timeout=0.01))
        except TimeoutError:
            print("TimeoutErrors are for nerds")

        pprint(client.rpc_get("horus::xtn::control::rpc", ["get_pipeline"]))

        # result = client.rpc_set("horus::xtn::control::rpc", [
        #   "set_pipeline",
        #   "/home/root/.config/horus/horus_app_system_v2/user_data/bert.hrp"
        # ])

        # print(client.rpc_get_cababilties("Signal Generator"))

        pprint(client.rpc_get("Signal Generator", ["signal_gen_a", "signal_gen_f"]))

        # pprint(client.rpc_set("Signal Generator", ["signal_gen_f", 5]))

        # pprint(client.rpc_request("udpsink", ["port", 5000, "host", "127.0.0.1"]))

        # pprint(client.list_grabber_plugins())

        pprint(client.stop_pipeline())

        # Wait until we get a stop pipeline event.
        while running:
            sleep(1)


if __name__ == "__main__":
    main()
