import pyperclip
from bleak import BleakClient, BleakScanner
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice
import asyncio
import typer
from dataclasses import dataclass
from typing import Optional

# Define the service and characteristic UUIDs
SERVICE_UUID = "12345678-1234-1234-1234-123456789012"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-210987654321"

typerApp = typer.Typer()

@dataclass
class ClipboardSnapshot:
    current_data: str
    previous_data: str

    def has_changed(self) -> bool:
        return self.current_data != self.previous_data


class EspPaste:
    def __init__(self):
        self._previous_clipboard = ""
        self.watch = False
        self._is_connecting = False
        self._client: Optional[BleakClient] = None
        self._scanner = BleakScanner(
            service_uuids=[SERVICE_UUID], detection_callback=self.detection_callback
        )

    async def start_ble_scanning(self):
        await self._scanner.start()

    async def write_text_to_characteristic(self, text: str):
        if not isinstance(text, str):
            return
        data_bytes = bytes(text, "utf-8")
        if self._client != None and self._client.is_connected:
            await self._client.write_gatt_char(CHARACTERISTIC_UUID, data_bytes)
        print("synced clipboard data to device")

    def get_clipboard_data(self) -> str:
        return pyperclip.paste()

    def snapshot_clipboard(self) -> ClipboardSnapshot:
        return ClipboardSnapshot(self.get_clipboard_data(), self._previous_clipboard)

    def detection_callback(self, device: BLEDevice, advertisement_data: AdvertisementData):
        print(device.address, advertisement_data)
        if self._client == None and SERVICE_UUID in advertisement_data.service_uuids:
            asyncio.create_task(self.perform_command(device))
        

    async def perform_command(self, device: BLEDevice):
        self._is_connecting = True
        await self._scanner.stop()
        await self.connect_to_device(device)
        
        if not self.watch:
            await self.write_text_to_characteristic(
                self.get_clipboard_data()
            )
        else:
            await self.listen_clipboard_loop()

    def disconnected_callback(self, client: BleakClient):
        self._client = None
        self._is_connecting = False
        asyncio.create_task(self.start_ble_scanning())
        print(f"Disconnected from {client.address}")

    async def listen_clipboard_loop(self):
        while self._client != None and self._client.is_connected:
            clipboard = self.snapshot_clipboard()
            if clipboard.has_changed():
                self._previous_clipboard = clipboard.current_data
                await self.write_text_to_characteristic(clipboard.current_data)
            await asyncio.sleep(1)

    async def connect_to_device(self, device: BLEDevice):
        if self._client != None:
            return
        self._client = BleakClient(
            device.address, disconnected_callback=self.disconnected_callback
        )
        await self._client.connect()
        self._is_connecting = False

    async def close(self):
        if self._client != None:
            await self._client.disconnect()


async def main_async(watch):
    try:
        app = EspPaste()
        app.watch = watch
        await app.start_ble_scanning()
        while True:
            await asyncio.sleep(1)
    finally:
        await app.close()

@typerApp.command("sync")
def sync_command():
    pass

@typerApp.command()
def main(watch: bool = typer.Option(False, help="Watch clipboard and sync changes"), value: Optional[str] = typer.Option(None, help="Value to sync to device")):

    asyncio.run(main_async(watch))


if __name__ == "__main__":
    typerApp()
