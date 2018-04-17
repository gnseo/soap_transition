import sys
import logging

from pysimplesoap.client import SoapClient, SimpleXMLElement
from pysimplesoap.server import SoapDispatcher, unicode, Date, Decimal
from os import environ as os_env
import datetime

# logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("=============================================")
try:
    logger.info("TRYING: something")

    # create the webservice client
    client = SoapClient(
        location = "http://61.14.208.38/KO856_Default/Services/MDM/PB3C104FL.asmx", #location, use wsdl,
        cache = None,
        #proxy = parse_proxy(proxy),
        #cacert = cacert,
        timeout = 20,
        ns = None,
        # TODO: find a better method to not include ns prefix in children:
        #   (wsdl parse should detect qualification instead of server dialect)
        # soap_server = "jetty",
        namespace = "http://www.unierp.com/",
        # soap_ns = "soapenv",
        trace = None
    )
except:
    logger.error("ERROR: Unexpected error: %s" % sys.exc_info()[0])
    sys.exit()

logger.info("SUCCESS: Connection to RDS mysql instance succeeded")

def handler_client(event, context):
    """
    """
    host = os_env["soap_host"] if "soap_host" in os_env else event["soap_host"]
    internal_IP = os_env["internal_IP"] if "internal_IP" in os_env else event["internal_IP"]

    # call the remote method
    pvStrGlobalCollection = [
    {"string": "SENERP"},
    {"string": host},
    {"string": "2"},
    {"string": host},
    {"string": "KO856"},
    {"string": "KRW"},
    {"string": "SENERP"},
    {"string": internal_IP},
    {"string": "a"},
    {"string": "b"},
    {"string": "KO"},
    {"string": "324000000000"},
    {"string": "d"},
    {"string": "e"},
    {"string": "yyyy-MM-dd"},
    {"string": "-"},
    {"string": "1900-01-01"},
    {"string": "f"},
    {"string": "unierp"},
    {"string": "g"},
    {"string": "h"},
    {"string": "h"},
    {"string": "'"},
    {"string": "3600"},
    {"string": "U"},
    {"string": "k"},
    {"string": "l"},
    {"string": "DD"},
    {"string": "V27AdminDB"},
    {"string": "20090207"},
    {"string": "XIMES003_KO_TEST"},
    {"string": "KO856_Default"},
    {"string": "F"},
    {"string": "3600"},
    {"string": "ko-KR"},
    {"string": "en-US"},
    {"string": "KO856"}
    ]

    I1_select_char = "Q"
    I2_item_cd = "1624-A2C018"

    result = ""

    try:
        logger.info("Calling remote method")
        results = client.cBLkUpItem_B_LOOK_UP_ITEM_SVR(pvStrGlobalCollection = pvStrGlobalCollection, I1_select_char = I1_select_char, I2_item_cd = I2_item_cd)
    except:
        pass
        raise
    else:
      # result = type(results) is SimpleXMLElement
      result = results.as_xml("resp", True)

      # for node in results.cBLkUpItem_B_LOOK_UP_ITEM_SVRResult(tag = "diffgr:diffgram", ns = True).children():
      #   logger.info("node name:" + node.get_name())
      # result = True if str(results.E5_B_ITEM.item_group_cd) == str(results.E4_B_ITEM_GROUP.item_group_cd) else False
      # result = str(results.E5_B_ITEM.item_group_cd) + str(results.E4_B_ITEM_GROUP.item_group_cd)

    finally:
        if "deployed" not in os_env.keys():
          # save sent and received messages for debugging:
          if type(client.xml_request) is bytes:
            open("request.xml", "w").write(str(client.xml_request,'utf8'))
            open("response.xml", "w").write(str(client.xml_response,'utf8'))
          else:
            open("request.xml", "w").write(client.xml_request)
            open("response.xml", "w").write(client.xml_response)

    return {
        'statusCode': 200,
        'headers': { 'Content-Type': 'application/xml' },
        'body': str(result,'utf8')
    }
def handler(event, context):

    dispatcher = SoapDispatcher(
        name="PySimpleSoapSample",
        location="http://localhost:8008/",
        action='http://localhost:8008/',  # SOAPAction
        namespace="http://example.com/pysimplesoapsamle/", prefix="ns0",
        documentation='Example soap service using PySimpleSoap',
        trace=True, debug=False,
        ns=True)

    def adder(p, c, dt=None):
        """Add several values"""
        dt = dt + datetime.timedelta(365)
        return {'ab': p['a'] + p['b'], 'dd': c[0]['d'] + c[1]['d'], 'dt': dt}

    dispatcher.register_function(
        'Adder', adder,
        returns={'AddResult': {'ab': int, 'dd': unicode, 'dt': datetime.date}},
        args={'p': {'a': int, 'b': int}, 'dt': Date, 'c': [{'d': Decimal}]}
    )

    for method, doc in dispatcher.list_methods():
        request, response, doc = dispatcher.help(method)

    wsdl = dispatcher.wsdl()


    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/xml'
            # 'Content-Disposition': 'attachment; filename="dev.wsdl"'
        },
        'body': str(wsdl,'utf8')
    }
