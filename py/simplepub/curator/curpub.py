#!/usr/bin/env python3

# new_server.py
# tinySSB simplepub websocket server

import asyncio
import hashlib
import json
import os
import signal
import sys
import time
import traceback
import websockets
import platform

WS_PORT = 8080

import simplepub.node
import simplepub.ble

# ---------------------------------------------------------------------------

start_time = None

i_pkt_cnt = 0
o_pkt_cnt = 0

def nowstr():
    global start_time
    t = time.time()
    if start_time == None:
        start_time = t
    t -= start_time
    return f"{t:.03f}"

async def launch_adv(sock, get_adv_fct, args):
    global o_pkt_cnt
    while True:
        pkts, tout = get_adv_fct()
        for p in pkts:
            o_pkt_cnt += 1
            if args.v:
                print(f"{sock.nm}> {nowstr()} o={o_pkt_cnt:<4} {len(p):3}B 0x{p[:32].hex()}..")
            await sock.send(p)
        await asyncio.sleep(tout)
        
async def onConnect(sock, node, args):
    global i_pkt_cnt, o_pkt_cnt
    if args.v:
        print(f"-- <{sock.nm}> connection up")
    tasks = [ asyncio.create_task(launch_adv(sock,fct,args)) for fct in
              [ lambda: node.get_entry_adv(),
                lambda: node.get_chain_adv(),
                lambda: node.get_GOset_adv() ] ]

    pkt_cnt = 0
    while True:
        try:
            pkt = await sock.recv()
            i_pkt_cnt += 1
            if args.v:
                print(f"<{sock.nm} {nowstr()} i={i_pkt_cnt:<4} {len(pkt):3}B 0x{pkt[:20].hex()}.. h={hashlib.sha256(pkt).digest()[:10].hex()}..")
            for p in node.rx(pkt):
                o_pkt_cnt += 1
                if args.v:
                    print(f"{sock.nm}> {nowstr()} o={o_pkt_cnt:<4} {len(p):3}B 0x{p[:32].hex()}..")
                await sock.send(p)
            await asyncio.sleep(0)
        except (websockets.exceptions.ConnectionClosedOK,
                websockets.exceptions.ConnectionClosedError,
                simplepub.ble.ConnectionGone):
            break
        except Exception as e:
            traceback.print_exc()
            break
    for t in tasks:
        try:    t.cancel()
        except: pass
    if args.v:
        print(f"-- <{sock.nm}> connection down")

async def receiveCurator(data, curatorFidBytes, url):
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    if platform.system() != 'Windows':
        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    if url is None:
        url = "ws://127.0.0.1:8081"
    
    role = 'in' #developer will always be the initiator

    node = simplepub.node.PubNode(data, role, gosetKeys=curatorFidBytes, type='user')

    #initialize args
    args = type('', (), {})()
    args.v = True
    args.uri_or_port = url
    args.ble = False
    args.data = data
    args.role = role


    try:
        if type(url) == int:
            if simplepub.ble.is_installed:
                asyncio.create_task(
                    simplepub.ble.serve(lambda s: onConnect(s, node, args)))
            else:
                print(f"BLE interface not supported")
            print(f"Starting websocket responder on port {url}")
            async with websockets.serve(lambda s: onConnect(s, node, args),
                                        "0.0.0.0", url):
                await stop
        else:
            print(f"Connecting to {url}")
            async with websockets.connect(url) as wsock:
                wsock.nm = 'w'
                await onConnect(wsock, node, args)
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass


async def mainOut(data, url):
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    if platform.system() != 'Windows':
        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    if url is None:
        url = "ws://127.0.0.1:8080"
    
    role = 'out' #developer will always be the initiator

    node = simplepub.node.PubNode(data, role)

    #initialize args
    args = type('', (), {})()
    args.v = True
    args.uri_or_port = url
    args.ble = False
    args.data = data
    args.role = role


    try:
        if type(url) == int:
            if simplepub.ble.is_installed:
                asyncio.create_task(
                    simplepub.ble.serve(lambda s: onConnect(s, node, args)))
            else:
                print(f"BLE interface not supported")
            print(f"Starting websocket responder on port {url}")
            async with websockets.serve(lambda s: onConnect(s, node, args),
                                        "0.0.0.0", url):
                await stop
        else:
            print(f"Connecting to {url}")
            async with websockets.connect(url) as wsock:
                wsock.nm = 'w'
                await onConnect(wsock, node, args)
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass

async def mainIn(data, url):
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    if platform.system() != 'Windows':
        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    if url is None:
        url = "ws://127.0.0.1:8080"
    
    role = 'in' #developer will always be the initiator

    node = simplepub.node.PubNode(data, role)

    #initialize args
    args = type('', (), {})()
    args.v = True
    args.uri_or_port = url
    args.ble = False
    args.data = data
    args.role = role


    try:
        if type(url) == int:
            if simplepub.ble.is_installed:
                asyncio.create_task(
                    simplepub.ble.serve(lambda s: onConnect(s, node, args)))
            else:
                print(f"BLE interface not supported")
            print(f"Starting websocket responder on port {url}")
            async with websockets.serve(lambda s: onConnect(s, node, args),
                                        "0.0.0.0", url):
                await stop
        else:
            print(f"Connecting to {url}")
            async with websockets.connect(url) as wsock:
                wsock.nm = 'w'
                await onConnect(wsock, node, args)
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass
