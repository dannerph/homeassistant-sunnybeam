# Sunny Beam [[Home Assistant](https://www.home-assistant.io/) Component]

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

This custom component integrates the SMA Sunny Beam into Home Assistant. The sensor values are fetched via USB.

## Installation

Copy content of custom_components to your local custom_components folder and add the following lines to your configuration.

In order to allow non-root users and thus Home Assistant to access the USB device, add the following udev rule (```/etc/udev/rules.d/99-sma-sunny-beam.rules```), re-plug the Sunny Beam and restart Home Assistant.

```bash
SUBSYSTEMS=="usb", ATTRS{idVendor}=="1587", ATTRS{idProduct}=="002d", MODE="666"
```

## Configuration

```yaml
sunnybeam:
  scan_interval: 10
```

Configuration variables:

* **scan_interval** (optional): How often new data values should be fetched. In seconds, default 10 seconds. You might want to adjust the update interval also in our Sunny Beam (7 - 120s)
