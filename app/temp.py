import asyncio
import time
async def f1():
    print("started f1:")
    await asyncio.sleep(2)
    print("ended f1.")
    
async def f2():
    print("started f2:")
    await asyncio.sleep(2)
    print("ended f2.")

async def main():
    await asyncio.gather(f2(), f1())
    
asyncio.run(main())