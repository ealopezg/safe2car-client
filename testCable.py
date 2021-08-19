import subprocess


def checkLanCable():
    cmd = subprocess.run(['cat', '/sys/class/net/eth0/operstate'], stdout=subprocess.PIPE)
    if cmd.returncode == 0:
        return cmd.stdout.decode().strip() == 'up'
    else:
        return False

print(checkLanCable())