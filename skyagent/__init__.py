import argparse
import six
import txaio
import subprocess
import os

from twisted.internet import reactor
from twisted.internet.error import ReactorNotRunning
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.types import SubscribeOptions, RegisterOptions

class Agent:
    def __init__(self):
        self.skyid = os.environ.get('SKY_ID')
    
    def get_config():
            config = str(subprocess.check_output(['uci', 'show']))
            return config
    def get_chilli():
            clients = str(subprocess.check_output(['sky_env', 'chilli_clients']))
            return clients 

class ClientSession(ApplicationSession):
    log = txaio.make_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output.')
    parser.add_argument('--url', dest='url', type=six.text_type, default=u'ws://ws.skywifi.space:8080', help='The router URL (default: "ws://ws.skywifi.pro:8080/ws").')
    parser.add_argument('--realm', dest='realm', type=six.text_type, default=u'sky', help='The realm to join (default: "sky").')
    parser.add_argument('--skyId', dest='skyId', type=six.text_type, default=u'', help='Sky ID')
    args = parser.parse_args()

    def onConnect(self):
        self.log.info("Client connected")
        self.join(self.config.realm, [u'anonymous'])


    def onLeave(self, details):
        self.log.info("Router session closed ({details})", details=details)
        self.disconnect()

    def onDisconnect(self):
        self.log.info("Router connection closed")
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    @inlineCallbacks
    def onJoin(self, details):
        skyid=self.args.skyId
        topic=str("sky.devices.") + str(skyid)
        self.log.info("Client session joined {details}", details=details)
        self.log.info("Topic: {topic}", topic=topic)

        def cmd_agent_update():
            os.execl("/etc/sky/agent/agent","");

        def cmd_get_config():
            config = {
                "network" : str(subprocess.check_output(['ls', '-l'])),
                "memory"  : str(subprocess.check_output(['ls', '-l']))
            }
            return str(config)

        def dev_internal(message, details):
            self.log.info("Message {message}", message=message)

        def dev_public(message, details):
            self.log.info("Message {message}", message=message)
            cmd_agent_update()

        yield self.subscribe(dev_internal, u"{topic}", options=SubscribeOptions(details_arg='details'))
        self.log.info("subscribed to topic '{topic}'", topic=topic)

        yield self.subscribe(dev_public, u"sky.devices", options=SubscribeOptions(details_arg='details'))
        self.log.info("subscribed to topic sky.devices")

        self.publish(u"sky.devices", {"skyId":str(skyid), "action":"up", "config": Agent.get_config() })
        self.publish(u"sky.devices", {"skyId":str(skyid), "action":"chilli_state", "clients": Agent.get_chilli() })




def start_session():
    agent=Agent()
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest='url', type=six.text_type, default=u'ws://ws.skywifi.space:8080', help='The router URL (default: "ws://ws.skywifi.pro:8080/ws").')
    parser.add_argument('--realm', dest='realm', type=six.text_type, default=u'sky', help='The realm to join (default: "sky").')
    args = parser.parse_args()

    runner = ApplicationRunner(url=args.url, realm=args.realm)
    runner.run(ClientSession)
