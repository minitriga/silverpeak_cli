import click
from silverpeak import *
import json
import urllib3
import re
from prettytable import PrettyTable

class Device(object):
    def __init__(self, ip=None, port=None, username=None, password=None, table=None):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.table = table
    
    def set_up(self):
        return Silverpeak(user=self.username, user_pass=self.password, sp_server=self.ip, sp_port=self.port, disable_warnings=True)

@click.group()
# ip addresses or dns of devices
@click.option('--ip', help="ip or dns address of orchestrator")
# file of ip addresses or dns of devices
@click.option('--file', help="file ip addresses of the orchestators")
# option for custom port
@click.option('--port', default=443, help="device port, default = 443")
# option for output format table or json
@click.option('--table', is_flag=True, help="output in table format")
# prompts user for username/password of the orchestrator
@click.option('--username', help="orchestrator username", prompt=True, hide_input=False)
@click.option('--password', help="orchestrator password", prompt=True, hide_input=True)
@click.pass_context

def main(ctx, ip, file, port, username, password, table):
    """Gather Silver Peak Orchestrator Information using API's"""
    devices = []
    if ip:
        device = Device(ip, port, username, password, table)
        devices.append(device)
        click.secho("Working....")
    else:
        try:
            with open(file) as f:
                device_data = json.load(f)
        except(ValueError, IOError, OSError) as err:
            print("Could not read the 'devices' file:", err)

        for device_info in device_data.values():
            ip = device_info['IP']
            device = Device(device_info['IP'], port, username, password)
            devices.append(device)
            click.secho("Working....{}".format(ip))
    ctx.obj = devices

def keys_exists(element, *keys):
    '''
    Check if *keys (nested) exists in `element` (dict).
    '''
    if type(element) is not dict:
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True

def table(result):
    x = PrettyTable()
    headers = []
    num = 0
    if isinstance(result, list):
        for r in result:
            if num == 0:
                headers = r.keys()
                num = +1 
                x.field_names = headers
            x.add_row(r.values())
    else:
        x.field_names = result.keys()
        x.add_row(result.values())
    print(x)

def outFormat(device, result):
    if device:
        table(result)
    else:
        print(json.dumps(result, indent=1))


@main.command('get_appliances')
@click.pass_obj
def get_appliances(devices):
    """Gather All Appliance Information"""
    for device in devices:
        api = device.set_up()
        result = api.get_appliances().data
        outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_appliance')
@click.argument('ec')
@click.pass_obj
def get_appliance(devices, ec):
    """Gather EdgeConnect Information"""
    for device in devices:
        api = device.set_up()
        result = api.get_appliance(ec).data
        outFormat(device.table, result)
        click.secho("Task Completed")