#!/usr/bin/env python3
"""
Complete Customer Success FTE System Startup Script
This script starts all necessary services for the complete system operation.
"""

import os
import sys
import subprocess
import signal
import time
import threading
from pathlib import Path

def run_service(service_name, cmd, cwd=None):
    """Run a service in a subprocess and return the process"""
    print(f"🚀 Starting {service_name}...")

    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd or os.getcwd(),
            text=True
        )

        # Wait a bit to see if there are immediate startup errors
        time.sleep(2)

        # Check if process is still running after startup
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ {service_name} failed to start:")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            return None

        print(f"✅ {service_name} started successfully")
        return process
    except Exception as e:
        print(f"❌ Error starting {service_name}: {e}")
        return None

def main():
    """Main function to start all services"""
    print("🚀 Starting Customer Success FTE System...")
    print("=" * 50)

    # Change to the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # List to store all running processes
    processes = []

    try:
        # Start the main API server
        print("\n1. Starting Main API Server...")
        api_process = run_service(
            "Main API Server",
            "python -m src.api.main",
            cwd=str(project_root)
        )

        if api_process:
            processes.append(("Main API Server", api_process))

        # Start the message processor
        print("\n2. Starting Message Processor...")
        processor_process = run_service(
            "Message Processor",
            "python -m src.workers.message_processor",
            cwd=str(project_root)
        )

        if processor_process:
            processes.append(("Message Processor", processor_process))

        print("\n" + "=" * 50)
        print("✅ All services started successfully!")
        print("\n📊 Service Status:")
        for name, proc in processes:
            print(f"   {name}: PID {proc.pid if proc.poll() is None else 'STOPPED'}")

        print(f"\n🌐 Access the system at: http://localhost:8000/")
        print(f"📧 Email interface: http://localhost:8000/email")
        print(f"💬 WhatsApp interface: http://localhost:8000/whatsapp")
        print(f"📝 Web form: http://localhost:8000/web-form")
        print("\n⚠️  Press Ctrl+C to stop all services")
        print("=" * 50)

        # Wait for all processes to finish (or until interrupted)
        try:
            while True:
                time.sleep(1)

                # Check if any process has died
                for i, (name, proc) in enumerate(processes):
                    if proc.poll() is not None:
                        print(f"\n⚠️  {name} died unexpectedly (PID: {proc.pid})")
                        stdout, stderr = proc.communicate()
                        if stdout:
                            print(f"   stdout: {stdout}")
                        if stderr:
                            print(f"   stderr: {stderr}")
                        print(f"   Restarting {name}...")

                        # Restart the service
                        if name == "Main API Server":
                            new_proc = run_service(
                                "Main API Server",
                                "python -m src.api.main",
                                cwd=str(project_root)
                            )
                        elif name == "Message Processor":
                            new_proc = run_service(
                                "Message Processor",
                                "python -m src.workers.message_processor",
                                cwd=str(project_root)
                            )

                        if new_proc:
                            processes[i] = (name, new_proc)

        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down services...")

            # Terminate all processes
            for name, proc in processes:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)  # Wait up to 5 seconds
                except subprocess.TimeoutExpired:
                    proc.kill()  # Force kill if it doesn't respond
                print(f"✅ {name} stopped")

            print("\n👋 Customer Success FTE System stopped.")

    except Exception as e:
        print(f"\n❌ Error starting system: {e}")
        # Try to stop any running processes
        for name, proc in processes:
            try:
                proc.terminate()
            except:
                pass
        print("\n⚠️  Attempted to clean up processes.")

if __name__ == "__main__":
    main()