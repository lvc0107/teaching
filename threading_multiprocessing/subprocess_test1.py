import asyncio
import subprocess


async def run_command_with_create_subprocess_shell(cmd):
    print(f"Running command: {cmd}")
    process = await asyncio.create_subprocess_shell(
        cmd,
    )
    stdout, stderr = await process.communicate()
    print(f"Command finished with return code {process.returncode}")
    if stdout:
        print(f"Standard Output:\n{stdout.decode()}")
    if stderr:
        print(f"Standard Error:\n{stderr.decode()}")


async def run_command_with_asyncio_to_thread(cmd):
    print(f"Running command: {cmd}")
    process = await asyncio.to_thread(
        subprocess.run,
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,

    )
    stdout, stderr = await process.communicate()
    print(f"Command finished with return code {process.returncode}")
    if stdout:
        print(f"Standard Output:\n{stdout.decode()}")
    if stderr:
        print(f"Standard Error:\n{stderr.decode()}")


commands = [
    ["whoami"],
    ["ping", "-c", "5", "google.com"],
    #["lsb_release", "-a"],
    ["python", "--version"],
]


async def main():
    tasks = []
    for cmd in commands:
        task = asyncio.create_task(run_command_with_asyncio_to_thread(cmd))
        tasks.append(task)
    await asyncio.gather(*tasks)


asyncio.run(main())
