import sys
import logging

from pysimplesoap.client import SoapClient, SimpleXMLElement, SoapFault, REVERSE_TYPE_MAP
from pysimplesoap.server import SoapDispatcher, unicode, Date, Decimal
from os import environ as os_env
import datetime
import re

# logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("=============================================")

# run_as = "run_as"
original_url = "http://61.14.208.38/KO856_Default/Services/MDM/PB3C104FL.asmx"

def handler(event, context):

  # if not "queryStringParameters" in event or event["queryStringParameters"] is None:
  #   return {
  #       'statusCode': 200,
  #       'headers': {
  #           'Content-Type': 'application/xml'
  #           # 'Content-Disposition': 'attachment; filename="dev.wsdl"'
  #       },
  #       'body': "<responseFault>" + "%s is required. Possible values: client, server." % run_as + "</responseFault>"
  #   }
  # else:
  #   if not run_as in event["queryStringParameters"] is None:
  #       return {
  #           'statusCode': 200,
  #           'headers': {
  #               'Content-Type': 'application/xml'
  #               # 'Content-Disposition': 'attachment; filename="dev.wsdl"'
  #           },
  #           'body': "<responseFault>" + "%s is required. Possible values: client, server." % run_as + "</responseFault>"
  #       }
  logger.info("Getting: event keys")
  for e in event.keys():
    logger.info(e)
    logger.info(str(event[e]))
    logger.info(event[e])

  if event["requestContext"]["httpMethod"] == "GET":
    return handler_server(event, context)

  if event["requestContext"]["httpMethod"] == "POST":
    return handler_client(event, context)

