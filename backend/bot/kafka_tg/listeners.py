import threading

def listener_factory(receiver):
    threading.get_ident()
    receiver = receiver()
    receiver.start_listening()

