#!/usr/bin/env python3
# vim: set noexpandtab:

from aiohttp import web
from collections import namedtuple
from io import StringIO, BytesIO
import asyncio

Stat = namedtuple('Stat', ('name', 'type', 'description', 'handler'))

async def process_stat(stat):
	output = StringIO()
	output.write("# HELP {var} {desc}\n".format(var=stat.name, desc=stat.description))
	output.write("# TYPE {var} {type}\n".format(var=stat.name, type=stat.type))
	for val, labels in await stat.handler():
		var = stat.name
		if labels:
			var += "{" + ",".join(k + '="' + v + '"' for k, v in labels.items()) + "}"
		output.write("{var} {val}\n".format(var=var, val=val))
	return output.getvalue().encode()

async def metrics_handler(request):
	output = BytesIO()
	stat_coros = await asyncio.wait([process_stat(stat) for stat in stats], timeout=3)
	for stat_output in stat_coros[0]:  # only use complete, ignore others
		output.write(await stat_output)
	return web.Response(body=output.getvalue())


stats = []

app = web.Application()
app.router.add_route('GET', '/metrics', metrics_handler)

def serve(port=8745, host='127.0.0.1'):
	web.run_app(app, host=host, port=port)

def register_stat(name, type, description, handler):
	"""
	await handler() -> [value, {labels}]
	"""
	stats.append(Stat(name, type, description, handler))

def build_decorator_for(type):
	def decorator1(description):
		def decorator2(fn):
			register_stat(fn.__name__, type, description, fn)
			return fn
		return decorator2
	return decorator1

gauge = build_decorator_for('gauge')
counter = build_decorator_for('counter')
