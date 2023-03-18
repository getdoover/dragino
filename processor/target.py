#!/usr/bin/python3
from operator import truediv
import os, sys, time, json

from regex import P


## This is the definition for a tiny lambda function
## Which is run in response to messages processed in Doover's 'Channels' system

## In the doover_config.json file we have defined some of these subscriptions
## These are under 'processor_deployments' > 'tasks'


## You can import the pydoover module to interact with Doover based on decisions made in this function
## Just add the current directory to the path first
sys.path.append(os.path.dirname(__file__))
import pydoover as pd


class target:

    def __init__(self, *args, **kwargs):

        self.kwargs = kwargs
        ### kwarg
        #     'agent_id' : The Doover agent id invoking the task e.g. '9843b273-6580-4520-bdb0-0afb7bfec049'
        #     'access_token' : A temporary token that can be used to interact with the Doover API .e.g 'ABCDEFGHJKLMNOPQRSTUVWXYZ123456890',
        #     'api_endpoint' : The API endpoint to interact with e.g. "https://my.doover.com",
        #     'package_config' : A dictionary object with configuration for the task - as stored in the task channel in Doover,
        #     'msg_obj' : A dictionary object of the msg that has invoked this task,
        #     'task_id' : The identifier string of the task channel used to run this processor,
        #     'log_channel' : The identifier string of the channel to publish any logs to


    ## This function is invoked after the singleton instance is created
    def execute(self):

        start_time = time.time()

        self.create_doover_client()

        self.add_to_log( "kwargs = " + str(self.kwargs) )
        self.add_to_log( str( start_time ) )

        try:
            
            ## Do any processing you would like to do here
            message_type = None
            if 'message_type' in self.kwargs['package_config'] and 'message_type' is not None:
                message_type = self.kwargs['package_config']['message_type']

            if message_type == "DEPLOY":
                self.deploy()

            if message_type == "DOWNLINK":
                self.downlink()

            if message_type == "UPLINK":
                self.uplink()

        except Exception as e:
            self.add_to_log("ERROR attempting to process message - " + str(e))

        self.complete_log()



    def deploy(self):
        ## Run any deployment code here
        
        ## Get the deployment channel
        ui_state_channel = self.cli.get_channel(
            channel_name="ui_state",
            agent_id=self.kwargs['agent_id'] )

        ui_obj = {
            "state" : {
                "type" : "uiContainer",
                "displayString" : "",
                "children" : {
                    "temp": {
                        "type": "uiVariable",
                        "name": "temp",
                        "displayString": "Temperature (C)",
                        "varType": "float",
                        "decPrecision": 1,
                        "form": "radialGauge",
                        "ranges": [
                            {
                                "label" : "Freezing",
                                "min" : -10,
                                "max" : 0,
                                "colour" : "yellow",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Cold",
                                "min" : 0,
                                "max" : 15,
                                "colour" : "blue",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Warm",
                                "min" : 15,
                                "max" : 30,
                                "colour" : "yellow",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Hot",
                                "min" : 30,
                                "max" : 45,
                                "colour" : "red",
                                "showOnGraph" : True
                            }
                        ]
                    },
                    "humidity": {
                        "type": "uiVariable",
                        "name": "humidity",
                        "displayString": "Humidity (%)",
                        "varType": "float",
                        "decPrecision": 1,
                        "form": "radialGauge",
                        "ranges": [
                            {
                                "label" : "Very Dry",
                                "min" : 0,
                                "max" : 30,
                                "colour" : "yellow",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Normal",
                                "min" : 30,
                                "max" : 60,
                                "colour" : "green",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Wet",
                                "min" : 60,
                                "max" : 100,
                                "colour" : "blue",
                                "showOnGraph" : True
                            }
                        ]
                    },
                    "rawBattery": {
                                "type": "uiVariable",
                                "name": "rawBattery",
                                "displayString": "Battery (V)",
                                "varType": "float",
                                "decPrecision": 2
                    },
                    "signalStrength": {
                        "type": "uiVariable",
                        "name": "signalStrength",
                        "displayString": "Signal Strength (%)",
                        "varType": "float",
                        "decPrecision": 0,
                        "ranges": [
                            {
                                "label" : "Low",
                                "min" : 0,
                                "max" : 30,
                                "colour" : "yellow",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Ok",
                                "min" : 30,
                                "max" : 60,
                                "colour" : "blue",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Strong",
                                "min" : 60,
                                "max" : 100,
                                "colour" : "green",
                                "showOnGraph" : True
                            }
                        ]
                    },
                    "details_submodule": {
                        "type": "uiSubmodule",
                        "name": "details_submodule",
                        "displayString": "Details",
                        "children": {
                            "lastRSSI": {
                                "type": "uiVariable",
                                "name": "lastRSSI",
                                "displayString": "Last RSSI",
                                "varType": "float"
                            },
                            "lastSNR": {
                                "type": "uiVariable",
                                "name": "lastSNR",
                                "displayString": "Last SNR",
                                "varType": "float"
                            },
                            "lastUsedGateway": {
                                "type": "uiVariable",
                                "name": "lastUsedGateway",
                                "displayString": "Lora Gateway",
                                "varType": "text"
                            }
                        }
                    },
                    "node_connection_info": {
                        "type": "uiConnectionInfo",
                        "name": "node_connection_info",
                        "connectionType": "periodic",
                        "connectionPeriod": 600,
                        "nextConnection": 600
                    }
                }
            }
        }

        ui_state_channel.publish(
            msg_str=json.dumps(ui_obj)
        )


    def downlink(self):
        ## Run any downlink processing code here
        pass

    def uplink(self):
        
        ## Get the deployment channel
        ui_state_channel = self.cli.get_channel(
            channel_name="ui_state",
            agent_id=self.kwargs['agent_id']
        )
        
        self.update_reported_signal_strengths(ui_state_channel)


    def update_reported_signal_strengths(self, state_channel):

        msg_id = channel_id = payload = None
        if 'msg_obj' in self.kwargs and self.kwargs['msg_obj'] is not None:
            msg_id = self.kwargs['msg_obj']['message']
            channel_id = self.kwargs['msg_obj']['channel']
            payload = self.kwargs['msg_obj']['payload']

        if not msg_id:
            self.add_to_log( "No trigger message passed - skipping processing" )
        else:
            
            # trigger_msg = pd.message_log(
            #     api_client=self.cli.api_client,
            #     message_id=msg_id,
            #     channel_id=channel_id,
            # )
            # trigger_msg.update()

            # payload = json.loads( trigger_msg.get_payload() )

            rssi = snr = gateway_id = None
            try:
                rssi = payload['uplink_message']['rx_metadata'][0]['rssi']
                snr = payload['uplink_message']['rx_metadata'][0]['snr']
                gateway_id = payload['uplink_message']['rx_metadata'][0]['gateway_ids']['gateway_id']
            except Exception as e:
                self.add_to_log("Could not extract rssi and snr data")
                pass

            if rssi and snr and gateway_id:
                
                min_rssi = -130
                max_rssi = -50
                signal_strength_percent = int(((rssi - max_rssi) / (max_rssi - min_rssi) + 1) * 100)
                signal_strength_percent = max(signal_strength_percent, 0)
                signal_strength_percent = min(signal_strength_percent, 100)

                msg_obj = {
                    "state" : {
                        "children" : {
                            "signalStrength" : {
                                "currentValue" : signal_strength_percent
                            },
                            "details_submodule" : {
                                "children" : {
                                    "lastRSSI" : {
                                        "currentValue" : rssi
                                    },
                                    "lastSNR" : {
                                        "currentValue" : snr
                                    },
                                    "lastUsedGateway" : {
                                        "currentValue" : gateway_id
                                    }
                                }
                            }
                        }
                    }
                }
                state_channel.publish(
                    msg_str=json.dumps(msg_obj),
                    save_log=False
                )


    def create_doover_client(self):
        self.cli = pd.doover_iface(
            agent_id=self.kwargs['agent_id'],
            access_token=self.kwargs['access_token'],
            endpoint=self.kwargs['api_endpoint'],
        )

    def add_to_log(self, msg):
        if not hasattr(self, '_log'):
            self._log = ""
        self._log = self._log + str(msg) + "\n"

    def complete_log(self):
        if hasattr(self, '_log') and self.log is not None:
            log_channel = self.cli.get_channel( channel_id=self.kwargs['log_channel'] )
            log_channel.publish(
                msg_str=self._log
            )