# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import egoisticlily_pb2 as egoisticlily__pb2


class EgoisticLilyServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Convert = channel.unary_unary(
        '/egoisticlily.EgoisticLilyService/Convert',
        request_serializer=egoisticlily__pb2.ConvertReq.SerializeToString,
        response_deserializer=egoisticlily__pb2.ConvertResp.FromString,
        )
    self.PartialConvert = channel.unary_unary(
        '/egoisticlily.EgoisticLilyService/PartialConvert',
        request_serializer=egoisticlily__pb2.PartialConvertReq.SerializeToString,
        response_deserializer=egoisticlily__pb2.PartialConvertResp.FromString,
        )


class EgoisticLilyServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Convert(self, request, context):
    """多分変換
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def PartialConvert(self, request, context):
    """多分部分変換
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_EgoisticLilyServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Convert': grpc.unary_unary_rpc_method_handler(
          servicer.Convert,
          request_deserializer=egoisticlily__pb2.ConvertReq.FromString,
          response_serializer=egoisticlily__pb2.ConvertResp.SerializeToString,
      ),
      'PartialConvert': grpc.unary_unary_rpc_method_handler(
          servicer.PartialConvert,
          request_deserializer=egoisticlily__pb2.PartialConvertReq.FromString,
          response_serializer=egoisticlily__pb2.PartialConvertResp.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'egoisticlily.EgoisticLilyService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
