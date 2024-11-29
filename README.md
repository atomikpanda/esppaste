# ESP Paste (Wireless USB clipboard)

This is the script to send text to your ESP32-S3 device over BLE. 

 The board receives text over BLE (Bluetooth Low Energy) and emulates a USB HID (keyboard) to type out the clipboard contents when a designated button is pressed.

## Install the Firmware on your board
Follow the instructions in the firmware repo before proceeding:
https://github.com/atomikpanda/esppaste_firmware

## Getting Started

### Setting up a Virtual Environment

1. Open your terminal.
2. Navigate to your project directory:
    ```sh
    cd /Users/atomikpanda/Development/Repos/esppaste
    ```
3. Create a virtual environment:
    ```sh
    python3 -m venv venv
    ```
4. Activate the virtual environment:
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```

### Installing Requirements

1. Ensure your virtual environment is activated.
2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

You are now ready to use the ESP Paste script.