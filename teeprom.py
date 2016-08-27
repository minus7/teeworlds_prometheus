#!/usr/bin/env python3
# vim: set noexpandtab:

import asyncio
import prom
import udpconn
from struct import unpack

async def query_master(server):
	print("running", server)
	conn = await udpconn.connect(server, 8300)
	conn.send(10*b'\xff' + b'cou2')
	resp = await conn.recv()
	assert resp[10:14] == b'siz2'
	count = unpack('!H', resp[14:16])[0]
	print("done", server)
	return (count, {'server': server})

@prom.gauge("Servers currently registered with Teeworlds master")
async def teeworlds_mastersrv_count():
	servers = ('master{}.teeworlds.com'.format(i) for i in range(1, 5))
	queries = [query_master(s) for s in servers]
	complete, pending = await asyncio.wait(queries, timeout=2)
	return [q.result() for q in complete if not q.exception()]

prom.serve()
