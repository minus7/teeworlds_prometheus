#!/usr/bin/env python3
# vim: set noexpandtab:

import asyncio

class ClientProtocol:
	def __init__(self):
		self.transport = None
		self.recv_queue = asyncio.Queue()
		self.recvers = asyncio.Queue()
		self.connected = False

	def connection_made(self, transport):
		self.transport = transport
		self.connected = True

	def datagram_received(self, data, addr):
		try:
			self.recvers.get_nowait().set_result(data)
		except asyncio.QueueEmpty:
			self.recv_queue.put_nowait(data)

	def error_received(self, exc):
		self.kill()

	def connection_lost(self, exc):
		self.kill()

	def kill(self):
		self.connected = False
		try:
			while True:
				fut = self.recvers.get_nowait()
				fut.cancel()
		except asyncio.QueueEmpty:
			pass
	
	def recv(self):
		fut = asyncio.Future()
		if not self.connected:
			fut.cancel()
		else:
			try:
				fut.set_result(self.recv_queue.get_nowait())
			except asyncio.QueueEmpty:
				self.recvers.put_nowait(fut)
		return fut

class UdpConnection:
	def __init__(self, transport, protocol):
		self.transport = transport
		self.protocol = protocol

	def send(self, data):
		self.transport.sendto(data)

	async def recv(self):
		return await self.protocol.recv()

	def close(self):
		self.transport.close()


async def connect(host, port, loop=None):
	if not loop:
		loop = asyncio.get_event_loop()
	connect = loop.create_datagram_endpoint(
			ClientProtocol,
			remote_addr=(host, port))
	transport, protocol = await connect
	return UdpConnection(transport, protocol)
