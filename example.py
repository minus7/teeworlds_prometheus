#!/usr/bin/env python3
# vim: set noexpandtab:

import asyncio
import prom

async def test():
	await asyncio.sleep(2)
	return [(123, {"label": "test"})]

@prom.counter("test number 2")
async def test2():
	await asyncio.sleep(2)
	return [(124, {"label": "test2"})]

prom.register_stat("teststat", "counter", "just some testing", test)
prom.serve()