def create_client_by_url(url):
  """
    Create Client Object by URL

    arguments:
      url: string
    return:
      client: SoapClient
  """
  client = None
  try:
      logger.info("TRYING: Create Client Object by URL")

      # create the webservice client
      client = SoapClient(
          location = url, #location, use wsdl,
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

  logger.info("SUCCESS: Creation Client Object succeeded")

  return client

def prepare_parameters(event):
    params = {}

    host = os_env["soap_host"] if "soap_host" in os_env else event["soap_host"]
    internal_IP = os_env["internal_IP"] if "internal_IP" in os_env else event["internal_IP"]

    # call the remote method
    params["pvStrGlobalCollection"] = [
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

    params["I1_select_char"] = "Q"
    params["I2_item_cd"] = "1624-A2C018"

    return params

def get_client_result(event):

  client = create_client_by_url(original_url)

  if client is None:
    sys.exit()

  result = ""

  try:
      logger.info("Calling remote method")
      results = client.cBLkUpItem_B_LOOK_UP_ITEM_SVR(**prepare_parameters(event))
  except SoapFault:
    for f in SoapFault.children():
      logger.error(f.get_name())
    sys.exit()
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
  return {client, results}

def handler_client(event, context):
    """
    """
    client, results = get_client_result(event)

    result_xml = results.as_xml("resp", True)

    return {
        'statusCode': 200,
        'headers': { 'Content-Type': 'application/xml' },
        'body': str(result_xml,'utf8')
    }

def handler_server(event, context):

    if "deployed" not in os_env.keys():
      with open("response.xml", "r") as res:
        result_xml = res.read()

      try:
        results = SimpleXMLElement(result_xml)
      except:
        logger.error("ERROR: Unexpected error: %s" % sys.exc_info()[0])
      logger.info("results")
      logger.info(type(results))
    else:
      client, results = get_client_result(event)

    # result_xml = results.as_xml("resp", True)
    returns_types = results_to_field_types(results)
    # args_types = results_to_field_types(prepare_parameters(event))

    dispatcher = SoapDispatcher(
        name="PB3C104FL",
        location="https://e77je9smo5.execute-api.ap-northeast-2.amazonaws.com/dev/",
        action='https://e77je9smo5.execute-api.ap-northeast-2.amazonaws.com/dev/',  # SOAPAction
        namespace="http://www.unierp.com/", prefix="ns0",
        documentation='Example soap service transition from POP to ByDesign',
        trace=True, debug=False,
        ns=True)

    def adder(p, c, dt=None):
        """Add several values"""
        dt = dt + datetime.timedelta(365)
        return {'ab': p['a'] + p['b'], 'dd': c[0]['d'] + c[1]['d'], 'dt': dt}

    # dispatcher.register_function(
    #     'Adder', adder,
    #     returns={'AddResult': {'ab': int, 'dd': unicode, 'dt': datetime.date}},
    #     args={'p': {'a': int, 'b': int}, 'dt': Date, 'c': [{'d': Decimal}]}
    # )

    # returns_types = {'AA': int}
    args_types = {'BB': int}
    dispatcher.register_function(
        'cBLkUpItem_B_LOOK_UP_ITEM_SVR', adder,
        # returns={'AddResult': {'ab': int, 'dd': unicode, 'dt': datetime.date}},
        returns=returns_types,
        args=args_types
    )

    # for method, doc in dispatcher.list_methods():
    #     request, response, doc = dispatcher.help(method)

    wsdl = dispatcher.wsdl()


    return wsdl

    # return {
    #     'statusCode': 200,
    #     'headers': {
    #         'Content-Type': 'application/xml'
    #         # 'Content-Disposition': 'attachment; filename="dev.wsdl"'
    #     },
    #     'body': str(wsdl,'utf8')
    # }

def results_to_field_types(results):
  returns_types = {}

  def parse_attribute(node, returned_scheme = None):
    if type(node).__name__ == "SoapClient":
      logger.error("Error: node type should not be SoapClient")
      sys.exit()

    returns_sub = {}

    if node.children() is None:
      returns_sub = returned_scheme[node.get_name()]["py_type"]
    else:
      for tag in node.children():

        if tag.get_name() == "xs:schema":
          returned_scheme = schema_to_dict(tag)
          # logger.info(returned_scheme)
          continue

        if isinstance(tag, SimpleXMLElement):
          # logger.info(type(v).__name__)
          # returns[tag.get_name()] = {}
          is_array = False

          if returned_scheme is not None:
            if tag.get_name() in returned_scheme:
              if "is_array" in returned_scheme[tag.get_name()]:
                is_array = returned_scheme[tag.get_name()]["is_array"]

          if is_array == True:
            returns_sub[tag.get_name()] = [parse_attribute(tag, returned_scheme)]
          else:
            returns_sub[tag.get_name()] = parse_attribute(tag, returned_scheme)
        else:
          logger.info("Unexcepted tag: %s, type: %s" % tag.get_name(), type(tag).__name__ )

    return returns_sub

  returns_types = parse_attribute(results)

  return returns_types

def schema_to_dict(schema, parent_name = None):
  schema_dict = {}
  local_parent_name = None

  if schema.children() is None: # element in last depth, it could be wanted field
    if schema.get_name() == "xs:element":
      new_item = {
          "soap_type": re.sub(".+\:","",schema["type"])
      }
      new_item.update({
          "py_type": REVERSE_TYPE_MAP.get(new_item["soap_type"])
      })
      schema_dict[schema["name"]] = new_item
  else:

    if schema.get_name() == "xs:element": # which has children, it could be Array
      new_item = {}
      schema_dict[schema["name"]] = new_item

      local_parent_name = schema["name"]
    elif schema.get_name() == "xs:complexType":
      if parent_name is not None:
        schema_dict[parent_name] = {
            "is_dict": True,
            "is_array": False
        }
        local_parent_name = parent_name
    elif schema.get_name() == "xs:choice":
      if parent_name is not None:
        schema_dict[parent_name] = {
            "is_dict": False,
            "is_array": True
        }

    for child in schema.children():
      schema_dict.update(schema_to_dict(child, local_parent_name))

  return schema_dict
