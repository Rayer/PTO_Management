import os
import server


def pid_lock(pid_file, main_logic):
    pid = str(os.getpid())
    if os.path.isfile(pid_file):
        with open(pid_file, 'r') as file:
            old_pid = file.read(6)
        print('Service is already running at {0}, deleting this file and restart'.format(old_pid))
        try:
            os.kill(int(old_pid), 9)
        except OSError as e:
            print('Error deleting PID {0} : {1}'.format(old_pid, e.strerror))
        finally:
            os.remove(pid_file)

    with open(pid_file, 'w') as file:
        print('Start application at PID {0}'.format(pid))
        file.write(pid)

    try:
        main_logic()
    finally:
        os.remove(pid_file)


if __name__ == '__main__':
    pid_lock('/tmp/ptomanagement.pid', server.main)
