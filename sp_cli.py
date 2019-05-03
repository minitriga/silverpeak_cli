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

@main.command('get_reach_app')
@click.argument('ec')
@click.pass_obj
def get_reach_app(devices, ec):
    """Get the reachability status from the appliance"""
    for device in devices:
        api = device.set_up()
        result = api.get_reach_app(ec).data
        outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_reach_gms')
@click.argument('ec')
@click.pass_obj
def get_reach_gms(devices, ec):
    """Get the reachability status from the orchestrator"""
    for device in devices:
        api = device.set_up()
        result = api.get_reach_gms(ec).data
        outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_groups')
@click.pass_obj
def get_groups(devices):
    """Get all orchestrator groups"""
    for device in devices:
        api = device.set_up()
        result = api.get_groups().data
        outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_group')
@click.argument('id')
@click.pass_obj
def get_group(devices, id):
    """Get a sigle group from orchestrator"""
    for device in devices:
        api = device.set_up()
        result = api.get_group(id).data
        outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_group_root')
@click.pass_obj
def get_group_root(devices):
    """Get root group"""
    for device in devices:
        api = device.set_up()
        result = api.get_group_root().data
        outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_grnodes')
@click.pass_obj
def get_grnodes(devices):
    """Get appliance positions on a map for topology"""
    for device in devices:
        api = device.set_up()
        result = api.get_grnodes().data
        outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_discovered')
@click.pass_obj
def get_discovered(devices):
    """Returns all the discovered appliances"""
    for device in devices:
        api = device.set_up()
        result = api.get_discovered().data
        outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_approved')
@click.pass_obj
def get_approved(devices):
    """Returns all approved appliances"""
    for device in devices:
        api = device.set_up()
        result = api.get_approved().data
        outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_interfaces')
@click.argument('ec')
@click.option('--cached/--no-cached', default=True)
@click.pass_obj
def get_interfaces(devices, ec, cached):
    """Returns all approved appliances"""
    for device in devices:
        cached = str(cached).lower()
        api = device.set_up()
        result = api.get_interfaces(ec, cached).data
        outFormat(device.table, result)
        click.secho("Task Completed")

# @main.command('get_device_alarms')
# @click.argument('ec')
# @click.option('--view', help="all, active, closed", default="all", type=click.Choice(['all', 'active', 'closed']))
# @click.option('--severity', help="Filters alarms by severity (warning, minor, major, critical)", default='')
# @click.option('--order', help="Order by alarm severity (true, false)", type=click.Choice(['true', 'false']))
# @click.option('--max-alarms', help="How many alarms to show (default=5)", default=5)
# @click.pass_obj
# def get_device_alarms(devices, ec, view, severity, order, max_alarms):
#     """Returns all approved appliances"""
#     for device in devices:
#         api = device.set_up()
#         result = api.get_device_alarms(ec).data
#         print(result)
#         outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_alarms')
@click.option('--view', help="all, active, closed", default="all")
@click.option('--severity', help="Filters alarms by severity (warning, minor, major, critical)")
@click.pass_obj
def get_alarms(devices, view, severity):
    """Returns all approved appliances"""
    for device in devices:
        api = device.set_up()
        result = api.get_alarms(view, severity).data
        outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_alarm_summary')
@click.pass_obj
def get_alarm_summary(devices):
    """Returns all approved appliances"""
    for device in devices:
        api = device.set_up()
        result = api.get_alarm_summary().data
        outFormat(device.table, result)
        click.secho("Task Completed")

@main.command('get_alarm_summary_type')
@click.option('--alarm-type', help="Alarm Type (gms,appliance)", type=click.Choice(['gms', 'appliance']))
@click.pass_obj
def get_alarm_summary_type(devices, alarm_type):
    """Alarm Type (gms,appliance)"""
    for device in devices:
        api = device.set_up()
        result = api.get_alarm_summary_type(alarm_type).data
        outFormat(device.table, result)
        click.secho("Task Completed")