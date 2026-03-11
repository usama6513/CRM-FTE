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
import webbrowser

def run_service(service_name, cmd, cwd=None):
    """Run a service in a subprocess and return the process"""
    print(f"[START] Starting {service_name}...")

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
        time.sleep(3)

        # Check if process is still running after startup
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"[WARN] {service_name} had startup messages:")
            if stdout:
                print(f"   stdout: {stdout.strip()}")
            if stderr and "pydantic" not in stderr.lower():  # Ignore pydantic warnings for now
                print(f"   stderr: {stderr.strip()}")
            # Still return the process as it might be running despite warnings
            return process

        print(f"[OK] {service_name} started successfully")
        return process
    except Exception as e:
        print(f"[ERROR] Error starting {service_name}: {e}")
        return None

def main():
    """Main function to start all services"""
    print("[START] Starting Customer Success FTE System...")
    print("=" * 60)
    print("This system provides: Multi-channel support (Email, WhatsApp, Web)")
    print("AI-powered customer success agent with 24/7 availability")
    print("Enterprise-grade reliability and scalability")
    print("=" * 60)

    # Change to the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # List to store all running processes
    processes = []

    try:
        # First, start our working UI server that provides all channel interfaces
        print("\n1. Starting Multi-Channel UI Server...")
        ui_process = run_service(
            "Multi-Channel UI Server",
            "python run_project_full.py",
            cwd=str(project_root)
        )

        if ui_process:
            processes.append(("Multi-Channel UI Server", ui_process))

        # Start the message processor
        print("\n2. Starting AI Message Processor...")
        processor_process = run_service(
            "AI Message Processor",
            "python -m src.workers.message_processor",
            cwd=str(project_root)
        )

        if processor_process:
            processes.append(("AI Message Processor", processor_process))

        print(f"\n[INFO] Opening browser to main interface...")
        time.sleep(2)  # Wait for servers to fully start
        webbrowser.open("http://localhost:8082/")  # Our working UI server

        print("\n" + "=" * 60)
        print("[OK] Customer Success FTE System is now running!")
        print("\n📊 Active Services:")
        for name, proc in processes:
            status = "RUNNING" if proc.poll() is None else "STOPPED"
            print(f"   - {name}: PID {proc.pid if proc.poll() is None else 'ERROR'} ({status})")

        print(f"\n🔗 System Access Points:")
        print(f"   Dashboard: http://localhost:8082/")
        print(f"   WhatsApp Interface: http://localhost:8082/whatsapp.html")
        print(f"   WhatsApp-Style: http://localhost:8082/whatsapp-style.html")
        print(f"   Email Interface: http://localhost:8082/email.html")
        print(f"   Web Form: http://localhost:8082/web_form.html")
        print(f"   API Status: http://localhost:8082/health")

        print(f"\n⚡ Features Active:")
        print(f"   • Multi-channel message handling (Email, WhatsApp, Web Form)")
        print(f"   • AI-powered customer success agent")
        print(f"   • Real-time channel interface")
        print(f"   • Cross-channel customer context")
        print(f"   • Automatic escalation to human agents")
        print(f"   • Enterprise security and monitoring")

        print(f"\n🎯 Channel-Specific Endpoints:")
        print(f"   POST /api/whatsapp/send - Process WhatsApp messages")
        print(f"   POST /api/email/send - Process email messages")
        print(f"   POST /api/web-form/submit - Process web form submissions")
        print(f"   POST /api/support/submit - Legacy web form endpoint")
        print(f"   GET /conversations/{{conversation_id}} - Get conversation history")
        print(f"   GET /customers/lookup?email={{email}} - Look up customer")

        print(f"\n[INFO] Press Ctrl+C to stop all services")
        print("=" * 60)

        # Wait for all processes to finish (or until interrupted)
        try:
            while True:
                time.sleep(1)

                # Check if any process has died
                for i, (name, proc) in enumerate(processes):
                    if proc.poll() is not None:
                        print(f"\n[WARN] {name} died unexpectedly (PID: {proc.pid})")
                        try:
                            stdout, stderr = proc.communicate(timeout=1)
                            if stdout:
                                print(f"   stdout: {stdout}")
                            if stderr:
                                print(f"   stderr: {stderr}")
                        except:
                            pass
                        print(f"   Attempting to restart {name}...")

                        # Restart the service
                        if name == "Multi-Channel UI Server":
                            new_proc = run_service(
                                "Multi-Channel UI Server",
                                "python run_project_full.py",
                                cwd=str(project_root)
                            )
                        elif name == "AI Message Processor":
                            new_proc = run_service(
                                "AI Message Processor",
                                "python -m src.workers.message_processor",
                                cwd=str(project_root)
                            )

                        if new_proc:
                            processes[i] = (name, new_proc)

        except KeyboardInterrupt:
            print("\n\n[STOP] Shutting down Customer Success FTE System...")

            # Terminate all processes
            for name, proc in processes:
                try:
                    proc.terminate()
                    try:
                        proc.wait(timeout=10)  # Wait up to 10 seconds
                    except subprocess.TimeoutExpired:
                        proc.kill()  # Force kill if it doesn't respond
                    print(f"[STOP] {name} stopped")
                except Exception as e:
                    print(f"[ERROR] Error stopping {name}: {e}")

            print(f"\n[STOP] Customer Success FTE System has been stopped.")
            print(f"Thank you for using the Customer Success FTE solution!")

    except Exception as e:
        print(f"\n[ERROR] Error starting Customer Success FTE System: {e}")
        # Try to stop any running processes
        for name, proc in processes:
            try:
                proc.terminate()
            except:
                pass
        print("\n[WARN] Attempted to clean up processes.")

if __name__ == "__main__":
    main()